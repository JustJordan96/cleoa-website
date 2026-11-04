import assert from 'node:assert/strict';
import {readFile,stat,readdir,writeFile} from 'node:fs/promises';
import {resolve,join,extname} from 'node:path';
const root=resolve('dist');
const readJSON=async p=>JSON.parse(await readFile(p,'utf8'));
const routes=await readJSON('audit/build-routes.json');
const inventory=await readJSON('audit/inventory.json');
const manifest=await readJSON('audit/media-manifest.json');
const articles=await readJSON('content/articles.json');
const projects=await readJSON('content/projects.json');
const tagAudit=await readJSON('audit/tag-pages.json');
const decode=s=>s.replace(/&#x([0-9a-f]+);/gi,(_,n)=>String.fromCodePoint(parseInt(n,16))).replace(/&#(\d+);/g,(_,n)=>String.fromCodePoint(+n)).replaceAll('&amp;','&').replaceAll('&quot;','"').replaceAll('&apos;',"'").replaceAll('&lt;','<').replaceAll('&gt;','>').replaceAll('&nbsp;',' ');
const norm=s=>decode(s.replace(/<[^>]*>/g,' ')).replace(/[\s\u200b]+/g,' ').trim();
const errors=[];
let localLinks=0,images=0;
const htmls=new Map();
for(const route of [...routes,'/404']){
 const file=route==='/'?'index.html':route==='/404'?'404.html':route.slice(1)+'/index.html';
 htmls.set(route,await readFile(join(root,file),'utf8'));
}
const routeFor=path=>path==='/'?'/':path.replace(/\/$/,'');
for(const [route,html] of htmls){
 if((html.match(/<h1\b/g)||[]).length!==1)errors.push(`${route}: expected exactly one h1`);
 if(!html.includes('name="description"')||!html.includes('rel="canonical"'))errors.push(`${route}: missing search metadata`);
 if(/<(?:script|img|source)[^>]+src="https?:/i.test(html))errors.push(`${route}: automatic remote asset dependency`);
 for(const match of html.matchAll(/<(?:a|img|script|link|source|video)\b[^>]*>/g)){
  const tag=match[0];
  if(tag.startsWith('<img')){images++;if(!/\balt="/.test(tag))errors.push(`${route}: image without alt`);}
  for(const attr of tag.matchAll(/\b(?:href|src|poster)="([^"]+)"/g)){
   const value=decode(attr[1]);
   if(!value.startsWith('/')&&!value.startsWith('#'))continue;
   const url=new URL(value,'http://local'+route);
   const pathname=decodeURIComponent(url.pathname);
   const target=routeFor(pathname);
   localLinks++;
   if(htmls.has(target)){
    if(url.hash){const id=decodeURIComponent(url.hash.slice(1));if(!htmls.get(target).includes(`id="${id}"`))errors.push(`${route}: missing fragment ${value}`);}
   }else{
    try{assert((await stat(join(root,pathname))).isFile());}catch{errors.push(`${route}: missing local file ${value}`);}
   }
  }
 }
 for(const block of html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)){
  try{JSON.parse(block[1]);}catch{errors.push(`${route}: invalid structured data`);}
 }
}
for(const source of inventory){if(!routes.includes(source.path))errors.push(`Original route missing: ${source.path}`);}
for(const archive of tagAudit.pages){
 if(archive.status!==200)errors.push(`Original archive inspection incomplete: ${archive.path}`);
 if(!routes.includes(archive.path))errors.push(`Original archive missing: ${archive.path}`);
 const expected=articles.filter(a=>a.tags?.some(t=>t.path===archive.path)).map(a=>'/post/'+a.slug);
 for(const post of archive.linkedPostPaths)if(!expected.includes(post))errors.push(`Archive membership missing: ${archive.path} -> ${post}`);
}
for(const a of articles){
 const html=htmls.get('/post/'+a.slug)||'';
 const body=html.split('<div class="article-prose prose">')[1]?.split('</div></div><footer')[0]||'';
 if(norm(body)!==norm(a.html))errors.push(`Article text mismatch: ${a.slug}`);
 for(const tag of a.tags||[])if(!routes.includes(tag.path))errors.push(`Tag route missing: ${tag.path}`);
}
const portfolio=norm(htmls.get('/projects'));
for(const p of projects){
 for(const paragraph of p.html.matchAll(/<p>([\s\S]*?)<\/p>/g)){
  const value=norm(paragraph[1]).replace(/here\s*-{2,}>/g,'below.').replace(/-{3,}>/g,'');
  if(value&&!portfolio.includes(value))errors.push(`Portfolio paragraph missing: ${p.title}: ${value.slice(0,90)}`);
 }
}
for(const [source,a] of Object.entries(manifest.assets)){
 try{assert((await stat(join(root,a.local))).size>0);}catch{errors.push(`Asset missing: ${source}`);}
}
assert.equal(articles.length,28,'All 28 original articles must remain');
assert.equal(projects.length,23,'22 portfolio entries plus events');
assert.equal(manifest.errors.length,0,'Asset migration should be complete');
const report={passed:errors.length===0,pages:routes.length,originalSitemapPages:inventory.length,articles:articles.length,portfolioEntries:projects.length-1,tagArchives:routes.filter(r=>/\/writing\/(tags|hashtags)\//.test(r)).length,localAssets:Object.keys(manifest.assets).length,checkedLocalReferences:localLinks,imageInstances:images,errors};
await writeFile('audit/validation.json',JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));
if(errors.length)process.exitCode=1;
