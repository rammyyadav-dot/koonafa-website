(() => {
    const section = document.getElementById('client-stories');
    if (!section) return;

    const rail = section.querySelector('.client-stories-rail');
    const controls = section.querySelector('.client-stories-controls');
    const previous = controls.querySelector('[data-direction="-1"]');
    const next = controls.querySelector('[data-direction="1"]');
    const rotation = section.querySelector('.client-stories-rotation');
    const cards = Array.from(rail.children);
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    let inView = false;
    let hovering = false;
    let requested = !reducedMotion.matches;
    let timer;

    function syncRotation() {
        clearInterval(timer);
        rotation.textContent = requested ? 'Pause slideshow' : 'Play slideshow';
        if (!requested || !inView || hovering || document.hidden) return;
        timer = setInterval(() => {
            if (next.disabled) {
                rail.scrollTo({ left: 0, behavior: 'instant' });
            } else {
                move(1);
            }
        }, 5500);
    }

    function pause() {
        requested = false;
        syncRotation();
    }

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

    previous.addEventListener('click', () => { pause(); move(-1); });
    next.addEventListener('click', () => { pause(); move(1); });
    rail.addEventListener('scroll', syncControls, { passive: true });
    rail.addEventListener('keydown', (event) => {
        if (event.target !== rail || !['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
        event.preventDefault();
        pause();
        move(event.key === 'ArrowLeft' ? -1 : 1);
    });
    window.addEventListener('resize', syncControls);
    rotation.addEventListener('click', () => {
        requested = !requested;
        syncRotation();
    });
    section.addEventListener('focusin', (event) => {
        if (event.target !== rotation) pause();
        else clearInterval(timer);
    });
    rotation.addEventListener('focusout', syncRotation);
    section.addEventListener('pointerenter', (event) => {
        if (event.pointerType !== 'mouse') return;
        hovering = true;
        syncRotation();
    });
    section.addEventListener('pointerleave', () => {
        hovering = false;
        syncRotation();
    });
    rail.addEventListener('pointerdown', pause, { passive: true });
    document.addEventListener('visibilitychange', syncRotation);
    reducedMotion.addEventListener('change', () => {
        if (reducedMotion.matches) pause();
    });
    new IntersectionObserver(([entry]) => {
        inView = entry.isIntersecting;
        syncRotation();
    }, { threshold: 0.35 }).observe(rail);
    controls.hidden = false;
    rotation.hidden = false;
    syncControls();
})();
