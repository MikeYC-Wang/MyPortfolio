<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import axios from 'axios';

// === 引入所有元件 ===
import IntroScene from '@/components/IntroScene.vue';
import AboutMe from '@/components/AboutMe.vue';
import ExperienceTimeline from '@/components/ExperienceTimeline.vue';
import RadarChart from '@/components/RadarChart.vue';

interface Project {
  id: number;
  title: string;
  description: string;
  tech_stack: string;
}

const projects = ref<Project[]>([]);
const errorMsg = ref('');
const isEntered = ref(false);

// === 關鍵修正：改用 ref + MutationObserver 來真正監聽深色模式 ===
const isDark = ref(true); // 預設先給 True (讓它一開始就是黑的)

let observer: MutationObserver | null = null;

const updateTheme = () => {
  if (typeof document !== 'undefined') {
    // 檢查 body 是否有 theme-dark class
    isDark.value = document.body.classList.contains('theme-dark');
  }
};

const handleEnterSite = () => {
  isEntered.value = true;
};

onMounted(async () => {
  // 1. 初始化檢查主題
  updateTheme();

  // 2. 建立監聽器：當 body 的 class 改變時，自動更新 isDark
  if (typeof document !== 'undefined') {
    observer = new MutationObserver(updateTheme);
    observer.observe(document.body, {
      attributes: true,
      attributeFilter: ['class'],
    });
  }

  // 3. 強制瀏覽器忘記捲動位置，回到最上方
  if ('scrollRestoration' in history) {
    history.scrollRestoration = 'manual';
  }
  window.scrollTo(0, 0);
  await nextTick();
  window.scrollTo(0, 0);

  // 4. 獲取專案
  try {
    const response = await axios.get('/api/projects');
    projects.value = response.data;
  } catch (err) {
    console.error(err);
    errorMsg.value = '無法連線到後端，請檢查 FastAPI 是否有在跑？';
  }
});

// 記得在組件銷毀時移除監聽器，避免效能問題
onUnmounted(() => {
  if (observer) observer.disconnect();
});
</script>

<template>
  <div class="page-wrapper">
    <div class="scene-wrapper" :class="{ 'background-mode': isEntered }">
      <IntroScene :isDark="isDark" @enter-site="handleEnterSite" />
    </div>

    <div class="main-content" :class="{ 'dark-mode': isDark }">
      
      <section id="about">
        <AboutMe :isDark="isDark" />
      </section>

      <section id="experience">
        <ExperienceTimeline :isDark="isDark" />
      </section>

      <section id="skills-projects" class="container">
        <div class="content-grid">
          
          <div class="chart-area sticky-chart">
             <RadarChart :isDark="isDark" />
          </div>

          <div class="projects-area">
            <h2 class="section-title">
              <i class="fa-solid fa-code-branch"></i> 專案作品 (Projects)
            </h2>

            <p v-if="errorMsg" class="error"><i class="fa-solid fa-circle-exclamation"></i> {{ errorMsg }}</p>
            <p v-else-if="projects.length === 0" class="loading-text">
              <i class="fa-solid fa-spinner fa-spin"></i> 正在從資料庫載入專案...
            </p>
            
            <div v-else class="projects-list">
              <div v-for="p in projects" :key="p.id" class="project-card">
                <div class="card-header">
                  <h3>{{ p.title }}</h3>
                  <div class="folder-icon"><i class="fa-regular fa-folder-open"></i></div>
                </div>
                <p class="desc">{{ p.description }}</p>
                <div class="tags">
                  <span class="tech-tag" v-for="tech in p.tech_stack.split(',')" :key="tech">
                    {{ tech.trim() }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <footer class="footer">
        <p>© 2025 Mikey Wang. Built with Vue 3, Three.js & FastAPI.</p>
        <div class="social-links">
          <a href="#" target="_blank"><i class="fa-brands fa-github"></i></a>
          <a href="#" target="_blank"><i class="fa-brands fa-linkedin"></i></a>
          <a href="#" target="_blank"><i class="fa-solid fa-envelope"></i></a>
        </div>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.page-wrapper {
  width: 100%;
  position: relative;
  background-color: #0d1117; /* 預設底色為黑，避免載入閃爍 */
}

/* === 3D 場景容器 === */
.scene-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  z-index: 10;
  transition: opacity 0.5s ease;
}

.scene-wrapper.background-mode {
  pointer-events: none;
}

/* === 主要內容區域 === */
.main-content {
  position: relative;
  z-index: 20;
  margin-top: 100vh; 
  min-height: 100vh;
  box-shadow: 0 -10px 30px rgba(0,0,0,0.5);
  transition: background-color 0.3s ease, color 0.3s ease;
  
  /* 預設樣式 (Light Mode) */
  background-color: #f8f9fa;
  color: #333;
}

/* 深色模式樣式 (Dark Mode) */
.main-content.dark-mode {
  background-color: #0d1117; /* GitHub Dark 背景色 */
  color: #e0e0e0;
}

/* === 佈局樣式 === */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 40px;
}

@media (min-width: 900px) {
  .content-grid {
    grid-template-columns: 400px 1fr;
    align-items: start;
  }
  
  .sticky-chart {
    position: sticky;
    top: 20px;
  }
}

.section-title {
  font-size: 2rem;
  margin-bottom: 30px;
  color: inherit;
  display: flex;
  align-items: center;
  gap: 10px;
}

/* === 專案卡片樣式 === */
.projects-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.project-card {
  /* 預設淺色卡片 */
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  transition: transform 0.3s, box-shadow 0.3s;
  border: 1px solid rgba(0,0,0,0.05);
}

/* 深色模式下的專案卡片 */
.main-content.dark-mode .project-card {
  background: #1e1e1e;
  border-color: #444;
  color: #e0e0e0;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

.project-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0,123,255,0.15);
  border-color: #007bff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.card-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #007bff;
}

.main-content.dark-mode .card-header h3 {
  color: #4dabf7;
}

.folder-icon {
  color: #ffd700;
  font-size: 1.2rem;
}

.desc {
  color: #666;
  font-size: 0.95rem;
  line-height: 1.6;
  margin-bottom: 15px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.main-content.dark-mode .desc {
  color: #aaa;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tech-tag {
  background: #eef2f7;
  color: #555;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.main-content.dark-mode .tech-tag {
  background: #333;
  color: #ccc;
}

/* === 頁尾 === */
.footer {
  text-align: center;
  padding: 40px 20px;
  background: #f1f1f1;
  color: #333;
  margin-top: 60px;
  border-top: 1px solid #ddd;
}

.main-content.dark-mode .footer {
  background: #000;
  color: #fff;
  border-top: 1px solid #333;
}

.social-links {
  margin-top: 15px;
  display: flex;
  justify-content: center;
  gap: 20px;
}

.social-links a {
  color: inherit;
  font-size: 1.5rem;
  transition: color 0.3s;
}

.social-links a:hover {
  color: #00ffff;
}

.error { color: #dc3545; font-weight: bold; }
.loading-text { color: #6c757d; }
</style>