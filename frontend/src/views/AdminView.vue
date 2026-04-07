<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
// import axios from 'axios';
import axios from '@/api';
import { useRouter } from 'vue-router';
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-dark.css';
import { useToast } from 'vue-toastification';
import '@/assets/css/admin.css';
import SiteFooter from '@/components/SiteFooter.vue';

// --- 型別定義 ---
interface Post {
  id: number;
  title: string;
  content: string;
  cover_image: string;
  is_published: boolean;
  created_at?: string;
}

interface Project {
  id: number;
  title: string;
  description: string;
  tech_stack: string;
  content?: string;
}

// --- 全域狀態 ---
const router = useRouter();
const toast = useToast();
const adminMode = ref<'posts' | 'projects'>('posts');
const isSubmitting = ref(false);
const isUploading = ref(false);
const isSidebarOpen = ref(true);
const textareaRef = ref<HTMLTextAreaElement | null>(null);

// --- 文章狀態 ---
const posts = ref<Post[]>([]);
const currentPostId = ref<number | null>(null);
const postForm = ref({
  title: '',
  cover_image: '',
  content: '',
  is_published: true
});

// --- 專案狀態 ---
const projects = ref<Project[]>([]);
const currentProjectId = ref<number | null>(null);
const projectForm = ref({
  title: '',
  description: '',
  tech_stack: '',
  content: ''
});

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
      try { return '<pre class="hljs"><code>' + hljs.highlight(str, { language: lang, ignoreIllegals: true }).value + '</code></pre>'; } catch (__) {}
    }
    return '<pre class="hljs"><code>' + escapeHtml(str) + '</code></pre>';
  }
});

// 即時預覽計算 (文章與專案分開)
const renderedContent = computed(() => md.render(postForm.value.content));
const renderedProjectContent = computed(() => md.render(projectForm.value.content || ''));

// --- 共用方法 ---
const logout = async () => {
  const refreshToken = localStorage.getItem('admin_refresh_token');
  try {
    await axios.post('/api/logout', { refresh_token: refreshToken });
  } catch (e) {
    // Ignore backend errors so logout still works offline
  }
  localStorage.removeItem('admin_token');
  localStorage.removeItem('admin_refresh_token');
  toast.success('已成功登出系統');
  router.push('/login');
};

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    const file = target.files[0];
    const validTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/gif'];
    if (!validTypes.includes(file.type)) {
      toast.warning('格式錯誤！僅允許上傳 JPG, PNG 或 GIF 圖片。');
      target.value = '';
      return;
    }
    const formData = new FormData();
    formData.append('file', file);
    isUploading.value = true;
    try {
      const res = await axios.post('/api/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
      postForm.value.cover_image = `http://127.0.0.1:8000${res.data.url}`;
      toast.success('圖片上傳成功！');
    } catch (error) {
      toast.error('圖片上傳失敗');
    } finally {
      isUploading.value = false;
    }
  }
};

// 自動判斷目前是文章還是專案的工具列
const insertMarkdown = (type: string) => {
  if (!textareaRef.value) return;
  const textarea = textareaRef.value;
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  
  const isPostMode = adminMode.value === 'posts';
  const text = isPostMode ? postForm.value.content : projectForm.value.content;
  const selectedText = text.substring(start, end);
  
  let insertText = '';

  switch (type) {
    case 'bold': insertText = `**${selectedText || '粗體文字'}**`; break;
    case 'italic': insertText = `*${selectedText || '斜體文字'}*`; break;
    case 'h1': insertText = `# ${selectedText || '大標題'}\n`; break;
    case 'h2': insertText = `## ${selectedText || '次標題'}\n`; break;
    case 'code': insertText = `\`${selectedText || '程式碼'}\``; break;
    case 'blockcode': insertText = `\n\`\`\`javascript\n${selectedText || 'console.log("Code");'}\n\`\`\`\n`; break;
    case 'link': insertText = `[${selectedText || '連結文字'}](url)`; break;
    case 'image': insertText = `![圖片描述](${selectedText || '圖片網址'})`; break;
    case 'hr': insertText = `\n---\n`; break;
  }

  const newText = text.substring(0, start) + insertText + text.substring(end);
  
  if (isPostMode) {
    postForm.value.content = newText;
  } else {
    projectForm.value.content = newText;
  }

  setTimeout(() => {
    textarea.focus();
    textarea.setSelectionRange(start + insertText.length, start + insertText.length);
  }, 0);
};

