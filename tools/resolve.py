import json,sys,urllib.request,urllib.parse,io,os,time
from PIL import Image
names=[l.strip() for l in open('tools/names.txt',encoding='utf-8') if l.strip()]
API='https://db.ygoprodeck.com/api/v7/cardinfo.php?'
def get(q):
    try:
        with urllib.request.urlopen(urllib.request.Request(API+q,headers={'User-Agent':'meta-page/1'}),timeout=30) as r: return json.load(r)['data']
    except Exception: return None
ids=json.load(open('ids.json')) if os.path.exists('ids.json') else {}
miss=[]
for n in names:
    if n in ids and os.path.exists(f'images/{ids[n]}.jpg'): continue
    d=get('name='+urllib.parse.quote(n)); time.sleep(0.06)
    if not d: d=get('fname='+urllib.parse.quote(n))
    if not d: miss.append(n); continue
    c=d[0]; cid=c['id']; ids[n]=cid
    try:
        url=c['card_images'][0]['image_url_cropped']
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'meta-page/1'}),timeout=30) as r: im=Image.open(io.BytesIO(r.read())).convert('RGB')
        im.thumbnail((200,200)); im.save(f'images/{cid}.jpg',quality=72)
    except Exception as e: miss.append(n+' (img)')
    time.sleep(0.06)
json.dump(ids,open('ids.json','w'),indent=0,ensure_ascii=False)
print('ok',len(ids),'missing',miss)
