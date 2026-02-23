<script setup lang="ts">
import { ref, onMounted } from 'vue';
// import axios from 'axios';
import axios from '@/api';
import { RouterLink } from 'vue-router';

interface Post {
  id: number;
  title: string;
  content: string;
  cover_image?: string;
  created_at: string;
}

const posts = ref<Post[]>([]);
const loading = ref(true);

// 截取文章摘要 (前 100 字)
const getExcerpt = (text: string) => {
  return text.slice(0, 100).replace(/[#*`]/g, '') + '...';
};

const getImageUrl = (path: string) => {
  if (!path) return '';
  // 如果已經是完整的網址 (http開頭)，就直接回傳
  if (path.startsWith('http')) return path;
  // 否則補上後端網址
  return `http://127.0.0.1:8000${path}`;
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
  <div class="blog-container">
    <h1 class="page-title"><i class="fa-solid fa-pen-nib"></i> 個人部落格</h1>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-else class="post-grid">
      <div v-for="post in posts" :key="post.id" class="post-card">
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
</style>