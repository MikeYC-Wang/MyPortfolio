<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
// import axios from 'axios';
import axios from '@/api';
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-dark.css';

const route = useRoute();
const router = useRouter();
const post = ref<any>(null);
const loading = ref(true);

const escapeHtml = (unsafe: string): string => {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
};

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str: string, lang: string): string {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return '<pre class="hljs"><code>' +
               hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
               '</code></pre>';
      } catch (__) {}
    }
    return '<pre class="hljs"><code>' + escapeHtml(str) + '</code></pre>';
  }
});

onMounted(async () => {
  try {
    const res = await axios.get(`/api/posts/${route.params.id}`);
    post.value = res.data;
  } catch (error) {
    console.error('文章讀取失敗', error);
    router.push('/blog');
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="post-detail-container">
    <div v-if="loading" class="loading-state">
      <i class="fa-solid fa-spinner fa-spin"></i> Loading...
    </div>
    
    <article v-else-if="post" class="markdown-body">
      <RouterLink to="/blog" class="back-link">
         <i class="fa-solid fa-arrow-left"></i> 回列表
      </RouterLink>

      <div class="post-header">
        <h1>{{ post.title }}</h1>
      </div>
      
      <img 
        v-if="post.cover_image" 
        :src="post.cover_image.startsWith('http') ? post.cover_image : `http://127.0.0.1:8000${post.cover_image}`" 
        class="main-cover" 
      />

      <div class="content" v-html="md.render(post.content || '')"></div>
    </article>

    <div v-else class="error-state">
      文章載入錯誤或不存在。
    </div>
  </div>
</template>

<style scoped>
.post-detail-container { 
  max-width: 800px; 
  margin: 0 auto; 
  padding: 4rem 2rem; 
  color: var(--text-color);
  position: relative; /* 關鍵：讓絕對定位參考此容器 */
  z-index: 10; 
  min-height: 80vh;
}

.loading-state, .error-state {
  text-align: center;
  font-size: 1.5rem;
  margin-top: 50px;
  color: var(--link-color);
}

.post-header { margin-bottom: 2rem; text-align: center; margin-top: 1rem; } /* 增加一點 margin-top 避開按鈕 */
h1 { font-size: 2.5rem; margin-bottom: 1rem; color: var(--text-color); }
.main-cover { width: 100%; border-radius: 12px; margin-bottom: 3rem; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }

/* ✨ 修改後的按鈕樣式 */
.back-link { 
  position: absolute; /* 絕對定位 */
  top: 20px;          /* 距離容器頂部 20px */
  left: 20px;         /* 距離容器左邊 20px */
  
  display: inline-flex; 
  align-items: center; 
  gap: 5px; 
  color: var(--link-color); 
  text-decoration: none; 
  font-size: 0.9rem; 
  transition: 0.3s;
}

.back-link:hover { color: var(--link-active); transform: translateX(-5px); }

/* RWD: 手機版如果太窄，讓按鈕回到正常流向，不然會蓋到標題 */
@media (max-width: 600px) {
  .back-link {
    position: static;
    display: block;
    margin-bottom: 10px;
  }
}

:deep(.content) { line-height: 1.8; font-size: 1.1rem; }
:deep(h1), :deep(h2), :deep(h3) { margin-top: 2rem; margin-bottom: 1rem; color: var(--link-active); }
:deep(p) { margin-bottom: 1.5rem; color: var(--text-color); opacity: 0.9; }
:deep(pre) { background: #282c34; padding: 1.5rem; border-radius: 8px; overflow-x: auto; margin: 1.5rem 0; }
:deep(code) { font-family: 'Fira Code', monospace; }
:deep(a) { color: #58a6ff; text-decoration: none; }
:deep(a:hover) { text-decoration: underline; }
:deep(ul), :deep(ol) { padding-left: 1.5rem; margin-bottom: 1.5rem; }
:deep(li) { margin-bottom: 0.5rem; }
:deep(blockquote) { border-left: 4px solid var(--link-active); padding-left: 1rem; color: #8b949e; margin: 1.5rem 0; }
:deep(img) { max-width: 100%; border-radius: 8px; }
</style>