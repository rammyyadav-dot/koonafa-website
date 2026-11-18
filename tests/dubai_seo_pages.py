from pathlib import Path
import json
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

R=Path(__file__).resolve().parents[1]
base=R/"global"/"UAE"/"dubai"/"services"
data=json.loads((R/"config"/"dubai-seo-topics.json").read_text())
sitemap={x.text for x in ET.parse(R/"sitemap.xml").findall(".//{*}loc")}
class Page(HTMLParser):
    def __init__(self):super().__init__();self.h1=0;self.title=0;self.canonical=[];self.desc=[];self.links=[];self.schema=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="h1":self.h1+=1
        if tag=="title":self.title+=1
        if tag=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href"))
        if tag=="meta" and a.get("name")=="description":self.desc.append(a.get("content"))
        if tag=="a":self.links.append(a.get("href"))
        if tag=="script" and a.get("type")=="application/ld+json":self.schema.append(1)
def check(path,url):
    assert path.is_file(),path
    p=Page();p.feed(path.read_text(encoding="utf-8"))
    assert p.h1==p.title==1,(path,p.h1,p.title)
    assert p.canonical==[url],(path,p.canonical)
    assert len(p.desc)==1 and len(p.schema)==1,path
    assert url in sitemap,url
    return p
index=check(base/"index.html","https://koonafa.com/global/UAE/dubai/services/")
seen=set()
count=0
for g in data["groups"]:
    hub=f"https://koonafa.com/global/UAE/dubai/services/{g['id']}/"
    check(base/g["id"]/"index.html",hub)
    assert f"/global/UAE/dubai/services/{g['id']}/" in index.links,g["id"]
    for e in g["pages"]:
        url=f"{hub}{e['slug']}/"
        assert url not in seen,url
        seen.add(url)
        check(base/g["id"]/e["slug"]/"index.html",url)
        count+=1
assert count==100,count
dubai=Page();dubai.feed((R/"global"/"UAE"/"dubai"/"index.html").read_text())
assert "/global/UAE/dubai/services/" in dubai.links
print("PASS 100 Dubai specialist pages, 9 pillar hubs, directory, sitemap and canonical/metadata contracts")
