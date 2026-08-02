// 主题切换 + 记忆
const toggle = document.getElementById('themeToggle');
const root = document.documentElement;

const saved = localStorage.getItem('theme');
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
const initial = root.getAttribute('data-theme') || saved || (prefersDark ? 'dark' : 'light');
root.setAttribute('data-theme', initial);

if (toggle) {
  toggle.textContent = initial === 'dark' ? '☀️' : '🌙';
  toggle.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    toggle.textContent = next === 'dark' ? '☀️' : '🌙';
  });
}

// 滚动出现动画：不隐藏 Hero，避免等 JS 才显示首屏
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('is-visible');
      io.unobserve(e.target);
    }
  });
}, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

document.querySelectorAll('.section').forEach(el => {
  el.classList.add('reveal');
  io.observe(el);
});

// 兜底：若 IO 异常，2 秒后强制显示，防止内容一直透明
setTimeout(() => {
  document.querySelectorAll('.section.reveal:not(.is-visible)').forEach(el => {
    el.classList.add('is-visible');
  });
}, 2000);

// ============================================================
// 左侧导航：当前区块高亮 + 阅读进度（仅首页存在 #sideNav）
// ============================================================
(function initSideNav() {
  const sideNav = document.getElementById('sideNav');
  if (!sideNav) return;

  const thumb = document.getElementById('snThumb');
  const railFill = document.getElementById('snRailFill');
  const progressFill = document.getElementById('snProgressFill');
  const progressNum = document.getElementById('snProgressNum');
  const snToggle = document.getElementById('snToggle');
  const backdrop = document.getElementById('snBackdrop');

  const items = [];
  sideNav.querySelectorAll('.sn-link').forEach(link => {
    const target = document.querySelector(link.getAttribute('href'));
    if (target) items.push({ link, target });
  });
  if (!items.length) return;

  let activeIndex = -1;

  function setActive(index) {
    if (index === activeIndex) return;
    activeIndex = index;

    items.forEach((item, i) => {
      const on = i === index;
      item.link.classList.toggle('is-active', on);
      if (on) {
        item.link.setAttribute('aria-current', 'true');
      } else {
        item.link.removeAttribute('aria-current');
      }
    });

    const link = items[index].link;
    thumb.style.height = link.offsetHeight + 'px';
    thumb.style.transform = 'translateY(' + link.offsetTop + 'px)';
    sideNav.classList.add('is-tracking');

    // 轨道填充到当前条目中心，直观表示读到第几块
    const railTop = 6;
    const railHeight = sideNav.querySelector('.sn-nav').offsetHeight - railTop * 2;
    const center = link.offsetTop + link.offsetHeight / 2 - railTop;
    railFill.style.height = Math.max(0, Math.min(100, (center / railHeight) * 100)) + '%';
  }

  function update() {
    // 探测线放在视口上方 1/3 处：区块标题刚进入阅读区就切换
    const probe = window.scrollY + window.innerHeight * 0.32;
    let index = 0;
    for (let i = 0; i < items.length; i++) {
      if (items[i].target.getBoundingClientRect().top + window.scrollY <= probe) index = i;
    }

    const docHeight = document.documentElement.scrollHeight;
    const scrollable = docHeight - window.innerHeight;
    // 滚到底部时无条件点亮最后一项，避免末尾短区块永远高亮不到
    if (scrollable > 0 && window.scrollY >= scrollable - 4) index = items.length - 1;

    setActive(index);

    const ratio = scrollable > 0 ? window.scrollY / scrollable : 0;
    const percent = Math.round(Math.max(0, Math.min(1, ratio)) * 100);
    progressFill.style.width = percent + '%';
    progressNum.textContent = percent + '%';
  }

  let ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      ticking = false;
      update();
    });
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', () => {
    activeIndex = -1; // 尺寸变化后滑块需重算
    update();
  });
  update();

  // ---- 移动端抽屉 ----
  if (!snToggle || !backdrop) return;

  function closeDrawer() {
    sideNav.classList.remove('is-open');
    backdrop.classList.remove('is-open');
    snToggle.setAttribute('aria-expanded', 'false');
    setTimeout(() => {
      if (!sideNav.classList.contains('is-open')) backdrop.hidden = true;
    }, 260);
  }

  function openDrawer() {
    backdrop.hidden = false;
    requestAnimationFrame(() => backdrop.classList.add('is-open'));
    sideNav.classList.add('is-open');
    snToggle.setAttribute('aria-expanded', 'true');
  }

  snToggle.addEventListener('click', () => {
    if (sideNav.classList.contains('is-open')) closeDrawer();
    else openDrawer();
  });
  backdrop.addEventListener('click', closeDrawer);
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && sideNav.classList.contains('is-open')) closeDrawer();
  });
  items.forEach(item => item.link.addEventListener('click', closeDrawer));

  // 从窄屏拉回宽屏时侧栏已常驻，遮罩必须撤掉
  window.matchMedia('(min-width: 981px)').addEventListener('change', e => {
    if (e.matches) closeDrawer();
  });
})();
