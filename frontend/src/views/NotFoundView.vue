<script setup lang="ts">
import { useRouter } from 'vue-router';
import SiteFooter from '@/components/SiteFooter.vue';

const router = useRouter();

const goHome = () => {
  router.push('/');
};
</script>

<template>
  <div>
    <div class="not-found-container">
      <div class="glitch-wrapper">
        <h1 class="glitch" data-text="404">404</h1>
        <p class="desc">SYSTEM ERROR: Page Not Found.</p>
        <p class="sub-desc">Oops! 看來你闖入了一片未知的虛空...</p>
        
        <button class="home-btn" @click="goHome">
          <i class="fa-solid fa-code"></i> 返回首頁
        </button>
      </div>
    </div>
    <SiteFooter />
  </div>
</template>

<style scoped>
.not-found-container {
  min-height: calc(100vh - 80px); /* 扣掉 header 高度 */
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 20px;
}

.glitch-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

/* 駭客風格 Glitch 特效核心 */
.glitch {
  font-size: 8rem;
  font-weight: 900;
  font-family: 'Fira Code', monospace;
  position: relative;
  color: var(--text-color);
  margin: 0;
  letter-spacing: 5px;
}

.glitch::before,
.glitch::after {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: var(--bg-color, #0d1117); /* 背景需與畫布一致，避免破圖 */
}

/* 淺色模式支援 */
:global(body.theme-light) .glitch::before,
:global(body.theme-light) .glitch::after {
  background: #faf7f2;
}

.glitch::before {
  left: 3px;
  text-shadow: -2px 0 #ff00c1;
  clip: rect(44px, 450px, 56px, 0);
  animation: glitch-anim 3s infinite linear alternate-reverse;
}

.glitch::after {
  left: -3px;
  text-shadow: -2px 0 #00fff9;
  clip: rect(44px, 450px, 56px, 0);
  animation: glitch-anim2 2.5s infinite linear alternate-reverse;
}

.desc {
  font-size: 1.5rem;
  font-family: 'Fira Code', monospace;
  color: #ff00c1;
  margin: 0;
}

.sub-desc {
  font-size: 1rem;
  color: #aaa;
  margin-bottom: 20px;
}

:global(body.theme-light) .sub-desc { color: #666; }

.home-btn {
  padding: 12px 24px;
  font-size: 1.1rem;
  font-weight: bold;
  font-family: 'Fira Code', monospace;
  color: #121212;
  background: linear-gradient(135deg, var(--milk-tea, #e6ccb2) 0%, var(--milk-tea-dark, #d4b595) 100%);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 4px 15px rgba(212, 181, 149, 0.3);
}

.home-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(212, 181, 149, 0.6);
}

/* CSS 切割動畫，製造訊號不良的錯覺 */
@keyframes glitch-anim {
  0% { clip: rect(13px, 9999px, 8px, 0); }
  20% { clip: rect(4px, 9999px, 73px, 0); }
  40% { clip: rect(19px, 9999px, 90px, 0); }
  60% { clip: rect(77px, 9999px, 49px, 0); }
  80% { clip: rect(91px, 9999px, 52px, 0); }
  100% { clip: rect(10px, 9999px, 88px, 0); }
}

@keyframes glitch-anim2 {
  0% { clip: rect(65px, 9999px, 100px, 0); }
  20% { clip: rect(67px, 9999px, 61px, 0); }
  40% { clip: rect(31px, 9999px, 92px, 0); }
  60% { clip: rect(55px, 9999px, 12px, 0); }
  80% { clip: rect(70px, 9999px, 99px, 0); }
  100% { clip: rect(43px, 9999px, 17px, 0); }
}
</style>