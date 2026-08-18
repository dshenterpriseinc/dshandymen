import http.server, socketserver, os, urllib.parse, json
OUT = r"R:/Documents/Claude/Projects/DSHandymen/build/captured"
os.makedirs(OUT, exist_ok=True)

class H(http.server.BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST,OPTIONS')
    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()
    def do_POST(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        name = (q.get('name') or ['unnamed'])[0]
        n = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(n)
        safe = "".join(c for c in name if c.isalnum() or c in '-_.')
        with open(os.path.join(OUT, safe + '.json'), 'wb') as f:
            f.write(data)
        self.send_response(200); self._cors()
        self.send_header('Content-Type','text/plain'); self.end_headers()
        self.wfile.write(b'ok')
    def log_message(self, *a): pass

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", 8100), H) as httpd:
    httpd.serve_forever()
