  /* ---------- list finder: search, tabs, mega menu (all links already exist in the HTML) ---------- */
  function norm(s){ return String(s||'').toLowerCase().replace(/[^a-z0-9 ]/g,' ').replace(/\s+/g,' ').trim(); }
  function find(q){
    q = norm(q); if (!q) return [];
    var hits = [], seen = {};
    function add(it, w){ if (!seen[it.u+it.t]){ seen[it.u+it.t]=1; hits.push({it:it, w:w}); } }
    FINDER.lists.forEach(function(it){
      var t = norm(it.t), g = norm(it.g);
      if (t.indexOf(q) === 0) add(it, 3); else if (t.indexOf(q) > -1) add(it, 2); else if (g.indexOf(q) > -1) add(it, 1);
    });
    Object.keys(FINDER.syn).forEach(function(k){
      if (q.indexOf(k) > -1 || (q.length > 2 && k.indexOf(q) === 0)) FINDER.lists.forEach(function(it){ if (it.t === FINDER.syn[k]) add(it, 2.5); });
    });
    return hits.sort(function(a,b){ return b.w - a.w; }).slice(0,8).map(function(h){ return h.it; });
  }
  function resultsFor(input){
    var box = input.parentNode.querySelector('.results');
    if (!box){ box = document.createElement('div'); box.className = 'results'; box.setAttribute('role','listbox'); input.insertAdjacentElement('afterend', box); }
    return box;
  }
  document.querySelectorAll('[data-finder-input]').forEach(function(input){
    input.addEventListener('input', function(){
      var box = resultsFor(input), q = input.value.trim();
      if (!q){ box.hidden = true; box.innerHTML = ''; return; }
      var r = find(q);
      box.innerHTML = r.length
        ? r.map(function(it){ return '<a role="option" href="' + it.u + '"><span>' + esc(it.t) + '</span><small>' + esc(it.g) + '</small></a>'; }).join('')
        : '<div class="nomatch"><p class="hand">No ready list for &ldquo;' + esc(q) + '&rdquo; yet.</p><p>We build custom lists for niches like this. Tell a strategist who you sell to and get counts back.</p><a class="btn btn-ink" href="#strategist"><span>Request a custom list</span><span class="arr"><i>&#8594;</i><i>&#8594;</i></span></a></div>';
      box.hidden = false;
    });
    input.addEventListener('keydown', function(e){
      if (e.key === 'Enter'){ var first = resultsFor(input).querySelector('a'); if (first){ e.preventDefault(); first.click(); } }
      if (e.key === 'Escape'){ input.value = ''; input.dispatchEvent(new Event('input')); }
    });
  });

  var finderEl = document.getElementById('lists');
  if (finderEl){
    finderEl.classList.add('tabbed');
    var tabsEls = finderEl.querySelectorAll('[role=tab]');
    function sel(btn){
      tabsEls.forEach(function(b){ var on = b === btn; b.setAttribute('aria-selected', on ? 'true' : 'false'); b.tabIndex = on ? 0 : -1; document.getElementById(b.getAttribute('aria-controls')).classList.toggle('on', on); });
    }
    tabsEls.forEach(function(b, i){
      b.addEventListener('click', function(){ sel(b); });
      b.addEventListener('keydown', function(e){ var d = e.key === 'ArrowDown' || e.key === 'ArrowRight' ? 1 : e.key === 'ArrowUp' || e.key === 'ArrowLeft' ? -1 : 0; if (d){ e.preventDefault(); var n = tabsEls[(i + d + tabsEls.length) % tabsEls.length]; n.focus(); sel(n); } });
    });
    sel(tabsEls[0]);
  }

  var mega = document.getElementById('mega'), trigs = document.querySelectorAll('.mtrig'), hoverT;
  function openMega(which, btn){
    mega.setAttribute('data-open', which || '');
    trigs.forEach(function(t){ t.setAttribute('aria-expanded', which && t === btn ? 'true' : 'false'); });
    document.documentElement.classList.toggle('mega-open', !!which);
  }
  trigs.forEach(function(t){
    t.addEventListener('click', function(e){
      e.stopPropagation();
      var which = t.classList.contains('burger') ? 'all' : t.getAttribute('data-panel');
      openMega(mega.getAttribute('data-open') === which ? '' : which, t);
    });
    if (matchMedia('(hover:hover) and (pointer:fine)').matches && !t.classList.contains('burger')){
      t.addEventListener('mouseenter', function(){ clearTimeout(hoverT); hoverT = setTimeout(function(){ openMega(t.getAttribute('data-panel'), t); }, 120); });
    }
  });
  if (mega){
    mega.addEventListener('mouseleave', function(){ if (matchMedia('(hover:hover)').matches){ hoverT = setTimeout(function(){ openMega(''); }, 250); } });
    mega.addEventListener('mouseenter', function(){ clearTimeout(hoverT); });
    mega.addEventListener('click', function(e){ if (e.target.closest('a')) openMega(''); });
    document.addEventListener('click', function(e){ if (!e.target.closest('#mega') && !e.target.closest('.mtrig')) openMega(''); });
    document.addEventListener('keydown', function(e){ if (e.key === 'Escape') openMega(''); });
  }

  /* ---------- hero form: file first, then work email ---------- */
  var heroForm = document.getElementById('drop'), later = document.getElementById('later');
  document.getElementById('file').addEventListener('change', function(){ setTimeout(function(){ if (!state.isSample) later.classList.add('show'); }, 300); });
  if (heroForm) heroForm.addEventListener('submit', function(e){
    e.preventDefault();
    var v = (document.getElementById('hemail').value || '').trim().toLowerCase(), r = check(v);
    if (state.isSample){ showErr('Choose your list file first.'); return; }
    if (r.s === 'bad' || r.why === 'typo'){ showErr('That email does not look right. Check the spelling.'); return; }
    if (r.why === 'free'){ showErr('Please use your work email. Personal addresses like Gmail cannot receive verification results.'); return; }
    showErr(''); state.email = v; state.stage = 'done';
    document.getElementById('foot').innerHTML = foot(Math.min(1000, state.a.n)); wire();
    document.getElementById('report').scrollIntoView({behavior: reduce ? 'auto' : 'smooth', block: 'nearest'});
  });
