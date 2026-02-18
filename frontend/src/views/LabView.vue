<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import '@/assets/css/lab.css';

interface Snippet {
  id: number;
  title: string;
  description: string;
  html_code: string;
  css_code: string;
  js_code: string;
}

const snippets = ref<Snippet[]>([]);
const isLoading = ref(true);

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

// 產生預覽內容 (這部分的 CSS 必須寫在字串裡，因為是塞給 iframe 的)
const getSrcDoc = (snippet: Snippet) => {
  return `
    <html>
      <head>
        <style>
          /* 預覽視窗強制深色背景，讓特效比較明顯 */
          body { 
            margin: 0; 
            overflow: hidden; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            background: #1e1e1e; 
            color: #fff; 
            font-family: sans-serif;
          }
          /* 使用者自訂 CSS */
          ${snippet.css_code}
        </style>
      </head>
      <body>
        ${snippet.html_code}
        <script>
          /* 使用者自訂 JS */
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
  alert('即將前往編輯器頁面 (功能開發中)');
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
      <div v-for="item in snippets" :key="item.id" class="snippet-card">
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
            <span class="tag">HTML</span>
            <span class="tag">CSS</span>
            <span class="tag">JS</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>