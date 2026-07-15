// 主题切换 + 记忆
const toggle = document.getElementById('themeToggle');
const root = document.documentElement;

// 初始化：读取本地存储或跟随系统
const saved = localStorage.getItem('theme');
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
const initial = saved || (prefersDark ? 'dark' : 'light');
root.setAttribute('data-theme', initial);
toggle.textContent = initial === 'dark' ? '☀️' : '🌙';

toggle.addEventListener('click', () => {
  const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  root.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  toggle.textContent = next === 'dark' ? '☀️' : '🌙';
});

// 滚动出现动画
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.style.opacity = 1;
      e.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.section, .hero').forEach(el => {
  el.style.opacity = 0;
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
  io.observe(el);
});
