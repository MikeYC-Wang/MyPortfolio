<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

interface Project {
  id: number;
  title: string;
  description: string;
  tech_stack: string;
}

const projects = ref<Project[]>([]);
const errorMsg = ref('');

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
    <p v-else-if="projects.length === 0">正在載入資料庫...</p>

    <div v-else class="grid">
      <!-- 列表渲染卡片 -->
      <div v-for="p in projects" :key="p.id" class="card">
        <!-- 標題套用漸層 -->
        <h2 class="gradient-text">{{ p.title }}</h2>
        <p class="desc">{{ p.description }}</p>
        <div class="tags">技術棧: {{ p.tech_stack }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Helvetica Neue', Arial, sans-serif;
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
  /* 確保不受到 text-fill-color: transparent 的影響 */
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

.grid { display: grid; gap: 1.5rem; }

/* 👇 卡片樣式：使用全域變數 */
.card {
  background: var(--card-bg);
  /* 確保邊框是 solid 的，不讓漸層跑出去 */
  border: 1px solid var(--card-border); 
  
  box-shadow: var(--card-shadow);
  backdrop-filter: blur(10px);
  color: var(--text-color);
  padding: 1.5rem;
  border-radius: 12px;
  transition: transform 0.3s, box-shadow 0.3s;
}

/* 👇 關鍵修復：使用 --card-hover-shadow 變數，達成深色發光/淺色陰影切換 */
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