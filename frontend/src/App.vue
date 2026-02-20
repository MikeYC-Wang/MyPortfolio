<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { RouterLink, RouterView } from 'vue-router';
import Background3D from '@/components/Background3D.vue';
import HackerIntro from '@/components/HackerIntro.vue';
import CustomCursor from '@/components/CustomCursor.vue';
import { useTheme } from '@/composables/useTheme';
import "./assets/css/Theme.css";

// 使用共用的主題狀態
const { isDark, toggleTheme, initTheme } = useTheme();

// 進場動畫狀態
const isIntroFinished = ref(false);

// 手機版選單狀態
const isMobileMenuOpen = ref(false);

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false;
};

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
    
    <CustomCursor /> <Background3D 
      :isDark="isDark" 
      :isReady="isIntroFinished" 
    />

    <header>
      <div class="nav-left">
        <RouterLink to="/" class="logo-link" @click="closeMobileMenu">
          <img src="/logo.png" alt="MikeYC Logo" class="site-logo" />
        </RouterLink>

        <nav class="nav-links desktop-only">
          <RouterLink to="/">首頁</RouterLink>
          <RouterLink to="/lab">靈感碎片</RouterLink>
          <RouterLink to="/blog">個人部落格</RouterLink>
          <RouterLink to="/admin">後台管理</RouterLink>
          <RouterLink to="/dashboard">系統監控</RouterLink>
        </nav>
      </div>

      <div class="actions nav-right">
        <button class="theme-btn" @click="toggleTheme" :title="isDark ? '切換到奶茶模式' : '切換到深色模式'">
          <svg v-if="isDark" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
          <span class="btn-text">{{ isDark ? 'Dark' : 'Light' }}</span>
        </button>

        <button class="hamburger-btn" @click="toggleMobileMenu">
          <i class="fa-solid" :class="isMobileMenuOpen ? 'fa-xmark' : 'fa-bars'"></i>
        </button>
      </div>
    </header>

    <transition name="mobile-menu">
      <div v-if="isMobileMenuOpen" class="mobile-drawer">
        <nav class="mobile-nav-links">
          <RouterLink to="/" @click="closeMobileMenu">首頁</RouterLink>
          <RouterLink to="/lab" @click="closeMobileMenu">靈感碎片</RouterLink>
          <RouterLink to="/blog" @click="closeMobileMenu">個人部落格</RouterLink>
          <RouterLink to="/admin" @click="closeMobileMenu">後台管理</RouterLink>
          <RouterLink to="/dashboard" @click="closeMobileMenu">系統監控</RouterLink>
        </nav>
      </div>
    </transition>

    <main>
      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
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
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color);
  transition: background 0.5s, border 0.5s;
}

/* --- 左側區域 --- */
.nav-left {
  display: flex;
  align-items: center;
  gap: 40px;
}

.site-logo {
  height: 50px;
  width: auto;
  display: block;
  transition: transform 0.3s ease;
}

.site-logo:hover {
  transform: scale(1.05) rotate(-3deg);
}

.nav-links {
  display: flex;
  gap: 50px;
}

.nav-links a {
  color: var(--link-color);
  text-decoration: none;
  font-weight: bold;
  font-size: 1rem;
  transition: 0.3s;
  padding: 8px 0;
  position: relative;
}

.nav-links a:hover, .nav-links a.router-link-active { 
  color: var(--link-active);
}

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

/* --- 右側區域 --- */
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

/* 漢堡按鈕樣式 */
.hamburger-btn {
  display: none; /* 桌機版預設隱藏 */
  background: transparent;
  border: none;
  color: var(--text-color);
  font-size: 1.5rem;
  cursor: pointer;
  padding: 5px;
  transition: transform 0.3s;
}

.hamburger-btn:hover {
  transform: scale(1.1);
  color: var(--link-active);
}

/* 手機版選單 Drawer 樣式 */
.mobile-drawer {
  position: fixed;
  top: 80px;
  left: 0;
  width: 100%;
  height: calc(100vh - 80px);
  background: var(--nav-bg);
  backdrop-filter: blur(25px);
  z-index: 99;
  display: flex;
  justify-content: center;
  align-items: center;
}

.mobile-nav-links {
  display: flex;
  flex-direction: column;
  gap: 40px;
  text-align: center;
}

.mobile-nav-links a {
  color: var(--link-color);
  font-size: 1.5rem;
  font-weight: bold;
  text-decoration: none;
  letter-spacing: 2px;
  transition: 0.3s;
}

.mobile-nav-links a:hover, 
.mobile-nav-links a.router-link-active {
  color: var(--link-active);
  transform: translateY(-3px);
}

/* 手機選單進退場動畫 */
.mobile-menu-enter-active,
.mobile-menu-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.mobile-menu-enter-from,
.mobile-menu-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* --- RWD 手機版響應式設定 --- */
@media (max-width: 768px) {
  header {
    padding: 0 20px; /* 手機版內縮小一點 */
  }
  
  .desktop-only {
    display: none; /* 隱藏桌機文字選單 */
  }

  .hamburger-btn {
    display: block; /* 顯示漢堡按鈕 */
  }
}

main { padding-top: 100px; min-height: 100vh; overflow-x: hidden; }

/* 頁面轉場動畫 CSS */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(15px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-15px);
}
</style>