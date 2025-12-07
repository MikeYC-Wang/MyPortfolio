<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import RadarChart from '@/components/RadarChart.vue';
import IntroScene from '@/components/IntroScene.vue';
import VscodeScreen from '@/components/VscodeScreen.vue';

interface Project {
  id: number;
  title: string;
  description: string;
  tech_stack: string;
}

const projects = ref<Project[]>([]);
const errorMsg = ref('');

const isDark = computed(() => {
  if (typeof document !== 'undefined') {
    return document.body.classList.contains('theme-dark');
  }
  return true;
});

onMounted(async () => {
  try {
    const response = await axios.get('/api/projects');
    projects.value = response.data;
  } catch (err) {
    console.error(err);
    errorMsg.value = '無法連線到後端，請檢查 Python 是否有在跑？';
  }
});
</script>

<template>
  <div class="page-wrapper">
    <IntroScene :isDark="isDark" />

    <div class="main-content container">
      <h1 class="main-title">
        <span class="emoji">🚀</span>
        <span class="gradient-text">我的全端作品集</span>
      </h1>
      
      <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
      <p v-else-if="projects.length === 0 && !errorMsg" class="loading-text">正在載入資料庫...</p>

      <div v-else class="content-wrapper">
        <div class="chart-area">
          <RadarChart :isDark="isDark" />
        </div>

        <div class="projects-list grid">
          <div v-for="p in projects" :key="p.id" class="card">
            <h2 class="gradient-text">{{ p.title }}</h2>
            <p class="desc">{{ p.description }}</p>
            <div class="tags">技術棧: {{ p.tech_stack }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 原本 container 的樣式保留，但我們包了一層 page-wrapper */
.page-wrapper {
  width: 100%;
}

.main-content {
  position: relative;
  z-index: 10;
  background: transparent; 
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Helvetica Neue', Arial, sans-serif;
}

/* ... 以下保留原本的 CSS ... */
.content-wrapper {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

@media (min-width: 900px) {
  .content-wrapper {
    grid-template-columns: 400px 1fr;
  }
}

.chart-area { min-height: 400px; }
.projects-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.loading-text { text-align: center; color: var(--text-color); opacity: 0.7; }

.main-title {
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
}

.emoji { display: inline-block; -webkit-text-fill-color: initial; }

.gradient-text {
  background: var(--gradient-text);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: inline-block;
}

.error { color: red; font-weight: bold; text-align: center;}

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

.desc { margin: 10px 0; opacity: 0.8; line-height: 1.6; }
.tags { font-size: 0.9rem; font-weight: bold; margin-top: 1rem; opacity: 0.9; }
</style>