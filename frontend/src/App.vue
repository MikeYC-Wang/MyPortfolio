<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink, RouterView } from 'vue-router';
import Background3D from '@/components/Background3D.vue';
import HackerIntro from '@/components/HackerIntro.vue'; // 引入進場特效組件

// 主題狀態
const isDark = ref(true);

// 進場動畫狀態
const isIntroFinished = ref(false);

const toggleTheme = () => {
  isDark.value = !isDark.value;
};

// 當 HackerIntro 動畫播放完畢時觸發
const handleIntroComplete = () => {
  console.log("System Access Granted.");
  isIntroFinished.value = true;
};
</script>

<template>
  <HackerIntro @intro-complete="handleIntroComplete" />

  <div class="app-wrapper" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
    
    <Background3D 
      :isDark="isDark" 
      :isReady="isIntroFinished" 
    />

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
  --card-hover-shadow: 0 8px 20px rgba(0,0,0,0.4); 
}

/* 🌑 深色模式 (深灰底 + 淺色發光陰影) */
.theme-dark {
  --text-color: #f0f0f0;
  --link-color: #bbbbbb;
  --link-active: #e0cda9;
  /* 導覽列背景：比背景 (1a1a1a) 更深的半透明黑 */
  --nav-bg: rgba(16, 16, 16, 0.7); 
  --border-color: rgba(255, 255, 255, 0.15);
  --btn-bg: rgba(255, 255, 255, 0.1);
  --btn-hover: rgba(255, 255, 255, 0.2);
  --gradient-text: linear-gradient(135deg, #ffffff 30%, #e0cda9 100%);
  
  /* 卡片：深灰半透明 */
  --card-bg: rgba(44, 44, 44, 0.7);
  --card-border: rgba(255, 255, 255, 0.1);
  /* 陰影：米白色微光暈 (反色) */
  --card-shadow: 0 4px 15px rgba(224, 205, 169, 0.15); 
  /* Hover 陰影：更強的奶茶色發光 */
  --card-hover-shadow: 0 8px 20px rgba(224, 205, 169, 0.35); 
}

/* ☀️ 亮色模式 (米白底 + 深色陰影) */
.theme-light {
  --text-color: #5d4037;
  /* 導覽列背景：深咖啡色 (70% 透明度)，比網頁背景深 */
  --nav-bg: rgba(93, 64, 55, 0.7);
  
  /* 連結顏色：淺奶茶色，確保在深色背景上清楚 */
  --link-color: #e0cda9;
  --link-active: #f0f0f0; 
  
  --border-color: rgba(93, 64, 55, 0.15);
  /* 按鈕背景色改成網頁背景色 (米白色) */
  --btn-bg: #fdfbf7; 
  --btn-hover: rgba(93, 64, 55, 0.2);
  --gradient-text: linear-gradient(135deg, #5d4037 0%, #a1887f 100%);

  /* 卡片：米白半透明 */
  --card-bg: rgba(255, 255, 255, 0.65); 
  --card-border: rgba(141, 110, 99, 0.2);
  /* 陰影：深咖啡色陰影 */
  --card-shadow: 0 6px 15px rgba(93, 64, 55, 0.1);
  /* Hover 陰影：更深的陰影 */
  --card-hover-shadow: 0 10px 25px rgba(93, 64, 55, 0.2); 
}

body {
  margin: 0;
  font-family: 'Helvetica Neue', Arial, sans-serif;
  color: var(--text-color);
  transition: color 0.5s ease;
  /* 確保在 HackerIntro 存在時，
    底層背景也是深色，避免揭幕時有白色閃爍 
  */
  background-color: #1a1a1a; 
}
</style>

<style scoped>
.app-wrapper { min-height: 100vh; }

header {
  position: fixed;
  top: 0;
  width: 100%;
  /* 增加高度：從 70px 增加到 80px */
  height: 80px; 
  box-sizing: border-box;
  padding: 0 40px;
  background: var(--nav-bg);
  /* 強化毛玻璃效果 */
  backdrop-filter: blur(15px); 
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
  /* 👇 修改點：在 Light 模式下，按鈕邊框會是透明，與背景融合 */
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
/* 覆寫 Dark 模式的按鈕邊框，確保在 Dark 模式下邊框依然存在 */
.theme-dark .theme-btn {
  border: 1px solid var(--border-color);
}


.theme-btn:hover {
  background: var(--btn-hover);
  transform: translateY(-2px);
}

/* 內容區：增加頂部間距來避開更高的 Header */
main { padding-top: 100px; min-height: 100vh; }
</style>