(() => {
    const section = document.getElementById('client-stories');
    if (!section) return;

    const rail = section.querySelector('.client-stories-rail');
    const controls = section.querySelector('.client-stories-controls');
    const previous = controls.querySelector('[data-direction="-1"]');
    const next = controls.querySelector('[data-direction="1"]');
    const cards = Array.from(rail.children);
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    function syncControls() {
        const maxScroll = rail.scrollWidth - rail.clientWidth;
        previous.disabled = rail.scrollLeft <= 1;
        next.disabled = rail.scrollLeft >= maxScroll - 1;
    }

    function move(direction) {
        const stride = cards[1].offsetLeft - cards[0].offsetLeft;
        const maxScroll = rail.scrollWidth - rail.clientWidth;
        const targetIndex = direction > 0
            ? Math.floor((rail.scrollLeft + 1) / stride) + 1
            : Math.ceil((rail.scrollLeft - 1) / stride) - 1;
        rail.scrollTo({
            left: Math.max(0, Math.min(maxScroll, targetIndex * stride)),
            behavior: reducedMotion.matches ? 'instant' : 'smooth',
        });
    }

    previous.addEventListener('click', () => move(-1));
    next.addEventListener('click', () => move(1));
    rail.addEventListener('scroll', syncControls, { passive: true });
    rail.addEventListener('keydown', (event) => {
        if (event.target !== rail || !['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
        event.preventDefault();
        move(event.key === 'ArrowLeft' ? -1 : 1);
    });
    window.addEventListener('resize', syncControls);
    controls.hidden = false;
    syncControls();
})();
