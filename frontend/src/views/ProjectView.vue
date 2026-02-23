<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
// ✨ 引入 Markdown 解析器與高亮套件
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-dark.css';
import '@/assets/css/projects.css';

interface Project {
  id: number;
  title: string;
  description: string;
  tech_stack: string;
  content?: string; // ✨ 新增 content 屬性
}

const projects = ref<Project[]>([]);
const isLoading = ref(true);
const errorMsg = ref('');

// 控制彈出視窗的狀態
const selectedProject = ref<Project | null>(null);

// ✨ Markdown 解析器設定 (與後台完全相同)
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

// ✨ 計算當前選中專案的 Markdown 內容
const renderedProjectContent = computed(() => {
  if (!selectedProject.value || !selectedProject.value.content) return '';
  return md.render(selectedProject.value.content);
});

// 開啟全文彈窗
const openModal = (project: Project) => {
  selectedProject.value = project;
  document.body.style.overflow = 'hidden'; // 鎖定背景，防止捲動到底下
};

// 關閉全文彈窗
const closeModal = () => {
  selectedProject.value = null;
  document.body.style.overflow = ''; // 恢復背景捲動
};

onMounted(async () => {
  window.scrollTo(0, 0);
  
  try {
    const response = await axios.get('/api/projects');
    projects.value = response.data;
  } catch (err) {
    console.error('無法載入專案資料:', err);
    errorMsg.value = '無法連線到伺服器，請稍後再試。';
  } finally {
    isLoading.value = false;
  }
});
</script>

<template>
  <div class="projects-page">
    <div class="projects-container">
      
      <div class="page-header">
        <h1 class="page-title">
          <i class="fa-solid fa-code-branch"></i> 專案作品集
        </h1>
        <p class="subtitle">開發紀錄與實戰專案</p>
      </div>

      <div v-if="isLoading" class="status-message">
        <i class="fa-solid fa-spinner fa-spin"></i> 正在載入作品...
      </div>
      <div v-else-if="errorMsg" class="status-message error">
        <i class="fa-solid fa-triangle-exclamation"></i> {{ errorMsg }}
      </div>

      <div v-else class="projects-grid">
        <div 
          v-for="p in projects" 
          :key="p.id" 
          class="project-card"
          @click="openModal(p)"
        >
          <div class="card-top">
            <div class="folder-icon"><i class="fa-regular fa-folder-open"></i></div>
          </div>
          
          <h2 class="project-title">{{ p.title }}</h2>
          <p class="project-desc">{{ p.description }}</p>
          
          <div class="tech-stack">
            <span class="tech-tag" v-for="tech in (p.tech_stack ? p.tech_stack.split(',') : [])" :key="tech">
              {{ tech.trim() }}
            </span>
          </div>
        </div>
      </div>

    </div>

    <Transition name="modal-fade">
      <div v-if="selectedProject" class="modal-overlay" @click.self="closeModal">
        <div class="modal-content">
          <button class="modal-close-btn" @click="closeModal">
            <i class="fa-solid fa-xmark"></i>
          </button>
          
          <div class="modal-header">
            <div class="folder-icon"><i class="fa-regular fa-folder-open"></i></div>
            <h2 class="modal-title">{{ selectedProject.title }}</h2>
          </div>
          
          <div class="modal-body">
            <div class="project-summary-box" v-if="selectedProject.description">
              <p>{{ selectedProject.description }}</p>
            </div>
            
            <div v-if="selectedProject.content" class="markdown-body content-preview" v-html="renderedProjectContent"></div>
          </div>
          
          <div class="modal-footer">
            <div class="tech-stack">
              <span class="tech-tag" v-for="tech in (selectedProject.tech_stack ? selectedProject.tech_stack.split(',') : [])" :key="tech">
                {{ tech.trim() }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<style scoped>
:deep(.content-preview) {
  color: var(--text-color);
  line-height: 1.8;
  font-size: 1.05rem;
}

:deep(.content-preview h1), 
:deep(.content-preview h2), 
:deep(.content-preview h3) {
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.5rem;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  color: var(--link-active);
}

:deep(.content-preview p) {
  margin-bottom: 1rem;
}

:deep(.content-preview pre) {
  background: #282c34;
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
  margin: 15px 0;
}

:deep(.content-preview code) {
  font-family: 'Fira Code', monospace;
}

:deep(.content-preview img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 15px 0;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

:deep(.content-preview blockquote) {
  border-left: 4px solid var(--link-active);
  padding-left: 1rem;
  color: var(--text-color);
  opacity: 0.8;
  margin: 15px 0;
  background: rgba(255, 255, 255, 0.05);
  padding: 10px 15px;
  border-radius: 4px;
}

:deep(.content-preview ul), 
:deep(.content-preview ol) {
  padding-left: 20px;
  margin-bottom: 1rem;
}

:deep(.content-preview a) {
  color: #58a6ff;
  text-decoration: none;
}

:deep(.content-preview a:hover) {
  text-decoration: underline;
}
</style>