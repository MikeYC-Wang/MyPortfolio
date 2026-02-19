<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';
import gsap from 'gsap';
import ScrambleTextPlugin from 'gsap/ScrambleTextPlugin';

gsap.registerPlugin(ScrambleTextPlugin);

const emit = defineEmits(['intro-complete']);

const containerRef = ref<HTMLElement | null>(null);
const canvasRef = ref<HTMLCanvasElement | null>(null);
const cnTextRef = ref<HTMLElement | null>(null);
const enTextRef = ref<HTMLElement | null>(null);

let animationFrameId: number;

// --- 📝 自我介紹 ---
const introSequence = [
  {
    cn: "哈囉，我是 Mike",
    en: "Hello, I am MIKE."
  },
  {
    cn: "歡迎來到我的網站！",
    en: "Welcome to my website!"
  },
];

const logs = [
  "> System check...",
  "> Allocating memory...",
  "> Loading visual modules...",
  "> BYPASSING FIREWALL..."
];

// 🎨 極速雜訊渲染引擎 (Pre-rendering Optimization)
const startNoiseLoop = () => {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d', { alpha: false });
  if (!ctx) return;

  // 使用低解析度畫布，CSS 負責拉大
  const w = canvas.width = 400; 
  const h = canvas.height = 200;
  
  // 🚀 關鍵優化：預先產生 10 幀雜訊，而不是每幀即時運算
  const noiseFrames: ImageData[] = [];
  for (let f = 0; f < 10; f++) {
    const idata = ctx.createImageData(w, h);
    const buffer32 = new Uint32Array(idata.data.buffer);
    const len = buffer32.length;
    for (let i = 0; i < len; i++) {
        if (Math.random() < 0.1) {
           const gray = (Math.random() * 150 + 50) | 0;
           buffer32[i] = 0xff000000 | (gray << 16) | (gray << 8) | gray;
        } else if (Math.random() < 0.005) { 
           buffer32[i] = 0xffffffff; // 白點
        } else {
           buffer32[i] = 0xff000000; // 黑底
        }
    }
    noiseFrames.push(idata);
  }

  let frameCount = 0;

  const loop = () => {
    // 每 4 幀切換一次圖片 (約 15FPS)，製造復古低幀率感，同時極省效能
    if (frameCount % 4 === 0 && noiseFrames.length > 0) {
        const frameIndex = (frameCount / 4) % noiseFrames.length;
        const frame = noiseFrames[frameIndex];
        if (frame) {
            ctx.putImageData(frame, 0, 0);
        }
    }
    
    frameCount++;
    animationFrameId = requestAnimationFrame(loop);
  };
  loop();
};

