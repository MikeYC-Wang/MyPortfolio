<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import axios from '@/api';
import { useRouter } from 'vue-router';
import { useTheme } from '@/composables/useTheme';

// 引入 GSAP 動畫庫來做滾動滑入特效
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

// === 引入所有元件 ===
import IntroScene from '@/components/IntroScene.vue';
import AboutMe from '@/components/AboutMe.vue';
import ExperienceTimeline from '@/components/ExperienceTimeline.vue';
import SiteFooter from '@/components/SiteFooter.vue';

gsap.registerPlugin(ScrollTrigger);

// === 專案資料介面 ===
interface Project {
  id: number;
  title: string;
  description: string;
  tech_stack: string;
}

// === 文章資料介面 ===
interface Post {
  id: number;
  title: string;
  content: string;
  cover_image?: string;
  created_at: string;
}

// === 狀態變數 ===
const projects = ref<Project[]>([]);
const recentPosts = ref<Post[]>([]);
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

// === 處理部落格圖片與摘要的工具函數 ===
const getExcerpt = (text: string) => {
  return text.slice(0, 200).replace(/[#*`\n]/g, '') + '...';
};

const getImageUrl = (path: string | undefined) => {
  if (!path) return '';
  if (path.startsWith('http')) return path;
  return `http://127.0.0.1:8000${path}`;
};

// ==========================================
// === 專案輪播邏輯 (Carousel Logic) ===
// ==========================================
const currentIndex = ref(0);
const itemsPerView = ref(5); 
const gap = 20; 
let autoplayTimer: number | null = null;

const maxIndex = computed(() => Math.max(0, projects.value.length - itemsPerView.value));

const updateItemsPerView = () => {
  const width = window.innerWidth;
  if (width < 768) itemsPerView.value = 1;
  else if (width < 1024) itemsPerView.value = 2;
  else if (width < 1440) itemsPerView.value = 3; 
  else if (width < 1600) itemsPerView.value = 4; 
  else itemsPerView.value = 5; 
  
  if (currentIndex.value > maxIndex.value) {
    currentIndex.value = maxIndex.value;
  }
};

const nextSlide = () => {
  if (currentIndex.value < maxIndex.value) currentIndex.value++;
  else currentIndex.value = 0; 
};

const prevSlide = () => {
  if (currentIndex.value > 0) currentIndex.value--;
  else currentIndex.value = maxIndex.value; 
};

const goToSlide = (index: number) => {
  currentIndex.value = index;
};

const startAutoplay = () => {
  if (autoplayTimer) window.clearInterval(autoplayTimer); 
  if (projects.value.length > itemsPerView.value) {
    autoplayTimer = window.setInterval(nextSlide, 3500); 
  }
};

const pauseAutoplay = () => {
  if (autoplayTimer) window.clearInterval(autoplayTimer);
};

const trackStyle = computed(() => {
  const shouldCenter = projects.value.length <= itemsPerView.value;
  return {
    transform: `translateX(calc(-${currentIndex.value} * ((100% + ${gap}px) / ${itemsPerView.value})))`,
    transition: 'transform 0.5s ease-in-out',
    display: 'flex',
    gap: `${gap}px`,
    width: '100%',
    justifyContent: shouldCenter ? 'center' : 'flex-start' 
  };
});

const cardStyle = computed(() => {
  const cardWidth = `calc((100% - ${gap * (itemsPerView.value - 1)}px) / ${itemsPerView.value})`;
  return {
    flex: `0 0 ${cardWidth}`,
    maxWidth: cardWidth 
  };
});

// ==========================================
// === 動態滑入特效 (Scroll Animations) ===
// ==========================================
const initScrollAnimations = () => {
  const rows = document.querySelectorAll('.feature-row');
  
  rows.forEach((row) => {
    // 判斷這一行是不是反轉的 (文左圖右)
    const isReverse = row.classList.contains('reverse');
    const img = row.querySelector('.feature-img');
    const text = row.querySelector('.feature-text');

    // 1. 圖片滑入設定
    // 如果是反轉，圖片在右邊，所以從右邊(x: 100)滑入；反之從左邊(x: -100)滑入
    gsap.fromTo(img, 
      { x: isReverse ? 100 : -100, opacity: 0 },
      { 
        x: 0, 
        opacity: 1, 
        duration: 1, 
        ease: 'power3.out',
        scrollTrigger: {
          trigger: row,
          start: 'top 85%', // 當該區塊頂部進入視窗 85% 位置時觸發動畫
          toggleActions: 'play none none none'
        }
      }
    );

    // 2. 文字滑入設定
    // 文字與圖片的反向進場，並且加上 0.2 秒延遲 (delay) 創造視覺層次感
    gsap.fromTo(text, 
      { x: isReverse ? -100 : 100, opacity: 0 },
      { 
        x: 0, 
        opacity: 1, 
        duration: 1, 
        ease: 'power3.out',
        delay: 0.2, 
        scrollTrigger: {
          trigger: row,
          start: 'top 85%',
          toggleActions: 'play none none none'
        }
      }
    );
  });
};

// ==========================================
// === 生命週期 (Lifecycle) ===
// ==========================================
onMounted(async () => {
  initTheme();
  
  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
  window.scrollTo(0, 0);

  try {
    const [projectsRes, postsRes] = await Promise.all([
      axios.get('/api/projects'),
      axios.get('/api/posts')
    ]);

    projects.value = projectsRes.data;
    recentPosts.value = postsRes.data.slice(0, 4); 

    updateItemsPerView();
    window.addEventListener('resize', updateItemsPerView);
    startAutoplay();
    
    // 資料抓取完畢，等待 Vue 將 HTML 渲染到畫面上之後，啟動滾動特效！
    await nextTick();
    initScrollAnimations();
    
  } catch (err) {
    console.error(err);
    errorMsg.value = '無法連線到後端';
  }
});

onUnmounted(() => {
  window.removeEventListener('resize', updateItemsPerView);
  pauseAutoplay();
  // 離開頁面時清除動畫監聽，防止效能浪費或破圖
  ScrollTrigger.getAll().forEach(t => t.kill()); 
});
</script>

<template>
  <div class="page-wrapper">
    <div class="scene-wrapper" :class="{ 'background-mode': isEntered }">
      <IntroScene :isDark="isDark" @enter-site="handleEnterSite" />
    </div>

    <div class="main-content" :class="{ 'light-mode': !isDark, 'visible': isEntered }">
      
      <section id="about" class="full-section bg-gray">
        <div class="container" style="max-width: 1600px;">
          <AboutMe :isDark="isDark" />
        </div>
      </section>

      <section id="experience" class="full-section bg-dark">
        <div class="container" style="max-width: 1600px;">
          <ExperienceTimeline :isDark="isDark" />
        </div>
      </section>

      <div class="tech-marquee-wrapper">
        <div class="marquee-track">
          <div class="marquee-item"><i class="fa-brands fa-wordpress"></i> WordPress</div>
          <div class="marquee-item"><i class="fa-brands fa-html5"></i> HTML5</div>
          <div class="marquee-item"><i class="fa-brands fa-css3-alt"></i> CSS3</div>
          <div class="marquee-item"><i class="fa-brands fa-js"></i> JavaScript</div>
          <!-- <div class="marquee-item"><i class="fa-brands fa-typescript"></i> TypeScript</div> -->
          <div class="marquee-item"><i class="fa-brands fa-vuejs"></i> Vue.js</div>
          <div class="marquee-item"><i class="fa-brands fa-bootstrap"></i> Bootstrap</div>
          <div class="marquee-item"><i class="fa-brands fa-node-js"></i> Node.js</div>
          <div class="marquee-item"><i class="fa-solid fa-c"></i> C#</div>
          <div class="marquee-item"><i class="fa-brands fa-python"></i> Python</div>
          <div class="marquee-item"><i class="fa-brands fa-windows"></i> .NET</div>
          <div class="marquee-item"><i class="fa-solid fa-microchip"></i> Arduino</div>
          <div class="marquee-item"><i class="fa-brands fa-git-alt"></i> Git</div>
          <div class="marquee-item"><i class="fa-brands fa-npm"></i> npm</div>
          
          <div class="marquee-item"><i class="fa-brands fa-wordpress"></i> WordPress</div>
          <div class="marquee-item"><i class="fa-brands fa-html5"></i> HTML5</div>
          <div class="marquee-item"><i class="fa-brands fa-css3-alt"></i> CSS3</div>
          <div class="marquee-item"><i class="fa-brands fa-js"></i> JavaScript</div>
          <!-- <div class="marquee-item"><i class="fa-brands fa-typescript"></i> TypeScript</div> -->
          <div class="marquee-item"><i class="fa-brands fa-vuejs"></i> Vue.js</div>
          <div class="marquee-item"><i class="fa-brands fa-bootstrap"></i> Bootstrap</div>
          <div class="marquee-item"><i class="fa-brands fa-node-js"></i> Node.js</div>
          <div class="marquee-item"><i class="fa-solid fa-c"></i> C#</div>
          <div class="marquee-item"><i class="fa-brands fa-python"></i> Python</div>
          <div class="marquee-item"><i class="fa-brands fa-windows"></i> .NET</div>
          <div class="marquee-item"><i class="fa-solid fa-microchip"></i> Arduino</div>
          <div class="marquee-item"><i class="fa-brands fa-git-alt"></i> Git</div>
          <div class="marquee-item"><i class="fa-brands fa-npm"></i> npm</div>
        </div>
      </div>

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

      <section id="latest-posts" class="full-section bg-dark">
        <div class="container" style="max-width: 1600px;">
          <h2 class="section-title" style="justify-content: center; margin-bottom: 60px;">
            <i class="fa-solid fa-pen-nib"></i> 最新文章 (Latest Posts)
          </h2>
          
          <div v-if="recentPosts.length > 0" class="feature-container">
            <div 
              v-for="(post, index) in recentPosts" 
              :key="post.id" 
              class="feature-row"
              :class="{ 'reverse': index % 2 !== 0 }"
            >
              <div class="feature-img">
                <div 
                  v-if="post.cover_image" 
                  class="blog-cover-img" 
                  :style="{ backgroundImage: `url(${getImageUrl(post.cover_image)})` }"
                ></div>
                <div v-else class="blog-cover-img placeholder">
                  <i class="fa-solid fa-code"></i>
                </div>
              </div>
              
              <div class="feature-text">
                <h3>{{ post.title }}</h3>
                <p>{{ getExcerpt(post.content) }}</p>
                <RouterLink :to="`/blog/${post.id}`" class="feature-btn">
                  閱讀全文 <i class="fa-solid fa-arrow-right"></i>
                </RouterLink>
              </div>
            </div>
          </div>
          <p v-else class="loading-text" style="text-align: center;">無文章資料</p>

          <div style="text-align: center; margin-top: 80px;">
            <RouterLink to="/blog" class="feature-btn" style="padding: 15px 40px; font-size: 1.1rem;">
              探索更多文章 <i class="fa-solid fa-arrow-right"></i>
            </RouterLink>
          </div>
        </div>
      </section>

      <section id="lab-teaser" class="full-section bg-gray">
        <div class="container" style="max-width: 1600px;">
          <div class="feature-row">
            
            <div class="feature-img lab-visual-container">
              <div class="morphing-blob"></div>
              <div class="morphing-blob-shadow"></div>
            </div>
            
            <div class="feature-text">
              <div class="badge">Experimental</div>
              <h2 class="section-title" style="margin-bottom: 20px;">
                <i class="fa-solid fa-flask"></i> 靈感碎片 (Lab)
              </h2>
              <p>
                這裡是我存放奇思妙想的程式碼遊樂場。從酷炫的 CSS 動畫、WebGL 著色器，到各種實驗性質的 UI 互動特效。每一次的無聊嘗試，都可能成為下一個專案的亮點。
              </p>
              <RouterLink to="/lab" class="feature-btn" style="margin-top: 20px;">
                進入實驗室探索 <i class="fa-solid fa-arrow-right"></i>
              </RouterLink>
            </div>

          </div>
        </div>
      </section>

      <SiteFooter />
    </div>
  </div>
</template>

<style scoped src="@/assets/css/home.css"></style>