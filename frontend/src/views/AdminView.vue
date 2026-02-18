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
const posts = ref<Post[]>([]);
const currentPostId = ref<number | null>(null);
const isSubmitting = ref(false);
const isUploading = ref(false);
const isSidebarOpen = ref(true);

// 編輯器參照 (用來插入文字)
const textareaRef = ref<HTMLTextAreaElement | null>(null);

// 表單資料
const postForm = ref({
  title: '',
  cover_image: '',
  content: '',
  is_published: true
});

// --- 功能 3: Markdown 工具列輔助 ---
const insertMarkdown = (type: string) => {
  if (!textareaRef.value) return;
  
  const textarea = textareaRef.value;
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const text = postForm.value.content;
  const selectedText = text.substring(start, end);
  
  let insertText = '';
  let newCursorPos = 0;

  switch (type) {
    case 'bold':
      insertText = `**${selectedText || '粗體文字'}**`;
      newCursorPos = start + 2;
      break;
    case 'italic':
      insertText = `*${selectedText || '斜體文字'}*`;
      newCursorPos = start + 1;
      break;
    case 'h1':
      insertText = `# ${selectedText || '大標題'}\n`;
      newCursorPos = start + 2;
      break;
    case 'h2':
      insertText = `## ${selectedText || '次標題'}\n`;
      newCursorPos = start + 3;
      break;
    case 'code':
      insertText = `\`${selectedText || '程式碼'}\``;
      newCursorPos = start + 1;
      break;
    case 'blockcode':
      insertText = `\n\`\`\`javascript\n${selectedText || 'console.log("Code");'}\n\`\`\`\n`;
      newCursorPos = start + 14;
      break;
    case 'link':
      insertText = `[${selectedText || '連結文字'}](url)`;
      newCursorPos = start + 1;
      break;
    case 'image':
      insertText = `![圖片描述](${selectedText || '圖片網址'})`;
      newCursorPos = start + 2;
      break;
    case 'hr':
      insertText = `\n---\n`;
      newCursorPos = start + 5;
      break;
  }

  // 插入文字
  postForm.value.content = text.substring(0, start) + insertText + text.substring(end);
  
  // 重新聚焦並移動游標 (稍微延遲以確保 DOM 更新)
  setTimeout(() => {
    textarea.focus();
    textarea.setSelectionRange(start + insertText.length, start + insertText.length);
  }, 0);
};

// --- API 操作 ---
const fetchPosts = async () => {
  try {
    const res = await axios.get('/api/posts');
    posts.value = res.data;
  } catch (error) {
    console.error('載入文章列表失敗', error);
  }
};

const initCreateMode = () => {
  currentPostId.value = null;
  postForm.value = {
    title: '',
    cover_image: '',
    content: '# 在這裡開始寫新文章...',
    is_published: true
  };
};

const selectPostToEdit = (post: Post) => {
  currentPostId.value = post.id;
  postForm.value = {
    title: post.title,
    cover_image: post.cover_image || '',
    content: post.content,
    is_published: post.is_published
  };
  if (window.innerWidth < 768) {
    isSidebarOpen.value = false;
  }
};

const handleDelete = async (id: number) => {
  if (!confirm('確定要刪除這篇文章嗎？此動作無法復原！')) return;
  try {
    await axios.delete(`/api/posts/${id}`);
    alert('刪除成功');
    if (currentPostId.value === id) initCreateMode();
    fetchPosts();
  } catch (error) {
    console.error(error);
    alert('刪除失敗');
  }
};

const submitPost = async () => {
  if (!postForm.value.title || !postForm.value.content) {
    alert('標題與內容不能為空！');
    return;
  }
  isSubmitting.value = true;
  try {
    if (currentPostId.value) {
      await axios.put(`/api/posts/${currentPostId.value}`, postForm.value);
      alert('文章更新成功！');
    } else {
      await axios.post('/api/posts', postForm.value);
      alert('新文章發布成功！');
      initCreateMode();
    }
    fetchPosts();
  } catch (error) {
    console.error(error);
    alert('操作失敗，請檢查後端連線');
  } finally {
    isSubmitting.value = false;
  }
};

// --- 功能 3 & 4: 上傳限制與成功提示 ---
const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    const file = target.files[0];
    
    // 1. 檢查檔案類型
    const validTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/gif'];
    if (!validTypes.includes(file.type)) {
      alert('格式錯誤！僅允許上傳 JPG, PNG 或 GIF 圖片。');
      target.value = ''; // 清空選擇
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    isUploading.value = true;
    try {
      const res = await axios.post('/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      // 強制加上後端網址
      postForm.value.cover_image = `http://127.0.0.1:8000${res.data.url}`;
      
      // 2. 成功提示
      alert('圖片上傳成功！');
      
    } catch (error) {
      console.error('上傳失敗', error);
      alert('圖片上傳失敗');
    } finally {
      isUploading.value = false;
    }
  }
};

