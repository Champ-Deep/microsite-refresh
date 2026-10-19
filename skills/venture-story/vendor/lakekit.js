/* LakeKit v1: attribute-driven micro-interactions and scroll choreography. Vanilla JS, no dependencies.
   GSAP + ScrollTrigger are only needed for LakeKit.journey(). Reduced motion and touch are respected throughout. */
(function(){
"use strict";
var RM=window.matchMedia("(prefers-reduced-motion: reduce)").matches,
    FINE=window.matchMedia("(hover:hover) and (pointer:fine)").matches,
    HASIO="IntersectionObserver" in window;
function $$(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s));}
function mk(k){return $$('[data-mk~="'+k+'"]');}
var LK=window.LakeKit={};

/* magnetic */
if(FINE&&!RM)mk("magnetic").forEach(function(el){
  el.addEventListener("pointermove",function(e){var r=el.getBoundingClientRect();
    el.style.setProperty("--mx",((e.clientX-(r.left+r.width/2))*0.10).toFixed(1)+"px");
    el.style.setProperty("--my",((e.clientY-(r.top+r.height/2))*0.18).toFixed(1)+"px");});
  el.addEventListener("pointerleave",function(){el.style.setProperty("--mx","0px");el.style.setProperty("--my","0px");});
});

/* glow */
mk("glow").forEach(function(el){
  ["a","b"].forEach(function(c){var s=document.createElement("span");s.className="mk-g "+c;s.setAttribute("aria-hidden","true");el.appendChild(s);});
  if(FINE&&!RM){
    el.addEventListener("pointermove",function(e){var r=el.getBoundingClientRect();el.style.setProperty("--glow-x",Math.max(0,Math.min(100,(e.clientX-r.left)/r.width*100)).toFixed(1)+"%");});
    el.addEventListener("pointerleave",function(){el.style.setProperty("--glow-x","50%");});
  }
});

/* swap: text-only elements. The label stays readable through aria-label */
mk("swap").forEach(function(el){
  if(el.children.length)return;
  var label=el.textContent.replace(/\s+/g," ").trim(),w=document.createElement("span");
  w.className="mk-sw";w.setAttribute("aria-hidden","true");
  label.split("").forEach(function(ch,i){
    var l=document.createElement("span"),a=document.createElement("span"),b=document.createElement("span");
    l.className="mk-l";l.style.setProperty("--i",i);a.textContent=b.textContent=ch===" "?" ":ch;l.appendChild(a);l.appendChild(b);w.appendChild(l);
  });
  el.setAttribute("aria-label",label);el.textContent="";el.appendChild(w);
});

/* spot and tilt */
if(FINE&&!RM){
  mk("spot").forEach(function(el){
    el.addEventListener("pointermove",function(e){var r=el.getBoundingClientRect();el.style.setProperty("--sx",(e.clientX-r.left).toFixed(0)+"px");el.style.setProperty("--sy",(e.clientY-r.top).toFixed(0)+"px");});
  });
  mk("tilt").forEach(function(el){
    el.addEventListener("pointermove",function(e){var r=el.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-0.5,y=(e.clientY-r.top)/r.height-0.5;
      el.style.setProperty("--ry",(x*8).toFixed(2)+"deg");el.style.setProperty("--rx",(-y*8).toFixed(2)+"deg");});
    el.addEventListener("pointerleave",function(){el.style.setProperty("--rx","0deg");el.style.setProperty("--ry","0deg");});
  });
  mk("aura").forEach(function(el){
    el.addEventListener("pointermove",function(e){var r=el.getBoundingClientRect();el.style.setProperty("--ax",(e.clientX-r.left).toFixed(0)+"px");el.style.setProperty("--ay",(e.clientY-r.top).toFixed(0)+"px");});
  });
}

/* slide: one indicator follows the active child. data-mk-slide="selector" (default: aria-pressed, aria-selected or .is-active) */
$$("[data-mk-slide]").forEach(function(box){
  var ind=document.createElement("span");ind.className="mk-ind";ind.setAttribute("aria-hidden","true");box.insertBefore(ind,box.firstChild);
  var sel=box.getAttribute("data-mk-slide")||"[aria-pressed='true'],[aria-selected='true'],.is-active";
  function place(instant){
    var a=box.querySelector(sel);if(!a){ind.style.opacity="0";return;}
    if(instant)ind.style.transition="none";
    ind.style.opacity="1";ind.style.width=a.offsetWidth+"px";ind.style.height=a.offsetHeight+"px";
    ind.style.transform="translate("+a.offsetLeft+"px,"+a.offsetTop+"px)";
    if(instant){void ind.offsetWidth;ind.style.transition="";}
  }
  place(true);
  if(window.MutationObserver)new MutationObserver(function(){place(false);}).observe(box,{attributes:true,subtree:true,attributeFilter:["aria-pressed","aria-selected","class"]});
  if(window.ResizeObserver)new ResizeObserver(function(){place(true);}).observe(box);
  if(document.fonts&&document.fonts.ready)document.fonts.ready.then(function(){place(true);});
});

