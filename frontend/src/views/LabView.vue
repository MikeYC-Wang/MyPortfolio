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
          body { margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; background: #fff; }
          /* 插入使用者 CSS */
          ${code.css_code}
        </style>
        <!-- 確保 iframe 內可以運行 Three.js 等大型庫 -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"><\/script>
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
    <!-- 標題：套用主題顏色 -->
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
  color: var(--text-color); /* 使用全域文字色 */
}

/* 標題樣式 */
.page-title { 
  text-align: center; 
  margin-bottom: 2rem; 
  font-size: 2.5rem;
  
  /* 預設為 Dark 模式的亮藍色 */
  color: #00f3ff; 
  text-shadow: 0 0 10px #00f3ff; 
}

/* 針對 Light 模式修正標題顏色 */
.theme-light .page-title {
  /* 👇 關鍵修正：Light 模式下使用深色文字 */
  color: var(--text-color); /* 改為深咖啡色 */
  text-shadow: 0 0 10px rgba(93, 64, 55, 0.3); /* 陰影也改為深咖啡色系 */
}

.grid { 
  display: grid; 
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
  gap: 2rem; 
}

.lab-card {
  /* 使用全域卡片變數 */
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--card-border);
  box-shadow: var(--card-shadow);
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
}
.lab-card:hover { 
  transform: translateY(-5px); 
  box-shadow: var(--card-hover-shadow);
}

.preview-box {
  width: 100%;
  height: 200px;
  background: var(--nav-bg); /* 使用較深的導覽列顏色當作預覽區背景 */
  border-bottom: 1px solid var(--card-border);
}
iframe { 
  width: 100%; 
  height: 100%; 
  pointer-events: none; 
}

.info { padding: 1rem; }
.info h3 { 
  margin: 0 0 0.5rem 0; 
  /* 實驗室卡片標題也應該用漸層 */
  background: var(--gradient-text);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: inline-block;
}
.info p { font-size: 0.9rem; color: var(--link-color); margin: 0; }
</style>