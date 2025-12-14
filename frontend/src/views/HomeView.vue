<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
import axios from 'axios';
import { useTheme } from '@/composables/useTheme';

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

const { isDark, initTheme } = useTheme();

// === 修正 1: 進入網站時，強制校正捲動位置 ===
const handleEnterSite = () => {
  isEntered.value = true;
  
  // 等待 Vue 更新 DOM 後執行
  nextTick(() => {
    // 取得 About 區塊的位置
    const aboutSection = document.getElementById('about');
    if (aboutSection) {
      // 平滑捲動到 About 區塊的頂部
      aboutSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else {
      // 備案：捲動到 100vh (內容開始的地方)
      window.scrollTo({ top: window.innerHeight, behavior: 'smooth' });
    }
  });
};

onMounted(async () => {
  initTheme();

  // 強制重置捲動位置
  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
  window.scrollTo(0, 0);
  await nextTick();
  window.scrollTo(0, 0);

  try {
    const response = await axios.get('/api/projects');
    projects.value = response.data;
  } catch (err) {
    console.error(err);
    errorMsg.value = '無法連線到後端';
  }
});
</script>

<template>
  <div class="page-wrapper">
    <div class="scene-wrapper" :class="{ 'background-mode': isEntered }">
      <IntroScene :isDark="isDark" @enter-site="handleEnterSite" />
    </div>

    <div class="main-content" :class="{ 'light-mode': !isDark, 'visible': isEntered }">
      
      <section id="about" class="full-section section-gray">
        <div class="container">
          <AboutMe :isDark="isDark" />
        </div>
      </section>

      <section id="experience" class="full-section section-dark">
        <div class="container">
          <ExperienceTimeline :isDark="isDark" />
        </div>
      </section>

      <section id="skills-projects" class="full-section section-gray">
        <div class="container">
          <div class="content-grid">
            <div class="chart-area sticky-chart">
               <RadarChart :isDark="isDark" />
            </div>

            <div class="projects-area">
              <h2 class="section-title">
                <i class="fa-solid fa-code-branch"></i> 專案作品 (Projects)
              </h2>
              
              <div v-if="projects.length > 0" class="projects-list">
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
              <p v-else class="loading-text">
                 <i class="fa-solid fa-spinner fa-spin"></i> Loading...
              </p>
            </div>
          </div>
        </div>
      </section>

      <footer class="footer">
        <p>© 2025 Mikey Wang.</p>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.page-wrapper { width: 100%; position: relative; background-color: #0d1117; }
.scene-wrapper { position: fixed; top: 0; left: 0; width: 100%; height: 100vh; z-index: 10; transition: opacity 0.5s ease; }
.scene-wrapper.background-mode { pointer-events: none; }

.main-content {
  position: relative; z-index: 20; margin-top: 100vh; min-height: 100vh;
  opacity: 0; pointer-events: none; transition: opacity 1.5s ease-in-out;
  /* 預設底色 (會在 section 被覆蓋，這裡只是防漏) */
  background-color: #0d1117; color: #e0e0e0;
}

.main-content.visible { opacity: 1; pointer-events: auto; }

/* === 修正 2: 設定交錯背景色 === */
.full-section {
  width: 100%;
  padding: 80px 0; /* 上下留白 */
}

/* 深灰區塊 (AboutMe, Skills) */
.section-gray {
  background-color: #1a1a1a;
  color: #e0e0e0;
}

/* 全黑區塊 (Experience) */
.section-dark {
  background-color: #0d1117;
  color: #e0e0e0;
}

/* 淺色模式覆蓋 (若切換到 Light Mode) */
.main-content.light-mode .section-gray { background-color: #f8f9fa; color: #333; }
.main-content.light-mode .section-dark { background-color: #ffffff; color: #333; }


/* === 其他樣式保持不變 === */
.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
.content-grid { display: grid; grid-template-columns: 1fr; gap: 40px; }
@media (min-width: 900px) { .content-grid { grid-template-columns: 400px 1fr; align-items: start; } .sticky-chart { position: sticky; top: 20px; } }

.section-title { font-size: 2rem; margin-bottom: 30px; display: flex; align-items: center; gap: 10px; color: inherit; }
.projects-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.project-card { background: #1e1e1e; border-radius: 12px; padding: 20px; border: 1px solid #444; color: #e0e0e0; box-shadow: 0 4px 15px rgba(0,0,0,0.3); transition: transform 0.3s, box-shadow 0.3s; }
.main-content.light-mode .project-card { background: #fff; border-color: #eee; color: #333; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
.project-card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0,123,255,0.15); border-color: #007bff; }
.card-header { display: flex; justify-content: space-between; margin-bottom: 10px; }
.card-header h3 { margin: 0; font-size: 1.2rem; color: #4dabf7; }
.main-content.light-mode .card-header h3 { color: #007bff; }
.folder-icon { color: #ffd700; font-size: 1.2rem; }
.desc { color: #aaa; margin-bottom: 15px; display: -webkit-box; -webkit-line-clamp: 3; line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.main-content.light-mode .desc { color: #666; }
.tags { display: flex; flex-wrap: wrap; gap: 8px; }
.tech-tag { background: #333; color: #ccc; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; }
.main-content.light-mode .tech-tag { background: #eef2f7; color: #555; }
.footer { text-align: center; padding: 40px; background: #000; color: #fff; margin-top: 0; border-top: 1px solid #333; }
.main-content.light-mode .footer { background: #f1f1f1; color: #333; border-top: 1px solid #ddd; }
</style>