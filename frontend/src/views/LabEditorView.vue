<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { useRouter, useRoute } from 'vue-router';
import '@/assets/css/lab-editor.css';

const router = useRouter();
const route = useRoute();

// 判斷當前是新增還是編輯 (從路由參數取得 slug)
const snippetSlug = computed(() => route.params.slug);
const isEditMode = computed(() => !!snippetSlug.value);

// 資料狀態
const title = ref('Untitled Pen');
const description = ref(''); 
const htmlCode = ref(''); 
const cssCode = ref('');  
const jsCode = ref('');   
const isSaving = ref(false);

// 1. 如果是編輯模式，載入舊資料 (透過 slug 查詢)
const fetchOldData = async () => {
  if (!isEditMode.value) return;
  try {
    const res = await axios.get(`/api/snippets/${snippetSlug.value}`);
    title.value = res.data.title;
    description.value = res.data.description;
    htmlCode.value = res.data.html_code;
    cssCode.value = res.data.css_code;
    jsCode.value = res.data.js_code;
  } catch (error) {
    console.error('載入作品失敗', error);
    alert('找不到該作品，或作品連結已失效');
    router.push('/lab');
  }
};

// 即時預覽：將三種代碼組合成完整的 HTML
const srcDoc = computed(() => {
  return `
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <style>
          /* 預設 CSS Reset */
          html, body { 
            margin: 0; 
            padding: 0; 
            width: 100%; 
            min-height: 100vh; 
            background-color: transparent; 
          }
          ${cssCode.value}
        </style>
      </head>
      <body>
        ${htmlCode.value}
        <script>
          try { 
            ${jsCode.value} 
          } catch (err) { 
            console.error('Runtime Error:', err); 
          }
        <\/script>
      </body>
    </html>
  `;
});

// 2. 儲存或更新作品
const saveSnippet = async () => {
  if (!title.value.trim()) {
    alert('請輸入專案標題！');
    return;
  }
  
  isSaving.value = true;
  const payload = {
    title: title.value,
    description: description.value || '在 Code Playground 中創造',
    html_code: htmlCode.value,
    css_code: cssCode.value,
    js_code: jsCode.value,
    is_published: true
  };

  try {
    if (isEditMode.value) {
      // 編輯模式：呼叫 PUT 並帶上 slug
      await axios.put(`/api/snippets/${snippetSlug.value}`, payload);
      alert('作品已成功更新！');
    } else {
      // 新增模式：呼叫 POST (後端會自動產生新 slug)
      await axios.post('/api/snippets', payload);
      alert('作品已儲存成功！');
    }
    // 儲存成功後跳轉回列表頁
    router.push('/lab');
  } catch (error) {
    console.error('儲存失敗', error);
    alert('操作失敗，請稍後再試。');
  } finally {
    isSaving.value = false;
  }
};

// 初始化時嘗試抓取資料
onMounted(fetchOldData);
</script>

<template>
  <div class="editor-container">
    <header class="editor-header">
      <div class="header-left">
        <button class="btn-back" @click="router.push('/lab')" title="返回列表">
          <i class="fa-solid fa-chevron-left"></i>
        </button>
        <div class="meta-inputs">
          <input v-model="title" type="text" placeholder="輸入標題..." class="input-title" />
          <input v-model="description" type="text" placeholder="新增作品描述..." class="input-desc" />
        </div>
      </div>
      
      <button class="btn-save" @click="saveSnippet" :disabled="isSaving">
        <span v-if="isSaving"><i class="fa-solid fa-spinner fa-spin"></i> Saving...</span>
        <span v-else>
          <i class="fa-solid" :class="isEditMode ? 'fa-save' : 'fa-cloud-arrow-up'"></i> 
          {{ isEditMode ? 'Update Pen' : 'Save Pen' }}
        </span>
      </button>
    </header>

    <div class="workspace">
      <div class="code-panel">
        <div class="editor-section">
          <div class="section-header html-label">
            <i class="fa-brands fa-html5"></i> HTML
          </div>
          <textarea v-model="htmlCode" class="code-input" spellcheck="false" placeholder=""></textarea>
        </div>
        
        <div class="editor-section">
          <div class="section-header css-label">
            <i class="fa-brands fa-css3-alt"></i> CSS
          </div>
          <textarea v-model="cssCode" class="code-input" spellcheck="false" placeholder="/* CSS */"></textarea>
        </div>
        
        <div class="editor-section">
          <div class="section-header js-label">
            <i class="fa-brands fa-js"></i> JS
          </div>
          <textarea v-model="jsCode" class="code-input" spellcheck="false" placeholder="// JavaScript"></textarea>
        </div>
      </div>

      <div class="preview-panel">
        <div class="preview-header">Result</div>
        <iframe 
          :srcdoc="srcDoc" 
          title="preview" 
          sandbox="allow-forms allow-scripts allow-modals"
        ></iframe>
      </div>
    </div>
  </div>
</template>