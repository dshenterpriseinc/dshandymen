import io, re, sys

p = r"R:/Documents/Claude/Projects/DSHandymen/site-export/chat-widget.js"
s = io.open(p, encoding='utf-8').read()

# ---------------------------------------------------------------- 1. full-figure art
# The head-and-shoulders 3D renders read as a generic circular chat bubble.
# The full-body cutouts are the actual mascot and have real personality.
if 'BEAR_FIG' not in s:
    anchor = "  const BEAR_AV = (s) =>"
    figs = (
"  // full-figure art — the mascot standing, not a cropped head in a circle\n"
"  const BEAR_FIG = {\n"
"    neutral:   __DSH_BASE+'assets/web/mascot-bear-shovel-hero.png',\n"
"    waving:    __DSH_BASE+'assets/web/mascot-waving.png',\n"
"    listening: __DSH_BASE+'assets/web/mascot-bear-shovel-hero.png',\n"
"    delighted: __DSH_BASE+'assets/web/mascot-waving.png',\n"
"    pointing:  __DSH_BASE+'assets/web/mascot-ladder-drill.png',\n"
"    thumbsup:  __DSH_BASE+'assets/web/mascot-waving.png'\n"
"  };\n"
"  const BIRD_FIG = { neutral: __DSH_BASE+'assets/web/mascot-pigeon-blueprint.png' };\n"
"  const FIG = (persona, state) => (persona === 'bear'\n"
"      ? (BEAR_FIG[state] || BEAR_FIG.neutral)\n"
"      : (BIRD_FIG[state] || BIRD_FIG.neutral));\n"
    )
    s = s.replace(anchor, figs + anchor, 1)

# ---------------------------------------------------------------- 2. launcher styling
old_css = re.search(r"  \.launcher\{[^}]*\}\n(?:  \.launcher:hover\{[^}]*\}\n)?(?:  \.launcher:focus-visible\{[^}]*\}\n)?", s)
if old_css and 'figwrap' not in s:
    new_css = """  .launcher{position:fixed;right:18px;bottom:14px;width:auto;height:auto;border:0;border-radius:0;
    background:none;padding:0;cursor:pointer;z-index:9000;line-height:0;
    filter:drop-shadow(0 10px 18px rgba(12,22,32,.34));transition:transform .25s cubic-bezier(.2,1.2,.4,1)}
  .launcher img{height:132px;width:auto;display:block;pointer-events:none}
  .launcher:hover{transform:translateY(-6px) scale(1.04)}
  .launcher:focus-visible{outline:3px solid ${p.accent};outline-offset:6px;border-radius:10px}
  .launcher .pip{position:absolute;top:6px;right:2px;width:14px;height:14px;border-radius:50%;
    background:${p.accent};border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.3)}
  @keyframes bob{0%,100%{transform:translateY(0) rotate(-.6deg)}50%{transform:translateY(-9px) rotate(.6deg)}}
  @keyframes wave{0%,88%,100%{transform:rotate(0)}92%{transform:rotate(-7deg)}96%{transform:rotate(7deg)}}
"""
    s = s[:old_css.start()] + new_css + s[old_css.end():]

# breathe -> bob on the figure
s = s.replace(".breathe{animation:breathe 3.6s ease-in-out infinite}",
              ".breathe img{animation:bob 4.2s ease-in-out infinite}\n"
              "  .launcher:hover img{animation:wave 1.6s ease-in-out infinite}")
s = s.replace("@media(prefers-reduced-motion:reduce){.breathe{animation:none}.launcher:hover{transform:none}}",
              "@media(prefers-reduced-motion:reduce){.breathe img,.launcher:hover img{animation:none}.launcher:hover{transform:none}}")

# ---------------------------------------------------------------- 3. launcher markup
s = s.replace(
  """<button class="launcher breathe" aria-label="Open chat — ${p.title}" style="background-image:url('${this._av('neutral')}')"></button>""",
  """<button class="launcher breathe" aria-label="Open chat — ${p.title}"><img alt="" src="${FIG(this.persona,'waving')}"><span class="pip"></span></button>""")

# ---------------------------------------------------------------- 4. panel head figure
s = s.replace("""    <img alt="" src="${this._av('waving')}">""",
              """    <img class="headfig" alt="" src="${FIG(this.persona,'waving')}">""")

# bigger head figure, bottom-aligned so he stands on the header
s = s.replace(".head{display:flex;align-items:center;gap:12px;",
              ".head{display:flex;align-items:flex-end;gap:10px;")
if '.headfig{' not in s:
    s = s.replace(".nudge{position:fixed;",
                  ".headfig{height:84px;width:auto;margin-bottom:-14px;filter:drop-shadow(0 4px 8px rgba(0,0,0,.25))}\n"
                  "  .nudge{position:fixed;", 1)

# ---------------------------------------------------------------- 5. state swaps use figures
s = s.replace("this.$launcher.style.backgroundImage = `url('${url}')`;",
              "var lim = this.$launcher.querySelector('img'); if (lim) lim.src = FIG(this.persona, state);")
s = s.replace("if (this.persona === 'bird') { this._birdFallback(this.$headImg, false); this._birdFallback(this.$launcher, true); }",
              "if (this.$headImg) this.$headImg.src = FIG(this.persona, state);")
s = s.replace("if (this.persona === 'bird') this._birdFallback(this.$launcher, true);", "")

io.open(p, 'w', encoding='utf-8').write(s)
print("patched")
