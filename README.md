# 个人网站

一个零依赖、零构建的极简单页个人主页，适合用于自我介绍、面试展示、求职。

## 📁 文件结构

```
个人网站/
├── index.html      # 页面结构（改这里就能改文字）
├── style.css       # 样式（颜色、字体、布局）
├── script.js       # 主题切换 & 滚动动画
├── resume.pdf      # 你的简历（自己放进来）
└── README.md
```

## ✏️ 如何修改内容

直接用记事本/VSCode 打开 `index.html`，把里面的占位文字替换成你自己的：

| 位置 | 改什么 |
|---|---|
| `<title>` | 浏览器标签标题 |
| `.hero` 区域 | 头像、姓名、一句话简介 |
| `#about` | 关于我、技能栈 |
| `#projects` 里每个 `.card` | 项目截图、名称、描述、链接 |
| `#blog` 里每个 `<li>` | 博客文章日期与标题 |
| `#contact` | 邮箱、GitHub、LinkedIn |

**头像**：默认用了 dicebear 在线生成的卡通头像。换成你自己的：
- 把照片放到本目录，比如命名 `avatar.jpg`
- 把 `<img src="..." class="avatar">` 的 src 改成 `avatar.jpg`

**项目截图**：默认用 picsum.photos 占位图。把项目截图放进目录后，把 `<img src="...">` 改成 `images/project1.png` 之类。

**简历下载**：把你的简历命名为 `resume.pdf` 放在同目录即可。

## 🚀 本地预览

双击 `index.html` 即可在浏览器打开。

## 🌐 上线部署（推荐 Vercel，最快 1 分钟）

### 方式 A：Vercel（推荐，无需懂 Git）
1. 注册 [vercel.com](https://vercel.com)（用 GitHub 账号登录）
2. 点 **Add New → Project → Import**
3. 把整个文件夹拖进去，点 Deploy
4. 几秒后会得到一个网址，比如 `https://yourname.vercel.app`
5. 之后修改 → 重新拖一次即可更新

### 方式 B：GitHub Pages（免费，需要 GitHub 账号）
1. 在 [github.com](https://github.com) 创建一个新仓库，命名为 `yourname.github.io`（务必这个名字）
2. 把本目录下所有文件上传到该仓库
3. 进入仓库 **Settings → Pages**，Source 选 `main` 分支，保存
4. 等待 1 分钟，访问 `https://yourname.github.io` 即可

### 方式 C：Netlify
1. 注册 [netlify.com](https://netlify.com)
2. 点 **Add new site → Deploy manually**
3. 把整个文件夹拖进去，立即上线

## 🎨 想换配色？

打开 `style.css`，改最上面的 `--accent` 颜色变量即可：

```css
--accent: #4f46e5;  /* 紫色 → 改成你喜欢的，比如 #ff6b6b 红、#10b981 绿 */
```

## 💡 面试加分小技巧

1. **每个项目讲清楚 4 件事**：背景、难点、你的方案、可量化的成果
2. **放真实链接**：在线 Demo + 源码，让面试官能点开看
3. **关键词加粗**：比如「**主导**了从 0 到 1」「性能提升 **40%**」
4. **保持简洁**：项目卡片 3-6 个最佳，不要堆砌

## 📜 License

随便用，不用署名。祝你面试顺利！
