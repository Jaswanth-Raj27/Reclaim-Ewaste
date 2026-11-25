"""Read-only LAN passport viewer. No signing, mining, forms or account controls."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit,parse_qs
from datetime import datetime,timezone
import html,os
from blockchain_client import connect,product_id,STAGES
from web3 import Web3

def page(title,content,status=200):
    return status,('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Reclaim passport</title><style>
    *{box-sizing:border-box}body{margin:0;background:#f6f5f2;color:#232323;font:16px/1.6 system-ui,sans-serif}main{max-width:760px;margin:0 auto;padding:28px 20px}header{color:#b74936;font-weight:600;margin-bottom:32px}h1{font-size:28px;line-height:1.2;font-weight:500}h2{font-size:20px;font-weight:500}article{background:white;border:1px solid #dfdcd7;padding:18px;margin:14px 0;border-radius:4px}code{overflow-wrap:anywhere;font-size:12px}.meta{color:#6e6a65;font-size:13px}p{overflow-wrap:anywhere}strong{font-weight:600}</style><main><header>Reclaim / Product passport</header><h1>'''+html.escape(title)+'</h1>'+content+'<p class="meta">Read-only local Ethereum prototype. Recorded statements require independent physical verification.</p></main></html>').encode()

def render_passport(query):
    ref=query.get('product',[''])[0]
    if not ref:return page('Scan a product QR','<p>Open the QR link generated in Reclaim to view a product’s recorded lifecycle.</p>')
    if len(ref)>256:return page('Invalid reference','<p>Product reference is too long.</p>',400)
    w,c=connect()
    if query.get('chain',[str(w.eth.chain_id)])[0]!=str(w.eth.chain_id) or query.get('contract',[c.address])[0].lower()!=c.address.lower():
        return page('Different deployment','<p>This QR belongs to another blockchain or contract.</p>',409)
    try:
        pid=product_id(ref);p=c.functions.getProduct(pid).call()
    except Exception:return page('Passport not found','<p>This reference is not registered on the current contract.</p>',404)
    esc=html.escape
    content=f'<p>{esc(p[1])} · <strong>{STAGES[p[4]]}</strong></p><article><p class="meta">Product ID</p><code>{Web3.to_hex(pid)}</code><p class="meta">Current custodian address</p><code>{p[2]}</code></article>'
    content+=f'<p class="meta">Chain {w.eth.chain_id} · Contract <code>{c.address}</code> · Latest block {w.eth.block_number}</p><h2>Recorded history</h2>'
    count=c.functions.historyCount(pid).call()
    for i in reversed(range(max(0,count-100),count)):
        r=c.functions.historyAt(pid,i).call()
        stamp=datetime.fromtimestamp(r[0],timezone.utc).strftime('%d %b %Y, %H:%M UTC')
        content+=f'<article><strong>{esc(r[2])}</strong><p class="meta">{stamp}</p><p>{esc(r[3])}</p><p class="meta">Recorded by</p><code>{r[1]}</code>'
        if r[4]!=bytes(32):content+='<p class="meta">Evidence SHA-256</p><code>'+r[4].hex()+'</code>'
        content+='</article>'
    if count>100:content+='<p class="meta">Showing the latest 100 events. Complete history remains on-chain.</p>'
    return page(p[0],content)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if urlsplit(self.path).path!='/':status,body=page('Not found','<p>Unknown page.</p>',404)
        else:
            try:status,body=render_passport(parse_qs(urlsplit(self.path).query))
            except Exception:status,body=page('Temporarily unavailable','<p>The local blockchain is unavailable. Ask the operator to start the node and viewer.</p>',503)
        self.send_response(status)
        for k,v in {'Content-Type':'text/html; charset=utf-8','Content-Length':str(len(body)),'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'"}.items():self.send_header(k,v)
        self.end_headers();self.wfile.write(body)
    def log_message(self,*args):pass

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--host',default='127.0.0.1');parser.add_argument('--port',type=int,default=8502);args=parser.parse_args()
    print(f'Read-only passport viewer: http://{args.host}:{args.port}',flush=True)
    ThreadingHTTPServer((args.host,args.port),Handler).serve_forever()
