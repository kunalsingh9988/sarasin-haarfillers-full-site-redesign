(() => {
  const page = document.querySelector('.women-feature');
  if (!page) return;

  function prepareDialog(dialog) {
    let opener;
    const body = dialog.querySelector('.wf-dialog-body');
    dialog.querySelector('.wf-dialog-close').addEventListener('click', () => dialog.close());
    dialog.addEventListener('close', () => {
      body.replaceChildren();
      if (document.activeElement === document.body || dialog.contains(document.activeElement)) {
        opener?.focus({ preventScroll: true });
      }
    });
    return (trigger, content) => {
      opener = trigger;
      body.replaceChildren(content);
      dialog.showModal();
    };
  }

  const gallery = page.querySelector('.wf-results');
  const cases = [...gallery.querySelectorAll('[data-case]')];
  const controls = gallery.querySelector('[data-gallery-controls]');
  const count = controls.querySelector('.wf-result-count');
  const thumbnails = controls.querySelector('.wf-thumbnails');
  const photoDialog = gallery.querySelector('.wf-photo-dialog');
  const showPhoto = typeof photoDialog.showModal === 'function' ? prepareDialog(photoDialog) : null;
  let current = 0;

  function displayCase(index) {
    current = (index + cases.length) % cases.length;
    const active = cases[current];
    renderComparison(active);
    cases.forEach((photo, number) => { photo.hidden = number !== current; });
    [...thumbnails.children].forEach((button, number) => {
      button.setAttribute('aria-pressed', String(number === current));
    });
    const thumb = thumbnails.children[current].getBoundingClientRect();
    const track = thumbnails.getBoundingClientRect();
    if (thumb.right > track.right) thumbnails.scrollLeft += thumb.right - track.right + 5;
    else if (thumb.left < track.left) thumbnails.scrollLeft -= track.left - thumb.left + 5;
    count.textContent = `${current + 1} / ${cases.length}`;
  }

  function renderComparison(photo) {
    if (photo.querySelector('.wf-comparer')) return;
    const originalLink = photo.querySelector('.wf-original');
    const originalImage = originalLink.querySelector('img');
    const ratio = Number(originalImage.getAttribute('width')) / (2 * Number(originalImage.getAttribute('height')));
    if (!Number.isFinite(ratio) || ratio <= 0) return;

    const comparison = document.createElement('div');
    comparison.className = 'wf-comparer';
    comparison.innerHTML = `
      <div class="wf-compare-frame" aria-hidden="true">
        <div class="wf-compare-divider"></div>
        <div class="wf-compare-labels"><span>Voor</span><span>Na</span></div>
      </div>
      <label class="wf-slider-label"><span>Schuif om te vergelijken</span>
        <input type="range" min="0" max="100" value="50" aria-label="Vergelijk voor en na">
      </label>
      <a class="wf-zoom wf-link">Bekijk de volledige voor-en-nafoto</a>`;
    const frame = comparison.querySelector('.wf-compare-frame');
    frame.style.setProperty('--wf-compare-ratio', ratio.toFixed(5));
    frame.style.setProperty('--wf-compare-width', `${Math.round(ratio * 540)}px`);
    frame.prepend(...['wf-after', 'wf-before'].map(className => {
      const image = originalImage.cloneNode();
      image.className = className;
      image.alt = '';
      image.draggable = false;
      return image;
    }));
    const range = comparison.querySelector('input');
    const [beforeLabel, afterLabel] = frame.querySelectorAll('.wf-compare-labels span');
    function updateComparison() {
      const before = Number(range.value);
      frame.style.setProperty('--wf-position', `${before}%`);
      range.setAttribute('aria-valuetext', `${before}% voor, ${100 - before}% na`);
      beforeLabel.hidden = before < 20;
      afterLabel.hidden = before > 80;
    }
    range.addEventListener('input', updateComparison);
    updateComparison();

    function moveDivider(event) {
      const frameRect = frame.getBoundingClientRect();
      range.value = Math.round((event.clientX - frameRect.left) / frameRect.width * 100);
      updateComparison();
    }
    frame.addEventListener('pointerdown', event => {
      if (event.pointerType === 'touch' || event.button !== 0) return;
      frame.setPointerCapture(event.pointerId);
      moveDivider(event);
    });
    frame.addEventListener('pointermove', event => {
      if (frame.hasPointerCapture(event.pointerId)) moveDivider(event);
    });

    let start;
    frame.addEventListener('touchstart', event => { start = event.touches[0]; }, { passive: true });
    frame.addEventListener('touchend', event => {
      if (!start) return;
      const touch = event.changedTouches[0];
      const dx = touch.clientX - start.clientX;
      const dy = touch.clientY - start.clientY;
      if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.3) displayCase(current + (dx < 0 ? 1 : -1));
      start = null;
    }, { passive: true });
    frame.addEventListener('touchcancel', () => { start = null; }, { passive: true });

    const zoom = comparison.querySelector('.wf-zoom');
    zoom.href = originalLink.href;
    if (showPhoto) {
      zoom.addEventListener('click', event => {
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        const enlarged = originalImage.cloneNode();
        enlarged.loading = 'eager';
        showPhoto(zoom, enlarged);
      });
    }
    originalLink.hidden = true;
    originalLink.after(comparison);
  }

  if (cases.length) {
    cases.forEach((photo, index) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'wf-thumb';
      button.setAttribute('aria-label', `Toon resultaat ${index + 1}`);
      const thumbnail = photo.querySelector('img').cloneNode();
      thumbnail.src = photo.dataset.thumbnail;
      thumbnail.alt = '';
      button.append(thumbnail);
      button.addEventListener('click', () => displayCase(index));
      thumbnails.append(button);
    });
    controls.querySelector('.wf-prev').addEventListener('click', () => displayCase(current - 1));
    controls.querySelector('.wf-next').addEventListener('click', () => displayCase(current + 1));
    displayCase(0);
    controls.hidden = false;
  }

  const videoDialog = page.querySelector('.wf-video-dialog');
  if (typeof videoDialog.showModal === 'function') {
    const showVideo = prepareDialog(videoDialog);
    const nativeVideo = page.querySelector('.wf-primary-video video');
    page.querySelectorAll('[data-youtube]').forEach(card => {
      const id = card.dataset.youtube;
      if (!/^[\w-]{11}$/.test(id)) return;
      card.addEventListener('click', event => {
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        nativeVideo.pause();
        const title = card.querySelector('strong').textContent;
        const player = document.createElement('iframe');
        player.title = title;
        player.src = `https://www.youtube-nocookie.com/embed/${id}?playsinline=1`;
        player.allow = 'encrypted-media; picture-in-picture';
        player.referrerPolicy = 'strict-origin-when-cross-origin';
        player.allowFullscreen = true;
        videoDialog.querySelector('#wf-video-title').textContent = title;
        videoDialog.querySelector('.wf-video-fallback a').href = `https://www.youtube.com/watch?v=${id}`;
        showVideo(card, player);
      });
    });
  }

  if ('IntersectionObserver' in window) {
    const mobileBook = page.querySelector('.wf-mobile-book');
    const hero = page.querySelector('.wf-hero');
    const closing = page.querySelector('.wf-closing');
    const footer = document.querySelector('.site-footer');
    const observer = new IntersectionObserver(() => {
      const closed = hero.getBoundingClientRect().bottom > 0 ||
        (closing.getBoundingClientRect().top < window.innerHeight && closing.getBoundingClientRect().bottom > 0) ||
        (footer && footer.getBoundingClientRect().top < window.innerHeight);
      mobileBook.hidden = closed;
    });
    [hero, closing, footer].filter(Boolean).forEach(element => observer.observe(element));
  }

  const pageLinks = page.querySelectorAll('.wf-sticky a');
  function indicateJump() {
    pageLinks.forEach(link => {
      if (link.hash === location.hash) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  }
  window.addEventListener('hashchange', indicateJump);
  indicateJump();
})();
