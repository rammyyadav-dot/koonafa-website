/* Shared progressive accessibility behavior for the four public landing pages. */
(() => {
  'use strict';
  const body = document.body;
  const page = body.dataset.a11yPage;
  document.querySelector('.skip-link')?.addEventListener('click', event => {
    event.preventDefault(); event.stopImmediatePropagation();
    const main = document.getElementById('main-content');
    main?.focus({preventScroll:true});
    main?.scrollIntoView({behavior:'instant',block:'start'});
  }, true);
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const motionButton = document.querySelector('.motion-control');
  let manuallyPaused = false;
  try { manuallyPaused = sessionStorage.getItem('koonafa-motion-paused') === 'true'; } catch (_) {}
  function updateMotion() {
    const paused = manuallyPaused || reduceMotion.matches || document.hidden;
    window.__siteMotionPaused = paused;
    body.classList.toggle('motion-paused', paused);
    if (motionButton) {
      motionButton.disabled = reduceMotion.matches;
      motionButton.textContent = reduceMotion.matches ? 'Reduced motion on' : manuallyPaused ? 'Resume motion' : 'Pause motion';
      motionButton.setAttribute('aria-pressed', String(paused));
    }
    if (window.gsap) window.gsap.globalTimeline.paused(paused);
    if (paused) document.querySelectorAll('.nb-n[data-target]').forEach(el => {
      el.textContent = `${el.dataset.prefix || ''}${el.dataset.target}${el.dataset.suffix || ''}`;
    });
    document.querySelectorAll('video').forEach(video => {
      if (paused) video.pause();
      else video.play().catch(() => {});
    });
    try {
      if (window.player && typeof window.player.pauseVideo === 'function') {
        if (paused) window.player.pauseVideo();
        else window.player.playVideo();
      }
    } catch (_) {}
  }
  motionButton?.addEventListener('click', () => {
    manuallyPaused = !manuallyPaused;
    try { sessionStorage.setItem('koonafa-motion-paused', String(manuallyPaused)); } catch (_) {}
    updateMotion();
  });
  reduceMotion.addEventListener('change', updateMotion);
  document.addEventListener('visibilitychange', updateMotion);
  updateMotion();
  if (!window.gsap || !window.ScrollTrigger) body.classList.add('enhancements-unavailable');

  const header = document.querySelector('#mainNav,#navbar,#header');
  const updateHeaderSize = () => {
    if (header) document.documentElement.style.setProperty('--a11y-header-height', `${Math.ceil(header.getBoundingClientRect().height)}px`);
  };
  updateHeaderSize();
  if (header && 'ResizeObserver' in window) new ResizeObserver(updateHeaderSize).observe(header);

  const modal = page === 'index' || page === 'global';
  const menu = document.querySelector(page === 'index' ? '#menuOverlay' : page === 'global' ? '#mobileMenu' : '#nav');
  const trigger = document.querySelector('#hamburger,#menuToggle');
  if (!menu || !trigger) return;
  const breakpoint = matchMedia(`(max-width:${page === 'index' ? 1000 : page === 'global' ? 968 : 960}px)`);
  let open = false;
  let previousFocus;
  let previousOverflow = '';
  const backgroundStates = new Map();
  const focusables = () => Array.from(menu.querySelectorAll('a[href],button:not([disabled]),[tabindex="0"]')).filter(el => el.getClientRects().length && getComputedStyle(el).visibility !== 'hidden');
  function setBackgroundInert(active) {
    if (!modal) return;
    if (active) {
      Array.from(body.children).forEach(el => {
        if (el === menu || el.contains(menu) || ['SCRIPT','STYLE','LINK'].includes(el.tagName)) return;
        backgroundStates.set(el, el.inert);
        el.inert = true;
      });
    } else {
      backgroundStates.forEach((wasInert, el) => { el.inert = wasInert; });
      backgroundStates.clear();
    }
  }
  function closeMenu(restoreFocus = true) {
    const wasOpen = open;
    open = false;
    menu.classList.remove('open');
    trigger.setAttribute('aria-expanded', 'false');
    trigger.setAttribute('aria-label', 'Open navigation');
    if (!modal) trigger.textContent = '☰';
    const hidden = modal || breakpoint.matches;
    menu.inert = hidden;
    if (hidden) menu.setAttribute('aria-hidden', 'true');
    else menu.removeAttribute('aria-hidden');
    if (wasOpen) {
      setBackgroundInert(false);
      body.style.overflow = previousOverflow;
      if (restoreFocus && previousFocus?.isConnected) previousFocus.focus();
    }
  }
  function openMenu() {
    if (open || !breakpoint.matches) return;
    previousFocus = document.activeElement;
    previousOverflow = body.style.overflow;
    open = true;
    menu.inert = false;
    menu.setAttribute('aria-hidden', 'false');
    menu.classList.add('open');
    trigger.setAttribute('aria-expanded', 'true');
    trigger.setAttribute('aria-label', 'Close navigation');
    if (!modal) trigger.textContent = '×';
    menu.querySelectorAll('.mo-link').forEach(el => { el.style.opacity = '1'; el.style.transform = 'none'; });
    if (modal) {
      body.style.overflow = 'hidden';
      setBackgroundInert(true);
      focusables()[0]?.focus();
    }
  }
  // Replace legacy click handlers without accumulating duplicate toggles.
  trigger.addEventListener('click', event => {
    event.preventDefault();
    event.stopImmediatePropagation();
    if (open) closeMenu(); else openMenu();
  }, true);
  menu.querySelector('.mo-close,.mobile-menu-close')?.addEventListener('click', event => {
    event.preventDefault(); event.stopImmediatePropagation(); closeMenu();
  }, true);
  menu.addEventListener('click', event => {
    const link = event.target.closest('a[href]');
    if (!open || !link) return;
    event.stopImmediatePropagation();
    closeMenu(false);
    if (link.getAttribute('href').startsWith('#')) {
      const target = document.getElementById(link.hash.slice(1));
      if (target) {
        if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
        target.focus({preventScroll:true});
      }
    }
  }, true);
  document.addEventListener('keydown', event => {
    if (!open) return;
    if (event.key === 'Escape') {
      event.preventDefault(); event.stopImmediatePropagation(); closeMenu();
    } else if (modal && event.key === 'Tab') {
      const items = focusables();
      const first = items[0], last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    }
  }, true);
  document.addEventListener('click', event => {
    if (open && !modal && !menu.contains(event.target) && !trigger.contains(event.target)) closeMenu(false);
  });
  document.addEventListener('focusin', event => {
    if (open && !modal && !menu.contains(event.target) && !trigger.contains(event.target)) closeMenu(false);
  });
  breakpoint.addEventListener('change', () => closeMenu());
  if (page === 'index') { window.openMenu = openMenu; window.closeMenu = closeMenu; }
  if (page === 'global') { window.openMobileMenu = openMenu; window.closeMobileMenu = closeMenu; }
  closeMenu(false);
})();
