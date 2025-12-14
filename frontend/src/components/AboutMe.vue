<template>
  <div class="about-section">
    <div class="section-header" v-observe>
      <h2>關於我 (About Me)</h2>
      <div class="subtitle">汪宇晨 (Mikey) | 2002 Born</div>
    </div>

    <div class="content-grid">
      <div class="card profile-card" v-observe>
        <h3><i class="fa-solid fa-user-astronaut"></i> 個人特質</h3>
        <p>
          個性和善且善於傾聽，擅長換位思考，在團隊中扮演良好的溝通橋樑。
          堅持「既然投入時間成本，就必須產出最佳成果」的做事態度。
        </p>
        <p>
          熱愛學習新技術 (Codefinity, Google, AI)，認為 AI 是提升效率的最佳工具而非取代者。
          期許自己能成為資訊業中屹立不搖的專業人才。
        </p>
      </div>

      <div class="card edu-card" v-observe>
        <h3><i class="fa-solid fa-graduation-cap"></i> 學歷 & 證照</h3>
        <ul class="cert-list">
          <li class="highlight">★ 專利：寵物餵食器之餘糧清除裝置 ★</li>
          <li><strong>大學：</strong> ITE 遊戲企劃/美術、TQC+ App Inventor、TQC 人工智慧/物聯網</li>
          <li><strong>高中：</strong> 丙級工業電子、軟體應用、硬體裝修</li>
          <li><strong>競賽：</strong> 2023 中國科大 校園創新創業提案競賽 (學習簡報排版與 Arduino)</li>
        </ul>
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
    }, { threshold: 0.1 });
    observer.observe(el);
  }
};

defineProps<{ isDark: boolean }>();
</script>

<style scoped>
/* === 修正重點：移除背景色 === */
.about-section {
  /* 不要設背景色，讓父層的 Section 背景透出來 */
  background-color: transparent; 
  color: inherit; /* 跟隨父層文字顏色 */
}

/* Section Header 等樣式保持不變 */
.section-header { text-align: center; margin-bottom: 50px; opacity: 0; transform: translateY(30px); transition: all 0.8s ease; }
.section-header.visible { opacity: 1; transform: translateY(0); }
h2 { font-size: 2.5rem; margin-bottom: 10px; color: inherit; }
.subtitle { color: #888; font-size: 1.1rem; }
.content-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }

/* 卡片樣式 (保持深色卡片) */
.card {
  background-color: #2c2c2c; /* 卡片本體顏色，要在背景 #1a1a1a 上凸顯 */
  color: #e0e0e0;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
  opacity: 0;
  transform: translateY(50px);
  transition: all 0.8s ease;
  border: 1px solid #444;
}


.card.visible { opacity: 1; transform: translateY(0); }
.card h3 { margin-top: 0; border-bottom: 2px solid #007bff; padding-bottom: 10px; margin-bottom: 20px; display: inline-block; }

.cert-list { list-style: none; padding: 0; }
.cert-list li { margin-bottom: 12px; padding-left: 20px; position: relative; }
.cert-list li::before { content: '✓'; color: #007bff; position: absolute; left: 0; font-weight: bold; }
.highlight { color: #ffd700; font-weight: bold; } 

@media (max-width: 768px) { .content-grid { grid-template-columns: 1fr; } }
</style>