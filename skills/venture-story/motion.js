/* Venture Story. Static HTML is the baseline; GSAP enhances only capable viewports. */
(() => {
  'use strict';
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];
  const clamp = (n, min = 0, max = 1) => Math.min(max, Math.max(min, n));
  const menu = $('.menu-toggle');
  const mobileNav = $('#mobile-nav');
  function closeMenu(returnFocus = false) {
    mobileNav.hidden = true;
    menu.setAttribute('aria-expanded', 'false');
    menu.setAttribute('aria-label', 'Open navigation');
    if (returnFocus) menu.focus();
  }
  menu.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    mobileNav.hidden = !open;
  });
  mobileNav.addEventListener('click', e => { if (e.target.closest('a')) closeMenu(); });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && !mobileNav.hidden) closeMenu(true);
  });
  document.addEventListener('click', e => {
    if (!e.target.closest('.site-header') && !mobileNav.hidden) closeMenu();
  });

  window.addEventListener('resize', () => { if (innerWidth >= 1024) closeMenu(); });
  const filters = $$('[data-filter]');
  const ventures = $$('.venture');
  const status = $('.filter-status');
  let currentFilter = 'all';
  function filterVentures(id) {
    if (!filters.some(f => f.dataset.filter === id)) return;
    currentFilter = id;
    filters.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.filter === id)));
    ventures.forEach(v => { v.hidden = id !== 'all' && v.dataset.group !== id; });
    const n = ventures.filter(v => !v.hidden).length;
    status.textContent = `Showing ${n} ${n === 1 ? 'venture' : 'ventures'}`;
    if (window.ScrollTrigger) ScrollTrigger.refresh();
  }
  filters.forEach(b => b.addEventListener('click', () => filterVentures(b.dataset.filter)));
  $$('[data-show-group]').forEach(link => link.addEventListener('click', () => {
    filterVentures(link.dataset.showGroup);
    const heading = $('#portfolio-title');
    heading.setAttribute('tabindex', '-1');
    heading.focus({preventScroll: true});
  }));
  ventures.forEach(v => v.addEventListener('toggle', () => {
    if (window.ScrollTrigger) ScrollTrigger.refresh();
  }));

  const stage = $('.chapter-stage');
  const chapters = $$('.chapter');
  const jumps = $$('[data-chapter-jump]');
  let active = 0, timeline = null, pin = null;
  const diagnostics = { mode: 'static', progress: 0, hero: 0 };
  function activate(index) {
    active = index;
    chapters.forEach((chapter, i) => {
      chapter.inert = i !== index;
      chapter.setAttribute('aria-hidden', String(i !== index));
    });
    jumps.forEach((button, i) => {
      if (i === index) button.setAttribute('aria-current', 'step');
      else button.removeAttribute('aria-current');
    });
    $('.chapter-counter').textContent = `${String(index + 1).padStart(2, '0')} / ${String(chapters.length).padStart(2, '0')}`;
  }
  function restoreStatic() {
    stage.classList.remove('is-pinned');
    chapters.forEach(chapter => {
      chapter.inert = false;
      chapter.removeAttribute('aria-hidden');
    });
    diagnostics.mode = 'static';
    diagnostics.progress = 0;
    timeline = null;
    pin = null;
  }
  jumps.forEach(b => b.addEventListener('click', () => {
    const i = Number(b.dataset.chapterJump);
    if (pin && timeline) {
      const time = i * 1.2 + .46;
      window.scrollTo({top: pin.start + time / timeline.duration() * (pin.end - pin.start), behavior: 'auto'});
    } else chapters[i].scrollIntoView({behavior: 'auto'});
  }));
  window.VentureStory = Object.freeze({getState: () => ({...diagnostics, active, filter: currentFilter, visibleVentures: ventures.filter(v => !v.hidden).length, pinStart: pin?.start ?? null, pinEnd: pin?.end ?? null, chapterStyles: chapters.map(c => ({opacity:getComputedStyle(c).opacity,transform:getComputedStyle(c).transform,inert:c.inert}))})});

  if (!window.gsap || !window.ScrollTrigger) {
    document.body.dataset.ready = 'static';
    return;
  }
  gsap.registerPlugin(ScrollTrigger);
  const mm = gsap.matchMedia();
  mm.add('(prefers-reduced-motion: no-preference)', () => {
    const intro = gsap.timeline({defaults:{ease:'power3.out'}});
    intro.from('.hero-copy h1', {y:25,opacity:0,duration:.85}, .05)
      .from('.hero-copy .lede, .hero-copy .actions', {y:18,opacity:0,stagger:.1,duration:.7}, .25)
      .from('.hero-layer', {y:60,opacity:0,stagger:.13,duration:1}, .1)
      .from('.hero-label, .hero-axis', {opacity:0,duration:.75}, .7);
    gsap.to('.hero-layer', {y: (i) => (i-1.5)*24, ease:'none', scrollTrigger:{trigger:'.hero',start:'top top',end:'bottom top',scrub:.6}, onUpdate:()=> { diagnostics.hero = window.scrollY; }});
    const path = $('.line-draw');
    const length = path.getTotalLength();
    gsap.fromTo(path, {strokeDasharray:length,strokeDashoffset:length}, {strokeDashoffset:0,ease:'none',scrollTrigger:{trigger:'.statement',start:'top 75%',end:'bottom 60%',scrub:.5}});
    gsap.from('.reach .metrics .metric', {y:35,opacity:0,stagger:.12,duration:.8,ease:'power3.out',scrollTrigger:{trigger:'.metrics',start:'top 85%',once:true}});
    gsap.from('.closing h2', {y:50,duration:1,ease:'power3.out',scrollTrigger:{trigger:'.closing',start:'top 80%',once:true}});
    return () => { diagnostics.hero = 0; };
  });

  mm.add('(min-width:1024px) and (min-height:720px) and (prefers-reduced-motion:no-preference)', () => {
    stage.classList.add('is-pinned');
    diagnostics.mode = 'pinned';
    gsap.set(chapters, {autoAlpha:0,y:42});
    gsap.set(chapters[0], {autoAlpha:1,y:0});
    activate(0);
    const progress = $('.chapter-progress i');
    timeline = gsap.timeline({
      defaults:{ease:'power2.inOut'},
      scrollTrigger:{id:'venture-chapters',trigger:stage,start:'top top',end:()=>'+='+Math.round(innerHeight*3.5),pin:true,scrub:.65,invalidateOnRefresh:true},
      onUpdate() {
        diagnostics.progress = this.progress();
        const index = clamp(Math.floor((this.time()+.27)/1.2),0,chapters.length-1);
        if (index !== active) activate(index);
      }
    });
    timeline.to(progress,{scaleX:1,duration:4.6,ease:'none'},0);
    chapters.forEach((chapter,i) => {
      if (i) {
        timeline.to(chapters[i-1],{autoAlpha:0,y:-38,duration:.4},i*1.2-.35);
        timeline.fromTo(chapter,{autoAlpha:0,y:38},{autoAlpha:1,y:0,duration:.5},i*1.2-.22);
      }
      const units = $$('.visual-unit',chapter);
      timeline.fromTo(units,{y:26,rotation:-3},{y:0,rotation:0,stagger:.04,duration:.85},i*1.2);
      const lines = $$('.draw-path',chapter);
      lines.forEach(p => {
        const len=p.getTotalLength();
        timeline.fromTo(p,{strokeDasharray:len,strokeDashoffset:len},{strokeDashoffset:0,duration:.85,ease:'none'},i*1.2);
      });
    });
    pin = timeline.scrollTrigger;
    return restoreStatic;
  });
  document.fonts.ready.then(() => ScrollTrigger.refresh());
  window.addEventListener('load', () => ScrollTrigger.refresh(), {once:true});
  document.body.dataset.ready = 'true';
})();
