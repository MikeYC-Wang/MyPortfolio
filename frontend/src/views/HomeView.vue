<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
// 👇 引入雷達圖元件
import RadarChart from '@/components/RadarChart.vue';

interface Project {
  id: number;
  title: string;
  description: string;
  tech_stack: string;
}

const projects = ref<Project[]>([]);
const errorMsg = ref('');

// 函數：檢查當前是否為深色主題 (用於傳遞給雷達圖)
const isDark = computed(() => {
  if (typeof document !== 'undefined') {
    return document.body.classList.contains('theme-dark');
  }
  return true; // 預設為深色
});

onMounted(async () => {
  try {
    // 呼叫後端 API 取得作品集資料
    const response = await axios.get('/api/projects');
    projects.value = response.data;
  } catch (err) {
    console.error(err);
    errorMsg.value = '無法連線到後端，請檢查 Python 是否有在跑？';
  }
});
</script>

<template>
  <div class="container">
    <h1 class="main-title">
      <!-- 🚀 Emoji 保持原色 -->
      <span class="emoji">🚀</span>
      <!-- 文字套用漸層 -->
      <span class="gradient-text">我的全端作品集</span>
    </h1>
    
    <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
    <p v-else-if="projects.length === 0 && !errorMsg" class="loading-text">正在載入資料庫...</p>

    <div v-else class="content-wrapper">
      
      <!-- 1. 左側：雷達圖 -->
      <div class="chart-area">
        <!-- 將 isDark 狀態傳遞給雷達圖元件 -->
        <RadarChart :isDark="isDark" />
      </div>

      <!-- 2. 右側：作品集列表 -->
      <div class="projects-list grid">
        <div v-for="p in projects" :key="p.id" class="card">
          <h2 class="gradient-text">{{ p.title }}</h2>
          <p class="desc">{{ p.description }}</p>
          <div class="tags">技術棧: {{ p.tech_stack }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 1200px; /* 增加最大寬度以容納雷達圖 */
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Helvetica Neue', Arial, sans-serif;
}

/* 內容排版：分左右欄 */
.content-wrapper {
  display: grid;
  grid-template-columns: 1fr; /* 預設單欄 (手機版) */
  gap: 2rem;
}

@media (min-width: 900px) {
  .content-wrapper {
    grid-template-columns: 400px 1fr; /* 電腦版：左邊固定寬度給雷達圖 */
  }
}

.chart-area {
  /* 確保在手機版時，雷達圖也能佔滿空間 */
  min-height: 400px; 
}

.projects-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); /* 作品列表 */
  gap: 1.5rem;
}

.loading-text {
  text-align: center;
  color: var(--text-color);
  opacity: 0.7;
}

/* 標題排版 */
.main-title {
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
}

/* 🚀 Emoji 保持原色 */
.emoji {
  display: inline-block;
  -webkit-text-fill-color: initial; 
}

/* ✨ 漸層文字專用 class (顏色來自 App.vue 的 --gradient-text) */
.gradient-text {
  background: var(--gradient-text);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: inline-block;
}

.error { color: red; font-weight: bold; text-align: center;}

/* 👇 卡片樣式：使用全域變數 */
.card {
  background: var(--card-bg);
  border: 1px solid var(--card-border); 
  
  box-shadow: var(--card-shadow);
  backdrop-filter: blur(10px);
  color: var(--text-color);
  padding: 1.5rem;
  border-radius: 12px;
  transition: transform 0.3s, box-shadow 0.3s;
}

.card:hover { 
  transform: translateY(-5px); 
  box-shadow: var(--card-hover-shadow);
}

.desc { 
  margin: 10px 0; 
  opacity: 0.8;
  line-height: 1.6;
}

.tags { 
  font-size: 0.9rem; 
  font-weight: bold; 
  margin-top: 1rem;
  opacity: 0.9;
}
</style>