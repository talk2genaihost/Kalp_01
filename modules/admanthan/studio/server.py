from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
class H(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path=='/':
   data=(ROOT/'studio'/'index.html').read_bytes(); self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.end_headers(); self.wfile.write(data)
  else: self.send_error(404)
 def do_POST(self):
  if self.path!='/generate': self.send_error(404); return
  n=int(self.headers.get('Content-Length',0)); body=json.loads(self.rfile.read(n) or '{}')
  sys.path.insert(0,str(ROOT)); from core import EffectLibrary,AdManthan
  # The current GitHub Excel upload is stored directly under modules/admanthan.
  lib=EffectLibrary(ROOT/'Ad_Manthan_Effect_Shortcut_Library_v0_1.xlsx'); out=AdManthan(lib).generate_15s_6(body.get('brand',''),body.get('product',''),body.get('objective','brand awareness'))
  raw=json.dumps(out,ensure_ascii=False).encode(); self.send_response(200); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(raw)
if __name__=='__main__': HTTPServer(('127.0.0.1',8765),H).serve_forever()
