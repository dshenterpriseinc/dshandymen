/* DS Handymen — site behaviour.
   Re-implements the interactivity the design tool bound at runtime, as plain vanilla JS.
   Everything degrades safely: with JS off you still get a complete, readable page. */
var __DSH_BASE=(function(){var d=document.currentScript;if(!d){var a=document.querySelectorAll('script[src*="site.js"]');d=a[a.length-1];}return d?d.src.replace(/[^/]*$/,''):'/';})();

(function () {
  'use strict';
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------------------------------------------------------------- 1. main landmark */
  var main = document.querySelector('main') || document.querySelector('[aria-label="Main"]');
  if (main && !main.id) main.id = 'main';

  /* ---------------------------------------------------------------- 2. season engine */
  var SEASONS = {
    'deep-winter': {
      label: 'Deep Winter', slug: 'winter', bg: '#0C1620', pos: 'center 46%',
      headline: 'Lake effect snow? No problem.',
      sub: "Don't get stuck — get plowed. Two trucks on route across the Southtowns, seasonal contracts or one-off. Dave's out at 4am so you're out by 7.",
      cta: 'Get on the plow list', href: 'snow-plowing/'
    },
    'thaw': {
      label: 'Thaw', slug: 'thaw', bg: '#1B2A4A', pos: 'center 32%',
      headline: 'Wash away winter.',
      sub: "Salt stains, grime, a driveway that's seen five months of lake effect. If it's outside and it's dirty, we can help you out.",
      cta: 'Book a pressure wash', href: 'pressure-washing/'
    },
    'green': {
      label: 'Green', slug: 'green', bg: '#1B2A4A', pos: 'center 38%',
      headline: 'Perfect stripes. Every week.',
      sub: 'Mowing, mulch, planting and trim — plus decks, washing and every fix-it job on the list. Summer is short here. We make it count.',
      cta: 'Book landscaping', href: 'landscaping/'
    },
    'leaf-fall': {
      label: 'Leaf-Fall', slug: 'leaffall', bg: '#292D33', pos: 'center 28%',
      headline: "We'll clear your way.",
      sub: 'Gutters cleaned, leaves gone, shrubs wrapped — and the smart move: get on the plow list before the first lake-effect band rolls in.',
      cta: 'Beat the first snow', href: 'snow-plowing/'
    }
  };
  var ORDER = ['deep-winter', 'thaw', 'green', 'leaf-fall'];

  function seasonKey() {
    var forced = new URLSearchParams(location.search).get('season');
    if (forced && SEASONS[forced]) return forced;
    var m = new Date().getMonth();
    // the almanac runs one season ahead so people book before they need it
    var cur = (m >= 11 || m <= 1) ? 0 : m <= 4 ? 1 : m <= 7 ? 2 : 3;
    return ORDER[(cur + 1) % 4];
  }

  var hero = document.querySelector('section[aria-label="Seasonal welcome"]');
  if (hero) {
    var s = SEASONS[seasonKey()];
    hero.style.background = s.bg;

    var v = hero.querySelector('video');
    if (v) {
      // the renderer dropped these — without muted, autoplay is blocked everywhere
      v.muted = true; v.defaultMuted = true; v.loop = true;
      v.style.objectPosition = s.pos || 'center 40%';
      v.setAttribute('muted', ''); v.setAttribute('loop', '');
      v.setAttribute('playsinline', ''); v.setAttribute('aria-hidden', 'true');
      v.poster = __DSH_BASE+'assets/video/hero-' + s.slug + '-poster.jpg';
      if (reduced) {                       // honour reduced motion: poster only
        v.removeAttribute('autoplay'); v.pause();
        v.style.background = 'url(' + v.poster + ') center/cover no-repeat';
      } else {
        v.preload = 'none';
        var mp4 = __DSH_BASE+'assets/video/hero-' + s.slug + '.mp4';
        var webm = __DSH_BASE+'assets/video/hero-' + s.slug + '.webm';
        v.innerHTML = '';
        var s1 = document.createElement('source'); s1.src = webm; s1.type = 'video/webm';
        var s2 = document.createElement('source'); s2.src = mp4; s2.type = 'video/mp4';
        v.removeAttribute('src'); v.appendChild(s1); v.appendChild(s2);
        // only fetch once the hero is actually on screen
        var start = function () { v.preload = 'auto'; v.load(); var p = v.play(); if (p && p.catch) p.catch(function () {}); };
        if ('IntersectionObserver' in window) {
          var io = new IntersectionObserver(function (e) {
            if (e[0].isIntersecting) { start(); io.disconnect(); }
          }, { threshold: 0.1 });
          io.observe(hero);
        } else { start(); }
      }
    }
    var lbl = hero.querySelector('.sc-interp');
    if (lbl) lbl.textContent = s.label;
    var h1 = hero.querySelector('h1');
    if (h1) h1.textContent = s.headline;
    var ps = hero.querySelectorAll('p');
    if (ps.length > 1) ps[ps.length - 1].textContent = s.sub;
    var cta = hero.querySelector('a');
    if (cta) { cta.textContent = s.cta; cta.href = __DSH_BASE + s.href; }
  }

  /* ---------------------------------------------------------------- 2b. compact mobile header */
  /* The header is sticky, which on a phone meant three rows of nav pinned to the
     top for the whole visit - 298px, 35% of the viewport, permanently gone.
     Once the visitor has started reading, drop the nav and keep the bar that
     matters: the badge and the phone number. */
  var hdr = document.querySelector('header');
  if (hdr) {
    var narrow = window.matchMedia('(max-width: 760px)');
    var compact = function () {
      var y = window.scrollY || document.documentElement.scrollTop || 0;
      hdr.classList.toggle('dsh-compact', narrow.matches && y > 120);
    };
    window.addEventListener('scroll', compact, { passive: true });
    if (narrow.addEventListener) narrow.addEventListener('change', compact);
    else if (narrow.addListener) narrow.addListener(compact);
    compact();
  }

  /* ---------------------------------------------------------------- 3. before / after */
  var ba = document.querySelector('[role="slider"][aria-label="Before and after comparison"]');
  if (ba) {
    var imgs = ba.querySelectorAll('img');
    var after = imgs[1], bar = ba.querySelectorAll('div')[0], knob = ba.querySelectorAll('div')[1];
    var pct = 50, dragging = false;
    function paint() {
      if (after) after.style.clipPath = 'inset(0 0 0 ' + pct + '%)';
      if (bar) bar.style.left = pct + '%';
      if (knob) knob.style.left = pct + '%';
      ba.setAttribute('aria-valuenow', Math.round(pct));
    }
    function at(e) {
      var r = ba.getBoundingClientRect();
      var x = (e.touches ? e.touches[0].clientX : e.clientX) - r.left;
      pct = Math.max(0, Math.min(100, (x / r.width) * 100));
      paint();
    }
    ba.addEventListener('pointerdown', function (e) { dragging = true; try { ba.setPointerCapture(e.pointerId); } catch (x) {} at(e); });
    ba.addEventListener('pointermove', function (e) { if (dragging) at(e); });
    window.addEventListener('pointerup', function () { dragging = false; });
    ba.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { pct = Math.max(0, pct - 4); paint(); e.preventDefault(); }
      if (e.key === 'ArrowRight') { pct = Math.min(100, pct + 4); paint(); e.preventDefault(); }
      if (e.key === 'Home') { pct = 0; paint(); e.preventDefault(); }
      if (e.key === 'End') { pct = 100; paint(); e.preventDefault(); }
    });
    ba.style.touchAction = 'pan-y';
    paint();
  }

  /* ---------------------------------------------------------------- 4. badge stamp */
  var stamp = document.querySelector('img[src*="logo-badge-primary"]');
  if (stamp) {
    if (reduced || !('IntersectionObserver' in window)) {
      stamp.style.opacity = 1;
    } else {
      stamp.style.opacity = 0;
      var so = new IntersectionObserver(function (en) {
        if (en[0].isIntersecting) {
          stamp.style.animation = 'stamp .5s cubic-bezier(.2,1.3,.4,1) forwards';
          stamp.style.opacity = 1;
          so.disconnect();
        }
      }, { threshold: 0.5 });
      so.observe(stamp);
    }
  }

  /* ---------------------------------------------------------------- 5. radio ad */
  var radioBtn = document.querySelector('[aria-label="Play radio ad"]');
  if (radioBtn) {
    var audio = null, playing = false;
    var origLabel = radioBtn.getAttribute('aria-label');
    radioBtn.addEventListener('click', function () {
      if (!audio) {
        audio = new Audio(__DSH_BASE+'assets/audio/radio-ad.mp3');
        audio.addEventListener('ended', function () {
          playing = false; radioBtn.setAttribute('aria-label', origLabel); radioBtn.setAttribute('aria-pressed', 'false');
        });
      }
      if (playing) { audio.pause(); playing = false; radioBtn.setAttribute('aria-label', origLabel); }
      else { audio.play(); playing = true; radioBtn.setAttribute('aria-label', 'Pause radio ad'); }
      radioBtn.setAttribute('aria-pressed', playing ? 'true' : 'false');
    });
    radioBtn.setAttribute('aria-pressed', 'false');
  }

  /* ---------------------------------------------------------------- 6. external links */
  Array.prototype.forEach.call(document.querySelectorAll('a[href^="http"]'), function (a) {
    if (a.hostname && a.hostname !== location.hostname) {
      a.rel = 'noopener noreferrer';
      if (!a.target) a.target = '_blank';
    }
  });
})();
