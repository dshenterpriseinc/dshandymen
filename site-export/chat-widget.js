/* DS Handymen - "Ask the Bear".

   A vanilla web component, no network calls and no dependencies. The bear waits
   a few seconds, walks on, and says hello in a speech bubble that types itself
   out; the bubble carries the buttons rather than making people guess that the
   mascot is clickable.

   Speech in and out are both progressive enhancements. The microphone button is
   only rendered when the browser actually exposes SpeechRecognition, and the
   speaker toggle only when speechSynthesis exists, so neither can strand a
   visitor on a browser that lacks them.

   Colours here are authored in the old navy. postprocess.py rotates the built
   copy onto the brand hue along with everything else, so there is one place the
   brand colour is decided and this file is not it. */
var __DSH_BASE = (function () {
  var d = document.currentScript;
  if (!d) { var a = document.querySelectorAll('script[src*="chat-widget"]'); d = a[a.length - 1]; }
  return d ? d.src.replace(/[^/]*$/, '') : '/';
})();

(function () {
  'use strict';

  var PHONE = '(716) 803-0091';
  var PHONE_HREF = 'tel:+17168030091';
  var EMAIL = 'dshandymen@yahoo.com';
  var U = function (p) { return __DSH_BASE + p; };      // real site URLs, not design-tool paths

  var BEAR_FIG = {
    neutral:   U('assets/web/mascot-bear-shovel-hero.webp'),
    waving:    U('assets/web/mascot-waving.webp'),
    listening: U('assets/web/mascot-bear-shovel-hero.webp'),
    delighted: U('assets/web/mascot-waving.webp'),
    pointing:  U('assets/web/mascot-ladder-drill.webp'),
    thumbsup:  U('assets/web/mascot-waving.webp')
  };
  // The animation loop: three real poses of the same character. He waves,
  // pivots, folds his arms, holds, and pivots back. Frames rather than a
  // rendered clip so the animation is exactly the mascot on the cards and in the
  // logo, keeps a real alpha channel, and costs ~100 KB instead of megabytes.
  // The three come from the concept sheets, and the loop takes however many
  // poses it is given.
  var POSE_SET = ['bear-pose-wave', 'bear-pose-stand', 'bear-pose-arms'];
  var POSES = function () {
    return POSE_SET.map(function (n) { return U('assets/web/' + n + '.webp'); });
  };

  // Six seconds holding each pose, nearly two handing over. Built rather than
  // hand-written so the percentages move with the pose count.
  var HOLD = 5.6, FADE = 1.9;

  function poseCss(n) {
    var cycle = n * (HOLD + FADE);
    var seg = 100 / n;
    var f = FADE / cycle * 100;
    var out = ['  .figs{animation-duration:' + cycle.toFixed(1) + 's}',
               '  .figs img{animation-duration:' + cycle.toFixed(1) + 's}'];
    var mids = [];
    for (var i = 0; i < n; i += 1) {
      var a = i * seg, b = a + seg - f, c = a + seg;
      out.push('  .figs img:nth-child(' + (i + 1) + '){animation-name:pose' + i + '}');
      if (i === 0) {
        out.push('  @keyframes pose0{0%,' + b.toFixed(2) + '%{opacity:1}' +
                 c.toFixed(2) + '%,' + (100 - f).toFixed(2) + '%{opacity:0}100%{opacity:1}}');
      } else {
        out.push('  @keyframes pose' + i + '{0%,' + (a - f).toFixed(2) + '%{opacity:0}' +
                 a.toFixed(2) + '%,' + b.toFixed(2) + '%{opacity:1}' +
                 c.toFixed(2) + '%,100%{opacity:0}}');
        mids.push(a - f / 2);
      }
    }
    mids.push(100 - f / 2);
    // a squash at each hand-over, which reads as him turning on the spot
    var kf = ['0%{transform:scaleX(1)}'];
    mids.forEach(function (m) {
      kf.push(Math.max(0.1, m - 2).toFixed(2) + '%{transform:scaleX(1)}');
      kf.push(m.toFixed(2) + '%{transform:scaleX(.90) translateY(-3px)}');
      kf.push(Math.min(99.9, m + 2).toFixed(2) + '%{transform:scaleX(1)}');
    });
    kf.push('100%{transform:scaleX(1)}');
    out.push('  @keyframes pivot{' + kf.join('') + '}');
    return out.join('\n');
  }

  var FIG = function (state) { return BEAR_FIG[state] || BEAR_FIG.neutral; };

  var PERSONAS = {
    bear: {
      name: 'The Bear', title: 'Ask the Bear',
      tag: "Dave's sidekick — anything Dave does",
      header: '#1B2A4A', accent: '#00338D',
      panel: '#F4F8FB', bubbleBot: '#FFFFFF', bubbleUser: '#00338D',
      hello: "Hey — I'm the Bear. I'm here to help. Ask me anything about plowing, washing, mowing or remodelling.",
      helloShort: "Hey — I'm the Bear. Ask me anything.",
      greet: "Right then. What do you need doing?",
      chips: ['Snow plowing', 'Get a quote', 'Pricing', 'Service area', 'Talk to Dave'],
      voice: /(david|mark|guy|george|daniel|male)/i,
      pitch: 0.82, rate: 0.98, speed: 420
    }
  };

  // One character. The design side of the business used to have a mascot of its
  // own; the crew that came with it no longer works here and Dave's own people
  // do the interior work, so the design pages get the same Bear, in the same
  // colours, opening on what those visitors actually came to read.
  PERSONAS.design = (function (b) {
    var d = {}, k;
    for (k in b) d[k] = b[k];
    d.tag = "Dave's sidekick — kitchens, baths & finish work";
    d.hello = "Hey — I'm the Bear. Kitchens, baths, tile, trim and cabinets. Ask me anything about the inside work.";
    d.helloShort = "Hey — I'm the Bear. Ask me about the inside work.";
    d.greet = 'Right then. What are we planning?';
    d.chips = ['Kitchen remodel', 'Tile & backsplash', 'Who does the work?', 'Get a quote'];
    return d;
  }(PERSONAS.bear));

  var Q = { link: U('quote/'), label: 'Free quote' };

  /* ---------------------------------------------------------------- knowledge
     Ordered: the first pattern that matches wins, so the specific questions sit
     above the general ones. Prices are never guessed - every costing question
     routes to the quote form or the phone, because that is what Dave actually
     wants and a made-up number would cost him the job. */
  var BEAR_KB = [
    [/who does (the |your )?(design|interior|remodel|finish|inside)|do you (do|handle) (the )?design|sub.?contract|in.?house|own crew/i,
      "Dave and his own crew, start to finish. The same people design it, build it and hand it back — the finish work is not passed to somebody else."],
    [/kitchen/i,
      "Kitchens from the first drawing through to the last coat — cabinets, tile, lighting and the trim around them. Have a look at the work, then let's talk about your space.",
      { link: U('gallery/'), linkLabel: 'See the work' }],
    [/bathroom|vanit|shower/i,
      'Bathrooms too — vanities, tile, lighting and the finish carpentry around them.'],
    [/tile|backsplash/i,
      'Tile and backsplash, yes. Material and layout make more difference than people expect, so it is worth getting right first time.'],
    [/cabinet|trim work|moulding|crown|finish carpentr|drywall|paint(ing)?\b/i,
      'All in our wheelhouse. Proportion and prep are most of the job.'],
    [/interior design|colou?r scheme|paint colou?r|design only|just design|plans only|drawings/i,
      'We can design it, build it, or both — whichever suits.',
      { link: U('design-remodeling/'), linkLabel: 'Design & remodeling' }],
    [/timeline|lead time|how soon|when could you (start|come)/i,
      'It depends on scope and materials. Send photos through the quote form and we can talk properly about timing.',
      { link: Q.link, linkLabel: Q.label }],

    [/who are you|what are you|your name|are you (a )?(bot|robot|real|human|ai)/i,
      "I'm the Bear, Dave Schultz's sidekick — a helper on this website, not Dave himself. Dave's been fixing, plowing and building around Hamburg for 50 years. For anything I can't answer, call him on " + PHONE + '.', { call: true }],

    [/hours|open|when.*(open|closed)|weekend|sunday|saturday/i,
      'No fixed shop hours — Dave works around the jobs and the weather. Plow routes start about 4am after a storm. Call ' + PHONE + ' and he picks up.', { call: true }],
    [/emergenc|urgent|storm|right now|today|asap|stuck|burst|leak/i,
      'For anything urgent, skip me and call Dave directly on ' + PHONE + '.', { call: true }],

    [/how much.*(plow|driveway)|(plow|driveway).*(cost|price|rate|charge)/i,
      "Depends on the driveway — length, slope and where the snow can go. Send a photo through the quote form and you'll get a straight number.", { link: Q.link, linkLabel: Q.label }],
    [/seasonal|contract|per visit|one.?off|per storm/i,
      'Both. A seasonal contract is one flat price for the whole winter and you never call — you’re on the route. Or one-off per visit when a big storm catches you out.'],
    [/plow|snow|driveway|salt|shovel/i,
      'Residential driveways and commercial lots, two trucks on route. Seasonal contract or one-off. Dave is out at 4am so you’re out by 7.'],
    [/referral|refer a/i, 'Send us a neighbour who signs up for seasonal plowing and you get $20 off.'],

    [/pressure|power.?wash|wash(ing)?\b|grime|moss|algae|siding clean/i,
      "Driveways, siding, decks, roofs, sidewalks and pool decks. If it's outside and it's dirty, we can help you out."],
    [/mow|lawn|landscap|mulch|rake|shrub|hedge|tree|planting|leaves|fall clean/i,
      'Mowing, mulch, planting, trimming, fall raking and winter shrub protection.'],
    [/gutter/i, 'Gutter clean-outs, repairs and replacement.'],
    [/roof/i, 'Roof cleaning and repair work, and we de-moss without wrecking the shingles.'],
    [/deck|fence|patio/i, 'Decks and fences — washing, refinishing, repair and new build.'],
    [/sunroom|three.?season|helios|patio enclosure|screen room/i,
      "Three-season rooms, and we're a trained dealer and installer for Helios retractable glass sunrooms.",
      { link: U('sunrooms-patio-enclosures/'), linkLabel: 'Sunrooms & enclosures' }],
    [/attic|garage|clear.?out|clean.?out|estate|junk|declutter|hoard|house clearance/i,
      "House clearance — attics, garages and estate clear-outs. It can be overwhelming working out where to start, so we start."],
    [/window|basement|floor|remodel|renovat|handyman|repair|fix|install|shelf|door/i,
      'Windows, basements, kitchens, flooring, drywall, decks and three-season rooms. If it needs doing, the Bear does it.'],

    [/area|towns?|where|hamburg|blasdell|orchard park|lackawanna|southtowns|west seneca|east aurora|eden|boston|angola|springville|buffalo|do you come|travel/i,
      'Blasdell, Hamburg, Orchard Park and Lackawanna are the core, plus the wider Southtowns and Western New York. Not sure if you’re in range? Worst case we say so.',
      { link: U('service-area/'), linkLabel: 'Service area map' }],
    [/address|located|where are you based|shop/i,
      '135 Miriam Avenue, Suite 1, Blasdell, NY 14219.'],

    [/insur|licens|bonded|bbb|accredit|rating|trust|legit/i,
      'Fully insured, and BBB Accredited with an A+ rating since 2021. 4.7 stars from 13 reviews.',
      { link: U('reviews/'), linkLabel: 'Reviews' }],
    [/review|testimonial|reference|what do people say/i,
      '4.7 stars from 13 reviews, and every one is a real Southtowns job.', { link: U('reviews/'), linkLabel: 'Reviews' }],
    [/how long|since when|years in business|founded|established|experience/i,
      'DS Handymen has been going since November 2009 — 16 years. Dave himself has been at it in Hamburg for 50.'],
    [/who is dave|about dave|owner/i,
      "Dave Schultz — 50 years in Hamburg, 16 of them running DS Handymen. He's the one out at 4am when the lake dumps a foot on your driveway.",
      { link: U('about/'), linkLabel: 'About Dave' }],

    [/free estimate|estimate|survey|come (out|round|over)|look at/i,
      'Free estimates, always. Send photos through the quote form and Dave gets back to you as soon as he’s off the route.', { link: Q.link, linkLabel: Q.label }],
    [/book|schedule|appointment|get started|sign up|quote|contact/i,
      'Quote form is quickest — photos welcome — or call ' + PHONE + '.', { link: Q.link, linkLabel: Q.label }],
    [/photo|picture|send.*image/i,
      'Yes please — photos get you a far more accurate number. The quote form takes them.', { link: Q.link, linkLabel: Q.label }],
    [/email/i, 'You can reach the office at ' + EMAIL + ', though the quote form gets a faster reply.'],

    [/pay|venmo|cash|cheque|check\b|card|credit|invoice|deposit|financ/i,
      'Cash, cheque or Venmo — david schultz@dshandymeninc.'],
    [/gift|certificate|voucher|present/i,
      'Gift certificates in $100, $250 and $500, good toward any service.',
      { link: U('gift-certificates/'), linkLabel: 'Gift certificates' }],
    [/discount|veteran|senior|teacher|military|deal|cheap/i,
      "10% off for Veterans, Seniors and Teachers, and $20 off when you refer someone for plowing."],
    [/price|pricing|cost|how much|rate|quote me|ballpark|estimate cost/i,
      "Every job is different so I won't guess a number at you. Send photos through the quote form and you'll get a real one.", { link: Q.link, linkLabel: Q.label }],

    [/gallery|photos of work|see.*work|before.*after/i,
      'Before-and-afters from real jobs, all our own crew.', { link: U('gallery/'), linkLabel: 'Before & after' }],
    [/facebook|social|instagram/i, 'We post jobs at facebook.com/dshandymen.'],
    [/bills|buffalo|football|mafia/i, "Let's go Buffalo."],
    [/thank|cheers|appreciate|great|awesome|perfect|nice one/i, "Any time. Anything else?"],
    [/^(hi|hey|hello|yo|good (morning|afternoon|evening))\b/i, 'Hey. What can I help with?'],
    [/talk to dave|human|real person|speak to someone|phone|call/i,
      'Best way is to call ' + PHONE + '. Dave picks up.', { call: true }]
  ];

  var FALLBACK = "That one’s for Dave rather than me. Call " + PHONE +
    ' or send it through the quote form and he’ll set you straight.';

  var CHIP_TEXT = {
    'Snow plowing': 'Do you plow driveways?',
    'Get a quote': 'How do I book a job?',
    'Pricing': 'How much does it cost?',
    'Service area': 'What areas do you serve?',
    'Talk to Dave': 'Can I talk to Dave?',
    'Kitchen remodel': 'Do you do kitchen remodels?',
    'Tile & backsplash': 'Do you do tile and backsplash?',
    'Who does the work?': 'Who does the design and finish work?'
  };

  var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  var SS = window.speechSynthesis;
  var esc = function (s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); };

  class ChatWidget extends HTMLElement {
    connectedCallback() {
      if (this._built) return;
      this._built = true;
      // the same Bear either way; 'design' only changes what he opens with
      this.persona = this.getAttribute('persona') === 'design' ? 'design' : 'bear';
      this.reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      this.voiceOn = false;
      try { this.voiceOn = localStorage.getItem('dsh-voice') === 'on'; } catch (e) {}
      this.attachShadow({ mode: 'open' });
      this._render();
      // he waits, then walks on. Long enough not to jump the page load, short
      // enough that anyone still reading sees him arrive.
      this._entrance = setTimeout(function (self) {
        return function () { self._arrive(); };
      }(this), this.reduced ? 400 : 3600);
    }

    disconnectedCallback() {
      clearTimeout(this._entrance); clearTimeout(this._typer); clearTimeout(this._fold);
      if (SS) { try { SS.cancel(); } catch (e) {} }
    }

    _p() { return PERSONAS[this.persona]; }

    _render() {
      var p = this._p();
      var poses = POSES();
      this.shadowRoot.innerHTML = [
'<style>',
'  :host{all:initial}',
'  *{box-sizing:border-box;font-family:"Source Sans 3","Source Sans Pro",system-ui,sans-serif}',
'  button{font:inherit}',
'',
'  /* ---- the mascot ---- */',
'  /* the bubble sits ABOVE him, not beside. Beside, it reached back across the',
'     page and covered content; above, it stacks into the margin he already uses. */',
'  .stage{position:fixed;right:14px;bottom:0;z-index:9000;display:flex;flex-direction:column;',
'    align-items:flex-end;gap:0;',
'    pointer-events:none;opacity:0;transform:translateY(28px) scale(.96);',
'    transition:opacity .6s ease,transform .6s cubic-bezier(.2,1.1,.35,1)}',
'  .stage.in{opacity:1;transform:none}',
'  .stage.gone{opacity:0;transform:translateY(20px) scale(.94);pointer-events:none}',
'  .launcher{pointer-events:auto;border:0;background:none;padding:0;cursor:pointer;line-height:0;',
'    filter:drop-shadow(0 14px 26px rgba(12,22,32,.36));transition:transform .25s cubic-bezier(.2,1.2,.4,1)}',
'  /* three times the old size on a desktop, tied to viewport height so a short',
'     laptop screen is not swallowed by a giant bear */',
'  .figs{position:relative;display:block;height:min(400px,44vh);width:calc(min(400px,44vh) * 0.92);',
'    transform-origin:50% 100%;animation:pivot ease-in-out infinite}',
'  .figs img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;',
'    display:block;pointer-events:none;opacity:0;animation:pose0 ease-in-out infinite}',
'  .figs img:nth-child(1){opacity:1}',
poseCss(poses.length),
'  /* a tab in the background, or the panel open, has no business burning CPU */',
'  .stage.still .figs,.stage.still .figs img{animation-play-state:paused}',
'  .launcher:hover{transform:translateY(-8px) scale(1.03)}',
'  .launcher:focus-visible{outline:3px solid ' + p.accent + ';outline-offset:8px;border-radius:14px}',
'',
'  /* ---- speech bubble ---- */',
'  .hello{pointer-events:auto;position:relative;background:#fff;color:#0C1620;border-radius:16px;',
'    padding:16px 18px 14px;width:min(340px,calc(100vw - 32px));margin-bottom:14px;margin-right:8px;',
'    box-shadow:0 10px 34px rgba(12,22,32,.26);border:1px solid rgba(12,22,32,.08)}',
'  .hello:after{content:"";position:absolute;bottom:-9px;right:54px;width:18px;height:18px;background:#fff;',
'    border-right:1px solid rgba(12,22,32,.08);border-bottom:1px solid rgba(12,22,32,.08);',
'    transform:rotate(45deg)}',
'  .hello p{margin:0 0 12px;padding-right:22px;font-size:16.5px;line-height:1.45;min-height:1.45em}',
'  .caret{display:inline-block;width:2px;height:1.05em;background:' + p.accent + ';',
'    vertical-align:-2px;margin-left:1px;animation:caret 1s steps(1) infinite}',
'  @keyframes caret{0%,50%{opacity:1}51%,100%{opacity:0}}',
'  .hello-cta{display:flex;gap:8px;align-items:stretch}',
'  .ask{flex:1;min-height:44px;border:none;border-radius:10px;background:' + p.bubbleUser + ';color:#fff;',
'    font-weight:700;font-size:15.5px;cursor:pointer;padding:0 14px}',
'  .ask:hover{filter:brightness(1.08)}',
'  .mic{min-width:44px;min-height:44px;border-radius:10px;border:1.5px solid ' + p.header + ';',
'    background:#fff;color:' + p.header + ';cursor:pointer;font-size:17px;display:grid;place-items:center}',
'  .mic[aria-pressed="true"]{background:' + p.bubbleUser + ';color:#fff;border-color:' + p.bubbleUser + '}',
'  .hello-x{position:absolute;top:6px;right:8px;background:none;border:none;font-size:20px;line-height:1;',
'    color:#5a6472;cursor:pointer;min-width:32px;min-height:32px}',
'  .ask:focus-visible,.mic:focus-visible,.hello-x:focus-visible{outline:3px solid ' + p.accent + ';outline-offset:2px}',
'',
'  @media(max-width:900px){',
'    .figs{height:min(250px,32vh);width:calc(min(250px,32vh) * 0.92)}',
'    .hello{width:min(300px,calc(100vw - 40px))}',
'  }',
'  /* On a phone he was 172px of bear plus a full-width card - a fifth of the',
"     screen, permanently, over the content someone came to read. Smaller, and",
"     the bubble is a compact card rather than the width of the display. */",
'  @media(max-width:640px){',
'    .stage{right:6px}',
'    .figs{height:112px;width:104px}',
'    .hello{width:min(232px,calc(100vw - 132px));padding:10px 12px;margin-bottom:6px;',
'      margin-right:4px;border-radius:13px}',
'    .hello p{font-size:14px;line-height:1.38;margin-bottom:8px;padding-right:18px}',
'    .hello:after{right:30px;width:14px;height:14px;bottom:-8px}',
'    .ask{min-height:38px;font-size:14px;padding:0 10px}',
'    .mic{min-width:38px;min-height:38px;font-size:15px}',
'    .hello-x{min-width:28px;min-height:28px;font-size:17px;top:3px;right:4px}',
'  }',
'  @media(prefers-reduced-motion:reduce){',
'    .stage,.launcher{transition:none}.launcher:hover{transform:none}.caret{animation:none}',
'    .figs,.figs img{animation:none}',
'    .figs img{opacity:0}.figs img:nth-child(1){opacity:1}',
'  }',
'',
'  /* ---- panel ---- */',
'  .panel{position:fixed;right:22px;bottom:22px;width:min(390px,calc(100vw - 32px));',
'    max-height:min(600px,calc(100vh - 60px));display:flex;flex-direction:column;border-radius:14px;',
'    overflow:hidden;box-shadow:0 12px 40px rgba(12,22,32,.35);z-index:9001;',
'    background:var(--panel-bg,' + p.panel + ');transition:background .8s ease}',
'  .head{display:flex;align-items:flex-end;gap:10px;padding:12px 16px 14px;min-height:78px;color:#fff;',
'    background:var(--head-bg,' + p.header + ');transition:background .8s ease}',
'  .head img{height:92px;width:auto;object-fit:contain;flex:none;margin:0 0 -16px;',
'    filter:drop-shadow(0 5px 10px rgba(0,0,0,.3))}',
'  .head .nm{font-weight:700;font-size:17px;line-height:1.1}',
'  .head .tg{font-size:13px;opacity:.85}',
'  .head .tools{margin-left:auto;display:flex;gap:2px;align-items:center}',
'  .head .tools button{background:none;border:none;color:#fff;font-size:19px;cursor:pointer;',
'    line-height:1;min-width:40px;min-height:40px;border-radius:8px}',
'  .head .tools button[aria-pressed="true"]{background:rgba(255,255,255,.22)}',
'  .head .tools button:focus-visible{outline:2px solid #fff;outline-offset:2px}',
'  .msgs{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px}',
'  .m{max-width:85%;padding:9px 13px;border-radius:12px;font-size:15.5px;line-height:1.45;white-space:pre-line}',
'  .bot{align-self:flex-start;background:' + p.bubbleBot + ';color:#0C1620;border-bottom-left-radius:4px;',
'    box-shadow:0 1px 3px rgba(12,22,32,.10)}',
'  .usr{align-self:flex-end;color:#fff;border-bottom-right-radius:4px;',
'    background:var(--usr-bg,' + p.bubbleUser + ');transition:background .8s ease}',
'  .m a{color:var(--link,' + p.accent + ');font-weight:600}',
'  .sys{align-self:center;font-size:13px;color:#4a5462;font-style:italic;padding:2px 0}',
'  .chips{display:flex;flex-wrap:wrap;gap:8px;padding:0 16px 12px}',
'  .chips button{border:1.5px solid var(--head-bg,' + p.header + ');background:transparent;',
'    color:var(--chip,' + p.header + ');border-radius:999px;padding:8px 14px;font-size:14px;',
'    font-weight:600;cursor:pointer;min-height:38px}',
'  .chips button:hover{background:rgba(0,0,0,.06)}',
'  .chips button:focus-visible{outline:2px solid var(--link,' + p.accent + ');outline-offset:2px}',
'  .foot{padding:10px 16px 14px;border-top:1px solid rgba(12,22,32,.10)}',
'  .row{display:flex;gap:8px}',
'  input{flex:1;min-height:44px;border:1.5px solid rgba(12,22,32,.30);border-radius:8px;padding:9px 12px;',
'    font-size:16px;background:#fff;color:#0C1620}',
'  input:focus-visible{outline:2px solid var(--link,' + p.accent + ');outline-offset:1px}',
'  .send{border:none;border-radius:8px;padding:0 16px;min-height:44px;font-weight:700;font-size:15px;',
'    color:#fff;cursor:pointer;background:var(--usr-bg,' + p.bubbleUser + ')}',
'  .pmic{min-width:44px;min-height:44px;border-radius:8px;border:1.5px solid rgba(12,22,32,.30);',
'    background:#fff;cursor:pointer;font-size:17px;display:grid;place-items:center;color:#0C1620}',
'  .pmic[aria-pressed="true"]{background:var(--usr-bg,' + p.bubbleUser + ');color:#fff}',
'  .send:focus-visible,.pmic:focus-visible{outline:2px solid #0C1620;outline-offset:2px}',
'  .call{display:block;text-align:center;font-size:13.5px;color:#3d4756;margin-top:8px;text-decoration:none}',
'  .call strong{color:var(--link,' + p.accent + ')}',
'  .typing{display:inline-flex;gap:4px;align-items:center}',
'  .typing i{width:6px;height:6px;border-radius:50%;background:#7c8794;display:inline-block;',
'    animation:blink 1.2s infinite}',
'  .typing i:nth-child(2){animation-delay:.2s}.typing i:nth-child(3){animation-delay:.4s}',
'  @keyframes blink{0%,80%,100%{opacity:.25}40%{opacity:1}}',
'  .hidden{display:none}',
'</style>',
'<div class="stage">',
'  <div class="hello" role="group" aria-label="Message from ' + p.name + '">',
'    <button class="hello-x" aria-label="Dismiss ' + p.name + '">×</button>',
'    <p class="hello-txt"></p>',
'    <div class="hello-cta">',
'      <button class="ask">Ask me a question</button>',
'    </div>',
'  </div>',
'  <button class="launcher" aria-label="Open chat — ' + p.title + '" aria-expanded="false">',
'    <span class="figs">',
poses.map(function (u, i) {
  return '      <img alt="" ' + (i ? 'data-src' : 'src') + '="' + u + '" decoding="async">';
}).join('\n'),
'    </span>',
'  </button>',
'</div>',
'<div class="panel hidden" role="dialog" aria-label="' + p.title + '" aria-modal="false">',
'  <div class="head">',
'    <img alt="" src="' + FIG('waving') + '">',
'    <div><div class="nm"></div><div class="tg"></div></div>',
'    <div class="tools">',
'      <button class="spk" aria-pressed="false" aria-label="Read answers aloud" title="Read answers aloud">\u{1F50A}</button>',
'      <button class="close" aria-label="Close chat" title="Close">×</button>',
'    </div>',
'  </div>',
'  <div class="msgs" aria-live="polite"></div>',
'  <div class="chips"></div>',
'  <div class="foot">',
'    <div class="row">',
'      <input type="text" placeholder="Type your question…" aria-label="Type your question">',
'      <button class="pmic" aria-pressed="false" aria-label="Ask by voice">\u{1F3A4}</button>',
'      <button class="send">Send</button>',
'    </div>',
'    <a class="call" href="' + PHONE_HREF + '">Rather talk? Call <strong>' + PHONE + '</strong></a>',
'  </div>',
'</div>'].join('\n');

      var $ = function (s) { return this.shadowRoot.querySelector(s); }.bind(this);
      this.$stage = $('.stage'); this.$launcher = $('.launcher'); this.$hello = $('.hello');
      this.$helloTxt = $('.hello-txt'); this.$panel = $('.panel'); this.$msgs = $('.msgs');
      this.$chips = $('.chips'); this.$input = $('input'); this.$headImg = $('.head img');
      this.$nm = $('.nm'); this.$tg = $('.tg'); this.$spk = $('.spk'); this.$pmic = $('.pmic');

      var self = this;
      this.$launcher.addEventListener('click', function () { self._toggle(true); });
      $('.ask').addEventListener('click', function () { self._toggle(true); });
      $('.hello-x').addEventListener('click', function (e) { e.stopPropagation(); self._dismiss(); });
      $('.close').addEventListener('click', function () { self._toggle(false); });
      $('.send').addEventListener('click', function () { self._submit(); });
      this.$input.addEventListener('keydown', function (e) { if (e.key === 'Enter') self._submit(); });
      this.$input.addEventListener('input', function () { self._setAvatar('listening'); });
      this.$spk.addEventListener('click', function () { self._toggleVoice(); });
      this.$pmic.addEventListener('click', function () { self._listen(self.$pmic); });
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && self.open) self._toggle(false);
      });
      document.addEventListener('visibilitychange', function () {
        self._still(document.hidden || self.open);
      });

      // speech in and out are enhancements: only offer what the browser has
      if (SR) {
        var mic = document.createElement('button');
        mic.className = 'mic'; mic.type = 'button';
        mic.setAttribute('aria-pressed', 'false');
        mic.setAttribute('aria-label', 'Ask by voice');
        mic.title = 'Ask by voice';
        mic.textContent = '\u{1F3A4}';
        mic.addEventListener('click', function () { self._toggle(true); self._listen(self.$pmic); });
        $('.hello-cta').appendChild(mic);
      } else {
        this.$pmic.remove();
      }
      if (!SS) this.$spk.remove();
      else this.$spk.setAttribute('aria-pressed', String(this.voiceOn));

      this._applyPersona(true);
    }

    /* ------------------------------------------------------------- entrance */
    _arrive() {
      if (this._dismissed || this.open) return;
      // the later poses are not needed until the loop starts, so they stay off
      // the critical path rather than adding ~70 KB to every page load
      this._arrived = true;
      this.shadowRoot.querySelectorAll('.figs img[data-src]').forEach(function (im) {
        im.src = im.getAttribute('data-src');
        im.removeAttribute('data-src');
      });
      var p = this._p();
      // a phone has no room for the long version - it would bury the hero's
      // call to action behind the bubble for as long as it is up
      var line = (window.innerWidth < 700 && p.helloShort) ? p.helloShort : p.hello;
      // Reserve the final height before he becomes visible. Without this the
      // typewriter grows the bubble line by line, and since the stage is
      // anchored to the bottom of the viewport every new line nudges everything
      // above it - which the browser scores as layout shift, 0.037 a go.
      this.$helloTxt.textContent = line;
      this.$helloTxt.style.minHeight = this.$helloTxt.offsetHeight + 'px';
      this.$helloTxt.textContent = '';
      this.$stage.classList.add('in');
      if (this.reduced) { this.$helloTxt.textContent = line; return; }
      this._type(this.$helloTxt, line);
      // he has said his piece - fold the bubble away rather than camp on the
      // page, and leave the bear himself standing there to be clicked
      var self = this;
      this._fold = setTimeout(function () {
        if (!self.open && !self._dismissed) self.$hello.style.display = 'none';
      }, window.innerWidth < 700 ? 13000 : 26000);
    }

    _type(el, text) {
      var i = 0, self = this;
      el.textContent = '';
      var caret = document.createElement('span');
      caret.className = 'caret';
      el.appendChild(caret);
      var step = function () {
        if (i >= text.length) { caret.remove(); return; }
        caret.insertAdjacentText('beforebegin', text.charAt(i));
        i += 1;
        self._typer = setTimeout(step, text.charAt(i - 1) === ' ' ? 18 : 26);
      };
      this._typer = setTimeout(step, 260);
    }

    _dismiss() {
      this._dismissed = true;
      clearTimeout(this._typer);
      this.$stage.classList.add('gone');
    }

    /* ---------------------------------------------------------------- voice */
    _pickVoice() {
      if (!SS) return null;
      var all = SS.getVoices() || [];
      var en = all.filter(function (v) { return /^en(-|_|$)/i.test(v.lang || ''); });
      if (!en.length) en = all;
      var want = this._p().voice;
      var match = en.filter(function (v) { return want.test(v.name || ''); });
      return (match[0] || en[0] || null);
    }

    _speak(text) {
      if (!this.voiceOn || !SS) return;
      try {
        SS.cancel();
        var u = new SpeechSynthesisUtterance(String(text).replace(/\s+/g, ' ').trim());
        var v = this._pickVoice();
        if (v) { u.voice = v; u.lang = v.lang; }
        var p = this._p();
        u.pitch = p.pitch; u.rate = p.rate; u.volume = 1;
        SS.speak(u);
      } catch (e) {}
    }

    _toggleVoice() {
      this.voiceOn = !this.voiceOn;
      this.$spk.setAttribute('aria-pressed', String(this.voiceOn));
      this.$spk.setAttribute('aria-label', this.voiceOn ? 'Stop reading answers aloud' : 'Read answers aloud');
      try { localStorage.setItem('dsh-voice', this.voiceOn ? 'on' : 'off'); } catch (e) {}
      if (!this.voiceOn) { try { SS.cancel(); } catch (e) {} }
      else this._speak('Voice on. ' + this._p().greet);
    }

    _listen(btn) {
      if (!SR || this._rec) return;
      var self = this;
      var rec = new SR();
      this._rec = rec;
      rec.lang = 'en-US'; rec.interimResults = true; rec.maxAlternatives = 1;
      var setOn = function (on) {
        [self.$pmic, self.shadowRoot.querySelector('.mic')].forEach(function (b) {
          if (b) b.setAttribute('aria-pressed', String(on));
        });
      };
      setOn(true);
      this._setAvatar('listening');
      rec.onresult = function (e) {
        var t = '';
        for (var i = e.resultIndex; i < e.results.length; i += 1) t += e.results[i][0].transcript;
        self.$input.value = t;
        if (e.results[e.results.length - 1].isFinal) { rec.stop(); self._submit(); }
      };
      rec.onerror = function () {
        self._el('sys', 'Didn’t catch that — type it instead?');
      };
      rec.onend = function () { setOn(false); self._rec = null; };
      try { rec.start(); } catch (e) { setOn(false); this._rec = null; }
    }

    /* ---------------------------------------------------------------- panel */
    _applyPersona(first) {
      var p = this._p(), self = this;
      this.$nm.textContent = p.name; this.$tg.textContent = p.tag;
      var st = this.$panel.style;
      st.setProperty('--panel-bg', p.panel); st.setProperty('--head-bg', p.header);
      st.setProperty('--usr-bg', p.bubbleUser); st.setProperty('--link', p.accent);
      st.setProperty('--chip', p.header);
      this._setAvatar(first ? 'waving' : 'neutral');
      this.$chips.innerHTML = '';
      p.chips.forEach(function (c) {
        var b = document.createElement('button');
        b.type = 'button'; b.textContent = c;
        b.addEventListener('click', function () { self._ask(CHIP_TEXT[c] || c); });
        self.$chips.appendChild(b);
      });
    }

    _setAvatar(state) {
      // the big figure runs its own loop now; only the panel's head reacts to state
      if (this.$headImg) this.$headImg.src = FIG(state);
    }

    _still(on) { this.$stage.classList.toggle('still', !!on); }

    _toggle(open) {
      this.open = open;
      clearTimeout(this._entrance); clearTimeout(this._typer);
      this.$panel.classList.toggle('hidden', !open);
      this.$launcher.setAttribute('aria-expanded', String(open));
      this.$stage.classList.toggle('gone', open);
      this._still(open);
      if (open && !this._greeted) {
        this._greeted = true;
        this._bot(this._p().greet, 'waving');
      }
      if (open) this.$input.focus();
      else { if (SS) { try { SS.cancel(); } catch (e) {} } this.$launcher.focus(); }
    }

    _el(cls, html) {
      var d = document.createElement('div');
      d.className = cls; d.innerHTML = html;
      this.$msgs.appendChild(d);
      this.$msgs.scrollTop = this.$msgs.scrollHeight;
      return d;
    }

    _bot(text, state, opts) {
      var html = esc(text);
      if (opts && opts.link) html += ' <a href="' + opts.link + '">' + esc(opts.linkLabel) + ' →</a>';
      if (opts && opts.call) html += ' <a href="' + PHONE_HREF + '">Call now</a>';
      this._el('m bot', html);
      this._setAvatar(opts && (opts.link || opts.call) ? 'pointing' : (state || 'delighted'));
      this._speak(text);
    }

    _submit() {
      var v = this.$input.value.trim();
      if (!v) return;
      this.$input.value = '';
      this._ask(v);
    }

    _ask(text) {
      var self = this;
      this._el('m usr', esc(text));
      var kb = BEAR_KB;
      var hit = null;
      for (var i = 0; i < kb.length; i += 1) { if (kb[i][0].test(text)) { hit = kb[i]; break; } }
      var typing = this._el('m bot', '<span class="typing"><i></i><i></i><i></i></span>');
      this._setAvatar('listening');
      setTimeout(function () {
        typing.remove();
        if (!hit) { self._bot(FALLBACK, 'neutral', { link: Q.link, linkLabel: Q.label }); return; }
        self._bot(hit[1], 'delighted', hit[2]);
      }, this.reduced ? 60 : this._p().speed);
    }
  }

  if (!customElements.get('chat-widget')) customElements.define('chat-widget', ChatWidget);
})();
