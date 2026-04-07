<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
// import axios from 'axios';
import axios from '@/api';
import { RouterLink } from 'vue-router';
import SiteFooter from '@/components/SiteFooter.vue';

interface Post {
  id: number;
  title: string;
  content: string;
  cover_image?: string;
  created_at: string;
}

const posts = ref<Post[]>([]);
const loading = ref(true);

// --- 分頁設定 ---
const PAGE_SIZE = 9;
const currentPage = ref(1);
const totalPages = computed(() => Math.max(1, Math.ceil(posts.value.length / PAGE_SIZE)));
const pagedItems = computed(() =>
  posts.value.slice((currentPage.value - 1) * PAGE_SIZE, currentPage.value * PAGE_SIZE)
);
const pageNumbers = computed(() => {
  const total = totalPages.value;
  const cur = currentPage.value;
  let start = Math.max(1, cur - 2);
  let end = Math.min(total, start + 4);
  start = Math.max(1, end - 4);
  const arr: number[] = [];
  for (let i = start; i <= end; i++) arr.push(i);
  return arr;
});
const goToPage = (p: number) => {
  if (p < 1 || p > totalPages.value) return;
  currentPage.value = p;
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

// 截取文章摘要 (前 100 字)
const getExcerpt = (text: string) => {
  return text.slice(0, 100).replace(/[#*`]/g, '') + '...';
};

const getImageUrl = (path: string) => {
  if (!path) return '';
  // 如果已經是完整的網址 (http開頭)，就直接回傳
  if (path.startsWith('http')) return path;
  // 否則補上後端網址
  return `${import.meta.env.VITE_API_BASE_URL || ''}${path}`;
};

onMounted(async () => {
  try {
    const res = await axios.get('/api/posts');
    posts.value = res.data;
  } catch (error) {
    console.error('無法取得文章', error);
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div>
    <div class="blog-container">
      <h1 class="page-title"><i class="fa-solid fa-pen-nib"></i> 個人部落格</h1>

      <div v-if="loading" class="loading">Loading...</div>

      <div v-else class="post-grid">
        <div v-for="post in pagedItems" :key="post.id" class="post-card">
          <div 
          v-if="post.cover_image" 
          class="post-cover" 
          :style="{ backgroundImage: `url(${getImageUrl(post.cover_image)})` }"
          ></div>
          <div v-else class="post-cover placeholder">
              <i class="fa-solid fa-code"></i>
          </div>
          
          <div class="post-content">
            <h2>{{ post.title }}</h2>
            <p class="excerpt">{{ getExcerpt(post.content) }}</p>
            
            <RouterLink :to="`/blog/${post.id}`" class="read-more-btn">
              閱讀全文 <i class="fa-solid fa-arrow-right"></i>
            </RouterLink>
          </div>
        </div>
      </div>

      <div v-if="!loading && totalPages > 1" class="pagination">
        <button class="page-btn" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">
          &laquo; 上一頁
        </button>
        <button
          v-for="n in pageNumbers"
          :key="n"
          class="page-btn"
          :class="{ active: n === currentPage }"
          @click="goToPage(n)"
        >
          {{ n }}
        </button>
        <button class="page-btn" :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">
          下一頁 &raquo;
        </button>
      </div>
    </div>
    <SiteFooter />
  </div>
</template>

<style scoped>
.blog-container { max-width: 1000px; margin: 0 auto; padding: 2rem; min-height: 80vh; }
.page-title { text-align: center; color: var(--text-color); margin-bottom: 3rem; font-size: 2.5rem; }

.post-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 2rem; }

.post-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.3s;
  display: flex;
  flex-direction: column;
}
.post-card:hover { transform: translateY(-5px); box-shadow: var(--card-hover-shadow); }

.post-cover { height: 180px; background-size: cover; background-position: center; }
.post-cover.placeholder { display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.2); font-size: 3rem; color: var(--link-color); }

.post-content { padding: 1.5rem; flex-grow: 1; display: flex; flex-direction: column; }
h2 { 
  margin: 0 0 1rem 0; 
  font-size: 1.4rem; 
  color: var(--gradient-text); 
  background: var(--gradient-text); 
  -webkit-background-clip: text; 
  background-clip: text; 
  -webkit-text-fill-color: transparent; 
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.excerpt { 
  color: var(--link-color); 
  font-size: 0.95rem; 
  line-height: 1.6; 
  flex-grow: 1; 
  margin-bottom: 1.5rem; 
  word-break: break-all; 
  overflow-wrap: break-word; 
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  overflow: hidden;
}

.read-more-btn {
  align-self: flex-start;
  color: var(--link-active);
  text-decoration: none;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: gap 0.2s;
}
.read-more-btn:hover { gap: 10px; }

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 3rem;
  flex-wrap: wrap;
}
.page-btn {
  background: var(--btn-bg);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  padding: 8px 14px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  min-width: 40px;
  transition: all 0.2s;
}
.page-btn:hover:not(:disabled):not(.active) {
  background: var(--milk-tea);
  color: var(--text-color);
}
.page-btn.active {
  background: var(--milk-tea);
  color: var(--text-color);
  border-color: var(--milk-tea);
  font-weight: bold;
}
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }
</style>