"""Browser contract, run using an interpreter with Playwright + Chromium installed."""
import argparse
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

p=argparse.ArgumentParser();p.add_argument('artifact',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
a.out.mkdir(parents=True,exist_ok=True)
URL=a.artifact.resolve().as_uri()
report={'viewports':[],'scenes':[],'fallbacks':[],'interactions':[]}

def settle(page,ms=900): page.wait_for_timeout(ms)
def scroll(page,y): page.evaluate('(y)=>scrollTo({top:y,behavior:"instant"})',y);settle(page)
def rects(page):
    return page.evaluate('''() => [...document.querySelectorAll('body *')].filter(e=>{
      if(e.closest('svg')||e.matches('.skip,.pin-spacer,.mk-progress')||e.closest('[inert]'))return false;
      const r=e.getBoundingClientRect(),s=getComputedStyle(e);
      if(!r.width||!r.height||s.visibility==='hidden'||s.display==='none')return false;
      if(e.closest('details:not([open])')&&!e.closest('summary')&&!e.matches('details'))return false;
      return r.left < -1 || r.right > innerWidth+1;
    }).map(e=>({tag:e.tagName,cls:e.className,left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right}))''')

with sync_playwright() as pw:
 b=pw.chromium.launch()
 for width,height in [(320,740),(390,844),(768,1024),(1024,768),(1440,900),(1024,600)]:
  context=b.new_context(viewport={'width':width,'height':height},is_mobile=width<700,has_touch=width<700,offline=True)
  page=context.new_page();errors=[];remote=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('request',lambda r:remote.append(r.url) if r.url.startswith(('http:','https:')) else None)
  page.goto(URL);settle(page,1600)
  assert not errors,errors
  assert not remote,remote
  assert not rects(page),rects(page)
  page.screenshot(path=str(a.out/f'hero-{width}x{height}.png'))
  state=page.evaluate('VentureStory.getState()')
  expected='pinned' if width>=1024 and height>=720 else 'static'
  assert state['mode']==expected,state
  if expected=='pinned':
   hashes=[]
   for i,f in enumerate([.08,.34,.60,.87]):
    scroll(page,state['pinStart']+(state['pinEnd']-state['pinStart'])*f)
    s=page.evaluate('VentureStory.getState()')
    assert s['active']==i,s
    assert abs(s['progress']-f)<.015,s
    assert float(s['chapterStyles'][i]['opacity'])>.99,s
    assert sum(not z['inert'] for z in s['chapterStyles'])==1,s
    assert not rects(page),rects(page)
    # All visible chapter content must sit above the navigation, not behind it.
    box=page.locator('.chapter').nth(i).locator('.chapter-copy').bounding_box()
    nav=page.locator('.chapter-nav').bounding_box()
    assert box['y']+box['height'] <= nav['y']+1,(box,nav)
    img=page.screenshot(path=str(a.out/f'scene-{width}-{i}.png'))
    hashes.append(hashlib.sha256(img).hexdigest())
    report['scenes'].append({'width':width,'fraction':f,'active':s['active'],'opacity':s['chapterStyles'][i]['opacity']})
   assert len(set(hashes))==4
   for i in [0,3,1,2]:
    page.locator(f'[data-chapter-jump="{i}"]').click();settle(page,1100)
    assert page.evaluate('VentureStory.getState().active')==i
   # Reverse scroll recovers the first chapter.
   scroll(page,state['pinStart']+50);assert page.evaluate('VentureStory.getState().active')==0
   page.emulate_media(reduced_motion='reduce');settle(page)
   assert page.evaluate('VentureStory.getState().mode')=='static'
   assert page.locator('.pin-spacer').count()==0
   assert page.locator('.chapter[inert]').count()==0
   page.emulate_media(reduced_motion='no-preference');settle(page)
   assert page.evaluate('VentureStory.getState().mode')=='pinned'
  else:
   assert page.locator('.chapter[inert]').count()==0
  # Each filter, details disclosure and accessible destination remains live.
  for key,count in [('data',4),('founders',4),('wellness',3),('infrastructure',1),('all',12)]:
   el=page.locator(f'[data-filter="{key}"]')
   el.scroll_into_view_if_needed();el.tap() if width<700 else el.click();settle(page,700)
   assert page.locator('.venture:not([hidden])').count()==count
   assert el.get_attribute('aria-pressed')=='true'
   assert page.locator('.filter-status').inner_text()==f'Showing {count} '+('venture' if count==1 else 'ventures')
   assert not rects(page),rects(page)
  for i in range(12):
   summary=page.locator('.venture summary').nth(i)
   summary.click();assert page.locator('.venture').nth(i).get_attribute('open') is not None
   link=page.locator('.venture').nth(i).locator('.venture-body a')
   assert link.is_visible()
   assert link.get_attribute('href').startswith(('https://','mailto:'))
   summary.click()
  if width<1024:
   scroll(page,0)
   button=page.locator('.menu-toggle');button.tap() if width<700 else button.click()
   assert button.get_attribute('aria-expanded')=='true'
   assert page.locator('#mobile-nav').is_visible()
   page.screenshot(path=str(a.out/f'menu-{width}.png'))
   page.keyboard.press('Escape');assert page.locator('#mobile-nav').is_hidden()
   button.click();page.locator('#mobile-nav a[href="#portfolio"]').click();settle(page)
   assert page.locator('#mobile-nav').is_hidden()
  for section in ['connection','reach','portfolio','contact']:
   page.locator('#'+section).scroll_into_view_if_needed();settle(page)
   assert not rects(page),rects(page)
   if width in [390,1440]: page.screenshot(path=str(a.out/f'{section}-{width}.png'))
  assert not errors,errors
  report['viewports'].append({'width':width,'height':height,'mode':expected,'errors':errors,'externalRequests':remote,'overflow':[]})
  report['interactions'].append({'width':width,'filters':5,'disclosures':12,'chapterControls':expected=='pinned','mobileMenu':width<1024})
  context.close()
 # Initial reduced-motion, JavaScript-off and missing-library surfaces.
 for mode in ['reduce','no-js','no-gsap']:
  ctx=b.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce' if mode=='reduce' else 'no-preference',java_script_enabled=mode!='no-js',offline=True)
  page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  if mode=='no-gsap':
   # Remove the vendor globals immediately before application initialization.
   content=a.artifact.read_text().replace('/* Venture Story.','window.gsap=undefined;window.ScrollTrigger=undefined;\n/* Venture Story.')
   file=a.out/'no-gsap.html';file.write_text(content);page.goto(file.resolve().as_uri())
  else: page.goto(URL)
  settle(page,1500)
  assert page.locator('.is-pinned').count()==0
  assert page.locator('.chapter[inert]').count()==0
  assert page.locator('.chapter').count()==4
  for i in range(4):
   page.locator('.chapter').nth(i).scroll_into_view_if_needed();settle(page)
   assert page.locator('.chapter').nth(i).is_visible()
  if mode=='reduce':
   assert page.evaluate('document.getAnimations().filter(a=>a.playState==="running").length')==0
   page.locator('[data-filter="wellness"]').click();assert page.locator('.venture:not([hidden])').count()==3
  page.screenshot(path=str(a.out/f'fallback-{mode}.png'))
  assert not errors,errors
  report['fallbacks'].append({'mode':mode,'allChaptersVisible':True,'errors':errors})
  ctx.close()
 # Hover feedback: magnetic, swap, underline, spot; geometry returns after leave.
 ctx=b.new_context(viewport={'width':1440,'height':900});page=ctx.new_page();page.goto(URL);settle(page,1500)
 for selector,prop in [('.hero [data-mk="magnetic"]','--mx'),('.venture','--sx')]:
  el=page.locator(selector).first;el.scroll_into_view_if_needed();box=el.bounding_box()
  page.mouse.move(box['x']+box['width']*.8,box['y']+box['height']*.6);settle(page,400)
  value=el.evaluate('(e,p)=>e.style.getPropertyValue(p)',prop);assert value
  page.mouse.move(0,0);settle(page,400)
  if prop=='--mx':assert el.evaluate('(e,p)=>e.style.getPropertyValue(p)',prop)=='0px'
 report['interactions'].append({'hover':'magnetic and spot values changed; magnetic reset'})
 b.close()
(a.out/'browser-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'result':'PASS','viewports':len(report['viewports']),'sceneSamples':len(report['scenes']),'fallbacks':len(report['fallbacks'])}))
