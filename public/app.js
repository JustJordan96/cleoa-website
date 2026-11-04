document.documentElement.classList.add('js');
const $=(s,root=document)=>root.querySelector(s);
const $$=(s,root=document)=>[...root.querySelectorAll(s)];
const activePlayers=new Map();
function stopMedia(root,except=null){
 $$('audio,video',root).forEach(player=>{if(player!==except)player.pause();});
 for(const [frame,button] of activePlayers){if(root.contains(frame)){frame.replaceWith(button);activePlayers.delete(frame);}}
}
const menu=$('.menu-toggle'),nav=$('#primary-nav');
function closeMenu(){menu?.setAttribute('aria-expanded','false');nav?.classList.remove('is-open');}
menu?.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));nav.classList.toggle('is-open',open);});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&menu?.getAttribute('aria-expanded')==='true'){closeMenu();menu.focus();}});
nav?.addEventListener('click',e=>{if(e.target.closest('a'))closeMenu();});
matchMedia('(min-width:981px)').addEventListener('change',e=>{if(e.matches)closeMenu();});

const tabs=$$('[role=tab]');
function selectTab(tab){tabs.forEach(t=>{const selected=t===tab;t.setAttribute('aria-selected',String(selected));t.tabIndex=selected?0:-1;$('#'+t.getAttribute('aria-controls')).hidden=!selected;});}
tabs.forEach((tab,i)=>{tab.addEventListener('click',()=>selectTab(tab));tab.addEventListener('keydown',e=>{let next;if(e.key==='ArrowRight')next=(i+1)%tabs.length;if(e.key==='ArrowLeft')next=(i-1+tabs.length)%tabs.length;if(e.key==='Home')next=0;if(e.key==='End')next=tabs.length-1;if(next!==undefined){e.preventDefault();selectTab(tabs[next]);tabs[next].focus();}});});

$$('[data-filter-list]').forEach(list=>{
 const items=$$('[data-filter-item]',list),buttons=$$('[data-filter]',list),input=$('[data-search-input]',list),more=$('[data-load-more]',list),empty=$('[data-empty-results]',list),count=$('[data-result-count]',list);
 let filter='all',limit=12;
 if(input)input.value=new URLSearchParams(location.search).get('q')||'';
 function update(){
  const q=(input?.value||'').trim().toLocaleLowerCase();
  const terms=q.split(/\s+/).filter(Boolean);
  const matches=items.filter(item=>(filter==='all'||item.dataset.category===filter)&&terms.every(t=>(item.dataset.search||'').includes(t)));
  items.forEach(item=>{item.hidden=!matches.includes(item)||(Boolean(more)&&!q&&matches.indexOf(item)>=limit);if(item.hidden)stopMedia(item);});
  const noun=input?'article':'entry';
  count.textContent=`${matches.length} ${matches.length===1?noun:input?'articles':'entries'}${q?' found':''}`;
  if(empty)empty.hidden=matches.length>0;
  if(more)more.hidden=Boolean(q)||matches.length<=limit;
 }
 buttons.forEach(button=>button.addEventListener('click',()=>{filter=button.dataset.filter;buttons.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));update();}));
 input?.addEventListener('input',()=>{limit=12;update();const u=new URL(location.href);if(input.value.trim())u.searchParams.set('q',input.value.trim());else u.searchParams.delete('q');history.replaceState(null,'',u);});
 $('[data-clear-search]',list)?.addEventListener('click',()=>{input.value='';input.dispatchEvent(new Event('input'));input.focus();});
 more?.addEventListener('click',()=>{const previouslyVisible=items.filter(i=>!i.hidden).length;limit+=12;update();const firstNew=items.filter(i=>!i.hidden)[previouslyVisible];$('h2 a',firstNew||list)?.focus({preventScroll:true});});
 update();
});
function openHashProject(){const id=decodeURIComponent(location.hash.slice(1));if(!id)return;const item=document.getElementById(id);if(item?.matches('.project')){const list=item.closest('[data-filter-list]');$('[data-filter="all"]',list)?.click();item.open=true;item.scrollIntoView({block:'start'});}}
openHashProject();window.addEventListener('hashchange',openHashProject);

const lightbox=$('#lightbox');let activeGallery=[],activeImage=0,opener;
function updateLightbox(){const button=activeGallery[activeImage];const img=$('#lightbox-image');img.src=button.dataset.fullImage;img.alt=button.dataset.caption;$('#lightbox-caption').textContent=button.dataset.caption;$('#lightbox-count').textContent=`${activeImage+1} / ${activeGallery.length}`;$$('[data-lightbox-prev],[data-lightbox-next]').forEach(b=>b.hidden=activeGallery.length<2);}
$$('[data-full-image]').forEach(button=>button.addEventListener('click',()=>{opener=button;activeGallery=$$('[data-full-image]',button.closest('[data-gallery]'));activeImage=activeGallery.indexOf(button);updateLightbox();lightbox.showModal();$('[data-lightbox-close]').focus();}));
function shiftImage(n){activeImage=(activeImage+n+activeGallery.length)%activeGallery.length;updateLightbox();}
$('[data-lightbox-close]')?.addEventListener('click',()=>lightbox.close());
$('[data-lightbox-prev]')?.addEventListener('click',()=>shiftImage(-1));
$('[data-lightbox-next]')?.addEventListener('click',()=>shiftImage(1));
lightbox?.addEventListener('keydown',e=>{if(e.key==='ArrowLeft'){e.preventDefault();shiftImage(-1);}if(e.key==='ArrowRight'){e.preventDefault();shiftImage(1);}});
lightbox?.addEventListener('close',()=>{opener?.focus({preventScroll:true});$('#lightbox-image').removeAttribute('src');});
lightbox?.addEventListener('click',e=>{if(e.target===lightbox){const r=lightbox.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)lightbox.close();}});

$$('.project').forEach(project=>project.addEventListener('toggle',()=>{if(!project.open)stopMedia(project);}));
document.addEventListener('play',event=>{if(event.target.matches('audio,video'))stopMedia(document,event.target);},true);
$$('[data-video-src]').forEach(button=>button.addEventListener('click',()=>{stopMedia(document);const frame=document.createElement('iframe');frame.src=button.dataset.videoSrc;frame.title=button.dataset.title||'Video player';frame.allow='autoplay; encrypted-media; picture-in-picture; fullscreen';frame.allowFullscreen=true;frame.referrerPolicy='strict-origin-when-cross-origin';activePlayers.set(frame,button);button.replaceWith(frame);}));
$$('[data-copy-link]').forEach(button=>button.addEventListener('click',async()=>{const status=button.nextElementSibling;try{await navigator.clipboard.writeText(location.href.split('#')[0]);status.textContent='Link copied.';}catch{status.textContent='Copy the link from your address bar.';}}));
