"""Migrate public CLEO A media; preserve gallery order and standalone media metadata.

Requires beautifulsoup4, Pillow and imageio-ffmpeg (installed locally in .tools/python).
Fetches only URLs exposed by the public site's HTML, JSON, and media records.
"""
from pathlib import Path
import sys, json, re, io, hashlib, urllib.request, urllib.parse, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.tools/python'))
from bs4 import BeautifulSoup
from PIL import Image, ImageOps
ASSET = ROOT / 'public/assets'
for kind in ['images','video','audio','documents']: (ASSET / kind).mkdir(parents=True, exist_ok=True)
manifest = {'source':'https://www.cleoa.co.uk','auditedDate':'2026-11-03','assets':{},'components':{},'homeSlides':[],'notes':[],'errors':[]}
sources = {}
def canonical(url):
    if not url: return ''
    # A few Wix video thumbnail img src attributes incorrectly contain srcset text.
    if ' 1x,' in url: url=url.split(' 1x,',1)[0]
    if url.startswith('//'): url = 'https:' + url
    if url.startswith('https://static.wixstatic.com/media/'):
        return urllib.parse.unquote(url.split('/v1/')[0].split('?')[0])
    return url.split('?')[0] if re.search(r'\.(?:jpg|jpeg|png|webp|gif|mp3|mp4|pdf)(?:\?|$)',url,re.I) else url
def add(url, kind='image', title=''):
    if not url: return ''
    if not url.startswith(('https://','http://')):
        if re.match(r'[a-zA-Z0-9_-]+(?:~[^/]+)?\.(?:jpg|jpeg|png|webp|gif|svg)$',url,re.I): url='https://static.wixstatic.com/media/'+url
        else: return ''
    url=canonical(url)
    if url not in sources: sources[url]={'kind':kind,'title':title}
    return url
def read(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req,timeout=90) as r: return r.read()
def image_item(v):
    src=add(v.get('uri') or v.get('mediaUrl') or v.get('src'),title=v.get('title') or v.get('alt',''))
    return {'kind':'image','src':src,'title':v.get('title') or v.get('alt',''),'width':v.get('width'),'height':v.get('height')}
def all_images(v):
    found=[]
    if isinstance(v,dict):
        if v.get('uri') and re.search(r'\.(jpg|jpeg|png|webp|gif|svg)$',v['uri'],re.I): found.append(image_item(v))
        for x in v.values():
            if isinstance(x,(dict,list)): found+=all_images(x)
    elif isinstance(v,list):
        for x in v: found+=all_images(x)
    return found
def source_section(soup, cid, parent_map, structure):
    el=soup.find(id=cid)
    if el:
        sec=el.find_parent('section',id=True)
        if sec:return sec['id']
    parent=parent_map.get(cid)
    while parent:
        if structure.get(parent,{}).get('componentType') in ['ClassicSection','Slide']:return parent
        parent=parent_map.get(parent)
    return ''
def video_item(src,title='',desc='',poster='',duration=None):
    q=urllib.parse.urlsplit(src)
    if 'youtu' in q.netloc:
        vid=urllib.parse.parse_qs(q.query).get('v',[''])[0] or q.path.rstrip('/').split('/')[-1]
        poster=poster or 'https://i.ytimg.com/vi/'+vid+'/hqdefault.jpg'
        return {'kind':'youtube','src':'https://www.youtube-nocookie.com/embed/'+vid,'url':src,'videoId':vid,'title':title,'description':desc,'poster':add(poster),'duration':duration}
    return {'kind':'video','src':add(src,'video',title),'title':title,'description':desc,'poster':add(poster) if poster else '', 'duration':duration}

