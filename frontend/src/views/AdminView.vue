<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-dark.css';

// 定義文章型別
interface Post {
  id: number;
  title: string;
  content: string;
  cover_image: string;
  is_published: boolean;
  created_at?: string;
}

const router = useRouter();

// --- 狀態變數 ---
const posts = ref<Post[]>([]); // 左側文章列表
const currentPostId = ref<number | null>(null); // 目前正在編輯的文章 ID (null 代表新增模式)
const isSubmitting = ref(false);
const isUploading = ref(false);
const isSidebarOpen = ref(true); // 手機版控制側邊欄用

// 表單資料
const postForm = ref({
  title: '',
  cover_image: '',
  content: '',
  is_published: true
});

// --- API 操作 ---

// 1. 載入文章列表
const fetchPosts = async () => {
  try {
    const res = await axios.get('/api/posts');
    posts.value = res.data;
  } catch (error) {
    console.error('載入文章列表失敗', error);
  }
};

// 2. 切換到「新增模式」
const initCreateMode = () => {
  currentPostId.value = null;
  postForm.value = {
    title: '',
    cover_image: '',
    content: '# 在這裡開始寫新文章...',
    is_published: true
  };
};

// 3. 切換到「編輯模式」
const selectPostToEdit = (post: Post) => {
  currentPostId.value = post.id;
  // 深拷貝資料到表單，以免修改時直接連動列表顯示
  postForm.value = {
    title: post.title,
    cover_image: post.cover_image || '',
    content: post.content,
    is_published: post.is_published
  };
  // 手機版點選後自動收合側邊欄
  if (window.innerWidth < 768) {
    isSidebarOpen.value = false;
  }
};

// 4. 刪除文章
const handleDelete = async (id: number) => {
  if (!confirm('確定要刪除這篇文章嗎？此動作無法復原！')) return;
  
  try {
    await axios.delete(`/api/posts/${id}`);
    alert('刪除成功');
    // 如果刪除的是當前正在編輯的文章，就重置回新增模式
    if (currentPostId.value === id) {
      initCreateMode();
    }
    fetchPosts(); // 重新整理列表
  } catch (error) {
    console.error(error);
    alert('刪除失敗');
  }
};

// 5. 送出表單 (自動判斷是新增還是更新)
const submitPost = async () => {
  if (!postForm.value.title || !postForm.value.content) {
    alert('標題與內容不能為空！');
    return;
  }

  isSubmitting.value = true;
  try {
    if (currentPostId.value) {
      // --- 更新模式 (PUT) ---
      await axios.put(`/api/posts/${currentPostId.value}`, postForm.value);
      alert('✨ 文章更新成功！');
    } else {
      // --- 新增模式 (POST) ---
      await axios.post('/api/posts', postForm.value);
      alert('🎉 新文章發布成功！');
      initCreateMode(); // 清空表單
    }
    fetchPosts(); // 更新左側列表
  } catch (error) {
    console.error(error);
    alert('操作失敗，請檢查後端連線');
  } finally {
    isSubmitting.value = false;
  }
};

// 6. 圖片上傳 (保持原本邏輯)
const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    const file = target.files[0];
    const formData = new FormData();
    formData.append('file', file);

    isUploading.value = true;
    try {
      const res = await axios.post('/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      // 強制加上後端網址，避免 Proxy 問題
      postForm.value.cover_image = `http://127.0.0.1:8000${res.data.url}`;
    } catch (error) {
      console.error('上傳失敗', error);
      alert('圖片上傳失敗');
    } finally {
      isUploading.value = false;
    }
  }
};

// --- Markdown 設定 (保持原本邏輯) ---
const escapeHtml = (unsafe: string): string => {
  return unsafe.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
};
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str: string, lang: string): string {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return '<pre class="hljs"><code>' + hljs.highlight(str, { language: lang, ignoreIllegals: true }).value + '</code></pre>';
      } catch (__) {}
    }
    return '<pre class="hljs"><code>' + escapeHtml(str) + '</code></pre>';
  }
});
const renderedContent = computed(() => md.render(postForm.value.content));

// 初始化
onMounted(() => {
  fetchPosts();
  initCreateMode();
});
</script>

<template>
  <div class="admin-wrapper">
    <aside class="sidebar" :class="{ 'closed': !isSidebarOpen }">
      <div class="sidebar-header">
        <h2>文章列表</h2>
        <button @click="initCreateMode" class="btn-new">
          <i class="fa-solid fa-plus"></i> 新增文章
        </button>
      </div>
      
      <div class="post-list">
        <div 
          v-for="post in posts" 
          :key="post.id" 
          class="post-item" 
          :class="{ active: currentPostId === post.id }"
          @click="selectPostToEdit(post)"
        >
          <div class="post-info">
            <span class="post-title">{{ post.title }}</span>
            <span class="post-id">#{{ post.id }}</span>
          </div>
          <button @click.stop="handleDelete(post.id)" class="btn-delete" title="刪除文章">
            <i class="fa-solid fa-trash"></i>
          </button>
        </div>
      </div>
      
      <button class="toggle-sidebar-btn" @click="isSidebarOpen = !isSidebarOpen">
        <i class="fa-solid" :class="isSidebarOpen ? 'fa-chevron-left' : 'fa-chevron-right'"></i>
      </button>
    </aside>

    <main class="editor-container">
      <div class="header-actions">
        <h1>
          <i class="fa-solid fa-pen-to-square"></i> 
          {{ currentPostId ? '編輯文章' : '新增文章' }}
        </h1>
        <div class="action-buttons">
          <button @click="submitPost" :disabled="isSubmitting || isUploading" class="publish-btn" :class="{ 'update-mode': currentPostId }">
            <span v-if="isSubmitting"><i class="fa-solid fa-spinner fa-spin"></i> 處理中...</span>
            <span v-else>
              <i class="fa-solid" :class="currentPostId ? 'fa-save' : 'fa-paper-plane'"></i> 
              {{ currentPostId ? '更新文章' : '發布文章' }}
            </span>
          </button>
        </div>
      </div>

      <div class="form-grid">
        <div class="input-group">
          <input v-model="postForm.title" type="text" placeholder="請輸入文章標題..." class="title-input" />
        </div>

        <div class="input-group upload-group">
          <label class="upload-btn">
            <i class="fa-solid fa-cloud-arrow-up"></i> 
            <span v-if="isUploading">上傳中...</span>
            <span v-else>上傳封面</span>
            <input type="file" @change="handleFileUpload" accept="image/*" class="file-input" />
          </label>

          <div v-if="postForm.cover_image" class="image-preview">
            <img :src="postForm.cover_image" alt="Cover Preview" />
          </div>
          <input v-else v-model="postForm.cover_image" type="text" placeholder="或貼上圖片網址..." class="url-input" />
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
    </main>
  </div>
