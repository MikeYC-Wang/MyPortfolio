<template>
  <div class="timeline-section" :class="{ 'dark-mode': isDark }">
    <div class="section-header" v-observe>
      <h2><i class="fa-solid fa-briefcase"></i> 工作經歷 (Experience)</h2>
    </div>
    
    <div class="timeline-container">
      <div 
        v-for="(job, index) in experiences" 
        :key="index" 
        class="timeline-item"
        v-observe
      >
        <div class="timeline-line">
          <div class="timeline-icon-dot">
            <i :class="job.icon"></i>
          </div>
        </div>
        
        <div class="timeline-content">
          <div class="card-header">
            <div class="time-badge">
              <i class="fa-regular fa-calendar-days"></i> {{ job.duration }}
            </div>
            <div class="company-badge">
              <i class="fa-solid fa-building"></i> {{ job.company }}
            </div>
          </div>

          <h3 class="job-title">{{ job.title }}</h3>
          
          <ul class="job-description">
            <li v-for="(desc, i) in job.details" :key="i">
              <i class="fa-solid fa-caret-right list-icon"></i> {{ desc }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 自定義指令：捲動觸發動畫
const vObserve = {
  mounted: (el: HTMLElement) => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          el.classList.add('visible');
          observer.unobserve(el);
        }
      });
    }, { threshold: 0.15 });
    observer.observe(el);
  }
};

defineProps<{ isDark: boolean }>();

// === 真實數據 (加入 icon 欄位) ===
const experiences = [
  {
    title: '自動化程式設計實習生 (Intern)',
    company: '華碩電腦 (ASUS)',
    duration: '2024.06 - 至今',
    icon: 'fa-solid fa-laptop-code', // 💻 程式相關 icon
    details: [
      '隸屬於自動化程式設計一部，深入了解自動化流程如何提升產線效率。',
      '培養解決實務問題的能力，將所學技能應用於實際專案。',
      '協作開發內部工具，提升團隊作業效能。'
    ]
  },
  {
    title: '值班經理 / 訓練員',
    company: '摩斯漢堡 (基隆)',
    duration: '2019.04 - 2025.05',
    icon: 'fa-solid fa-burger', // 🍔 餐飲相關 icon
    details: [
      '從內外場基礎做起，晉升為值班經理，具備團隊管理與人員調度能力。',
      '考取訓練員資格，負責新進員工的教育訓練與 SOP 指導。',
      '學習溝通協調與顧客服務，在高壓環境下保持良好的應變能力。'
    ]
  }
];
</script>

