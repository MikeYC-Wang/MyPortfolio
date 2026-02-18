<script setup lang="ts">
import { ref, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
// 引入編輯器專用樣式
import '@/assets/css/lab-editor.css';

const router = useRouter();

// 資料狀態：預設為空字串，讓使用者從零開始
const title = ref('Untitled Pen');
const description = ref(''); 
const htmlCode = ref(''); 
const cssCode = ref('');  
const jsCode = ref('');   
const isSaving = ref(false);

// 即時預覽：將三種代碼組合成完整的 HTML
const srcDoc = computed(() => {
  return `
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <style>
          html {
            box-sizing: border-box;
          }
          *, *:before, *:after {
            box-sizing: inherit;
          }
          body {
            margin: 0;
            padding: 0;
            width: 100%;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
          }
          /* 使用者輸入的 CSS */
          ${cssCode.value}
        </style>
      </head>
      <body>
        ${htmlCode.value}
        <script>
          try {
            ${jsCode.value}
          } catch (err) {
            console.error(err);
          }
        <\/script>
      </body>
    </html>
  `;
});

// 儲存作品
const saveSnippet = async () => {
  if (!title.value.trim()) {
    alert('請輸入專案標題！');
    return;
  }
  
  isSaving.value = true;
  try {
    // 呼叫後端 API 儲存
    await axios.post('/api/snippets', {
      title: title.value,
      description: description.value || 'Created in Code Playground',
      html_code: htmlCode.value,
      css_code: cssCode.value,
      js_code: jsCode.value,
      is_published: true
    });
    
    alert('🎉 作品儲存成功！');
    router.push('/lab'); // 儲存後回到列表
  } catch (error) {
    console.error('儲存失敗', error);
    alert('儲存失敗，請檢查網路或後端狀態。');
  } finally {
    isSaving.value = false;
  }
};
</script>

<template>
  <div class="editor-container">
    <header class="editor-header">
      <div class="header-left">
        <button class="btn-back" @click="router.push('/lab')" title="返回列表">
          <i class="fa-solid fa-chevron-left"></i>
        </button>
        <div class="meta-inputs">
          <input v-model="title" type="text" placeholder="輸入專案標題..." class="input-title" />
        </div>
      </div>
      
      <button class="btn-save" @click="saveSnippet" :disabled="isSaving">
        <span v-if="isSaving"><i class="fa-solid fa-spinner fa-spin"></i> Saving...</span>
        <span v-else><i class="fa-solid fa-cloud-arrow-up"></i> Save Pen</span>
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
        <iframe :srcdoc="srcDoc" title="preview" sandbox="allow-scripts"></iframe>
      </div>
    </div>
  </div>
</template>