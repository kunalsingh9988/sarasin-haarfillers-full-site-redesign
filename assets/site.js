const menuToggle = document.querySelector('.menu-toggle');
const mobileMenu = document.querySelector('#mobile-menu');

if (menuToggle && mobileMenu) {
  const mobileViewport = window.matchMedia('(max-width: 800px)');
  const setOpen = (open, restoreFocus = false) => {
    mobileMenu.hidden = !open;
    menuToggle.setAttribute('aria-expanded', String(open));
    menuToggle.setAttribute('aria-label', open ? 'Sluit menu' : 'Open menu');
    if (restoreFocus) menuToggle.focus();
  };

  const isInside = (target) => mobileMenu.contains(target) || menuToggle.contains(target);
  const current = [...mobileMenu.querySelectorAll('.mobile-nav-link')].find((link) => {
    return location.pathname === link.pathname || location.pathname.startsWith(link.pathname);
  });
  if (current) current.setAttribute('aria-current', current.pathname === location.pathname ? 'page' : 'location');

  menuToggle.addEventListener('click', () => setOpen(mobileMenu.hidden));
  mobileMenu.addEventListener('click', (event) => {
    if (event.target.closest('a')) setOpen(false);
  });
  document.addEventListener('click', (event) => {
    if (!mobileMenu.hidden && !isInside(event.target)) setOpen(false);
  });
  document.addEventListener('focusin', (event) => {
    if (!mobileMenu.hidden && !isInside(event.target)) setOpen(false);
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !mobileMenu.hidden) {
      event.preventDefault();
      setOpen(false, true);
    }
  });
  mobileViewport.addEventListener('change', (event) => {
    if (!event.matches) setOpen(false);
  });
}

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

const heroResults = document.querySelector('.home-transformation');

if (heroResults) {
  const photos = [...heroResults.querySelectorAll('.transformation-images img')];
  const controls = heroResults.querySelector('.transformation-controls');
  const pause = heroResults.querySelector('.transformation-toggle');
  const next = heroResults.querySelector('.transformation-next');
  const count = heroResults.querySelector('.transformation-count');
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let active = 0;
  let playing = !motion.matches;
  let inView = !('IntersectionObserver' in window);
  let timer;

  const advance = () => {
    const target = (active + 1) % photos.length;
    if (!photos[target].complete || !photos[target].naturalWidth) return;
    photos[active].hidden = true;
    photos[target].hidden = false;
    active = target;
    count.textContent = `${active + 1} / ${photos.length}`;
  };

  const sync = () => {
    pause.textContent = playing ? 'Pauze' : 'Afspelen';
    clearInterval(timer);
    if (playing && inView && !document.hidden) timer = setInterval(advance, 3000);
  };

  pause.addEventListener('click', () => {
    playing = !playing;
    sync();
  });

  next.addEventListener('click', () => {
    playing = false;
    advance();
    sync();
  });

  motion.addEventListener('change', () => {
    playing = !motion.matches;
    sync();
  });

  document.addEventListener('visibilitychange', sync);
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(([entry]) => {
      inView = entry.isIntersecting;
      sync();
    });
    observer.observe(heroResults);
  }

  controls.hidden = false;
  sync();
}