// --- API 請求 ---
const fetchPosts = async () => {
  try {
    const res = await axios.get('/api/posts');
    posts.value = res.data;
  } catch (error) {
    console.error('載入文章列表失敗', error);
  }
};

const fetchAllData = async () => {
  await fetchPosts();
  try {
    const res = await axios.get('/api/projects');
    projects.value = res.data;
  } catch (error) {
    console.error('載入專案失敗', error);
  }
};

// --- 文章編輯模式 ---
const initCreateMode = () => {
  currentPostId.value = null;
  postForm.value = { title: '', cover_image: '', content: '# 在這裡開始寫新文章...', is_published: true };
};

const selectPostToEdit = (post: Post) => {
  currentPostId.value = post.id;
  postForm.value = { ...post };
  if (window.innerWidth < 768) isSidebarOpen.value = false;
};

const submitPost = async () => {
  if (!postForm.value.title || !postForm.value.content) {
    toast.warning('標題與內容不能為空！');
    return;
  }
  isSubmitting.value = true;
  try {
    if (currentPostId.value) {
      await axios.put(`/api/posts/${currentPostId.value}`, postForm.value);
      toast.success('文章更新成功！');
    } else {
      await axios.post('/api/posts', postForm.value);
      toast.success('新文章發布成功！');
      initCreateMode();
    }
    fetchPosts();
  } catch (error) {
    toast.error('操作失敗，請檢查後端連線');
  } finally {
    isSubmitting.value = false;
  }
};

const handleDelete = async (id: number) => {
  if (!confirm('確定要刪除這篇文章嗎？此動作無法復原！')) return;
  try {
    await axios.delete(`/api/posts/${id}`);
    toast.success('文章刪除成功');
    if (currentPostId.value === id) initCreateMode();
    fetchPosts();
  } catch (error) {
    toast.error('文章刪除失敗');
  }
};

// --- 專案編輯模式 ---
const initProjectMode = () => {
  currentProjectId.value = null;
  projectForm.value = { title: '', description: '', tech_stack: '', content: '' };
};

const selectProjectToEdit = (project: Project) => {
  currentProjectId.value = project.id;
  projectForm.value = { ...project, content: project.content || '' };
  if (window.innerWidth < 768) isSidebarOpen.value = false;
};

const submitProject = async () => {
  if (!projectForm.value.title) return toast.warning('請輸入專案標題');
  isSubmitting.value = true;
  try {
    if (currentProjectId.value) {
      await axios.put(`/api/projects/${currentProjectId.value}`, projectForm.value);
      toast.success('專案更新成功');
    } else {
      await axios.post('/api/projects', projectForm.value);
      toast.success('專案新增成功');
      initProjectMode();
    }
    fetchAllData();
  } catch (error) {
    toast.error('專案儲存失敗');
  } finally {
    isSubmitting.value = false;
  }
};

const deleteProject = async (id: number) => {
  if (!confirm('確定要刪除此專案？')) return;
  try {
    await axios.delete(`/api/projects/${id}`);
    toast.success('專案已刪除');
    fetchAllData();
  } catch (error) {
    toast.error('刪除失敗');
  }
};

watch(adminMode, (newMode) => {
  if (newMode === 'projects') {
    fetchAllData();
  } else {
    fetchPosts();
  }
});

onMounted(() => {
  fetchAllData();
  initCreateMode();
});
</script>

