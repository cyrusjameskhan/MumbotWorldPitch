/**
 * Slide entrance animations for <deck-stage> decks.
 * Listens for slidechange — staggered fade-up on slide content.
 */
(() => {
  const FADE_MS = 1050;
  const STAGGER_MS = 120;

  // Do not list `.grain` — it lives on the <section> itself, so closest()
  // would skip every element on every slide.
  const DECOR =
    '.corner-mark, .stars, .ghost, .ember-floaty, .ground, .eye, .ember, .divider';

  const FADE_SELECTORS = [
    '.eyebrow',
    'h1', 'h2', 'h3',
    'p', '.quote', '.body', '.lede', '.rule', '.invite',
    '.feels', '.meta', '.meta span',
    '.char-card', '.slot-frame', '.card', '.pillar',
    '.grid > *', '.alloc-row', '.contacts > span',
    'header', '.collage-cell', '.phase-card', '.phase',
    '.bee-item', '.roadmap-step', '.roadmap-col',
    '.hero', '.thumbs > .thumb', '.side-thumbs > *', '.thumb-card',
    '.wip-cell',
    '.concept-col', '.pillar-grid > *', '.timeline > *',
    '.closing .eye',
    'image-slot',
    '[data-deck-fade-ms]',
  ].join(', ');

  const reducedMq = matchMedia('(prefers-reduced-motion: reduce)');

  const prefersReduced = () => reducedMq.matches;

  const clearSlide = (slide) => {
    if (!slide) return;
    if (slide._deckAnimTimers) {
      slide._deckAnimTimers.forEach(clearTimeout);
      slide._deckAnimTimers = [];
    }
    slide.querySelectorAll('.deck-fade-target').forEach((el) => {
      el.classList.remove('deck-fade-in', 'deck-fade-target');
      el.style.removeProperty('--deck-delay');
      el.style.removeProperty('--deck-fade-ms');
    });
    slide.classList.remove('deck-entering', 'deck-enter-done');
  };

  const isInsideDecor = (el, slide) => {
    const hit = el.closest(DECOR);
    return hit && hit !== slide;
  };

  const collectFadeTargets = (slide) => {
    const raw = slide.querySelectorAll(FADE_SELECTORS);
    const out = [];
    for (const el of raw) {
      if (isInsideDecor(el, slide)) continue;
      if (!el.offsetParent && getComputedStyle(el).position === 'fixed') continue;
      let nested = false;
      for (const other of raw) {
        if (other !== el && other.contains(el)) {
          nested = true;
          break;
        }
      }
      if (!nested) out.push(el);
    }
    out.sort((a, b) => {
      const pos = a.compareDocumentPosition(b);
      if (pos & Node.DOCUMENT_POSITION_FOLLOWING) return -1;
      if (pos & Node.DOCUMENT_POSITION_PRECEDING) return 1;
      return 0;
    });
    return out;
  };

  const animateSlide = (slide, { instant = false } = {}) => {
    clearSlide(slide);
    if (!slide || prefersReduced() || instant) {
      slide?.classList.add('deck-enter-done');
      return;
    }

    const timers = [];
    slide._deckAnimTimers = timers;
    slide.classList.add('deck-entering');

    const fadeMsFor = (el) => {
      const n = parseInt(el.getAttribute('data-deck-fade-ms'), 10);
      return Number.isFinite(n) && n > 0 ? n : FADE_MS;
    };

    const targets = collectFadeTargets(slide);
    let t = 0;
    let maxEnd = 0;

    for (const el of targets) {
      const fadeMs = fadeMsFor(el);
      el.classList.add('deck-fade-target');
      el.style.setProperty('--deck-fade-ms', fadeMs + 'ms');
      el.style.setProperty('--deck-delay', t + 'ms');
      timers.push(
        setTimeout(() => {
          el.classList.add('deck-fade-in');
        }, t),
      );
      maxEnd = Math.max(maxEnd, t + fadeMs);
      t += STAGGER_MS;
    }

    timers.push(
      setTimeout(() => {
        slide.classList.remove('deck-entering');
        slide.classList.add('deck-enter-done');
      }, maxEnd + 120),
    );
  };

  const activeSlide = (ds) => {
    const s = ds.querySelector('[data-deck-active]');
    if (s) return s;
    return [...ds.children].find((c) => {
      const t = c.tagName;
      return t !== 'SCRIPT' && t !== 'STYLE' && t !== 'TEMPLATE';
    }) || null;
  };

  const bind = (ds) => {
    if (!ds || ds.dataset.deckAnimationsBound) return;
    ds.dataset.deckAnimationsBound = '1';

    ds.addEventListener('slidechange', (e) => {
      const { slide, previousSlide } = e.detail;
      if (previousSlide && previousSlide !== slide) clearSlide(previousSlide);
      animateSlide(slide, { instant: prefersReduced() });
    });

    const boot = activeSlide(ds);
    if (boot && !boot.classList.contains('deck-enter-done')) {
      requestAnimationFrame(() => animateSlide(boot, { instant: prefersReduced() }));
    }
  };

  const init = () => {
    const ds = document.querySelector('deck-stage');
    if (ds) bind(ds);
  };

  const start = () => {
    customElements.whenDefined('deck-stage').then(init).catch(init);
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
