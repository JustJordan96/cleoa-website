"""One-time migration: retain original public copy, links and article structure."""
import sys, json, re, html, math
from pathlib import Path
from urllib.parse import urlsplit
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
from bs4 import BeautifulSoup, NavigableString
RAW=ROOT/'audit/raw'
OUT=ROOT/'content'
OUT.mkdir(exist_ok=True)
def soup(name): return BeautifulSoup((RAW/(name+'.html')).read_text(encoding='utf-8'),'html.parser')
def text(el): return re.sub(r'\s+',' ',el.get_text(' ',strip=True).replace('\u200b','')).strip()
def link(url):
    if url and urlsplit(url).hostname in ['www.cleoa.co.uk','cleoa.co.uk']:
        p=urlsplit(url); return (p.path or '/')+('?' + p.query if p.query else '')+('#'+p.fragment if p.fragment else '')
    return url or ''
def image_url(url): return url.split('/v1/')[0] if url else ''
def images(el):
    seen=set(); result=[]
    for im in el.select('img'):
        src=image_url(im.get('src',''))
        if src and src not in seen:
            seen.add(src); result.append({'src':src,'alt':im.get('alt','')})
    return result
def sanitize(el, rich=False):
    if isinstance(el,NavigableString): return html.escape(str(el).replace('\u200b',''))
    if el.name in ['script','style','button','svg','noscript','iframe']: return ''
    if el.name=='img':
        return f'<img src="{html.escape(image_url(el.get("src","")),quote=True)}" alt="{html.escape(el.get("alt", ""),quote=True)}" loading="lazy">'
    if el.name=='a':
        href=link(el.get('href'))
        if not href or not href.startswith(('https://','http://','mailto:','tel:','/','#')): return ''.join(sanitize(c,rich) for c in el.children)
        extra=' target="_blank" rel="noopener noreferrer"' if href.startswith(('http://','https://')) else ''
        return f'<a href="{html.escape(href,quote=True)}"{extra}>'+''.join(sanitize(c,rich) for c in el.children)+'</a>'
    content=''.join(sanitize(c,rich) for c in el.children)
    tag=el.name
    if rich and tag in ['h1','h2','h3','h4','h5','h6']: tag='p'
    if tag in ['p','h2','h3','h4','h5','h6','ul','ol','li','blockquote','strong','b','em','i','figcaption','figure','sup','sub']:
        return f'<{tag}>{content}</{tag}>' if content.strip() else ''
    if tag=='br': return '<br>'
    return content
def clean_rich(el, remove_title=False):
    markup=sanitize(el,True)
    parts=re.split(r'<br\s*/?>|</p>|<p>',markup)
    rows=[]
    for part in parts:
        part=part.strip()
        if text(BeautifulSoup(part,'html.parser')): rows.append(part)
    title=text(BeautifulSoup(rows[0],'html.parser')) if rows else ''
    if remove_title: rows=rows[1:]
    body='\n'.join('<p>'+r+'</p>' for r in rows)
    return title,body
project_doc=soup('projects')
projects=[]
for sec in project_doc.select('#PAGES_CONTAINER section[id]'):
    rts=sec.select('[data-testid="richTextElement"]')
    for index,rt in enumerate(rts):
        title,body=clean_rich(rt,True)
        if title in ['Portfolio','Events'] or not title: continue
        kind='event' if sec.get('id')=='comp-ldkgessg2' else 'project'
        if kind=='event': title,body='Events & milestones', clean_rich(rt)[1]
        projects.append({'id':rt['id'],'sectionId':sec['id'],'title':title,'html':body,'images':images(sec) if index==0 or kind=='event' else [],'kind':kind})
about=soup('about-me')
about_rich=about.select('#PAGES_CONTAINER [data-testid="richTextElement"]')
about_blocks=[{'id':r['id'],'html':clean_rich(r)[1]} for r in about_rich if text(r) and text(r)!='About Me']
services=soup('services-9')
service_blocks=[{'id':r['id'],'title':clean_rich(r)[0],'html':clean_rich(r,True)[1]} for r in services.select('#PAGES_CONTAINER [data-testid="richTextElement"]') if text(r)]
articles=[]
for path in sorted(RAW.glob('post__*.html')):
    doc=BeautifulSoup(path.read_text(encoding='utf-8'),'html.parser')
    ld=next(json.loads(s.get_text()) for s in doc.select('script[type="application/ld+json"]') if 'BlogPosting' in s.get_text())
    body=doc.select_one('[data-hook="post-description"]')
    if body is None: raise ValueError('Missing body '+path.name)
    rawhtml=sanitize(body)
    clean=BeautifulSoup(rawhtml,'html.parser')
    for el in clean.select('p'):
        if not text(el) and not el.select_one('img'): el.decompose()
    cats=[]
    # The category navigation is outside this footer section; only actual assigned categories.
    for el in doc.select('[data-hook="post-categories"] a, [data-hook="categories"] a'):
        cats.append({'name':text(el),'path':link(el.get('href'))})
    if not cats:
        matches=doc.select('a[href*="/writing/categories/"]')[4:]
        cats=[{'name':text(a),'path':link(a.get('href'))} for a in matches]
    cats=list({x['path']:x for x in cats}.values())
    articles.append({'slug':path.stem.removeprefix('post__'),'title':ld['headline'],'description':ld.get('description',''),'date':ld['datePublished'][:10],'modified':ld['dateModified'][:10],'cover':image_url(ld.get('image',{}).get('url','')),'html':str(clean),'categories':cats,'minutes':max(1,math.ceil(len(text(body).split())/220)),'text':text(body)})
inventory=json.loads((ROOT/'audit/inventory.json').read_text(encoding='utf-8'))
for article in articles:
    page=next(p for p in inventory if p['path']=='/post/'+article['slug'])
    article['tags']=list({l['href']:{'name':l['text'],'path':link(l['href'])} for l in page['links'] if '/writing/tags/' in l['href'] or '/writing/hashtags/' in l['href']}.values())
writing=next(p for p in inventory if p['path']=='/writing')
order=[l['href'].split('/post/')[-1] for l in writing['links'] if '/post/' in l['href']]
articles.sort(key=lambda a:(a['date'],-order.index(a['slug']) if a['slug'] in order else -100),reverse=True)
for name,data in [('projects',projects),('articles',articles),('original-pages',{'about':about_blocks,'aboutImages':images(about.select_one('#PAGES_CONTAINER')),'services':service_blocks,'serviceImages':images(services.select_one('#PAGES_CONTAINER'))})]:
    (OUT/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Extracted {len(projects)} project/event entries, {len(articles)} complete articles, {len(about_blocks)} about blocks, {len(service_blocks)} service blocks.')
print('Service blocks:',[(b['id'],b['title'][:50]) for b in service_blocks])
print('Article categories:',[(a['slug'],[c['name'] for c in a['categories']]) for a in articles])
