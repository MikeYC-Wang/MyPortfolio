<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink, RouterView } from 'vue-router';
import Background3D from '@/components/Background3D.vue';

const isDark = ref(true);

const toggleTheme = () => {
  isDark.value = !isDark.value;
};
</script>

<template>
  <div class="app-wrapper" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
    <Background3D :isDark="isDark" />

    <header>
      <div class="nav-container">
        <nav>
          <RouterLink to="/">首頁</RouterLink>
          <RouterLink to="/lab">特效實驗室</RouterLink>
          <RouterLink to="/admin">後台管理</RouterLink>
        </nav>
      </div>

      <div class="actions">
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

<style>
/* --- 🎨 全域配色變數 --- */
:root {
  /* 基礎預設值 */
  --text-color: #ffffff;
  --link-color: #ccc;
  --link-active: #e0cda9; 
  --nav-bg: rgba(0, 0, 0, 0.5);
  --border-color: rgba(255, 255, 255, 0.1);
  --gradient-text: linear-gradient(135deg, #ffffff 0%, #e0cda9 100%);
  --btn-bg: rgba(255, 255, 255, 0.1);
  --btn-hover: rgba(255, 255, 255, 0.2);
  --card-bg: rgba(44, 44, 44, 0.7);
  --card-border: rgba(255, 255, 255, 0.1);
  --card-shadow: 0 4px 6px rgba(0,0,0,0.3);
  --card-hover-shadow: 0 8px 20px rgba(0,0,0,0.4); /* 預設深色陰影 */
}

/* 🌑 深色模式 (深灰底 + 淺色發光陰影) */
.theme-dark {
  --text-color: #f0f0f0;
  --link-color: #bbbbbb;
  --link-active: #e0cda9;
  --nav-bg: rgba(26, 26, 26, 0.85);
  --border-color: rgba(255, 255, 255, 0.15);
  --btn-bg: rgba(255, 255, 255, 0.1);
  --btn-hover: rgba(255, 255, 255, 0.2);
  --gradient-text: linear-gradient(135deg, #ffffff 30%, #e0cda9 100%);
  
  /* 卡片：深灰半透明 */
  --card-bg: rgba(44, 44, 44, 0.7);
  --card-border: rgba(255, 255, 255, 0.1);
  --card-shadow: 0 4px 15px rgba(224, 205, 169, 0.15); 
  
  /* 👇 關鍵修改：Hover 時變成更亮的奶茶色發光 */
  --card-hover-shadow: 0 8px 20px rgba(224, 205, 169, 0.35); 
}

/* ☀️ 亮色模式 (米白底 + 深色陰影) */
.theme-light {
  --text-color: #5d4037;
  --link-color: #8d6e63;
  --link-active: #a1887f;
  --nav-bg: rgba(253, 251, 247, 0.9);
  --border-color: rgba(93, 64, 55, 0.15);
  --btn-bg: rgba(93, 64, 55, 0.1);
  --btn-hover: rgba(93, 64, 55, 0.2);
  --gradient-text: linear-gradient(135deg, #5d4037 0%, #a1887f 100%);

  /* 卡片：米白半透明 */
  --card-bg: rgba(255, 255, 255, 0.65); 
  --card-border: rgba(141, 110, 99, 0.2);
  --card-shadow: 0 6px 15px rgba(93, 64, 55, 0.1);
  
  /* Hover 時維持深色陰影 */
  --card-hover-shadow: 0 10px 25px rgba(93, 64, 55, 0.2); 
}

body {
  margin: 0;
  font-family: 'Helvetica Neue', Arial, sans-serif;
  color: var(--text-color);
  transition: color 0.5s ease;
}
</style>

<style scoped>
.app-wrapper { min-height: 100vh; }

header {
  position: fixed;
  top: 0;
  width: 100%;
  height: 70px;
  box-sizing: border-box;
  padding: 0 40px;
  background: var(--nav-bg);
  backdrop-filter: blur(10px);
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color);
  transition: background 0.5s, border 0.5s;
}

nav { display: flex; gap: 2rem; }

nav a {
  color: var(--link-color);
  text-decoration: none;
  font-weight: bold;
  font-size: 1rem;
  transition: 0.3s;
  padding: 8px 0;
}

nav a:hover, nav a.router-link-active { color: var(--link-active); }

.theme-btn {
  background: var(--btn-bg);
  border: 1px solid var(--border-color);
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

.theme-btn:hover {
  background: var(--btn-hover);
  transform: translateY(-2px);
}

main { padding-top: 90px; min-height: 100vh; }
</style>