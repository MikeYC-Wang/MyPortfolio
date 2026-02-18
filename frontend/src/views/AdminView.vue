<script setup lang="ts">
import { ref, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-dark.css';

const router = useRouter();

// 表單資料
const postForm = ref({
  title: '',
  cover_image: '', // 這裡會存上傳成功後的圖片網址
  content: '# 在這裡開始寫你的文章...',
  is_published: true
});

const isSubmitting = ref(false);
const isUploading = ref(false); // 上傳狀態

// --- 圖片上傳處理邏輯 ---
const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    const file = target.files[0];
    
    // 建立 FormData 物件
    const formData = new FormData();
    formData.append('file', file);

    isUploading.value = true;
    try {
      // 傳送給後端新的上傳 API
      const res = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      postForm.value.cover_image = `http://127.0.0.1:8000${res.data.url}`;
    } catch (error) {
      console.error('上傳失敗', error);
      alert('圖片上傳失敗，請檢查後端是否啟動');
    } finally {
      isUploading.value = false;
    }
  }
};

// --- Markdown 解析設定 (保持不變) ---
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

// 即時預覽內容
const renderedContent = computed(() => {
  return md.render(postForm.value.content);
});

// --- 送出文章 ---
const submitPost = async () => {
  if (!postForm.value.title || !postForm.value.content) {
    alert('標題與內容不能為空！');
    return;
  }

  isSubmitting.value = true;
  try {
    // 呼叫後端 API
    await axios.post('/api/posts', postForm.value);
    
    alert('🎉 文章發布成功！');
    router.push('/blog');
  } catch (error) {
    console.error(error);
    alert('發布失敗，請檢查後端');
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<template>
  <div class="admin-container">
    <div class="header-actions">
      <h1><i class="fa-solid fa-user-secret"></i> 後台管理中心</h1>
      <button @click="submitPost" :disabled="isSubmitting || isUploading" class="publish-btn">
        <span v-if="isSubmitting"><i class="fa-solid fa-spinner fa-spin"></i> 發布中...</span>
        <span v-else><i class="fa-solid fa-paper-plane"></i> 發布文章</span>
      </button>
    </div>

    <div class="input-group">
      <input v-model="postForm.title" type="text" placeholder="請輸入文章標題..." class="title-input" />
    </div>

    <div class="input-group upload-group">
      <label class="upload-btn">
        <i class="fa-solid fa-cloud-arrow-up"></i> 
        <span v-if="isUploading">上傳中...</span>
        <span v-else>上傳封面圖片</span>
        <input type="file" @change="handleFileUpload" accept="image/*" class="file-input" />
      </label>

      <div v-if="postForm.cover_image" class="image-preview">
        <img :src="postForm.cover_image" alt="Cover Preview" />
        <span class="preview-label">目前封面</span>
      </div>
    </div>

    <div class="editor-area">
      <div class="editor-pane">
        <div class="pane-label">Markdown 編輯區</div>
        <textarea v-model="postForm.content" class="markdown-input"></textarea>
      </div>

      <div class="preview-pane">
        <div class="pane-label">即時預覽</div>
        <div class="markdown-body content-preview" v-html="renderedContent"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  height: calc(100vh - 100px);
  display: flex;
  flex-direction: column;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

h1 { margin: 0; color: var(--text-color); }

.publish-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 10px 24px;
  font-size: 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: 0.3s;
  font-weight: bold;
}
.publish-btn:hover { background: #218838; transform: translateY(-2px); }
.publish-btn:disabled { background: #555; cursor: not-allowed; }

.input-group { margin-bottom: 1rem; }

.title-input {
  width: 100%;
  padding: 15px;
  font-size: 1.5rem;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  color: var(--text-color);
  border-radius: 8px;
  box-sizing: border-box;
}

/* --- 上傳按鈕樣式 --- */
.upload-group {
  display: flex;
  align-items: center;
  gap: 20px;
  background: var(--card-bg);
  padding: 10px;
  border-radius: 8px;
  border: 1px solid var(--card-border);
}

.upload-btn {
  background: var(--btn-bg);
  color: var(--text-color);
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--border-color);
  transition: 0.2s;
}
.upload-btn:hover { background: var(--btn-hover); }

.file-input { display: none; } /* 隱藏原本醜醜的 input */

.image-preview {
  position: relative;
  height: 50px;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid var(--card-border);
  display: flex;
  align-items: center;
}

.image-preview img {
  height: 100%;
  object-fit: cover;
}

.preview-label {
  font-size: 0.8rem;
  margin-left: 10px;
  color: var(--link-color);
}

/* --- 雙欄編輯區 --- */
.editor-area {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  flex-grow: 1;
  min-height: 0;
}

.editor-pane, .preview-pane {
  display: flex;
  flex-direction: column;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  overflow: hidden;
}

.pane-label {
  background: rgba(0,0,0,0.2);
  padding: 8px 15px;
  font-size: 0.85rem;
  color: var(--link-color);
  border-bottom: 1px solid var(--card-border);
  font-weight: bold;
}

.markdown-input {
  flex-grow: 1;
  background: transparent;
  border: none;
  color: var(--text-color);
  padding: 20px;
  font-family: 'Fira Code', monospace;
  font-size: 1rem;
  line-height: 1.6;
  resize: none;
  outline: none;
}

.content-preview {
  flex-grow: 1;
  padding: 20px;
  overflow-y: auto;
  color: var(--text-color);
}

:deep(.content-preview) { line-height: 1.8; }
:deep(h1), :deep(h2), :deep(h3) { margin-top: 1rem; margin-bottom: 1rem; color: var(--link-active); }
:deep(pre) { background: #282c34; padding: 1rem; border-radius: 8px; overflow-x: auto; }
:deep(code) { font-family: 'Fira Code', monospace; }
:deep(p) { margin-bottom: 1rem; }
:deep(img) { max-width: 100%; border-radius: 8px; }
</style>