import io

p = r"R:/Documents/Claude/Projects/DSHandymen/site-export/chat-widget.js"
lines = io.open(p, encoding='utf-8').read().split('\n')

NEW = [
"  .launcher{position:fixed;right:16px;bottom:10px;width:auto;height:auto;border:0;border-radius:0;",
"    background:none;padding:0;cursor:pointer;z-index:9000;line-height:0;",
"    filter:drop-shadow(0 12px 20px rgba(12,22,32,.38));transition:transform .25s cubic-bezier(.2,1.2,.4,1)}",
"  .launcher img{height:136px;width:auto;display:block;pointer-events:none}",
"  .launcher:hover{transform:translateY(-7px) scale(1.05)}",
"  .launcher:focus-visible{outline:3px solid ${p.accent};outline-offset:6px;border-radius:12px}",
"  .launcher .pip{position:absolute;top:10px;right:4px;width:15px;height:15px;border-radius:50%;",
"    background:${p.accent};border:2px solid #fff;box-shadow:0 1px 5px rgba(0,0,0,.35)}",
"  @keyframes bob{0%,100%{transform:translateY(0) rotate(-.7deg)}50%{transform:translateY(-10px) rotate(.7deg)}}",
"  @keyframes wave{0%,100%{transform:rotate(0)}25%{transform:rotate(-6deg)}75%{transform:rotate(6deg)}}",
]

out, i, done = [], 0, False
while i < len(lines):
    ln = lines[i]
    if not done and ln.lstrip().startswith('.launcher{'):
        # consume the old launcher rules: the block, :hover, :focus-visible, @keyframes breathe
        while i < len(lines):
            t = lines[i].lstrip()
            if (t.startswith('.launcher') or t.startswith('@keyframes breathe')
                    or (out and not t.startswith('.') and not t.startswith('@') and t.endswith('}') and 'launcher' not in t and i > 0 and 'launcher' in lines[i-1])):
                i += 1
                # keep consuming continuation lines of a multi-line rule
                while i < len(lines) and not lines[i].lstrip().startswith(('.', '@', '<', '}')) and lines[i].strip():
                    i += 1
                continue
            break
        out.extend(NEW)
        done = True
        continue
    out.append(ln)
    i += 1

s = '\n'.join(out)
io.open(p, 'w', encoding='utf-8').write(s)
print("launcher css replaced:", done)
for n, l in enumerate(s.split('\n')):
    if '.launcher' in l or '@keyframes bob' in l:
        print("  %d: %s" % (n + 1, l.strip()[:96]))
