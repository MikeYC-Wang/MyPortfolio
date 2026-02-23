<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
// import axios from 'axios';
import axios from '@/api';
import '@/assets/css/lab.css';

// 定義資料結構，加入 slug
interface Snippet {
  id: number;
  slug: string; // 隨機碼欄位
  title: string;
  description: string;
  html_code: string;
  css_code: string;
  js_code: string;
}

const snippets = ref<Snippet[]>([]);
const isLoading = ref(true);
const router = useRouter();

// 載入列表
const fetchSnippets = async () => {
  try {
    const res = await axios.get('/api/snippets');
    snippets.value = res.data;
  } catch (error) {
    console.error('載入失敗', error);
  } finally {
    isLoading.value = false;
  }
};

// 產生預覽內容：加入 CSS Reset 確保小視窗預覽也能滿版
const getSrcDoc = (snippet: Snippet) => {
  return `
    <html>
      <head>
        <style>
          html, body { 
            margin: 0; 
            padding: 0; 
            width: 100%; 
            height: 100%; 
            overflow: hidden; 
            background: #1e1e1e; 
            color: #fff; 
            font-family: sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
          }
          ${snippet.css_code}
        </style>
      </head>
      <body>
        ${snippet.html_code}
        <script>
          try {
            ${snippet.js_code}
          } catch(e) {
            console.error(e);
          }
        <\/script>
      </body>
    </html>
  `;
};

// 跳轉到新增頁面
const createNewPen = () => {
  router.push('/lab/new');
};

// 跳轉到編輯頁面 (使用 slug)
const goToEdit = (slug: string) => {
  router.push(`/lab/edit/${slug}`);
};

onMounted(() => {
  fetchSnippets();
});
</script>

<template>
  <div class="playground-container">
    <div class="page-header">
      <div class="title-group">
        <i class="fa-brands fa-codepen logo-icon"></i>
        <div>
          <h1>Code Playground</h1>
          <span class="subtitle">快來分享你的創意!!!</span>
        </div>
      </div>

      <button class="btn-new-pen" @click="createNewPen">
        <i class="fa-solid fa-plus"></i> New Pen
      </button>
    </div>

    <div v-if="isLoading" class="loading">
      <i class="fa-solid fa-circle-notch fa-spin"></i> Loading Pens...
    </div>

    <div v-else class="snippets-grid">
      <div 
        v-for="item in snippets" 
        :key="item.id" 
        class="snippet-card"
        @click="goToEdit(item.slug)"
      >
        <div class="card-header">
          <div class="dots">
            <span class="dot red"></span>
            <span class="dot yellow"></span>
            <span class="dot green"></span>
          </div>
          <span class="card-title">{{ item.title }}</span>
        </div>

        <div class="iframe-wrapper">
          <iframe 
            :srcdoc="getSrcDoc(item)" 
            frameborder="0" 
            sandbox="allow-scripts"
            scrolling="no"
          ></iframe>
          <div class="overlay"></div>
        </div>

        <div class="card-info">
          <p>{{ item.description || 'No description provided.' }}</p>
          <div class="tags">
            <span class="tag tag-html">HTML</span>
            <span class="tag tag-css">CSS</span>
            <span class="tag tag-js">JS</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>