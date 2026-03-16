<template>
  <footer class="site-footer bg-dark">
    <div class="footer-container">
      <div class="footer-brand">
        <h3 class="footer-logo">MikeYC Wang</h3>
        <p>Full-Stack Developer crafting digital experiences. <br> 喜歡探索新技術，專注於打造兼具效能與美感的網頁應用。</p>
      </div>

      <div class="footer-links">
        <h4>Explore</h4>
        <div class="link-grid">
          <RouterLink to="/lab"><i class="fa-solid fa-flask"></i> 靈感碎片</RouterLink>
          <RouterLink to="/projects"><i class="fa-solid fa-code-branch"></i> 專案作品</RouterLink>
          <RouterLink to="/blog"><i class="fa-solid fa-pen-nib"></i> 個人部落格</RouterLink>
          <RouterLink to="/admin"><i class="fa-solid fa-gear"></i> 後台管理</RouterLink>
          <RouterLink to="/dashboard"><i class="fa-solid fa-chart-line"></i> 控制台</RouterLink>
        </div>
      </div>

      <div class="footer-social">
        <h4>Connect</h4>
        <div class="social-links">
          <a href="https://github.com/MikeYC-Wang" target="_blank" title="GitHub"><i class="fa-brands fa-github"></i> GitHub</a>
          <a href="https://codepen.io/Mike-YC" target="_blank" title="CodePen"><i class="fa-brands fa-codepen"></i> CodePen</a>
          <a href="https://www.instagram.com/wang_di_di_1130/" target="_blank" title="Instagram"><i class="fa-brands fa-instagram"></i> Instagram</a>
          <a href="mailto:asd384639@gmail.com" title="Email"><i class="fa-solid fa-envelope"></i> Email</a>
        </div>
      </div>
    </div>

    <div class="footer-bottom">
      <p>© 2026 MikeYC-Wang. All rights reserved.</p>
      <p class="build-info">Powered by Vue 3 & FastAPI</p>
    </div>
  </footer>
</template>

<style scoped>
.site-footer {
  width: 100%;
  padding: 80px 20px 20px;
  background-color: #080b10;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  color: #aaa;
}

:global(.light-mode) .site-footer {
  background-color: #f1f5f9;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  color: #666;
}

.footer-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 50px;
  padding-bottom: 50px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

:global(.light-mode) .footer-container { border-bottom: 1px solid rgba(0, 0, 0, 0.1); }

.footer-brand { flex: 2; min-width: 300px; }
.footer-logo { font-size: 1.8rem; color: #d4b595; margin-bottom: 15px; font-family: monospace; }
.footer-brand p { line-height: 1.6; font-size: 0.95rem; max-width: 400px; }

.footer-links, .footer-social { flex: 1; min-width: 150px; }
.footer-links h4, .footer-social h4 { color: #fff; font-size: 1.1rem; margin-bottom: 20px; letter-spacing: 1px; }

:global(.light-mode) .footer-links h4, 
:global(.light-mode) .footer-social h4 { color: #333; }

.link-grid, .social-links { display: flex; flex-direction: column; gap: 12px; }
.link-grid a, .social-links a { color: #aaa; text-decoration: none; font-size: 0.95rem; transition: all 0.3s ease; display: inline-block; width: fit-content; }

:global(.light-mode) .link-grid a, 
:global(.light-mode) .social-links a { color: #666; }

.link-grid a:hover, .social-links a:hover { color: #d4b595; transform: translateX(5px); }

.link-grid a i, .social-links a i { margin-right: 8px; font-size: 1.1rem; width: 20px; text-align: center; }

.footer-bottom { max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding-top: 20px; font-size: 0.85rem; }
.build-info { font-family: monospace; color: #555; }

@media (max-width: 768px) {
  .footer-container { flex-direction: column; gap: 40px; }
  .footer-bottom { flex-direction: column; gap: 10px; text-align: center; }
}
</style>