/* reveal, split, count: all fire once when the element enters the viewport */
var rootEl=document.documentElement;
function onceVisible(els,fn,opt){
  if(!els.length)return;
  if(!HASIO||RM){els.forEach(function(e){fn(e,true);});return;}
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){fn(e.target,false);io.unobserve(e.target);}});},opt||{threshold:0.15,rootMargin:"0px 0px -6% 0px"});
  els.forEach(function(e){io.observe(e);});
}
if(rootEl.classList.contains("rv-on"))onceVisible($$(".rv,[data-mk~='reveal'],.finale-glow,[data-reveal]"),function(el){el.classList.add("in");});

mk("split").forEach(function(el){
  if(RM||!HASIO)return;
  var n=0,walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT),nodes=[];
  while(walker.nextNode())nodes.push(walker.currentNode);
  el.setAttribute("aria-label",el.textContent.replace(/\s+/g," ").trim());
  nodes.forEach(function(t){
    var parts=t.nodeValue.split(/(\s+)/),f=document.createDocumentFragment();
    parts.forEach(function(p){
      if(!p)return;
      if(/^\s+$/.test(p)){f.appendChild(document.createTextNode(" "));return;}
      var w=document.createElement("span"),i=document.createElement("i");w.className="mk-w";w.setAttribute("aria-hidden","true");i.textContent=p;i.style.setProperty("--i",n++);w.appendChild(i);f.appendChild(w);
    });
    t.parentNode.replaceChild(f,t);
  });
  onceVisible([el],function(e){e.classList.add("in");},{threshold:0.3});
});

/* count: animates the number inside the text, keeps prefix and suffix, restores the exact original text at the end */
$$("[data-mk-count]").forEach(function(el){
  var txt=el.textContent,m=txt.match(/^([^\d-]*)(-?[\d,]*\.?\d+)(.*)$/);if(!m||RM||!HASIO)return;
  var dec=(m[2].split(".")[1]||"").length,to=parseFloat(m[2].replace(/,/g,""));
  onceVisible([el],function(e){
    var t0=performance.now(),dur=1500;
    (function step(now){var k=Math.min(1,(now-t0)/dur),v=to*(1-Math.pow(2,-10*k));if(k===1)v=to;
      e.textContent=m[1]+v.toLocaleString("en-US",{minimumFractionDigits:dec,maximumFractionDigits:dec})+m[3];
      if(k<1)requestAnimationFrame(step);else e.textContent=txt;})(t0);
  },{threshold:0.6});
});

/* rail: build a side navigation from [data-rail="Label"] sections */
(function(){
  var secs=$$("[data-rail]");if(!secs.length)return;
  var nav=document.createElement("nav"),bar=document.createElement("span");nav.className="mk-rail";nav.setAttribute("aria-label","Page sections");bar.className="mk-rail-bar";nav.appendChild(bar);
  secs.forEach(function(s){
    var a=document.createElement("a");a.href="#"+s.id;a.innerHTML="<i></i><span></span>";a.lastChild.textContent=s.getAttribute("data-rail");nav.appendChild(a);s._a=a;
    a.addEventListener("click",function(e){e.preventDefault();s.scrollIntoView({behavior:RM?"auto":"smooth",block:"start"});});
  });
  document.body.appendChild(nav);
  var cur=null,tick=false;
  function update(){
    tick=false;var vh=window.innerHeight,hit=null;
    secs.forEach(function(s){var r=s.getBoundingClientRect();if(r.top<=vh*0.5&&r.bottom>vh*0.5)hit=s;});
    nav.classList.toggle("on",!!hit);
    if(hit&&hit!==cur){cur=hit;secs.forEach(function(s){s._a.classList.toggle("cur",s===hit);});
      requestAnimationFrame(function(){var a=hit._a;bar.style.top=a.offsetTop+5+"px";bar.style.height=a.offsetHeight-10+"px";});}
  }
  window.addEventListener("scroll",function(){if(!tick){tick=true;requestAnimationFrame(update);}},{passive:true});
  window.addEventListener("resize",function(){cur=null;update();});update();
})();

/* progress bar */
if(document.body.hasAttribute("data-mk-progress")){
  var pb=document.createElement("div");pb.className="mk-progress";pb.setAttribute("aria-hidden","true");document.body.appendChild(pb);
  var pt=false;function pu(){pt=false;var h=document.documentElement.scrollHeight-window.innerHeight;pb.style.transform="scaleX("+(h>0?Math.min(1,window.scrollY/h):0).toFixed(4)+")";}
  window.addEventListener("scroll",function(){if(!pt){pt=true;requestAnimationFrame(pu);}},{passive:true});pu();
}

/* journey: scrubbed pinned scene. Sets --p (0 to 1) on the element and fires "lk:progress". Needs gsap + ScrollTrigger. */
LK.journey=function(el,o){
  o=o||{};
  if(RM||!window.gsap||!window.ScrollTrigger){el.style.setProperty("--p",o.reducedTo==null?"1":o.reducedTo);return null;}
  gsap.registerPlugin(ScrollTrigger);var st={p:0};
  return gsap.to(st,{p:1,ease:"none",onUpdate:function(){el.style.setProperty("--p",st.p.toFixed(4));el.dispatchEvent(new CustomEvent("lk:progress",{detail:st.p}));},
    scrollTrigger:{trigger:el,start:"top top",end:"bottom bottom",scrub:o.scrub==null?0.8:o.scrub}});
};
$$("[data-mk-journey]").forEach(function(el){LK.journey(el);});
})();