main={'home','about-me','services-9','projects','writing'}
for f in sorted((ROOT/'audit/raw').glob('*.html')):
    soup=BeautifulSoup(f.read_text(encoding='utf-8'),'html.parser')
    path='/' if f.stem=='home' else '/'+f.stem.replace('__','/')
    content=soup.find(id='PAGES_CONTAINER') or soup.body
    for im in content.select('img[src]'): add(im['src'],title=im.get('alt',''))
    for meta in soup.select('meta[property="og:image"]'): add(meta.get('content',''))
    for link in content.select('a[href]'):
        if re.search(r'\.(pdf|docx?|xlsx?|mp3|mp4)(\?|$)',link['href'],re.I): add(link['href'],'document',link.get_text(' ',strip=True))
    for icon in soup.select('link[rel="icon"],link[rel="shortcut icon"]'):add(icon.get('href',''),title='Site icon')
    if f.stem not in main: continue
    viewer=json.loads(soup.find(id='wix-viewer-model').string)
    page_files=viewer['siteAssets']['siteScopeParams']['pageJsonFileNames']
    warm=json.loads(soup.find(id='wix-warmup-data').string)
    # Follow literal, published preload URLs, without invoking the Wix runtime.
    feature_urls=[l['href'] for l in soup.select('link[href]') if 'module=thunderbolt-features' in l['href'] and page_files['masterPage'] not in l['href']]
    for feature_url in feature_urls:
        data=json.loads(read(feature_url))
        structure=data['structure']['components']
        parents={child:parent for parent,node in structure.items() for child in node.get('components',[])}
        props=data['props']['render']['compProps']
        for cid,v in props.items():
            ctype=structure.get(cid,{}).get('componentType','')
            items=[]
            if ctype in ['SliderGallery','PaginatedGridGallery']:
                items=[image_item(i.get('image',i)) for i in v.get('items',[])]
            elif ctype=='VideoPlayer':
                post=v.get('playableConfig',{}).get('poster',{})
                poster=('https://static.wixstatic.com/media/'+post['uri']) if post.get('uri') else ''
                items=[video_item(v['src'],v.get('title',''),v.get('playableConfig',{}).get('description',''),poster,v.get('duration'))]
            elif ctype=='SingleAudioPlayer':
                items=[{'kind':'audio','src':add(i['url'],'audio',i.get('trackName','')),'title':i.get('trackName',''),'artist':i.get('artistName','')} for i in v.get('playlist',[])]
            else: items=all_images(v)
            if items:
                unique={i['src']:i for i in items if i.get('src')}
                manifest['components'][cid]={'page':path,'sectionId':source_section(soup,cid,parents,structure),'type':ctype,'items':list(unique.values())}
        if f.stem=='home':
            for slide_id in ['comp-kgo3vvin','comp-ju1gkbcw','comp-kkng1bww','comp-jbrvklnn']:
                def descend(cid):
                    return [cid]+[c for child in structure.get(cid,{}).get('components',[]) for c in descend(child)]
                cids=descend(slide_id)
                text=[BeautifulSoup(props[c]['html'],'html.parser').get_text(' ',strip=True) for c in cids if props.get(c,{}).get('html')]
                images=[i for c in cids for i in manifest['components'].get(c,{}).get('items',[]) if i['kind']=='image']
                manifest['homeSlides'].append({'id':slide_id,'text':text,'images':images})
    for app in warm.get('appsWarmupData',{}).values():
        for key,value in app.items():
            if key.endswith('_galleryData'):
                cid=key.removesuffix('_galleryData')
                items=[]
                for i in value.get('items',[]):
                    m=i.get('metaData',{})
                    items.append(image_item({'uri':i['mediaUrl'],'title':m.get('title',''),'width':m.get('width'),'height':m.get('height')}))
                manifest['components'][cid]={'page':path,'sectionId':source_section(soup,cid,{},{}),'type':'ProGallery','items':items}
            elif key.startswith('vodWidgetData-'):
                channel=json.loads(value); cid=key.removeprefix('vodWidgetData-');items=[]
                for v in channel['__VIDEOS__']['data']:
                    poster=v.get('customCoverUrl') or v.get('coverUrl') or ''
                    if v.get('mediaExternUrl'):src=v['mediaExternUrl']
                    elif v.get('videoSource')=='youtube':src='https://www.youtube.com/watch?v='+v['externalId']
                    else:
                        qualities=v.get('mediaInfo',{}).get('fileOutput',{}).get('video',[])
                        quality=next((q for q in qualities if q.get('height')==720),qualities[-1] if qualities else {'quality':'720p'})['quality']
                        # The public record declares the exact filename, CDN and available rendition.
                        src='https://video.wixstatic.com/video/'+v['mediaFileName']+'/'+quality+'/mp4/file.mp4'
                    items.append(video_item(src,v['title'],v.get('description',''),poster,v.get('durationSec')))
                manifest['components'][cid]={'page':path,'sectionId':source_section(soup,cid,{},{}),'type':'VideoChannel','title':channel['__CHANNEL__']['title'],'items':items}