onMounted(() => {
  startNoiseLoop();

  const tl = gsap.timeline({
    onComplete: () => {
      emit('intro-complete');
    }
  });

  // 1. 終端機日誌
  tl.fromTo('.log-item', 
    { opacity: 0, x: -20 },
    { opacity: 1, x: 0, duration: 0.05, stagger: 0.03, ease: "power1.out" }
  );
  
  tl.to('.logs-container', { opacity: 0, duration: 0.5, display: 'none' }, "+=0.5");

  // 2. 循環播放自我介紹
  introSequence.forEach((item, index) => {
    const delay = index === 0 ? ">" : "+=0.2"; // 每一句之間的間隔
    
    // 中文進場 (變慢)
    tl.to(cnTextRef.value, {
      duration: 1.5, // 🔴 從 1.0 改為 1.5，解碼更從容
      scrambleText: {
        text: item.cn,
        chars: "01",
        speed: 0.3, // 🔴 速度放慢
        revealDelay: 0.2
      },
      ease: "none"
    }, delay);

    // 英文進場
    tl.to(enTextRef.value, {
      duration: 1.0,
      scrambleText: {
        text: item.en,
        chars: "upperCase",
        speed: 0.6
      },
      opacity: 1,
      ease: "none"
    }, "<0.3");

    // 閱讀停留時間 (變長)
    tl.to({}, { duration: 2.0 }); // 🔴 從 1.4 改為 2.0，讓觀眾看清楚

    // 文字退場
    if (index < introSequence.length - 1) {
      tl.to([cnTextRef.value, enTextRef.value], {
        opacity: 0,
        duration: 0.6, 
        y: -50, 
        ease: "power2.in"
      });

      tl.set([cnTextRef.value, enTextRef.value], { y: 0, opacity: 1, text: "" }); 
    }
  });

  // ------------------------------------------------
  // 3. 舊電視關機特效
  // ------------------------------------------------
  
  // A: 雜訊暴衝
  tl.to(canvasRef.value, { opacity: 0.8, duration: 0.2, ease: "rough" });

  // B: 垂直壓扁
  tl.to(containerRef.value, {
    scaleY: 0.002, 
    scaleX: 1.1,
    backgroundColor: '#fff',
    duration: 0.5, 
    ease: "power2.inOut",
    force3D: true
  });

  // C: 白光殘影
  tl.to(containerRef.value, {
    backgroundColor: '#000',
    duration: 0.15
  });

  // D: 水平縮成光點消失
  tl.to(containerRef.value, {
    scaleX: 0,
    duration: 0.4,
    ease: "expo.out",
    force3D: true
  });

  // E: 隱藏
  tl.set(containerRef.value, { display: 'none' });
});

onUnmounted(() => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
});
</script>

<template>
  <div ref="containerRef" class="hacker-intro">
    <canvas ref="canvasRef" class="noise-canvas"></canvas>
    
    <div class="scanlines"></div>

    <div class="content-wrapper">
      <div class="logs-container">
        <p v-for="(log, index) in logs" :key="index" class="log-item">{{ log }}</p>
      </div>

      <div class="subtitle-container">
        <h1 ref="cnTextRef" class="cn-text"></h1>
        <p ref="enTextRef" class="en-text"></p>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@500;700&family=Fira+Code:wght@400;600&display=swap');

.hacker-intro {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: #000;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  transform-origin: center center;
  will-change: transform; 
}

/* --- 📺 Canvas 雜訊層 --- */
.noise-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  opacity: 0.15;
  image-rendering: pixelated; 
  z-index: 1;
}

.scanlines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,0) 50%, rgba(0,0,0,0.3) 50%, rgba(0,0,0,0.3));
  background-size: 100% 3px;
  z-index: 10;
  pointer-events: none;
}

/* --- 📝 內容排版 --- */
.content-wrapper {
  position: relative;
  z-index: 20;
  width: 100%;
  max-width: 900px;
  text-align: center;
  padding: 0 20px;
  will-change: transform, opacity;
}

.logs-container {
  position: absolute;
  top: -150px;
  left: 50%;
  transform: translateX(-50%);
  font-family: 'Fira Code', monospace;
  font-size: 0.8rem;
  color: #555;
  text-align: left;
  width: 320px;
}

.subtitle-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px; /* 增加間距 */
}

.cn-text {
  font-family: 'Noto Sans TC', sans-serif;
  font-size: 3.5rem;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 0 20px rgba(255, 255, 255, 0.6);
  margin: 0;
  line-height: 1.4;
  letter-spacing: 3px;
  min-height: 1.4em; /* 確保高度固定，防止跳動 */
}

.en-text {
  font-family: 'Fira Code', monospace;
  font-size: 1.1rem;
  color: #00ff41;
  margin: 0;
  letter-spacing: 1px;
  text-transform: uppercase;
  opacity: 0;
  font-weight: 500;
  text-shadow: 0 0 5px rgba(0, 255, 65, 0.4);
  min-height: 1.2em;
}

/* RWD */
@media (max-width: 768px) {
  .cn-text {
    font-size: 2rem;
  }
  .en-text {
    font-size: 0.9rem;
  }
}
</style>