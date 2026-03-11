document.addEventListener('DOMContentLoaded', () => {
  // Mobile nav
  const burger = document.getElementById('navBurger');
  const menu = document.getElementById('navMenu');
  if (burger && menu) {
    burger.addEventListener('click', () => menu.classList.toggle('open'));
    menu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => menu.classList.remove('open')));
  }

  // Flash messages
  document.querySelectorAll('.flash').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity .4s, transform .4s';
      el.style.opacity = '0';
      el.style.transform = 'translateX(40px)';
      setTimeout(() => el.remove(), 400);
    }, 5000);
  });

  // Reveal on scroll
  if ('IntersectionObserver' in window) {
    const targets = document.querySelectorAll(
      '.prop-card, .tipo-card, .ventaja, .asesor-card, .valor-item, .nos-stat, .adm-stat, .ct-item'
    );
    targets.forEach((el, i) => {
      el.classList.add('reveal');
      const mod = i % 3;
      if (mod === 1) el.classList.add('reveal-d1');
      if (mod === 2) el.classList.add('reveal-d2');
    });
    const obs = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target); }
      });
    }, { threshold: 0.07, rootMargin: '0px 0px -24px 0px' });
    targets.forEach(el => obs.observe(el));
  }

  // Hero search: sync radio tabs visually
  const tabLabels = document.querySelectorAll('.tab-label input[type="radio"]');
  tabLabels.forEach(radio => {
    radio.addEventListener('change', () => {
      tabLabels.forEach(r => r.closest('.tab-label').querySelector('span').style.fontWeight = '600');
    });
  });
});
