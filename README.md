# 🌌 Interactive 3D Portfolio & Custom CMS

[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Three.js](https://img.shields.io/badge/Three.js-Black?style=for-the-badge&logo=three.js&logoColor=white)](https://threejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

> **這不只是一個履歷網站，這是我對全端開發與 3D 互動設計的火力展示。**

🌐 **Live Demo:**  
👉 [點此造訪我的專屬網站](https://mikeyc-wang.github.io/MyPortfolio/)

---

## 💡 專案簡介 (About The Project)

這是我從零開始架構並獨立開發的個人入口網站與專屬 CMS（內容管理系統）。  
專案徹底實踐了 **前後端分離（SPA + RESTful API）** 架構。

前台結合 **Three.js** 與 **GSAP** 打造沉浸式 3D 視覺與駭客終端機特效，  
並透過 Python 爬蟲與 **ECharts** 將 GitHub 真實貢獻度轉化為動態圖表。

後台則利用 **FastAPI** 打造高效能管理系統，具備雙 Token JWT 驗證、IP 鎖定、Rate Limiting 與安全標頭等多層資安防護，  
可隨時自主更新專案與文章內容。

更整合 **Claude + Gemini AI**，為自己提供寫作助手、為訪客提供智慧客服機器人，並導入 **GitHub Actions CI/CD** 自動化部署流程。

---

## ✨ 核心特色 (Key Features)

### 🎨 前端：極致的視覺與互動 (Frontend)

- **3D 沉浸式體驗**  
  使用 `Three.js` 渲染背景模型，搭配 `GSAP` 實現流暢動畫

- **駭客終端機 + VS Code UI**  
  自製打字動畫 + 音效，打造開發者風格介面

- **數據視覺化**  
  使用 `ECharts` 呈現：
  - 技能雷達圖  
  - GitHub Commit 熱力圖  

---

### ⚙️ 後端：高效能與高資安 (Backend)

- **RESTful API**  
  基於 `FastAPI` 的高併發非同步架構

- **專屬 CMS 管理後台**
  - Blog / Projects / Lab 完整 CRUD
  - 文章 / 專案後台支援拖曳排序與上下箭頭調整顯示順序
  - 公開列表自動過濾未發佈內容

- **資安防護（16 項漏洞修補）**
  - **雙 Token JWT 驗證**：15 分鐘 Access Token + 7 天 Refresh Token（hash 儲存、自動 rotation）
  - **登入防暴力破解**：3 分鐘內失敗 3 次自動鎖 IP，並透過 `X-Forwarded-For` 取得真實來源
  - **Rate Limiting**：使用 `slowapi` 對登入、上傳、AI 等敏感端點限流
  - **安全標頭**：自動加入 `HSTS / X-Content-Type-Options / X-Frame-Options / Referrer-Policy / Permissions-Policy`
  - **檔案上傳防護**：副檔名 + MIME 雙重白名單、5MB 分塊大小限制、自製 `/static/uploads/{filename}` regex 白名單路由
  - **CORS 收緊**：明列允許的 method 與 header
  - **全域例外處理**：避免 stack trace 外洩
  - **依賴漏洞掃描**：透過 `pip-audit` 定期檢查 CVE

- **自動化爬蟲**
  - 抓取 GitHub 貢獻數據並寫入 DB

- **AI 整合（雙 LLM 架構）**
  - **後台寫作助手**：整合 **Anthropic Claude Haiku 4.5**，提供潤稿、翻譯、摘要、標題生成 4 種 action
  - **公開客服機器人**：整合 **Google Gemini 2.5 Flash**（免費額度），自動將最新專案 / 文章注入 system prompt 作為 context
  - 兩個 API key 都採 lazy import，未配置時優雅降級（503）不影響其他路由

---

## 🛠️ 技術堆疊 (Tech Stack)

### 🎯 Frontend

- Framework: Vue 3 (Composition API), Vite  
- Language: TypeScript  
- State Management: Pinia  
- Routing: Vue Router  
- Styling: Tailwind CSS（自訂 milk-tea 主題系統，支援 light / dark mode 三模式切換）
- Animation & 3D: Three.js, GSAP  
- Charts: ECharts, ApexCharts  
- Code Editor: CodeMirror 6（Lab 程式碼 playground）
- Markdown: markdown-it + highlight.js
- SSG / Prerender: Puppeteer + sirv（建構時預渲染所有路由，產生對 SEO 友善的靜態 HTML 與 sitemap.xml）
- Bundle Splitting: 手動 vendor chunks（vue / three / gsap / codemirror / charts / markdown）
- Notifications: vue-toastification

---

### ⚙️ Backend

- Framework: FastAPI (Python)  
- ORM: SQLAlchemy  
- Database: PostgreSQL（Render 託管）
- Security:  
  - passlib (bcrypt) — 密碼雜湊
  - python-jose (JWT) — 雙 Token 驗證
  - slowapi — Rate Limiting
- AI / LLM:
  - `anthropic` — Claude Haiku 4.5（後台寫作助手）
  - `google-genai` — Gemini 2.5 Flash（公開客服機器人）
- Web Scraping: BeautifulSoup4, Requests  

---

### 🚀 Deployment

- Frontend: GitHub Pages（透過 **GitHub Actions CI/CD** 自動部署）
  - push 到 `main` 自動觸發 type-check + SSG build + 部署到 `gh-pages` 分支
  - PR 自動跑 lint + type-check
- Backend & DB: Render（git push 自動 redeploy）

---

## 🚀 本地端開發設置 (Local Development Setup)

請先安裝：

- Node.js  
- Python 3.8+  

---

### 1️⃣ Clone 專案

```bash
git clone https://github.com/MikeYC-Wang/MyPortfolio.git
cd MyPortfolio
```

---

### 2️⃣ 後端設置 (Backend)

```bash
# 進入後端資料夾
cd backend

# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
# Mac / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 設定環境變數 (.env)
# 參考 .env.example

# 啟動伺服器
uvicorn main:app --reload
```

👉 預設：http://localhost:8000

---

### 3️⃣ 前端設置 (Frontend)

```bash
# 進入前端資料夾
cd frontend

# 安裝依賴
npm install

# 啟動開發環境
npm run dev
```

👉 預設：http://localhost:5173

---

## 👨‍💻 作者 (Author)

**MikeYC-Wang**

- GitHub: https://github.com/MikeYC-Wang  
- Portfolio: https://mikeyc-wang.github.io/MyPortfolio/
