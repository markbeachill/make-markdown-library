
(function () {
  const root = document.documentElement;
  const saved = localStorage.getItem('mml-docs-theme');
  if (saved) root.setAttribute('data-theme', saved);
  document.getElementById('theme-toggle')?.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('mml-docs-theme', next);
  });
  document.querySelectorAll('.copy').forEach((button) => {
    button.addEventListener('click', async () => {
      const code = button.parentElement.querySelector('code')?.innerText || '';
      await navigator.clipboard?.writeText(code);
      button.textContent = 'Copied';
      setTimeout(() => button.textContent = 'Copy', 1200);
    });
  });
  const search = document.getElementById('search');
  search?.addEventListener('input', () => {
    const q = search.value.toLowerCase().trim();
    document.querySelectorAll('.nav-link').forEach((link) => {
      const hit = !q || link.textContent.toLowerCase().includes(q);
      link.style.display = hit ? 'block' : 'none';
    });
  });
})();
