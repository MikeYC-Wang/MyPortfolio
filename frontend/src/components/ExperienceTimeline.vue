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

// === 真實數據 ===
const experiences = [
  {
    title: '前端工程師 (Front End Engineer)',
    company: '方達科技股份有限公司',
    duration: '2025.07 - 2026.03',
    icon: 'fa-solid fa-globe',
    details: [
      '使用 ASP.NET Web Form、.NET Core 、C# 進行開發，負責前後端系統建置。',
      '維護與管理 MS SQL Server 資料庫，優化查詢效能。',
      '使用 SVN 進行版本控制，確保團隊協作順暢。',
      '參與影像串流與 GIS 相關功能開發。'
    ]
  },
  {
    title: '自動化程式設計實習生 (Intern)',
    company: '華碩電腦 (ASUS)',
    duration: '2024.06 - 2025.06',
    icon: 'fa-solid fa-code',
    details: [
      '隸屬於自動化程式設計一部，深入了解自動化流程如何提升產線效率。',
      '培養解決實務問題的能力，將所學技能應用於實際專案。',
      '追蹤及處理生產測試log相關問題。',
      '品質管理平台系統維運、系統備份／還原、資料庫備份／還原、系統憑證更新。',
      '品質管理平台系統前端使用者介面（UI）修改與維護。'
    ]
  },
  {
    title: '值班 / 訓練員',
    company: '摩斯漢堡 (基隆)',
    duration: '2019.04 - 2025.05',
    icon: 'fa-solid fa-burger',
    details: [
      '從內外場基礎做起，晉升為值班經理，具備團隊管理與人員調度能力。',
      '考取訓練員資格，負責新進員工的教育訓練與 SOP 指導。',
      '學習溝通協調與顧客服務，在高壓環境下保持良好的應變能力。'
    ]
  }
];
</script>

<style scoped>
  @import '../assets/css/ExperienceTimeline.css';
</style>