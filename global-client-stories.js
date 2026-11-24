(() => {
    const rail = document.getElementById('client-stories-rail');
    if (!rail) return;

    const cards = Array.from(rail.children);
    if (cards.length < 2) return;
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    let visible = false;
    let hovering = false;
    let focused = false;
    let paused = false;
    let timer;
    let settle;
    let pointer;

    const replicas = cards.map((card) => {
        const copy = card.cloneNode(true);
        copy.setAttribute('aria-hidden', 'true');
        copy.inert = true;
        return copy;
    });
    rail.append(...replicas);

    function position(card) {
        return card.offsetLeft - cards[0].offsetLeft;
    }

    function advance(direction) {
        const positions = [...cards, ...replicas].map(position);
        const left = rail.scrollLeft;
        const target = direction > 0
            ? positions.find((value) => value > left + 2)
            : positions.findLast((value) => value < left - 2);
        rail.scrollTo({ left: target ?? 0, behavior: motion.matches ? 'instant' : 'smooth' });
    }

    function sync() {
        clearInterval(timer);
        if (visible && !motion.matches && !paused && !hovering && !focused && !document.hidden) {
            timer = setInterval(() => advance(1), 4200);
        }
    }

    rail.addEventListener('scroll', () => {
        clearTimeout(settle);
        settle = setTimeout(() => {
            const loop = position(replicas[0]);
            if (loop > 0 && rail.scrollLeft >= loop - 1) {
                rail.scrollTo({ left: Math.max(0, rail.scrollLeft - loop), behavior: 'instant' });
            }
        }, 140);
    }, { passive: true });

    rail.addEventListener('pointerenter', (event) => {
        if (event.pointerType === 'mouse') { hovering = true; sync(); }
    });
    rail.addEventListener('pointerleave', () => { hovering = false; sync(); });
    rail.addEventListener('pointerdown', (event) => {
        pointer = { x: event.clientX, y: event.clientY };
        clearInterval(timer);
    });
    rail.addEventListener('pointerup', (event) => {
        if (pointer && Math.hypot(event.clientX - pointer.x, event.clientY - pointer.y) < 8) {
            paused = !paused;
            focused = paused;
        }
        pointer = undefined;
        sync();
    });
    rail.addEventListener('pointercancel', () => { pointer = undefined; sync(); });
    rail.addEventListener('focus', () => { focused = true; sync(); });
    rail.addEventListener('blur', () => { focused = false; sync(); });
    rail.addEventListener('keydown', (event) => {
        if (event.key === ' ') {
            event.preventDefault();
            paused = !paused;
            focused = paused;
            sync();
        } else if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
            event.preventDefault();
            paused = true;
            sync();
            advance(event.key === 'ArrowLeft' ? -1 : 1);
        }
    });
    document.addEventListener('visibilitychange', sync);
    motion.addEventListener('change', sync);
    new IntersectionObserver(([entry]) => {
        visible = entry.isIntersecting;
        sync();
    }, { threshold: 0.3 }).observe(rail);
})();
