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
  @import '../assets/css/AboutMe.css';
</style>