<style scoped>
/* 基本設定 */
.timeline-section {
  padding: 80px 20px;
  background-color: var(--bg-color, #f8f9fa);
  color: var(--text-color, #333);
  overflow: hidden;
}

.timeline-section.dark-mode {
  --bg-color: #1a1a1a;
  --text-color: #d4d4d4;
  --line-color: #444;
  --card-bg: #2c2c2c;
  --primary: #00ffff;
  --shadow-color: rgba(0, 255, 255, 0.15);
}

.section-header {
  text-align: center;
  margin-bottom: 70px;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.8s ease;
}
.section-header.visible { opacity: 1; transform: translateY(0); }

h2 { 
  font-size: 2.5rem; 
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 15px;
}

.timeline-container {
  max-width: 900px;
  margin: 0 auto;
  position: relative;
}

/* 中央垂直線 */
.timeline-container::after {
  content: '';
  position: absolute;
  width: 4px;
  background-color: var(--line-color, #e0e0e0);
  top: 0;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  border-radius: 2px;
}

/* === 單個項目的容器 (控制左右位置) === */
.timeline-item {
  padding: 10px 40px;
  position: relative;
  width: 50%;
  box-sizing: border-box;
  opacity: 0;
  transition: all 0.8s cubic-bezier(0.22, 1, 0.36, 1);
  margin-bottom: 40px;
}

/* 左側項目 */
.timeline-item:nth-child(odd) {
  left: 0;
  transform: translateY(100px) translateX(-50px);
}

/* 右側項目 */
.timeline-item:nth-child(even) {
  left: 50%;
  transform: translateY(100px) translateX(50px);
}

/* === 動畫觸發狀態 === */
.timeline-item.visible {
  opacity: 1;
  transform: translateY(0) translateX(0);
}

/* === 卡片樣式 (懸浮特效核心) === */
.timeline-content {
  padding: 30px;
  background: var(--card-bg, #fff);
  border-radius: 16px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
  position: relative;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); /* 彈性過渡 */
  border-left: 5px solid var(--primary, #007bff); /* 左側裝飾線 */
}

/* ✨ 懸浮效果 ✨ */
.timeline-content:hover {
  transform: translateY(-10px) scale(1.02); /* 向上浮起並微放大 */
  box-shadow: 0 20px 40px -10px var(--shadow-color, rgba(0, 123, 255, 0.3)); /* 加深陰影 */
}

/* 卡片箭頭 */
.timeline-content::before {
  content: '';
  position: absolute;
  top: 30px;
  width: 0; 
  height: 0; 
  border-top: 10px solid transparent;
  border-bottom: 10px solid transparent;
  transition: all 0.3s ease;
}

/* 左側卡片箭頭在右邊 */
.timeline-item:nth-child(odd) .timeline-content::before {
  right: -10px;
  border-left: 10px solid var(--card-bg, #fff);
}

/* 右側卡片箭頭在左邊 */
.timeline-item:nth-child(even) .timeline-content::before {
  left: -10px;
  border-right: 10px solid var(--card-bg, #fff);
}

.timeline-section.dark-mode .timeline-content {
  box-shadow: 0 10px 30px rgba(0,0,0,0.4);
}

/* === 時間軸 Icon 圓點 === */
.timeline-icon-dot {
  position: absolute;
  width: 50px;
  height: 50px;
  background: var(--primary, #007bff);
  color: #fff;
  border: 4px solid var(--bg-color, #f8f9fa);
  border-radius: 50%;
  top: 15px;
  z-index: 2;
  box-shadow: 0 0 0 4px rgba(0, 123, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  transition: transform 0.3s ease;
}

.timeline-item:hover .timeline-icon-dot {
  transform: scale(1.2) rotate(360deg); /* 滑鼠經過卡片時，中間的圖示也會轉動放大 */
  background: #ff4560; /* 互動變色 */
}

/* 調整點點位置 */
.timeline-item:nth-child(odd) .timeline-icon-dot { 
  right: -65px; /* 50px寬度 + 線條偏移計算 */
}
.timeline-item:nth-child(even) .timeline-icon-dot { 
  left: -65px; 
}

/* 內容排版 */
.card-header {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 15px;
  font-size: 0.9rem;
  color: #666;
}

.timeline-section.dark-mode .card-header { color: #aaa; }

.time-badge, .company-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(0,0,0,0.05);
  padding: 4px 10px;
  border-radius: 6px;
}

.timeline-section.dark-mode .time-badge,
.timeline-section.dark-mode .company-badge {
  background: rgba(255,255,255,0.1);
}

.job-title { 
  margin: 0 0 15px 0; 
  font-size: 1.5rem; 
  color: var(--text-color); 
  font-weight: 700;
}

.job-description { 
  padding: 0; 
  margin: 0; 
  list-style: none; 
}

.job-description li { 
  margin-bottom: 10px; 
  line-height: 1.6; 
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.list-icon {
  margin-top: 5px; /* 對齊文字頂部 */
  color: var(--primary, #007bff);
  font-size: 0.8rem;
}

/* === RWD 手機版調整 === */
@media (max-width: 768px) {
  .timeline-container::after { left: 30px; }
  
  .timeline-item {
    width: 100%;
    padding-left: 80px;
    padding-right: 20px;
    margin-bottom: 30px;
    transform: translateY(50px); /* 手機版統一從下方滑入 */
  }
  
  .timeline-item:nth-child(even) { left: 0; }
  
  /* 修正點點位置 */
  .timeline-item:nth-child(odd) .timeline-icon-dot,
  .timeline-item:nth-child(even) .timeline-icon-dot {
    left: 5px;
    right: auto;
    width: 40px;
    height: 40px;
    font-size: 1.1rem;
  }
  
  /* 修正箭頭 */
  .timeline-item:nth-child(odd) .timeline-content::before,
  .timeline-item:nth-child(even) .timeline-content::before {
    left: -10px;
    right: auto;
    border-right: 10px solid var(--card-bg, #fff);
    border-left: none;
  }
}
</style>