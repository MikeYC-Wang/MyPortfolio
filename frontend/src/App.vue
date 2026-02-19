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
      <div class="nav-left">
        <RouterLink to="/" class="logo-link">
          <img src="/logo.png" alt="MikeYC Logo" class="site-logo" />
        </RouterLink>

        <nav class="nav-links">
          <RouterLink to="/">首頁</RouterLink>
          <RouterLink to="/lab">靈感碎片</RouterLink>
          <RouterLink to="/blog">個人部落格</RouterLink>
          <RouterLink to="/admin">後台管理</RouterLink>
        </nav>
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
  background: var(--nav-bg);
  backdrop-filter: blur(15px);
  z-index: 100;
  display: flex;
  justify-content: space-between; /* 左右推開 */
  align-items: center;
  border-bottom: 1px solid var(--border-color);
  transition: background 0.5s, border 0.5s;
}

/* --- 左側區域 (Logo + 連結) --- */
.nav-left {
  display: flex;
  align-items: center;
  gap: 40px;
}

/* Logo 樣式 */
.site-logo {
  height: 50px;
  width: auto;
  display: block;
  transition: transform 0.3s ease;
}

.site-logo:hover {
  transform: scale(1.05) rotate(-3deg);
}

/* 文字連結區塊 */
.nav-links {
  display: flex;
  gap: 50px;
}

/* 連結樣式 (只針對 .nav-links 內的 a 標籤) */
.nav-links a {
  color: var(--link-color);
  text-decoration: none;
  font-weight: bold;
  font-size: 1rem;
  transition: 0.3s;
  padding: 8px 0;
  position: relative; /* 為了做底線特效 */
}

.nav-links a:hover, .nav-links a.router-link-active { 
  color: var(--link-active);
}

/* 下底線特效 (選用) */
.nav-links a::after {
  content: '';
  position: absolute;
  width: 0;
  height: 2px;
  bottom: 0;
  left: 0;
  background-color: var(--link-active);
  transition: width 0.3s;
}

.nav-links a:hover::after, .nav-links a.router-link-active::after {
  width: 100%;
}

/* --- 右側區域 (按鈕) --- */
.nav-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.theme-btn {
  background: var(--btn-bg);
  border: 1px solid transparent; 
  cursor: pointer;
  color: var(--text-color);
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

:global(body.theme-dark) .theme-btn {
  border: 1px solid var(--border-color);
}

.theme-btn:hover {
  background: var(--btn-hover);
  transform: translateY(-2px);
}

main { padding-top: 100px; min-height: 100vh; }
</style>