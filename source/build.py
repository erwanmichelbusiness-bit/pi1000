import json,re,os
from PIL import Image,ImageDraw,ImageFont
s=open('src.html').read()
D=open('D.txt').read().strip(); note=open('note.txt').read()
base=s.replace('%%D%%',D).replace('%%NOTE%%',json.dumps(note,ensure_ascii=False))
# Version artefact claude.ai
open('pi_app.html','w').write(base.replace('%%HEAD_EXTRA%%\n','').replace('%%SW%%\n',''))
# Version app d'écran d'accueil
head='''<meta name="theme-color" content="#2438d6">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="π 1000">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="icon" type="image/png" href="icon-192.png">
'''
sw='if("serviceWorker" in navigator){const had=!!navigator.serviceWorker.controller;navigator.serviceWorker.addEventListener("controllerchange",()=>{if(had)location.reload();});window.addEventListener("load",()=>{navigator.serviceWorker.register("sw.js").catch(()=>{});});}\n'
os.makedirs('pwa',exist_ok=True)
open('pwa/index.html','w').write(base.replace('%%HEAD_EXTRA%%\n',head).replace('%%SW%%\n',sw))
json.dump({"name":"Mille décimales de π","short_name":"π 1000","start_url":"./","scope":"./","display":"standalone",
 "background_color":"#f3f4f1","theme_color":"#2438d6","lang":"fr",
 "icons":[{"src":"icon-192.png","sizes":"192x192","type":"image/png","purpose":"any"},
          {"src":"icon-512.png","sizes":"512x512","type":"image/png","purpose":"any"},
          {"src":"icon-maskable-512.png","sizes":"512x512","type":"image/png","purpose":"maskable"}]},
 open('pwa/manifest.webmanifest','w'),ensure_ascii=False,indent=1)
open('pwa/sw.js','w').write('''const C="pi1000-v6";
const FILES=["./","index.html","manifest.webmanifest","icon-192.png","icon-512.png","icon-maskable-512.png","apple-touch-icon.png"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(FILES)));self.skipWaiting();});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
/* Page : réseau d'abord (version à jour), copie en cache hors ligne. Autres fichiers : cache tout de suite, mis à jour en arrière-plan */
self.addEventListener("fetch",e=>{
  if(e.request.method!=="GET")return;
  if(e.request.mode==="navigate"){
    e.respondWith(fetch(e.request).then(r=>{const cp=r.clone();caches.open(C).then(c=>c.put("index.html",cp));return r;}).catch(()=>caches.match("index.html")));
    return;
  }
  e.respondWith(caches.open(C).then(async c=>{
    const hit=await c.match(e.request,{ignoreSearch:true});
    const net=fetch(e.request).then(r=>{if(r&&(r.ok||r.type==="opaque"))c.put(e.request,r.clone());return r;}).catch(()=>hit);
    return hit||net;
  }));
});
''')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',10)
def icon(size,path,scale,rounded=False):
    im=Image.new('RGB',(size,size),(36,56,214)); d=ImageDraw.Draw(im)
    f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',int(size*scale))
    b=d.textbbox((0,0),'π',font=f); w=b[2]-b[0]; h=b[3]-b[1]
    d.text(((size-w)/2-b[0],(size-h)/2-b[1]),'π',font=f,fill=(255,255,255))
    im.save(path)
icon(192,'pwa/icon-192.png',0.62); icon(512,'pwa/icon-512.png',0.62)
icon(512,'pwa/icon-maskable-512.png',0.45); icon(180,'pwa/apple-touch-icon.png',0.62)
js=re.search(r'<script>(.*)</script>',base,re.S).group(1)
open('/tmp/all.js','w').write(js.replace('%%SW%%',''))
pure=js.split('/*PURE-START*/')[1].split('/*PURE-END*/')[0]
import re as _re
grab=lambda name:_re.search(r'function '+name+r'\(.*?\n(?=function |/\*)',js,_re.S).group(0)
extra="".join(grab(n) for n in ["stepOf","updDigit","segScore","statusOfScore","validState","backupCode","readBackup"])
open('/tmp/pure.js','w').write(pure+extra+r"""
P=parse(DEFAULT_NOTE);
S={v:4,note:DEFAULT_NOTE,d:[[600,0,0],[600,0,0]],sl:{},best:3,fs:17,rfs:32,mode:"alt",rc:0,every:50};
const rb=readBackup("x "+backupCode()+" ");console.log("backup ok:",!!rb.s&&rb.s.best===3);
const A=(e,t)=>align(e,t).map(v=>v?"1":"0").join("");
console.log("align sub:",A("1234","1294")," omission:",A("1234567890","1245678901")," ajout:",A("1234","12934"));
function run(seq,start,n0){S.d=[[start,n0||0,0]];const out=[];for(const c of seq){updDigit(0,c==="1",1);out.push(statusOfScore(S.d[0][0])[0]+S.d[0][0]);}return out.join(" ");}
console.log("départ niveau, 6 justes :",run("111111",600));
console.log("solide établi (20 justes) puis 1 erreur puis justes:",(()=>{run("1".repeat(20),600);const t=S.d[0][0];updDigit(0,false,1);const a=S.d[0][0];updDigit(0,true,1);return t+" -> "+a+" ("+statusOfScore(a)+") -> "+S.d[0][0];})());
console.log("solide établi puis 3 erreurs d'affilée:",(()=>{run("1".repeat(20),600);const r=[];for(let i=0;i<3;i++){updDigit(0,false,1);r.push(statusOfScore(S.d[0][0])+S.d[0][0]);}return r.join(" ");})());
console.log("nouveau morceau 500, 8 justes:",run("11111111",500));
""")
print("built")
