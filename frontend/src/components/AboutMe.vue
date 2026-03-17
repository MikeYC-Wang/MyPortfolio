<template>
  <div class="about-section">
    <div class="container">
      <div class="section-header" v-observe>
        <h2><i class="fa-solid fa-user-astronaut"></i> 關於我 (About Me)</h2>
        <div class="subtitle">汪宇晨 (Mike) | 2002 Born</div>
      </div>

      <div class="about-layout">
        
        <div class="info-cards-row">
          <div class="card profile-card" v-observe>
            <h3><i class="fa-solid fa-id-card"></i> 個人特質</h3>
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
              <li><strong>競賽：</strong> 2023 中國科大 校園創新創業提案競賽</li>
            </ul>
          </div>
        </div>

        <div class="about-chart-row" v-observe>
          <RadarChart :isDark="isDark" />
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import RadarChart from '@/components/RadarChart.vue'; // 引入雷達圖

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
.about-section {
  background-color: transparent; 
  color: inherit;
}

/* --- 佈局核心 --- */
.about-layout {
  display: flex;
  flex-direction: column;
  gap: 30px; /* 上下排的間距 */
}

/* --- 上半部：兩張卡片左右並排 --- */
.info-cards-row {
  display: grid;
  grid-template-columns: 1fr 1fr; /* 切成左右各半 */
  gap: 30px;
  align-items: stretch; /* 讓兩張卡片高度自動對齊 */
}

/* --- 下半部：雷達圖 --- */
.about-chart-row {
  width: 100%;
  opacity: 0;
  transform: translateY(50px);
  transition: all 0.8s ease;
}

.about-chart-row.visible {
  opacity: 1;
  transform: translateY(0);
}

/* --- 卡片共用樣式 --- */
.card {
  background-color: var(--card-bg, rgba(44, 44, 44, 0.7)); 
  border: 1px solid var(--card-border, rgba(255, 255, 255, 0.1));
  color: var(--text-color, #e0e0e0);
  box-shadow: var(--card-shadow, 0 4px 6px rgba(0,0,0,0.3));
  padding: 30px;
  border-radius: 16px;
  opacity: 0;
  transform: translateY(50px);
  transition: all 0.8s ease;
  display: flex;
  flex-direction: column;
}

.card.visible { opacity: 1; transform: translateY(0); }
.card h3 { margin-top: 0; border-bottom: 2px solid #007bff; padding-bottom: 10px; margin-bottom: 20px; display: inline-block; }

.cert-list { list-style: none; padding: 0; margin: 0; }
.cert-list li { margin-bottom: 12px; padding-left: 20px; position: relative; line-height: 1.5; }
.cert-list li::before { content: '✓'; color: #007bff; position: absolute; left: 0; font-weight: bold; }
.highlight { color: #ffd700; font-weight: bold; } 

:global(body.theme-light) .highlight { color: #d63384; }

.section-header { text-align: center; margin-bottom: 50px; opacity: 0; transform: translateY(30px); transition: all 0.8s ease; }
.section-header.visible { opacity: 1; transform: translateY(0); }
h2 { font-size: 2.5rem; margin-bottom: 10px; color: inherit; }
.subtitle { color: #888; font-size: 1.1rem; text-align:center !important; }

/* --- RWD 手機版：螢幕太窄時全部變上下排 --- */
@media (max-width: 960px) { 
  .info-cards-row { 
    grid-template-columns: 1fr;
  } 
}
</style>