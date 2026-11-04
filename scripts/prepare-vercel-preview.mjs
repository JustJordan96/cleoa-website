import {readFile, stat, mkdir, rm, cp, writeFile} from 'node:fs/promises';
import {resolve, dirname, join} from 'node:path';

const workspace=process.cwd();
const dist=resolve('dist');
const output=resolve('.vercel/output');
if(dirname(output)!==resolve('.vercel'))throw new Error('Unexpected Vercel output directory.');
const validation=JSON.parse(await readFile('audit/validation.json','utf8'));
if(!validation.passed)throw new Error('The static site must pass npm run check before deployment.');
await stat(join(dist,'index.html'));
const paths=JSON.parse(await readFile('audit/build-routes.json','utf8'));
const escapeRegex=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
const routes=[
  {src:'/(.*)',headers:{'X-Robots-Tag':'noindex, nofollow'},continue:true},
  ...paths.map(path=>({src:path==='/'?'^/$':`^${escapeRegex(path)}/?$`,dest:path==='/'?'/index.html':`${path}/index.html`})),
  {handle:'filesystem'},
  {src:'/.*',dest:'/404.html',status:404}
];
await rm(output,{recursive:true,force:true});
await mkdir(output,{recursive:true});
await cp(dist,join(output,'static'),{recursive:true});
// Social previews need an image origin that is reachable on the review host.
const previewOrigin=process.env.VERCEL_PREVIEW_ORIGIN;
if(previewOrigin){
  const origin=new URL(previewOrigin);
  if(origin.protocol!=='https:'||!origin.hostname.endsWith('.vercel.app')||origin.pathname!=='/')throw new Error('Expected a Vercel HTTPS origin.');
  const {domain}=JSON.parse(await readFile('content/site.json','utf8'));
  for(const path of [...paths,'/404']){
    const file=join(output,'static',path==='/'?'index.html':path==='/404'?'404.html':path.slice(1)+'/index.html');
    let html=await readFile(file,'utf8');
    html=html.replaceAll(domain+'/assets/',origin.origin+'/assets/');
    html=html.replace(/(<meta property="og:url" content=")[^"]+"/,`$1${origin.origin}${path==='/'?'':path}"`);
    await writeFile(file,html);
  }
}
await writeFile(join(output,'config.json'),JSON.stringify({version:3,routes},null,2));
console.log(`Prepared ${paths.length} verified pages for a Vercel review deployment. Search indexing is disabled.`);