// --- Markdown 設定 ---
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
    </aside>

    <button 
      class="toggle-sidebar-btn" 
      @click="isSidebarOpen = !isSidebarOpen"
      :style="{ left: isSidebarOpen ? '280px' : '0' }"
    >
      <i class="fa-solid" :class="isSidebarOpen ? 'fa-chevron-left' : 'fa-chevron-right'"></i>
    </button>

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
          <div class="pane-header">
            <span class="pane-label">Markdown 編輯區</span>
            <div class="toolbar">
              <button @click="insertMarkdown('h1')" title="大標題">H1</button>
              <button @click="insertMarkdown('h2')" title="次標題">H2</button>
              <button @click="insertMarkdown('bold')" title="粗體"><i class="fa-solid fa-bold"></i></button>
              <button @click="insertMarkdown('italic')" title="斜體"><i class="fa-solid fa-italic"></i></button>
              <button @click="insertMarkdown('code')" title="程式碼"><i class="fa-solid fa-code"></i></button>
              <button @click="insertMarkdown('blockcode')" title="程式碼區塊"><i class="fa-solid fa-file-code"></i></button>
              <button @click="insertMarkdown('link')" title="連結"><i class="fa-solid fa-link"></i></button>
              <button @click="insertMarkdown('image')" title="插入圖片"><i class="fa-solid fa-image"></i></button>
              <button @click="insertMarkdown('hr')" title="分隔線">HR</button>
            </div>
          </div>
          <textarea 
            ref="textareaRef"
            v-model="postForm.content" 
            class="markdown-input"
            placeholder="請輸入內容..."
          ></textarea>
        </div>

        <div class="preview-pane">
          <div class="pane-header">
            <span class="pane-label">即時預覽</span>
          </div>
          <div class="markdown-body content-preview" v-html="renderedContent"></div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* --- 修正 1: 全面改用 CSS 變數以支援淺色模式 --- */
.admin-wrapper {
  display: flex;
  height: calc(100vh - 80px);
  overflow: hidden;
  background-color: var(--nav-bg); /* 改用變數 */
  position: relative;
  color: var(--text-color); /* 改用變數 */
}

/* --- 左側邊欄 --- */
.sidebar {
  width: 280px;
  background: var(--card-bg); /* 改用變數 */
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  flex-shrink: 0;
}

.sidebar.closed {
  width: 0;
  overflow: hidden;
  border: none;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
}

.sidebar-header h2 { margin: 0 0 15px 0; font-size: 1.2rem; color: var(--text-color); }

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
  background: rgba(0,0,0,0.1); /* 微調背景 */
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: 0.2s;
}

.post-item:hover { background: var(--btn-hover); }
.post-item.active { 
  background: var(--btn-hover); 
  border-color: #007bff; 
  box-shadow: 0 0 10px rgba(0, 123, 255, 0.2);
}

.post-info { display: flex; flex-direction: column; overflow: hidden; }
.post-title { 
  color: var(--text-color); 
  font-weight: bold; 
  white-space: nowrap; 
  overflow: hidden; 
  text-overflow: ellipsis; 
}
.post-id { color: var(--link-color); font-size: 0.8rem; }

.btn-delete {
  background: transparent;
  border: none;
  color: var(--link-color);
  cursor: pointer;
  padding: 5px;
  transition: 0.2s;
}
.btn-delete:hover { color: #ff4d4d; }

.toggle-sidebar-btn {
  position: absolute;
  top: 50%;
  width: 20px;
  height: 40px;
  background: var(--card-bg); /* 改用變數 */
  border: 1px solid var(--border-color);
  border-left: none;
  border-radius: 0 4px 4px 0;
  color: var(--text-color);
  cursor: pointer;
  z-index: 100;
  transition: left 0.3s ease;
}

/* --- 右側編輯區 --- */
.editor-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  min-width: 0;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions h1 { margin: 0; font-size: 1.5rem; color: var(--text-color); display: flex; align-items: center; gap: 10px; }

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
.publish-btn.update-mode { background: #e0a800; }
.publish-btn.update-mode:hover { background: #c69500; }

.form-grid { margin-bottom: 15px; display: flex; flex-direction: column; gap: 15px; }

.title-input {
  width: 100%;
  padding: 15px;
  font-size: 1.5rem;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  color: var(--text-color);
  border-radius: 8px;
  box-sizing: border-box;
}

.upload-group { display: flex; align-items: center; gap: 15px; }
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
}
.upload-btn:hover { background: var(--btn-hover); }

.file-input { display: none; }
.url-input { 
  flex-grow: 1; 
  padding: 10px; 
  background: var(--card-bg); 
  border: 1px solid var(--border-color); 
  color: var(--text-color); 
  border-radius: 6px; 
}

.image-preview { height: 40px; border-radius: 4px; overflow: hidden; border: 1px solid var(--border-color); }
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
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.pane-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0,0,0,0.1);
  border-bottom: 1px solid var(--border-color);
  padding: 5px 10px;
}

.pane-label {
  font-size: 0.85rem;
  color: var(--link-color);
  font-weight: bold;
}

/* 工具列樣式 */
.toolbar {
  display: flex;
  gap: 5px;
}

.toolbar button {
  background: transparent;
  border: 1px solid transparent;
  color: var(--link-color);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  transition: 0.2s;
}
.toolbar button:hover {
  background: var(--btn-hover);
  color: var(--link-active);
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
  background: var(--card-bg); /* 確保背景色跟著主題 */
}

/* 預覽區樣式 - 確保 Markdown 有顏色 */
:deep(.content-preview) { line-height: 1.8; }
:deep(h1), :deep(h2) { 
  border-bottom: 1px solid var(--border-color); 
  padding-bottom: 0.5rem; 
  margin-bottom: 1rem; 
  color: var(--link-active); 
}
:deep(pre) { background: #282c34; padding: 1rem; border-radius: 8px; overflow-x: auto; margin: 10px 0; }
:deep(code) { font-family: 'Fira Code', monospace; }
:deep(img) { max-width: 100%; border-radius: 8px; margin: 10px 0; }
:deep(blockquote) { border-left: 4px solid var(--link-active); padding-left: 1rem; color: var(--link-color); }
:deep(ul), :deep(ol) { padding-left: 20px; }
:deep(a) { color: #58a6ff; text-decoration: none; }

/* RWD */
@media (max-width: 768px) {
  .editor-area { grid-template-columns: 1fr; grid-template-rows: 1fr 1fr; }
  .sidebar { position: absolute; height: 100%; z-index: 50; }
  .sidebar.closed { transform: translateX(-100%); width: 280px; }
}
</style>