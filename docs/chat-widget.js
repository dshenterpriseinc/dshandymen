/* DS Handymen — "Ask the Bear" / "Ask the Bird" scripted assistants with handoff.
   Vanilla web component, sprite-swap avatars, no network calls. */
var __DSH_BASE=(function(){var d=document.currentScript;if(!d){var a=document.querySelectorAll('script[src*="chat-widget"]');d=a[a.length-1];}return d?d.src.replace(/[^/]*$/,''):'/';})();

(function () {
  const PHONE = '(716) 803-0091';
  const PHONE_HREF = 'tel:+17168030091';
  // full-figure art — the mascot standing, not a cropped head in a circle
  const BEAR_FIG = {
    neutral:   __DSH_BASE+'assets/web/mascot-bear-shovel-hero.webp',
    waving:    __DSH_BASE+'assets/web/mascot-waving.webp',
    listening: __DSH_BASE+'assets/web/mascot-bear-shovel-hero.webp',
    delighted: __DSH_BASE+'assets/web/mascot-waving.webp',
    pointing:  __DSH_BASE+'assets/web/mascot-ladder-drill.webp',
    thumbsup:  __DSH_BASE+'assets/web/mascot-waving.webp'
  };
  const BIRD_FIG = { neutral: __DSH_BASE+'assets/web/mascot-pigeon-blueprint.webp' };
  const FIG = (persona, state) => (persona === 'bear'
      ? (BEAR_FIG[state] || BEAR_FIG.neutral)
      : (BIRD_FIG[state] || BIRD_FIG.neutral));
  const BEAR_AV = (s) => __DSH_BASE+`assets/web/chatbot-${s}.png`;
  const BIRD_AV = (s) => __DSH_BASE+`assets/web/pigeon-chatbot-${s}.png`;
  const BIRD_FALLBACK = __DSH_BASE+'assets/web/logo-pigeon-division.png';

  const PERSONAS = {
    bear: {
      name: 'The Bear', title: 'Ask the Bear',
      tag: "Dave's sidekick — outside work",
      bg: '#1B2A4A', header: '#1B2A4A', accent: '#00338D',
      panel: '#F4F8FB', bubbleBot: '#FFFFFF', bubbleUser: '#00338D',
      greet: "Hey — I'm the Bear. Snow, washing, mowing, fixing… what do you need?",
      chips: ['Snow plowing', 'Get a quote', 'Service area', 'Pricing', 'Talk to Dave'],
      speed: 420,
    },
    bird: {
      name: 'The Bird', title: 'Ask the Bird',
      tag: "Nichole's side — design & finish",
      bg: '#8A8078', header: '#6E655C', accent: '#B5673F',
      panel: '#F6F2ED', bubbleBot: '#FFFFFF', bubbleUser: '#B5673F',
      greet: "Hello — I'm the Bird. Design, trim, tile, cabinets. Where shall we start?",
      chips: ['Kitchen remodel', 'Tile & backsplash', 'The Pigeon Division', 'Get a quote'],
      speed: 700,
    },
  };

  // intent: [regex, reply, opts] — opts.handoff switches persona, opts.state sets avatar
  const BEAR_INTENTS = [
    [/tile|backsplash|cabinet|colou?r|paint\b|trim|layout|design|look good|kitchen remodel|bathroom remodel|finish work|interior/i,
      "That's the Bird's department — hang on.", { handoff: 'bird' }],
    [/who are you|what are you|your name/i,
      "I'm the Bear — Dave Schultz's sidekick. Dave's been fixing, plowing and building around Hamburg for 50 years."],
    [/area|towns?|where|hamburg|blasdell|orchard park|lackawanna|southtowns/i,
      'Blasdell, Hamburg, Orchard Park, Lackawanna and the wider Southtowns.'],
    [/insur|bbb|accredit|licens/i,
      'Fully insured, and BBB Accredited with an A+ rating since 2021.'],
    [/how long|since when|years in business|founded|established/i,
      'Since 2009 — 16 years.'],
    [/plow.*(cost|price)|(cost|price|charge).*plow/i,
      `Depends on the driveway. Call ${PHONE} or send a photo through the quote form.`, { link: 'Quote.dc.html', linkLabel: 'Quote form' }],
    [/plow|driveway|snow/i,
      'Yes — residential driveways and commercial lots. Seasonal contract or one-off. Two trucks on route.'],
    [/referral/i, 'Refer another seasonal customer, get $20 off.'],
    [/pressure|power wash|washing/i,
      `Driveways, siding, decks, roofs, sidewalks, pool decks. "If it's outside and it's dirty."`],
    [/sunroom|three.?season|helios|patio enclosure/i,
      "Three-season rooms, and we're a trained installer for Helios retractable glass sunrooms.", { link: 'Sunrooms.dc.html', linkLabel: 'Sunrooms' }],
    [/attic|garage|clear|clean.?out|estate|junk|declutter/i,
      'Yes — house clearance is one of our services.'],
    [/gutter/i, 'Clean-outs, repairs and replacement.'],
    [/storm|emergency|urgent|stuck/i, `Call Dave directly at ${PHONE}.`, { call: true }],
    [/free estimate|estimates?\b/i, 'Yes. Free estimates, always.'],
    [/how do i book|book|schedule|quote|appointment/i,
      `Quote form — photos welcome — or call ${PHONE}.`, { link: 'Quote.dc.html', linkLabel: 'Quote form' }],
    [/pay|venmo|cash|cheque|check\b/i,
      'Cash, cheque and Venmo — david schultz@dshandymeninc.'],
    [/gift/i, `$100, $250 or $500, good toward any service. "Give someone the gift of time."`, { link: 'GiftCertificates.dc.html', linkLabel: 'Gift certificates' }],
    [/discount|veteran|senior|teacher|deal/i,
      '10% off for Veterans, Seniors and Teachers, plus $20 off for a plowing referral.'],
    [/bills|buffalo|football/i, "Let's go Buffalo. 🦬"],
    [/price|pricing|cost|how much/i,
      `Every job's different, so I never guess prices. Call ${PHONE} or send photos through the quote form.`, { link: 'Quote.dc.html', linkLabel: 'Quote form' }],
    [/talk to dave|human|person|phone/i, `Best way: call ${PHONE}. Dave picks up.`, { call: true }],
    [/mow|lawn|landscap|mulch|rake|shrub|tree/i,
      'Mowing, mulch, planting, trimming, fall raking and winter shrub protection. All of it.'],
  ];
  const BIRD_INTENTS = [
    [/plow|snow|wash|gutter|mow|lawn|driveway|clearance|roof|outdoor|outside/i,
      "That's the Bear's side of the house — one moment.", { handoff: 'bear' }],
    [/who are you|your name/i,
      "I'm the Bird — Nichole Pigeon's side of the business. I look after design and finish work."],
    [/what is|pigeon division|division/i,
      'The design and finish arm of DS Handymen. Nichole is an RIT Design School graduate and the crew has over 40 years of collective experience.'],
    [/what do you do|services/i,
      'Custom design, trim, cabinets, drywall, paint, tile and finish work — plus exterior projects.'],
    [/kitchen/i,
      "Yes — design through finish. Have a look at the gallery, then let's talk about your space.", { link: 'Gallery.dc.html', linkLabel: 'Gallery' }],
    [/tile|backsplash/i,
      'Yes. Material and layout make more difference than people expect — worth getting right.'],
    [/design only|just design|plans only/i, 'We can design it, build it, or both.'],
    [/start|begin|quote|estimate|book/i,
      `Free estimate. Call ${PHONE} or send photos through the quote form.`, { link: 'Quote.dc.html', linkLabel: 'Quote form' }],
    [/price|cost|how much/i,
      `It depends on the space and the materials. Send photos through the quote form and we'll talk it through properly.`, { link: 'Quote.dc.html', linkLabel: 'Quote form' }],
    [/cabinet|trim|drywall|paint|finish/i,
      'All in our wheelhouse — proportion and prep are most of the job.'],
  ];
  const FALLBACK = {
    bear: `Good question — that one's for Dave. Call ${PHONE} or use the quote form and he'll set you straight.`,
    bird: `I'd rather Nichole answer that one properly. Call ${PHONE} or send it through the quote form.`,
  };
  const CHIP_TEXT = { 'Snow plowing': 'Do you plow driveways?', 'Get a quote': 'How do I book?', 'Service area': 'What areas do you serve?', 'Pricing': 'How much does it cost?', 'Talk to Dave': 'Can I talk to Dave?', 'Kitchen remodel': 'Do you do kitchen remodels?', 'Tile & backsplash': 'Do you do tile and backsplash?', 'The Pigeon Division': 'What is the Pigeon Division?' };

  class ChatWidget extends HTMLElement {
    connectedCallback() {
      if (this._built) return; this._built = true;
      this.persona = this.getAttribute('persona') === 'bird' ? 'bird' : 'bear';
      this.reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      this.attachShadow({ mode: 'open' });
      this._render();
      if (!this.reduced) {
        this._nudgeTimer = setTimeout(() => { if (!this.open) this._showNudge(); }, 20000);
      }
    }
    disconnectedCallback() { clearTimeout(this._nudgeTimer); }
    _av(state) {
      return this.persona === 'bear' ? BEAR_AV(state) : BIRD_AV(state);
    }
    _p() { return PERSONAS[this.persona]; }
    _render() {
      const p = this._p();
      this.shadowRoot.innerHTML = `
<style>
  :host{all:initial}
  *{box-sizing:border-box;font-family:'Source Sans 3','Source Sans Pro',system-ui,sans-serif}
  .launcher{position:fixed;right:16px;bottom:10px;width:auto;height:auto;border:0;border-radius:0;
    background:none;padding:0;cursor:pointer;z-index:9000;line-height:0;
    filter:drop-shadow(0 12px 20px rgba(12,22,32,.38));
    transition:transform .25s cubic-bezier(.2,1.2,.4,1),opacity .2s ease}
  /* the bear IS the launcher, so leaving him standing beside the open panel
     puts two of him on screen - step him aside while the panel is up */
  .launcher[aria-expanded="true"]{opacity:0;pointer-events:none;transform:translateY(14px) scale(.9)}
  .launcher img{height:136px;width:auto;display:block;pointer-events:none}
  .launcher:hover{transform:translateY(-7px) scale(1.05)}
  .launcher:focus-visible{outline:3px solid ${p.accent};outline-offset:6px;border-radius:12px}
  .launcher .pip{position:absolute;top:10px;right:4px;width:15px;height:15px;border-radius:50%;
    background:${p.accent};border:2px solid #fff;box-shadow:0 1px 5px rgba(0,0,0,.35)}
  @media(max-width:640px){
    .launcher img{height:92px}
    .launcher{right:10px;bottom:6px}
    .launcher .pip{width:12px;height:12px;top:6px;right:2px}
    .nudge{right:auto;left:12px;bottom:104px;max-width:calc(100vw - 130px)}
    .head img{height:70px;margin:-14px 0 -10px}
  }
  @keyframes bob{0%,100%{transform:translateY(0) rotate(-.7deg)}50%{transform:translateY(-10px) rotate(.7deg)}}
  @keyframes wave{0%,100%{transform:rotate(0)}25%{transform:rotate(-6deg)}75%{transform:rotate(6deg)}}
  .breathe img{animation:bob 4.2s ease-in-out infinite}
  .launcher:hover img{animation:wave 1.6s ease-in-out infinite}
  @media(prefers-reduced-motion:reduce){.breathe img,.launcher:hover img{animation:none}.launcher:hover{transform:none}}
  .nudge{position:fixed;right:96px;bottom:36px;background:#fff;color:#0C1620;padding:10px 14px;border-radius:10px;
    box-shadow:0 4px 16px rgba(12,22,32,.22);font-size:15px;z-index:9000;max-width:200px}
  .nudge:after{content:'';position:absolute;right:-6px;top:50%;width:12px;height:12px;background:#fff;transform:translateY(-50%) rotate(45deg)}
  .panel{position:fixed;right:22px;bottom:22px;width:min(370px,calc(100vw - 32px));max-height:min(560px,calc(100vh - 60px));
    display:flex;flex-direction:column;border-radius:14px;overflow:hidden;box-shadow:0 12px 40px rgba(12,22,32,.35);z-index:9001;
    background:var(--panel-bg,${p.panel});transition:background .8s ease}
  .head{display:flex;align-items:flex-end;gap:10px;padding:10px 16px 12px;min-height:74px;color:#fff;background:var(--head-bg,${p.header});transition:background .8s ease}
  .head img{height:88px;width:auto;border-radius:0;background:none;object-fit:contain;flex:none;
    margin:-18px 0 -14px;filter:drop-shadow(0 5px 10px rgba(0,0,0,.3))}
  .head .nm{font-weight:700;font-size:17px;line-height:1.1}
  .head .tg{font-size:13px;opacity:.85}
  .head button{margin-left:auto;background:none;border:none;color:#fff;font-size:22px;cursor:pointer;line-height:1;padding:4px 6px}
  .head button:focus-visible{outline:2px solid #fff;outline-offset:2px}
  .msgs{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px}
  .m{max-width:85%;padding:9px 13px;border-radius:12px;font-size:15.5px;line-height:1.45;white-space:pre-line}
  .bot{align-self:flex-start;background:${p.bubbleBot};color:#0C1620;border-bottom-left-radius:4px;box-shadow:0 1px 3px rgba(12,22,32,.10)}
  .usr{align-self:flex-end;color:#fff;border-bottom-right-radius:4px;background:var(--usr-bg,${p.bubbleUser});transition:background .8s ease}
  .m a{color:var(--link,${p.accent});font-weight:600}
  .sys{align-self:center;font-size:13px;color:#5a6472;font-style:italic;padding:2px 0}
  .chips{display:flex;flex-wrap:wrap;gap:8px;padding:0 16px 12px}
  .chips button{border:1.5px solid var(--head-bg,${p.header});background:transparent;color:var(--chip,${p.header});
    border-radius:999px;padding:6px 13px;font-size:14px;font-weight:600;cursor:pointer}
  .chips button:hover{background:rgba(0,0,0,.06)}
  .chips button:focus-visible{outline:2px solid var(--link,${p.accent});outline-offset:2px}
  .foot{padding:10px 16px 14px;border-top:1px solid rgba(12,22,32,.10)}
  .row{display:flex;gap:8px}
  input{flex:1;border:1.5px solid rgba(12,22,32,.25);border-radius:8px;padding:9px 12px;font-size:15.5px;background:#fff;color:#0C1620}
  input:focus-visible{outline:2px solid var(--link,${p.accent});outline-offset:1px}
  .send{border:none;border-radius:8px;padding:9px 16px;font-weight:700;font-size:15px;color:#fff;cursor:pointer;background:var(--usr-bg,${p.bubbleUser})}
  .send:focus-visible{outline:2px solid #0C1620;outline-offset:2px}
  .call{display:block;text-align:center;font-size:13.5px;color:#3d4756;margin-top:8px;text-decoration:none}
  .call strong{color:var(--link,${p.accent})}
  .typing{display:inline-flex;gap:4px;align-items:center}
  .typing i{width:6px;height:6px;border-radius:50%;background:#8a94a3;display:inline-block;animation:blink 1.2s infinite}
  .typing i:nth-child(2){animation-delay:.2s}.typing i:nth-child(3){animation-delay:.4s}
  @keyframes blink{0%,80%,100%{opacity:.25}40%{opacity:1}}
  .hidden{display:none}
</style>
<button class="launcher breathe" aria-label="Open chat — ${p.title}"><img alt="" src="${FIG(this.persona,'waving')}"><span class="pip"></span></button>
<div class="nudge hidden" role="status"></div>
<div class="panel hidden" role="dialog" aria-label="${p.title}">
  <div class="head">
    <img class="headfig" alt="" src="${FIG(this.persona,'waving')}">
    <div><div class="nm"></div><div class="tg"></div></div>
    <button class="close" aria-label="Close chat">×</button>
  </div>
  <div class="msgs" aria-live="polite"></div>
  <div class="chips"></div>
  <div class="foot">
    <div class="row">
      <input type="text" placeholder="Type a question…" aria-label="Type a question">
      <button class="send">Send</button>
    </div>
    <a class="call" href="${PHONE_HREF}">Rather talk? Call <strong>${PHONE}</strong></a>
  </div>
</div>`;
      const $ = (s) => this.shadowRoot.querySelector(s);
      this.$launcher = $('.launcher'); this.$panel = $('.panel'); this.$msgs = $('.msgs');
      this.$chips = $('.chips'); this.$input = $('input'); this.$nudge = $('.nudge');
      this.$headImg = $('.head img'); this.$nm = $('.nm'); this.$tg = $('.tg');
      
      this.$launcher.addEventListener('click', () => this._toggle(true));
      $('.close').addEventListener('click', () => this._toggle(false));
      $('.send').addEventListener('click', () => this._submit());
      this.$input.addEventListener('keydown', (e) => { if (e.key === 'Enter') this._submit(); });
      this.$input.addEventListener('input', () => this._setAvatar('listening'));
      this._applyPersona(true);
    }
    _birdFallback(el, isBg) {
      // if pigeon-chatbot-* isn't on disk yet, fall back to the division badge
      const probe = new Image();
      probe.onerror = () => { if (isBg) el.style.backgroundImage = `url('${BIRD_FALLBACK}')`; else el.src = BIRD_FALLBACK; };
      probe.src = this._av('neutral');
      if (!isBg) { el.onerror = () => { el.onerror = null; el.src = BIRD_FALLBACK; }; }
    }
    _applyPersona(first) {
      const p = this._p();
      this.$nm.textContent = p.name; this.$tg.textContent = p.tag;
      const st = this.$panel.style;
      st.setProperty('--panel-bg', p.panel); st.setProperty('--head-bg', p.header);
      st.setProperty('--usr-bg', p.bubbleUser); st.setProperty('--link', p.accent);
      st.setProperty('--chip', p.header);
      this._setAvatar(first ? 'waving' : 'neutral');
      this.$chips.innerHTML = '';
      p.chips.forEach((c) => {
        const b = document.createElement('button');
        b.textContent = c;
        b.addEventListener('click', () => this._ask(CHIP_TEXT[c] || c));
        this.$chips.appendChild(b);
      });
    }
    _setAvatar(state) {
      const url = this._av(state);
      this.$headImg.src = url;
      var lim = this.$launcher.querySelector('img'); if (lim) lim.src = FIG(this.persona, state);
      if (this.$headImg) this.$headImg.src = FIG(this.persona, state);
    }
    _showNudge() {
      this.$nudge.textContent = this.persona === 'bear' ? 'Need a quote? Ask me.' : 'Planning a room? Ask me.';
      this.$nudge.classList.remove('hidden');
      setTimeout(() => this.$nudge.classList.add('hidden'), 8000);
    }
    _toggle(open) {
      this.open = open;
      this.$panel.classList.toggle('hidden', !open);
      this.$launcher.setAttribute('aria-expanded', String(open));
      this.$nudge.classList.add('hidden');
      if (open && !this._greeted) {
        this._greeted = true;
        this._bot(this._p().greet, 'waving');
      }
      if (open) this.$input.focus();
    }
    _el(cls, html) { const d = document.createElement('div'); d.className = cls; d.innerHTML = html; this.$msgs.appendChild(d); this.$msgs.scrollTop = this.$msgs.scrollHeight; return d; }
    _bot(text, state, opts) {
      let html = text.replace(/&/g, '&amp;').replace(/</g, '&lt;');
      if (opts && opts.link) html += ` <a href="${opts.link}">${opts.linkLabel} →</a>`;
      if (opts && opts.call) html += ` <a href="${PHONE_HREF}">Call now</a>`;
      this._el('m bot', html);
      this._setAvatar(opts && (opts.link || opts.call) ? 'pointing' : (state || 'delighted'));
    }
    _submit() { const v = this.$input.value.trim(); if (!v) return; this.$input.value = ''; this._ask(v); }
    _ask(text) {
      this._el('m usr', text.replace(/&/g, '&amp;').replace(/</g, '&lt;'));
      const intents = this.persona === 'bear' ? BEAR_INTENTS : BIRD_INTENTS;
      let hit = null;
      for (const it of intents) { if (it[0].test(text)) { hit = it; break; } }
      const typing = this._el('m bot', '<span class="typing"><i></i><i></i><i></i></span>');
      this._setAvatar('listening');
      const delay = this.reduced ? 60 : this._p().speed;
      setTimeout(() => {
        typing.remove();
        if (!hit) { this._bot(FALLBACK[this.persona], 'neutral', { link: 'Quote.dc.html', linkLabel: 'Quote form' }); return; }
        const [, reply, opts] = hit;
        this._bot(reply, 'delighted', opts);
        if (opts && opts.handoff) this._handoff(opts.handoff, text);
      }, delay);
    }
    _handoff(to, originalQ) {
      const delay = this.reduced ? 200 : 1400;
      setTimeout(() => {
        this._el('sys', to === 'bird' ? 'The panel warms — the Bird takes over.' : 'The panel cools — the Bear steps back in.');
        this.persona = to;
        this._applyPersona(false);
        const greet = to === 'bird'
          ? "Hello — the Bird here. I heard the question. Let's take it properly."
          : "Bear again. Outside stuff — now we're talking.";
        setTimeout(() => {
          this._bot(greet, 'waving');
          // answer the original question in the new persona
          const intents = to === 'bear' ? BEAR_INTENTS : BIRD_INTENTS;
          for (const it of intents) {
            if (!it[2] || !it[2].handoff) { if (it[0].test(originalQ)) { setTimeout(() => this._bot(it[1], 'delighted', it[2]), this.reduced ? 100 : 900); break; } }
          }
        }, this.reduced ? 100 : 700);
      }, delay);
    }
  }
  if (!customElements.get('chat-widget')) customElements.define('chat-widget', ChatWidget);
})();
