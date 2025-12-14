<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
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
const isEntered = ref(false); // 控制是否已穿過 3D 場景

// 簡單的深色模式判斷 (預設為深色以符合 Hacker 風格)
const isDark = computed(() => {
  if (typeof document !== 'undefined') {
    return document.body.classList.contains('theme-dark');
  }
  return true; 
});

// 當 IntroScene 發出 enter-site 事件時觸發
const handleEnterSite = () => {
  isEntered.value = true;
};

// 獲取專案列表
onMounted(async () => {
  try {
    const response = await axios.get('/api/projects');
    projects.value = response.data;
  } catch (err) {
    console.error(err);
    errorMsg.value = '無法連線到後端，請檢查 FastAPI 是否有在跑？';
  }
});
</script>

<template>
  <div class="page-wrapper">
    <div class="scene-wrapper" :class="{ 'background-mode': isEntered }">
      <IntroScene :isDark="isDark" @enter-site="handleEnterSite" />
    </div>

    <div class="main-content">
      
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
}

/* === 3D 場景容器 === */
.scene-wrapper {
  position: fixed; /* 固定在視窗 */
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  z-index: 10; /* 最上層 */
  transition: opacity 0.5s ease;
}

/* 當進入網站後，讓 3D 場景不阻擋滑鼠事件 (變成背景) */
.scene-wrapper.background-mode {
  pointer-events: none;
  /* 選擇性：如果想讓背景變暗或消失，可以加 opacity: 0.1 */
}

/* === 主要內容區域 === */
.main-content {
  position: relative;
  z-index: 20; /* 蓋在 3D 場景之上 */
  /* 重要：留出 100vh 的空間給 3D 捲動特效，讓使用者先捲完 3D 再看到內容 */
  margin-top: 100vh; 
  background: var(--bg-color, #f8f9fa); /* 給背景色遮住 3D 場景 */
  min-height: 100vh;
  box-shadow: 0 -10px 30px rgba(0,0,0,0.1); /* 頂部陰影 */
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

/* 大螢幕時並排顯示技能與專案 */
@media (min-width: 900px) {
  .content-grid {
    grid-template-columns: 400px 1fr;
    align-items: start;
  }
  
  /* 讓圖表在捲動時稍微固定 */
  .sticky-chart {
    position: sticky;
    top: 20px;
  }
}

.section-title {
  font-size: 2rem;
  margin-bottom: 30px;
  color: #333;
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
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  transition: transform 0.3s, box-shadow 0.3s;
  border: 1px solid rgba(0,0,0,0.05);
}

.project-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
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

.folder-icon {
  color: #ffd700;
  font-size: 1.2rem;
}

.desc {
  color: #666;
  font-size: 0.95rem;
  line-height: 1.6;
  margin-bottom: 15px;
  /* 限制行數 */
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
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

/* === 頁尾 === */
.footer {
  text-align: center;
  padding: 40px 20px;
  background: #2c3e50;
  color: #fff;
  margin-top: 60px;
}

.social-links {
  margin-top: 15px;
  display: flex;
  justify-content: center;
  gap: 20px;
}

.social-links a {
  color: #fff;
  font-size: 1.5rem;
  transition: color 0.3s;
}

.social-links a:hover {
  color: #00ffff;
}

.error { color: #dc3545; font-weight: bold; }
.loading-text { color: #6c757d; }
</style>