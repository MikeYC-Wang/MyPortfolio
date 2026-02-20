<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import '@/assets/css/projects.css';

interface Project {
  id: number;
  title: string;
  description: string;
  tech_stack: string;
}

const projects = ref<Project[]>([]);
const isLoading = ref(true);
const errorMsg = ref('');

// 控制彈出視窗的狀態
const selectedProject = ref<Project | null>(null);

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
  // 捲動到最上方
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
            <p class="modal-desc">{{ selectedProject.description }}</p>
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