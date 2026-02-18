<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { useRouter, useRoute } from 'vue-router';
import '@/assets/css/lab-editor.css';
import CodeMirror from 'vue-codemirror6';
import { html } from '@codemirror/lang-html';
import { css } from '@codemirror/lang-css';
import { javascript } from '@codemirror/lang-javascript';
import { oneDark } from '@codemirror/theme-one-dark';
import { basicSetup } from 'codemirror';

const router = useRouter();
const route = useRoute();

const snippetSlug = computed(() => route.params.slug);
const isEditMode = computed(() => !!snippetSlug.value);

// 資料狀態
const title = ref('Untitled Pen');
const description = ref('');
const htmlCode = ref('');
const cssCode = ref('');
const jsCode = ref('');
const isSaving = ref(false);

// --- CodeMirror 設定 ---
const htmlExt = [basicSetup, html(), oneDark];
const cssExt = [basicSetup, css(), oneDark];
const jsExt = [basicSetup, javascript(), oneDark];

// 載入舊資料 (透過 slug)
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
    alert('找不到該作品');
    router.push('/lab');
  }
};

// 即時預覽 srcdoc
const srcDoc = computed(() => {
  return `
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="UTF-8" />
        <style>
          html, body { margin: 0; padding: 0; width: 100%; min-height: 100vh; background-color: #fff; }
          ${cssCode.value}
        </style>
      </head>
      <body>
        ${htmlCode.value}
        <script>
          try { ${jsCode.value} } catch (err) { console.error('Runtime Error:', err); }
        <\/script>
      </body>
    </html>
  `;
});

// 儲存或更新
const saveSnippet = async () => {
  if (!title.value.trim()) return alert('請輸入標題');
  isSaving.value = true;
  const payload = {
    title: title.value,
    description: description.value || '在 Code Sandbox 中創造',
    html_code: htmlCode.value,
    css_code: cssCode.value,
    js_code: jsCode.value,
    is_published: true
  };
  try {
    if (isEditMode.value) {
      await axios.put(`/api/snippets/${snippetSlug.value}`, payload);
      alert('作品已更新！');
    } else {
      await axios.post('/api/snippets', payload);
      alert('作品儲存成功！');
    }
    router.push('/lab');
  } catch (error) {
    alert('操作失敗，請確認資料庫欄位');
  } finally {
    isSaving.value = false;
  }
};

onMounted(fetchOldData);
</script>

<template>
  <div class="editor-container">
    <header class="editor-header">
      <div class="header-left">
        <button class="btn-back" @click="router.push('/lab')">
          <i class="fa-solid fa-chevron-left"></i>
        </button>
        <div class="meta-inputs">
          <input v-model="title" type="text" placeholder="標題..." class="input-title" />
          <input v-model="description" type="text" placeholder="描述..." class="input-desc" />
        </div>
      </div>
      <button class="btn-save" @click="saveSnippet" :disabled="isSaving">
        <i class="fa-solid" :class="isSaving ? 'fa-spinner fa-spin' : (isEditMode ? 'fa-save' : 'fa-cloud-arrow-up')"></i>
        {{ isEditMode ? 'Update Pen' : 'Save Pen' }}
      </button>
    </header>

    <div class="workspace">
      <div class="code-panel">
        <div class="editor-section">
          <div class="section-header html-label"><i class="fa-brands fa-html5"></i> HTML</div>
          <CodeMirror
            v-model="htmlCode"
            :extensions="htmlExt"
            class="cm-container"
          />
        </div>
        <div class="editor-section">
          <div class="section-header css-label"><i class="fa-brands fa-css3-alt"></i> CSS</div>
          <CodeMirror
            v-model="cssCode"
            :extensions="cssExt"
            class="cm-container"
          />
        </div>
        <div class="editor-section">
          <div class="section-header js-label"><i class="fa-brands fa-js"></i> JS</div>
          <CodeMirror
            v-model="jsCode"
            :extensions="jsExt"
            class="cm-container"
          />
        </div>
      </div>

      <div class="preview-panel">
        <div class="preview-header">Result</div>
        <iframe
          :srcdoc="srcDoc"
          sandbox="allow-forms allow-scripts allow-modals allow-same-origin"
        ></iframe>
      </div>
    </div>
  </div>
</template>