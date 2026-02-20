<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useTheme } from '@/composables/useTheme';

// === 引入所有元件 ===
import IntroScene from '@/components/IntroScene.vue';
import AboutMe from '@/components/AboutMe.vue';
import ExperienceTimeline from '@/components/ExperienceTimeline.vue';
// import RadarChart from '@/components/RadarChart.vue';

interface Project {
  id: number;
  title: string;
  description: string;
  tech_stack: string;
}

const projects = ref<Project[]>([]);
const errorMsg = ref('');
const isEntered = ref(false);
const router = useRouter();

const { isDark, initTheme } = useTheme();

const goToProjects = () => {
  router.push('/projects');
};

// === 進入網站後的處理 ===
const handleEnterSite = async () => {
  isEntered.value = true;
  
  await nextTick();
  const aboutSection = document.getElementById('about');
  if (aboutSection) {
    aboutSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
};

// ==========================================
// === 專案輪播邏輯 (Carousel Logic) ===
// ==========================================
const currentIndex = ref(0);
const itemsPerView = ref(5); 
const gap = 20; // 卡片間距 20px
let autoplayTimer: number | null = null;

// 計算最多可以按幾次下一頁
const maxIndex = computed(() => Math.max(0, projects.value.length - itemsPerView.value));

// 1. RWD：根據螢幕寬度自動調整顯示數量，確保卡片不會太窄
const updateItemsPerView = () => {
  const width = window.innerWidth;
  if (width < 768) itemsPerView.value = 1;
  else if (width < 1024) itemsPerView.value = 2;
  else if (width < 1440) itemsPerView.value = 3; // 一般筆電或螢幕顯示 3 個
  else if (width < 1600) itemsPerView.value = 4; // 較大螢幕顯示 4 個
  else itemsPerView.value = 5; // 超大寬螢幕才顯示 5 個
  
  // 如果視窗縮小導致當前 index 超出最大值，強制拉回
  if (currentIndex.value > maxIndex.value) {
    currentIndex.value = maxIndex.value;
  }
};

// 下一頁
const nextSlide = () => {
  if (currentIndex.value < maxIndex.value) currentIndex.value++;
  else currentIndex.value = 0; // 循環播放
};

// 上一頁
const prevSlide = () => {
  if (currentIndex.value > 0) currentIndex.value--;
  else currentIndex.value = maxIndex.value; // 循環播放
};

// 點擊小點點跳轉
const goToSlide = (index: number) => {
  currentIndex.value = index;
};

// 開始自動輪播
const startAutoplay = () => {
  if (autoplayTimer) window.clearInterval(autoplayTimer); // 避免重複設定
  if (projects.value.length > itemsPerView.value) {
    autoplayTimer = window.setInterval(nextSlide, 3500); // 3.5秒換一張
  }
};

// 暫停自動輪播 (滑鼠移入時觸發)
const pauseAutoplay = () => {
  if (autoplayTimer) window.clearInterval(autoplayTimer);
};

// 2. 動態計算輪播軌道的移動距離與對齊方式
const trackStyle = computed(() => {
  // 判斷是否需要置中 (當總數量 <= 當前螢幕應該顯示的數量時)
  const shouldCenter = projects.value.length <= itemsPerView.value;
  
  return {
    transform: `translateX(calc(-${currentIndex.value} * ((100% + ${gap}px) / ${itemsPerView.value})))`,
    transition: 'transform 0.5s ease-in-out',
    display: 'flex',
    gap: `${gap}px`,
    width: '100%',
    justifyContent: shouldCenter ? 'center' : 'flex-start' // 數量不足時強制置中
  };
});

// 3. 動態計算每張卡片的精確寬度
const cardStyle = computed(() => {
  const cardWidth = `calc((100% - ${gap * (itemsPerView.value - 1)}px) / ${itemsPerView.value})`;
  return {
    flex: `0 0 ${cardWidth}`,
    maxWidth: cardWidth // 強制最大寬度，防止卡片被意外擠壓或撐開
  };
});

// ==========================================
// === 生命週期 (Lifecycle) ===
// ==========================================
onMounted(async () => {
  initTheme();
  
  // 強制重置位置
  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
  window.scrollTo(0, 0);

  try {
    const response = await axios.get('/api/projects');
    projects.value = response.data;

    updateItemsPerView();
    window.addEventListener('resize', updateItemsPerView);
    startAutoplay();
    
  } catch (err) {
    console.error(err);
    errorMsg.value = '無法連線到後端';
  }
});

onUnmounted(() => {
  window.removeEventListener('resize', updateItemsPerView);
  pauseAutoplay();
});
</script>

<template>
  <div class="page-wrapper">
    <div class="scene-wrapper" :class="{ 'background-mode': isEntered }">
      <IntroScene :isDark="isDark" @enter-site="handleEnterSite" />
    </div>

    <div class="main-content" :class="{ 'light-mode': !isDark, 'visible': isEntered }">
      
      <section id="about" class="full-section bg-gray">
        <div class="container">
          <AboutMe :isDark="isDark" />
        </div>
      </section>

      <section id="experience" class="full-section bg-dark">
        <div class="container">
          <ExperienceTimeline :isDark="isDark" />
        </div>
      </section>

      <section id="projects" class="full-section bg-gray">
        <div class="projects-area">
          
          <h2 class="section-title" style="justify-content: center; margin-bottom: 40px;">
            <i class="fa-solid fa-code-branch"></i> 專案作品 (Projects)
          </h2>
          
          <div v-if="projects.length > 0" class="projects-carousel-container" @mouseenter="pauseAutoplay" @mouseleave="startAutoplay">
            
            <button v-if="projects.length > itemsPerView" class="nav-btn prev-btn" @click="prevSlide">
              <i class="fa-solid fa-chevron-left"></i>
            </button>

            <div class="carousel-viewport">
              <div class="carousel-track" :style="trackStyle">
                
                <div 
                  v-for="p in projects" 
                  :key="p.id" 
                  class="project-card" 
                  :style="cardStyle"
                  @click="goToProjects"
                >
                  <div class="card-header">
                    <h3>{{ p.title }}</h3>
                    <div class="folder-icon"><i class="fa-regular fa-folder-open"></i></div>
                  </div>
                  <p class="desc">{{ p.description }}</p>
                  <div class="tags">
                    <span class="tech-tag" v-for="tech in (p.tech_stack ? p.tech_stack.split(',') : [])" :key="tech">
                      {{ tech.trim() }}
                    </span>
                  </div>
                </div>

              </div>
            </div>

            <button v-if="projects.length > itemsPerView" class="nav-btn next-btn" @click="nextSlide">
              <i class="fa-solid fa-chevron-right"></i>
            </button>

            <div v-if="projects.length > itemsPerView" class="carousel-dots">
              <span 
                v-for="i in (projects.length - itemsPerView + 1)" 
                :key="i" 
                class="dot" 
                :class="{ active: currentIndex === i - 1 }"
                @click="goToSlide(i - 1)"
              ></span>
            </div>
            
          </div>
          
          <p v-else class="loading-text" style="text-align: center;">
             <i class="fa-solid fa-spinner fa-spin"></i> Loading...
          </p>
          
        </div>
      </section>

      <footer class="footer">
        <p>©2026 MikeYC-Wang.</p>
      </footer>
    </div>
  </div>
</template>

<style scoped src="@/assets/css/home.css"></style>