<template>
  <div>
    <div class="admin-wrapper">
      <aside class="sidebar" :class="{ 'closed': !isSidebarOpen }">
        <div class="admin-tabs">
          <button :class="{ active: adminMode === 'posts' }" @click="adminMode = 'posts'">
            <i class="fa-solid fa-file-lines"></i> 文章管理
          </button>
          <button :class="{ active: adminMode === 'projects' }" @click="adminMode = 'projects'">
            <i class="fa-solid fa-code-branch"></i> 專案管理
          </button>
        </div>

        <div class="sidebar-header">
          <h2>{{ adminMode === 'posts' ? '文章列表' : '專案列表' }}</h2>
          <button @click="adminMode === 'posts' ? initCreateMode() : initProjectMode()" class="btn-new">
            <i class="fa-solid fa-plus"></i> {{ adminMode === 'posts' ? '新增文章' : '新增專案' }}
          </button>
        </div>
        
        <div class="post-list">
          <template v-if="adminMode === 'posts'">
            <div v-for="post in posts" :key="post.id" class="post-item" :class="{ active: currentPostId === post.id }" @click="selectPostToEdit(post)">
              <div class="post-info">
                <span class="post-title">{{ post.title }}</span>
                <span class="post-id">#{{ post.id }}</span>
              </div>
              <button @click.stop="handleDelete(post.id)" class="btn-delete" title="刪除文章"><i class="fa-solid fa-trash"></i></button>
            </div>
          </template>

          <template v-else>
            <div v-for="p in projects" :key="p.id" class="post-item" :class="{ active: currentProjectId === p.id }" @click="selectProjectToEdit(p)">
              <div class="post-info">
                <span class="post-title">{{ p.title }}</span>
                <span class="post-id">#{{ p.id }}</span>
              </div>
              <button @click.stop="deleteProject(p.id)" class="btn-delete" title="刪除專案"><i class="fa-solid fa-trash"></i></button>
            </div>
          </template>
        </div>
      </aside>

      <button class="toggle-sidebar-btn" @click="isSidebarOpen = !isSidebarOpen" :style="{ left: isSidebarOpen ? '280px' : '0' }">
        <i class="fa-solid" :class="isSidebarOpen ? 'fa-chevron-left' : 'fa-chevron-right'"></i>
      </button>

      <main class="editor-container">
        <div class="header-actions">
          <h1>
            <i class="fa-solid" :class="adminMode === 'posts' ? 'fa-pen-to-square' : 'fa-laptop-code'"></i> 
            {{ adminMode === 'posts' ? (currentPostId ? '編輯文章' : '新增文章') : (currentProjectId ? '編輯專案' : '新增專案') }}
          </h1>
          
          <div class="action-buttons">
            <button @click="adminMode === 'posts' ? submitPost() : submitProject()" :disabled="isSubmitting || isUploading" class="publish-btn" :class="{ 'update-mode': (adminMode === 'posts' ? currentPostId : currentProjectId) }">
              <span v-if="isSubmitting"><i class="fa-solid fa-spinner fa-spin"></i> 處理中...</span>
              <span v-else>
                <i class="fa-solid" :class="(adminMode === 'posts' ? currentPostId : currentProjectId) ? 'fa-save' : 'fa-paper-plane'"></i> 
                {{ (adminMode === 'posts' ? currentPostId : currentProjectId) ? '更新' : '發布' }}
              </span>
            </button>
            <button @click="logout" class="logout-btn"><i class="fa-solid fa-right-from-bracket"></i> 登出</button>
          </div>
        </div>

        <div v-if="adminMode === 'posts'" class="editor-body-wrapper">
          <div class="form-grid">
            <div class="input-group">
              <input v-model="postForm.title" type="text" placeholder="請輸入文章標題..." class="title-input" />
            </div>
            <div class="input-group upload-group">
              <label class="upload-btn">
                <i class="fa-solid fa-cloud-arrow-up"></i> 
                <span v-if="isUploading">上傳中...</span><span v-else>上傳封面</span>
                <input type="file" @change="handleFileUpload" accept="image/*" class="file-input" />
              </label>
              
              <input v-model="postForm.cover_image" type="text" placeholder="或貼上圖片網址..." class="url-input" />
              
              <div v-if="postForm.cover_image" class="image-preview">
                <img :src="postForm.cover_image" alt="Cover" />
              </div>
            </div>
          </div>

          <div class="editor-area">
            <div class="editor-pane">
              <div class="pane-header">
                <span class="pane-label">Markdown 編輯區</span>
                <div class="toolbar">
                  <button @click="insertMarkdown('h1')">H1</button>
                  <button @click="insertMarkdown('h2')">H2</button>
                  <button @click="insertMarkdown('bold')"><i class="fa-solid fa-bold"></i></button>
                  <button @click="insertMarkdown('code')"><i class="fa-solid fa-code"></i></button>
                  <button @click="insertMarkdown('link')"><i class="fa-solid fa-link"></i></button>
                  <button @click="insertMarkdown('image')"><i class="fa-solid fa-image"></i></button>
                </div>
              </div>
              <textarea ref="textareaRef" v-model="postForm.content" class="markdown-input" placeholder="請輸入內容..."></textarea>
            </div>
            <div class="preview-pane">
              <div class="pane-header"><span class="pane-label">即時預覽</span></div>
              <div class="markdown-body content-preview" v-html="renderedContent"></div>
            </div>
          </div>
        </div>

        <div v-else class="editor-body-wrapper">
          <div class="project-top-section" style="display: flex; gap: 30px; flex-wrap: wrap; width: 100%; margin-bottom: 20px;">
            <div class="project-form-card" style="flex: 1; min-width: 300px;">
              <div class="input-group">
                <label>專案名稱</label>
                <input v-model="projectForm.title" type="text" placeholder="例如：Gamified Habit Tracker" class="title-input" />
              </div>
              <div class="input-group">
                <label>使用技術 (以逗號分隔)</label>
                <input v-model="projectForm.tech_stack" type="text" placeholder="例如：Vue3, Three.js, Python" class="title-input" />
              </div>
              <div class="input-group">
                <label>專案短述 (顯示於卡片外觀)</label>
                <textarea v-model="projectForm.description" class="project-desc-input" placeholder="請簡述專案的功能與亮點..." rows="4"></textarea>
              </div>
            </div>
            
            <div class="project-preview-section" style="width: 450px;">
              <h3 class="preview-title" style="margin-top: 0;">外觀卡片預覽</h3>
              <div class="project-card-preview">
                <div class="project-card">
                  <div class="card-header">
                    <h3>{{ projectForm.title || '專案標題' }}</h3>
                    <div class="folder-icon"><i class="fa-regular fa-folder-open"></i></div>
                  </div>
                  <p class="desc">{{ projectForm.description || '這裡會顯示專案的簡短描述...' }}</p>
                  <div class="tags">
                    <span class="tech-tag" v-for="tech in projectForm.tech_stack.split(',')" :key="tech">
                      {{ tech.trim() || '標籤' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="editor-area1" style="width: 100%;">
            <div class="editor-pane">
              <div class="pane-header">
                <span class="pane-label">Markdown 編輯區</span>
                <div class="toolbar">
                  <button @click="insertMarkdown('h1')">H1</button>
                  <button @click="insertMarkdown('h2')">H2</button>
                  <button @click="insertMarkdown('bold')"><i class="fa-solid fa-bold"></i></button>
                  <button @click="insertMarkdown('code')"><i class="fa-solid fa-code"></i></button>
                  <button @click="insertMarkdown('link')"><i class="fa-solid fa-link"></i></button>
                  <button @click="insertMarkdown('image')"><i class="fa-solid fa-image"></i></button>
                </div>
              </div>
              <textarea 
                ref="textareaRef" 
                v-model="projectForm.content" 
                class="markdown-input" 
                placeholder="請在這裡撰寫詳細的專案說明..."
              ></textarea>
            </div>
            <div class="preview-pane">
              <div class="pane-header"><span class="pane-label">即時預覽</span></div>
              <div class="markdown-body content-preview" v-html="renderedProjectContent"></div>
            </div>
          </div>
        </div>
      </main>
    </div>
    <SiteFooter />
  </div>
</template>

<style scoped>
:deep(.content-preview) { line-height: 1.8; }
:deep(h1), :deep(h2) { 
  border-bottom: 1px solid var(--border-color); 
  padding-bottom: 0.5rem; 
  margin-bottom: 1rem; 
  color: var(--link-active); 
}
:deep(pre) { background: #282c34; padding: 1rem; border-radius: 8px; overflow-x: auto; margin: 10px 0; }
:deep(code) { font-family: 'Fira Code', monospace; }
:deep(img) { max-width: 100%; border-radius: 8px; margin: 0 0; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
:deep(blockquote) { border-left: 4px solid var(--link-active); padding-left: 1rem; color: var(--link-color); }
:deep(ul), :deep(ol) { padding-left: 20px; }
:deep(a) { color: #58a6ff; text-decoration: none; }
</style>