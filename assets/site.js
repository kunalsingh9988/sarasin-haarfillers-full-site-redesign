const toggle=document.querySelector('.menu-toggle');
const mobile=document.querySelector('.mobile-nav');
if(toggle&&mobile){toggle.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')==='true';toggle.setAttribute('aria-expanded',String(!open));toggle.setAttribute('aria-label',open?'Open menu':'Sluit menu');mobile.hidden=open;});mobile.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{mobile.hidden=true;toggle.setAttribute('aria-expanded','false')}));}
const headings=[...document.querySelectorAll('.source-content h2[id]')];
if(headings.length&&'IntersectionObserver' in window){const links=[...document.querySelectorAll('.article-aside nav a')];const io=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(entry.isIntersecting){links.forEach(a=>a.style.color=a.hash==='#'+entry.target.id?'#18352d':'');}})},{rootMargin:'-20% 0px -70% 0px'});headings.forEach(h=>io.observe(h));}

const videoGallery = document.querySelector('.home-videos');
const videoDialog = videoGallery?.querySelector('dialog');

if (videoDialog?.showModal) {
  const player = videoDialog.querySelector('.video-dialog-player');
  const title = videoDialog.querySelector('h3');
  const source = videoDialog.querySelector('.video-dialog-source');
  let opener;

  videoGallery.addEventListener('click', (event) => {
    const card = event.target.closest('.video-preview');
    if (!card || event.defaultPrevented || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;

    event.preventDefault();
    opener = card;
    title.textContent = card.querySelector('strong').textContent;
    source.href = card.href;

    const youtubeId = card.dataset.youtube;
    const media = document.createElement(youtubeId ? 'iframe' : 'video');
    if (youtubeId) {
      media.title = title.textContent;
      media.allow = 'autoplay; encrypted-media; fullscreen; picture-in-picture';
      media.allowFullscreen = true;
      media.src = `https://www.youtube-nocookie.com/embed/${youtubeId}?autoplay=1&playsinline=1`;
    } else {
      media.setAttribute('aria-label', title.textContent);
      media.controls = true;
      media.playsInline = true;
      media.src = card.href;
      media.poster = card.querySelector('img').src;
    }

    document.querySelectorAll(".process-feature video").forEach((video) => video.pause());
    player.replaceChildren(media);
    videoDialog.showModal();
    if (!youtubeId) media.play().catch(() => {});
  });

  videoDialog.querySelector('.video-dialog-close').addEventListener('click', () => videoDialog.close());
  videoDialog.addEventListener('close', () => {
    player.replaceChildren();
    opener?.focus();
  });
}
