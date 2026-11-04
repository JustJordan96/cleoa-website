"""Read-only inventory of the original public website. No authenticated requests."""
from pathlib import Path
import sys, json, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.tools/python'))
from bs4 import BeautifulSoup
BASE = 'https://www.cleoa.co.uk'
OUT = ROOT / 'audit'
(OUT / 'raw').mkdir(parents=True, exist_ok=True)
def fetch(url):
    with urllib.request.urlopen(url, timeout=45) as response:
        return response.read().decode('utf-8')
urls = set()
for kind in ['pages', 'blog-posts', 'blog-categories']:
    xml = fetch(f'{BASE}/{kind}-sitemap.xml')
    (OUT / f'{kind}-sitemap.xml').write_text(xml, encoding='utf-8')
    root = ET.fromstring(xml)
    urls.update(el.text for el in root.findall('{*}url/{*}loc'))
def inspect(url):
    slug = urllib.parse.urlsplit(url).path.strip('/') or 'home'
    raw = OUT / 'raw' / (slug.replace('/', '__') + '.html')
    html = raw.read_text(encoding='utf-8') if raw.exists() else fetch(url)
    raw.write_text(html, encoding='utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    main = soup.find(id='PAGES_CONTAINER') or soup.find('main') or soup.body
    for el in main.select('script, style, noscript'): el.decompose()
    ld = []
    for s in soup.select('script[type="application/ld+json"]'):
        try: ld.append(json.loads(s.string or s.get_text()))
        except: pass
    result = {
        'url':url, 'path':'/' if slug=='home' else '/'+slug,
        'title':soup.title.get_text() if soup.title else '',
        'description':(soup.select_one('meta[name="description"]') or {}).get('content',''),
        'text':main.get_text('\n',strip=True),
        'links':[{'text':a.get_text(' ',strip=True), 'href':a.get('href'), 'title':a.get('aria-label')} for a in main.select('a[href]')],
        'images':[{'src':im.get('src'),'alt':im.get('alt'),'data':im.parent.get('data-image-info')} for im in main.select('img')],
        'iframes':[{'src':i.get('src'),'title':i.get('title')} for i in main.select('iframe')],
        'structured':ld,
    }
    return result
with ThreadPoolExecutor(max_workers=5) as pool:
    pages = list(pool.map(inspect, sorted(urls)))
(OUT / 'inventory.json').write_text(json.dumps(pages, indent=2, ensure_ascii=False), encoding='utf-8')
for p in pages:
    print(p['path'], len(p['text']), 'characters',len(p['images']),'images',len(p['links']),'links')
print('Total:', len(pages))