print('Discovered',len(sources),'assets and',len(manifest['components']),'media components',flush=True)
def download(entry):
    url,meta=entry;kind=meta['kind']
    try:
        parsed=urllib.parse.urlsplit(url)
        basename=urllib.parse.unquote(parsed.path.rsplit('/',1)[-1])
        if kind=='image':
            if 'ytimg.com' in parsed.netloc:basename='youtube-'+parsed.path.split('/')[2]+'-'+basename
            filename=basename+'.webp' if not basename.endswith('.svg') else basename
            local='/assets/images/'+filename
        elif kind=='video':local='/assets/video/'+parsed.path.split('/video/')[1].split('/')[0]+'.mp4'
        elif kind=='audio':local='/assets/audio/'+basename
        else:local='/assets/documents/'+basename
        target=ROOT/'public'/local.lstrip('/')
        out={**meta,'local':local}
        if not target.exists() or target.stat().st_size==0:
            raw=read(url)
            if kind=='image' and not basename.endswith('.svg'):
                im=ImageOps.exif_transpose(Image.open(io.BytesIO(raw)))
                if im.mode not in ['RGB','RGBA']:im=im.convert('RGB')
                # Article screenshot text is retained at full resolution.
                if '3e239c51bc4d44da8247a9c56d62cec4' not in basename: im.thumbnail((1600,1600),Image.Resampling.LANCZOS)
                im.save(target,'WEBP',quality=88,method=3)
            else:target.write_bytes(raw)
        out['bytes']=target.stat().st_size
        if kind=='image' and not basename.endswith('.svg'):
            with Image.open(target) as im:out.update(width=im.width,height=im.height)
        out['sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
        return url,out,None
    except Exception as e:return url,None,{'source':url,'error':str(e)}
with ThreadPoolExecutor(max_workers=6) as pool:
    jobs=[pool.submit(download,entry) for entry in sources.items()]
    for i,job in enumerate(as_completed(jobs),1):
        url,record,error=job.result()
        if record:manifest['assets'][url]=record
        if error:
            manifest['errors'].append(error)
            print('Unavailable:',url,error['error'],flush=True)
        if i%20==0:print('Downloaded',i,'/',len(sources),flush=True)

# Wix public channels return short-lived playback URLs. Refresh them through the
# same anonymous public-session endpoint used by the original website. Tokens
# remain in process memory: no URLs containing tokens are persisted or printed.
if any('/video.wixstatic.com/' in e['source'] or '://video.wixstatic.com/' in e['source'] for e in manifest['errors']):
    import imageio_ffmpeg
    soup=BeautifulSoup((ROOT/'audit/raw/projects.html').read_text(encoding='utf-8'),'html.parser')
    viewer=json.loads(soup.find(id='wix-viewer-model').string)
    warm=json.loads(soup.find(id='wix-warmup-data').string)
    channel=json.loads(warm['appsWarmupData']['14409595-f076-4753-8303-9a86f9f71469']['vodWidgetData-comp-kyubpcpj'])
    session=json.loads(read(viewer['accessTokensUrl']))
    instance=session['apps']['14409595-f076-4753-8303-9a86f9f71469']['instance']
    config=channel['__VIDEOS__']['config']
    params={k:str(v).lower() if isinstance(v,bool) else v for k,v in config['params'].items() if v is not None}
    url=urllib.parse.urljoin('https://www.cleoa.co.uk',config['url'])+'?'+urllib.parse.urlencode(params)
    request=urllib.request.Request(url,headers={'authorization':instance,'Accept':'application/json','x-wix-brand':'wix'})
    with urllib.request.urlopen(request,timeout=30) as r: videos=json.loads(r.read())['items']
    for video in videos:
        if video.get('video_source')!='computer' or not video.get('is_public'):continue
        asset_url=next((e['source'] for e in manifest['errors'] if video['media_file_name'] in e['source']),None)
        if not asset_url:continue
        target=ASSET/'video'/(video['media_file_name']+'.mp4')
        try:
            master_url=video['play_info']['url']
            master=read(master_url).decode().splitlines()
            variants=[line for line in master if line and not line.startswith('#')]
            rendition=next((v for v in variants if '/720p/' in v),variants[-1])
            playlist_url=urllib.parse.urljoin(master_url,rendition)
            playlist=read(playlist_url).decode().splitlines()
            if any(line.startswith('#EXT-X-KEY:') for line in playlist):
                raise ValueError('Encrypted HLS media requires the original player; not copied.')
            segments=[urllib.parse.urljoin(playlist_url,line) for line in playlist if line and not line.startswith('#')]
            data=b''.join(read(segment) for segment in segments)
            result=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-i','pipe:0','-c','copy','-movflags','+faststart',str(target)],input=data,capture_output=True)
            if result.returncode!=0:raise RuntimeError('Local MP4 remux failed')
            manifest['assets'][asset_url]={'kind':'video','title':video['title'],'local':'/assets/video/'+target.name,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'acquisition':'Refreshed public playback, 720p HLS remuxed without re-encoding'}
            manifest['errors']=[e for e in manifest['errors'] if e['source']!=asset_url]
            print('Recovered public video:',video['title'],flush=True)
        except Exception as error:
            print('Public video could not be recovered:',video['title'],type(error).__name__,flush=True)

for comp in manifest['components'].values():
    for item in comp['items']:
        if item.get('src') in manifest['assets']:item['local']=manifest['assets'][item['src']]['local']
        if item.get('poster') in manifest['assets']:item['posterLocal']=manifest['assets'][item['poster']]['local']
for slide in manifest['homeSlides']:
    for item in slide['images']:
        if item['src'] in manifest['assets']:item['local']=manifest['assets'][item['src']]['local']
manifest['notes']=[
    'Images are local WebP files, fitted within 1600 x 1600 without cropping. The Going Green article screenshot retains its original resolution for legibility.',
    'Original YouTube videos remain external embeds with locally stored thumbnails. Their availability and embedding permissions remain controlled by the original publishers.',
    'Wix-hosted public MP4 and MP3 media are downloaded locally, so they do not require the old Wix website to remain live.',
    'Two LAB videos required refreshing the normal anonymous public-player session and remuxing the public 720p HLS streams to MP4. Playback tokens are never persisted in the manifest or media files.',
    'Going Green contains an article JPEG and a YouTube link, with no PDF or document attachment exposed in the public article markup.',
]
(ROOT/'audit/media-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
notes='# Media migration\n\n'+'\n\n'.join(manifest['notes'])+'\n\n'
notes+=f"Downloaded {len(manifest['assets'])} assets ({sum(x['bytes'] for x in manifest['assets'].values())/1024/1024:.1f} MB). Extracted {len(manifest['components'])} media components.\n\n"
if manifest['errors']:notes+='## Unavailable source assets\n\n'+'\n'.join(f"- {e['source']}: {e['error']}" for e in manifest['errors'])+'\n'
(ROOT/'audit/media-notes.md').write_text(notes,encoding='utf-8')
print('Complete:',len(manifest['assets']),'assets;',len(manifest['errors']),'errors',flush=True)
for e in manifest['errors']:print(e)
