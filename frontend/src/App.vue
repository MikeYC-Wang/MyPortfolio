<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { RouterLink, RouterView } from 'vue-router';
import Background3D from '@/components/Background3D.vue';
import HackerIntro from '@/components/HackerIntro.vue';
import { useTheme } from '@/composables/useTheme';
import "./assets/css/Theme.css";

// 使用共用的主題狀態
const { isDark, toggleTheme, initTheme } = useTheme();

// 進場動畫狀態
const isIntroFinished = ref(false);

const handleIntroComplete = () => {
  console.log("System Access Granted.");
  isIntroFinished.value = true;
};

// 初始化時確保主題正確
onMounted(() => {
  initTheme();
});
</script>

<template>
  <HackerIntro 
    v-if="!isIntroFinished" 
    @intro-complete="handleIntroComplete" 
  />

  <div class="app-wrapper">
    
    <Background3D 
      :isDark="isDark" 
      :isReady="isIntroFinished" 
    />

    <header>
      <nav class="nav-left">
        <RouterLink to="/">首頁</RouterLink>
        <RouterLink to="/lab">靈感碎片</RouterLink>
        <RouterLink to="/blog">個人部落格</RouterLink>
        <RouterLink to="/admin">後台管理</RouterLink>
      </nav>

      <div class="nav-center">
        <RouterLink to="/">
          <img src="/logo.png" alt="MikeYC Logo" class="site-logo" />
        </RouterLink>
      </div>

      <div class="actions nav-right">
        <button class="theme-btn" @click="toggleTheme" :title="isDark ? '切換到奶茶模式' : '切換到深色模式'">
          <svg v-if="isDark" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
          <span class="btn-text">{{ isDark ? 'Dark' : 'Light' }}</span>
        </button>
      </div>
    </header>

    <main>
      <RouterView />
    </main>
  </div>
</template>

<style scoped>

.app-wrapper { min-height: 100vh; }

header {
  position: fixed;
  top: 0;
  width: 100%;
  height: 80px;
  box-sizing: border-box;
  padding: 0 40px;
  background: var(--nav-bg); /* 使用變數 */
  backdrop-filter: blur(15px);
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color); /* 使用變數 */
  transition: background 0.5s, border 0.5s;
}

/* 左側與右側區域 */
.nav-left, .nav-right {
  display: flex;
  align-items: center;
  gap: 20px;
  z-index: 2; /* 確保在 Logo 上層 */
}

/* 連結樣式 */
.nav-left a {
  color: var(--link-color); /* 使用變數 */
  text-decoration: none;
  font-weight: bold;
  font-size: 1rem;
  transition: 0.3s;
  padding: 8px 0;
}

.nav-left a:hover, .nav-left a.router-link-active { 
  color: var(--link-active); /* 使用變數 */
}

/* ✨ Logo 絕對置中設定 */
.nav-center {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  z-index: 1;
}

.site-logo {
  height: 50px; /* 根據 Logo 實際大小調整 */
  width: auto;
  display: block;
  transition: transform 0.3s ease;
}

.site-logo:hover {
  transform: scale(1.05);
}

/* 主題按鈕 */
.theme-btn {
  background: var(--btn-bg); /* 使用變數 */
  border: 1px solid transparent; 
  cursor: pointer;
  color: var(--text-color); /* 使用變數 */
  padding: 8px 16px;
  border-radius: 20px;
  transition: 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  font-size: 0.9rem;
  white-space: nowrap;
}

/* Dark Mode 強制顯示邊框 (需要用 global 因為 body 樣式在外面) */
:global(body.theme-dark) .theme-btn {
  border: 1px solid var(--border-color);
}

.theme-btn:hover {
  background: var(--btn-hover);
  transform: translateY(-2px);
}

main { padding-top: 100px; min-height: 100vh; }
</style>