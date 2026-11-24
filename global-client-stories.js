(() => {
    const rail = document.getElementById('client-stories-rail');
    if (!rail || rail.children.length < 2) return;

    const cards = Array.from(rail.children);
    const controls = rail.nextElementSibling;
    const playback = controls.querySelector('[data-playback]');
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    let visible = true;
    let browsing = false;
    let paused = motion.matches;
    let timer;

    function advance(direction) {
        const start = cards[0].getBoundingClientRect().left;
        const limit = rail.scrollWidth - rail.clientWidth;
        if (limit <= 1) return;
        const stops = cards.map(card => Math.min(limit, card.getBoundingClientRect().left - start));
        const left = rail.scrollLeft;
        const target = direction > 0
            ? stops.find(stop => stop > left + 2) ?? 0
            : stops.slice().reverse().find(stop => stop < left - 2) ?? limit;
        rail.scrollTo({ left: target, behavior: motion.matches ? 'instant' : 'smooth' });
    }

    function schedule() {
        clearTimeout(timer);
        playback.textContent = paused ? 'Play autoplay' : 'Pause autoplay';
        if (visible && !paused && !browsing && !document.hidden) {
            timer = setTimeout(() => {
                advance(1);
                schedule();
            }, 4200);
        }
    }

    controls.querySelectorAll('[data-step]').forEach(button => {
        button.addEventListener('click', () => {
            advance(Number(button.dataset.step));
            schedule();
        });
    });
    playback.addEventListener('click', () => {
        paused = !paused;
        schedule();
    });
    rail.addEventListener('keydown', event => {
        if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
        event.preventDefault();
        advance(event.key === 'ArrowLeft' ? -1 : 1);
        schedule();
    });
    rail.addEventListener('pointerdown', () => { browsing = true; schedule(); });
    ['pointerup', 'pointercancel'].forEach(type => {
        window.addEventListener(type, () => {
            if (!browsing) return;
            browsing = false;
            schedule();
        });
    });
    document.addEventListener('visibilitychange', schedule);
    if (motion.addEventListener) {
        motion.addEventListener('change', event => { paused = event.matches; schedule(); });
    }
    if ('IntersectionObserver' in window) {
        new IntersectionObserver(([entry]) => {
            visible = entry.isIntersecting;
            schedule();
        }).observe(rail);
    }
    controls.hidden = false;
    schedule();
})();
