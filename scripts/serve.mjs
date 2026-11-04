import http from 'node:http';
import {readFile, stat} from 'node:fs/promises';
import {resolve, extname, sep} from 'node:path';
const root=resolve('dist');
const port=Number(process.env.PORT || 4173);
const mime={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.webp':'image/webp','.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml','.woff2':'font/woff2','.ttf':'font/ttf','.mp4':'video/mp4','.mp3':'audio/mpeg','.pdf':'application/pdf','.xml':'application/xml; charset=utf-8','.txt':'text/plain; charset=utf-8'};
http.createServer(async(req,res)=>{
  try{
    const path=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
    let file=resolve(root,'.'+path);
    if(file!==root&&!file.startsWith(root+sep)){res.writeHead(403);res.end();return;}
    try{if((await stat(file)).isDirectory())file=resolve(file,'index.html');}
    catch{file=resolve(file,'index.html');}
    let data;
    try{data=await readFile(file);}catch{file=resolve(root,'404.html');data=await readFile(file);res.statusCode=404;}
    res.setHeader('Content-Type',mime[extname(file)]||'application/octet-stream');
    res.setHeader('Cache-Control','no-store');
    res.setHeader('X-Content-Type-Options','nosniff');
    if(req.headers.range && /\.(mp4|mp3)$/.test(file)){
      const m=/bytes=(\d+)-(\d*)/.exec(req.headers.range);
      if(m){const start=Number(m[1]),end=Math.min(m[2]?Number(m[2]):data.length-1,data.length-1);if(start> end){res.writeHead(416,{'Content-Range':`bytes */${data.length}`});res.end();return;}res.writeHead(206,{'Accept-Ranges':'bytes','Content-Range':`bytes ${start}-${end}/${data.length}`,'Content-Length':end-start+1});res.end(req.method==='HEAD'?undefined:data.subarray(start,end+1));return;}
    }
    res.setHeader('Content-Length',data.length);
    res.end(req.method==='HEAD'?undefined:data);
  }catch{res.writeHead(400);res.end('Bad request');}
}).listen(port,'127.0.0.1',()=>console.log(`Cleo Anderson preview: http://127.0.0.1:${port}`));
