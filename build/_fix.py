import io, ast

p = 'compile.py'
lines = io.open(p, encoding='utf-8').read().split('\n')

# rebuild the two script lines exactly, using concatenation so no escaping games
q = "'"
CHAT = '            + ' + q + '\\n<script src="' + q + " + prefix + " + q + 'chat-widget.js" defer></script>\\n' + q
SITE = '            + ' + q + '<script src="' + q + " + prefix + " + q + 'site.js" defer></script>\\n' + q

out = []
for ln in lines:
    st = ln.strip()
    if st.startswith('+ ') and 'defer></script>' in st:
        continue          # drop every malformed remnant
    out.append(ln)

# reinsert immediately after the "+ body" line
final = []
for ln in out:
    final.append(ln)
    if ln.strip() == '+ body':
        final.append(CHAT)
        final.append(SITE)

s = '\n'.join(final)
io.open(p, 'w', encoding='utf-8').write(s)
ast.parse(s)
print("syntax OK")
for i, l in enumerate(s.split('\n')):
    if 'defer></script>' in l:
        print("  line %d: %s" % (i + 1, l.strip()))