</template>

<style scoped>
.admin-wrapper {
  display: flex;
  height: calc(100vh - 80px); /* 扣掉 Top Nav 高度 */
  overflow: hidden;
  background-color: #121212;
}

/* --- 左側邊欄 --- */
.sidebar {
  width: 280px;
  background: #1e1e1e;
  border-right: 1px solid #333;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  position: relative;
  flex-shrink: 0;
}

.sidebar.closed {
  width: 0;
  overflow: hidden;
  border: none;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #333;
}

.sidebar-header h2 { margin: 0 0 15px 0; font-size: 1.2rem; color: #fff; }

.btn-new {
  width: 100%;
  padding: 10px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  transition: 0.2s;
}
.btn-new:hover { background: #0056b3; }

.post-list {
  flex-grow: 1;
  overflow-y: auto;
  padding: 10px;
}

.post-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  background: #2d2d2d;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: 0.2s;
}

.post-item:hover { background: #383838; }
.post-item.active { 
  background: #383838; 
  border-color: #007bff; 
  box-shadow: 0 0 10px rgba(0, 123, 255, 0.2);
}

.post-info {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.post-title { 
  color: #e0e0e0; 
  font-weight: bold; 
  white-space: nowrap; 
  overflow: hidden; 
  text-overflow: ellipsis; 
}
.post-id { color: #888; font-size: 0.8rem; }

.btn-delete {
  background: transparent;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 5px;
  transition: 0.2s;
}
.btn-delete:hover { color: #ff4d4d; }

.toggle-sidebar-btn {
  position: absolute;
  right: -20px;
  top: 50%;
  width: 20px;
  height: 40px;
  background: #333;
  border: none;
  border-radius: 0 4px 4px 0;
  color: #fff;
  cursor: pointer;
  z-index: 10;
}

/* --- 右側編輯區 --- */
.editor-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  min-width: 0; /* 防止 grid 溢出 */
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions h1 { margin: 0; font-size: 1.5rem; color: #fff; display: flex; align-items: center; gap: 10px; }

.publish-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: 0.2s;
}
.publish-btn:hover { background: #218838; transform: translateY(-2px); }
.publish-btn.update-mode { background: #e0a800; } /* 更新模式改用黃色系 */
.publish-btn.update-mode:hover { background: #c69500; }

.form-grid { margin-bottom: 15px; display: flex; flex-direction: column; gap: 15px; }

.title-input {
  width: 100%;
  padding: 15px;
  font-size: 1.5rem;
  background: #2d2d2d;
  border: 1px solid #444;
  color: #fff;
  border-radius: 8px;
  box-sizing: border-box;
}

.upload-group {
  display: flex;
  align-items: center;
  gap: 15px;
}

.upload-btn {
  background: #333;
  color: #fff;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid #555;
}
.file-input { display: none; }
.url-input { 
  flex-grow: 1; 
  padding: 10px; 
  background: #2d2d2d; 
  border: 1px solid #444; 
  color: #ccc; 
  border-radius: 6px; 
}

.image-preview { height: 40px; border-radius: 4px; overflow: hidden; border: 1px solid #555; }
.image-preview img { height: 100%; }

/* --- 雙欄編輯器 --- */
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
  background: #1e1e1e;
  border: 1px solid #333;
  border-radius: 12px;
  overflow: hidden;
}

.pane-label {
  background: rgba(255,255,255,0.05);
  padding: 8px 15px;
  font-size: 0.85rem;
  color: #888;
  border-bottom: 1px solid #333;
  font-weight: bold;
}

.markdown-input {
  flex-grow: 1;
  background: transparent;
  border: none;
  color: #e0e0e0;
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
  color: #e0e0e0;
}

/* 預覽區樣式 */
:deep(.content-preview) { line-height: 1.8; }
:deep(h1), :deep(h2) { border-bottom: 1px solid #444; padding-bottom: 0.5rem; margin-bottom: 1rem; color: #fff; }
:deep(pre) { background: #282c34; padding: 1rem; border-radius: 8px; overflow-x: auto; }
:deep(code) { font-family: 'Fira Code', monospace; }
:deep(img) { max-width: 100%; border-radius: 8px; }

/* RWD */
@media (max-width: 768px) {
  .editor-area { grid-template-columns: 1fr; grid-template-rows: 1fr 1fr; }
  .sidebar { position: absolute; height: 100%; z-index: 50; }
  .sidebar.closed { transform: translateX(-100%); width: 280px; }
}
</style>