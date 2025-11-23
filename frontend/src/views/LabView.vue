<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

interface CodeSnippet {
  id: number;
  title: string;
  description: string;
  html_code: string;
  css_code: string;
  js_code: string;
}

const snippets = ref<CodeSnippet[]>([]);

// 核心魔法：將 HTML/CSS/JS 組合成一個完整的網頁
const generatePreview = (code: CodeSnippet) => {
  return `
    <html>
      <head>
        <style>
          body { margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; }
          /* 插入使用者 CSS */
          ${code.css_code}
        </style>
      </head>
      <body>
        <!-- 插入使用者 HTML -->
        ${code.html_code}

        <script>
          // 插入使用者 JS
          try {
            ${code.js_code}
          } catch(e) { console.error(e); }
        <\/script>
      </body>
    </html>
  `;
};

onMounted(async () => {
  try {
    const res = await axios.get('/api/snippets');
    snippets.value = res.data;
  } catch (error) {
    console.error('無法取得特效資料', error);
  }
});
</script>

<template>
  <div class="lab-container">
    <h1 class="page-title">🧪 特效實驗室</h1>
    
    <div class="grid">
      <div v-for="item in snippets" :key="item.id" class="lab-card">
        <!-- 預覽視窗 (iframe) -->
        <div class="preview-box">
          <iframe 
            :srcdoc="generatePreview(item)" 
            frameborder="0"
            sandbox="allow-scripts" 
            title="preview"
          ></iframe>
        </div>
        
        <!-- 說明區 -->
        <div class="info">
          <h3>{{ item.title }}</h3>
          <p>{{ item.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.lab-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
  color: white;
}
.page-title { text-align: center; color: #00f3ff; margin-bottom: 2rem; text-shadow: 0 0 10px #00f3ff; }

.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }

.lab-card {
  background: rgba(44, 44, 44, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.3s;
}
.lab-card:hover { transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0, 243, 255, 0.2); }

.preview-box {
  width: 100%;
  height: 200px;
  background: #000;
  border-bottom: 1px solid #333;
}
iframe { width: 100%; height: 100%; pointer-events: none; /* 讓滑鼠可以直接穿透，如果你希望互動可以拿掉這行 */ }

.info { padding: 1rem; }
.info h3 { margin: 0 0 0.5rem 0; color: #42b883; }
.info p { font-size: 0.9rem; color: #aaa; margin: 0; }
</style>