(() => {
  const root = document.documentElement;
  const progress = document.getElementById('scroll-progress-bar');
  const sections = [...document.querySelectorAll('.module')];
  const navLinks = [...document.querySelectorAll('.quick-nav a')];

  root.classList.add('motion-ready');

  const revealItems = document.querySelectorAll('.module-heading, .module-one-grid, .module-two-grid, .module-three-grid, .module-footer, .closing');
  revealItems.forEach((item, index) => {
    item.classList.add('reveal');
    if (index % 3) item.classList.add(`reveal-delay-${index % 3}`);
  });

  if ('IntersectionObserver' in window) {
    const revealObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.12 });
    revealItems.forEach(item => revealObserver.observe(item));

    const sectionObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const active = `#${entry.target.id}`;
        navLinks.forEach(link => link.classList.toggle('is-active', link.getAttribute('href') === active));
      });
    }, { rootMargin: '-38% 0px -48% 0px' });
    sections.forEach(section => sectionObserver.observe(section));
  } else {
    revealItems.forEach(item => item.classList.add('is-visible'));
  }

  let frame = 0;
  const updateProgress = () => {
    if (frame) return;
    frame = window.requestAnimationFrame(() => {
      const scrollable = document.documentElement.scrollHeight - window.innerHeight;
      const ratio = scrollable > 0 ? window.scrollY / scrollable : 0;
      progress.style.width = `${Math.min(100, Math.max(0, ratio * 100))}%`;
      frame = 0;
    });
  };
  window.addEventListener('scroll', updateProgress, { passive: true });
  window.addEventListener('resize', updateProgress);
  updateProgress();
})();
