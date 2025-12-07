<script setup lang="ts">
import { onMounted, ref } from 'vue';
import gsap from 'gsap';
import ScrambleTextPlugin from 'gsap/ScrambleTextPlugin';

// 註冊插件
gsap.registerPlugin(ScrambleTextPlugin);

const emit = defineEmits(['intro-complete']);

const terminalRef = ref<HTMLElement | null>(null);
const mainTextRef = ref<HTMLElement | null>(null);
const overlayRef = ref<HTMLElement | null>(null);

// 模擬的啟動日誌
const logs = [
  "> Initializing Vue 3 core...",
  "> Loading modules...",
  "> Connecting to neural network...",
  "> ACCESS GRANTED."
];

onMounted(() => {
  const tl = gsap.timeline({
    onComplete: () => {
      // 動畫結束後通知父組件，並將此組件移除 (可選)
      emit('intro-complete');
    }
  });

  // 1. 模擬終端機日誌快速出現
  tl.fromTo('.log-item', 
    { opacity: 0, x: -20 },
    { 
      opacity: 1, 
      x: 0, 
      duration: 0.1, 
      stagger: 0.1, // 每行間隔 0.1 秒
      ease: "power1.out"
    }
  );

  // 2. 主標題亂碼解碼進場
  tl.to(mainTextRef.value, {
    duration: 2,
    scrambleText: {
      text: "HELLO, I'M MIKE", // 最終顯示的文字
      chars: "01", // 使用 0 和 1 作為亂碼字元 (或是 "upperCase", "lowerCase", "!@#$%^&*")
      revealDelay: 0.5,
      tweenLength: false,
      speed: 0.3
    },
    ease: "none"
  });

  // 3. 游標閃爍幾次 (選用)
  tl.to('.cursor', { opacity: 0, repeat: 3, yoyo: true, duration: 0.1 });

  // 4. 揭幕特效：背景從中間向上下裂開 (Clip Path 動畫)
  tl.to(overlayRef.value, {
    clipPath: 'inset(0 0 100% 0)', // 像捲簾一樣往上收
    // 或者使用中間裂開的效果: clipPath: 'inset(50% 0 50% 0)'
    duration: 1,
    ease: "power4.inOut"
  });
  
  // 5. 確保 DOM 完全隱藏
  tl.set(overlayRef.value, { display: 'none' });
});
</script>

<template>
  <div ref="overlayRef" class="hacker-intro">
    <div class="content-wrapper">
      <div ref="terminalRef" class="logs-container">
        <p v-for="(log, index) in logs" :key="index" class="log-item">{{ log }}</p>
      </div>

      <div class="title-container">
        <h1 ref="mainTextRef" class="glitch-text">_</h1>
        <span class="cursor">_</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 引入等寬字體，更有駭客感 */
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');

.hacker-intro {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: #050505; /* 極深灰/黑 */
  color: #00ff41;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Fira Code', monospace;
  overflow: hidden;
}

.content-wrapper {
  width: 80%;
  max-width: 800px;
}

.logs-container {
  font-size: 0.9rem;
  opacity: 0.7;
  margin-bottom: 2rem;
  min-height: 100px; /* 預留空間 */
}

.log-item {
  margin: 0.2rem 0;
}

.title-container {
  display: flex;
  align-items: center;
}

.glitch-text {
  font-size: 3rem;
  font-weight: 700;
  margin: 0;
  color: #fff; /* 主標題可以是白色，與日誌區分 */
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
}

.cursor {
  font-size: 3rem;
  animation: blink 1s infinite;
  margin-left: 10px;
  color: #00ff41;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* RWD 調整 */
@media (max-width: 768px) {
  .glitch-text {
    font-size: 2rem;
  }
  .logs-container {
    font-size: 0.8rem;
  }
}
</style>