<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const cursorDot = ref<HTMLElement | null>(null);
const cursorRing = ref<HTMLElement | null>(null);

const isHovering = ref(false);
const isClicking = ref(false);

// 儲存目標滑鼠座標 (滑鼠實際位置)
let targetX = window.innerWidth / 2;
let targetY = window.innerHeight / 2;

// 儲存 UI 元素當下座標
let dotX = targetX;
let dotY = targetY;
let ringX = targetX;
let ringY = targetY;

let rafId: number;

// mousemove 現在「只負責記錄座標」，不操作 DOM，這樣效能最高
const onMouseMove = (e: MouseEvent) => {
  targetX = e.clientX;
  targetY = e.clientY;

  // 判斷是否移到了可點擊的元素上
  const target = e.target as HTMLElement;

  if (
    target.tagName.toLowerCase() === 'a' ||
    target.tagName.toLowerCase() === 'button' ||
    target.tagName.toLowerCase() === 'label' || 
    target.closest('a') ||
    target.closest('button') ||
    target.closest('label') ||
    target.closest('.snippet-card') || 
    target.closest('.post-item') ||
    target.closest('.overlay') ||
    target.classList.contains('clickable')
  ) {
    isHovering.value = true;
  } else {
    isHovering.value = false;
  }
};

const onMouseDown = () => (isClicking.value = true);
const onMouseUp = () => (isClicking.value = false);

// 所有的畫面更新都集中在這個與螢幕刷新率同步的迴圈裡
const render = () => {
  // 內點：無延遲，直接跟隨目標座標
  dotX = targetX;
  dotY = targetY;

  // 外環：Lerp 平滑演算法，0.15 是跟隨的阻尼係數 (可依照喜好微調 0.1~0.3)
  ringX += (targetX - ringX) * 0.15;
  ringY += (targetY - ringY) * 0.15;

  // 統一操作 DOM，強制硬體加速
  if (cursorDot.value) {
    cursorDot.value.style.transform = `translate3d(calc(${dotX}px - 50%), calc(${dotY}px - 50%), 0)`;
  }
  if (cursorRing.value) {
    cursorRing.value.style.transform = `translate3d(calc(${ringX}px - 50%), calc(${ringY}px - 50%), 0)`;
  }

  rafId = requestAnimationFrame(render);
};

onMounted(() => {
  // 加上 { passive: true } 讓瀏覽器知道這個事件不會 block 畫面渲染
  window.addEventListener('mousemove', onMouseMove, { passive: true });
  window.addEventListener('mousedown', onMouseDown, { passive: true });
  window.addEventListener('mouseup', onMouseUp, { passive: true });
  rafId = requestAnimationFrame(render);
});

onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove);
  window.removeEventListener('mousedown', onMouseDown);
  window.removeEventListener('mouseup', onMouseUp);
  cancelAnimationFrame(rafId);
});
</script>

<template>
  <div class="cursor-container desktop-only">
    <div 
      ref="cursorDot" 
      class="cursor-dot"
      :class="{ 'hover': isHovering, 'click': isClicking }"
    ></div>
    <div 
      ref="cursorRing" 
      class="cursor-ring"
      :class="{ 'hover': isHovering, 'click': isClicking }"
    ></div>
  </div>
</template>

<style scoped>
.cursor-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 99999;
}

/* --- 內層實心點 --- */
.cursor-dot {
  position: absolute;
  top: 0;
  left: 0;
  width: 6px;
  height: 6px;
  background-color: var(--link-active, #e0cda9);
  border-radius: 50%;
  will-change: transform;
  transition-property: width, height, background-color, opacity;
  transition-duration: 0.2s;
  transition-timing-function: ease-out;
}

/* --- 外圍平滑光環 --- */
.cursor-ring {
  position: absolute;
  top: 0;
  left: 0;
  width: 32px;
  height: 32px;
  border: 1.5px solid var(--link-active, #e0cda9);
  border-radius: 50%;
  will-change: transform;
  transition-property: width, height, background-color, border-color, backdrop-filter;
  transition-duration: 0.2s;
  transition-timing-function: ease-out;
}

/* --- Hover 狀態特效 --- */
.cursor-dot.hover {
  width: 0px;
  height: 0px;
  opacity: 0;
}

.cursor-ring.hover {
  width: 50px;
  height: 50px;
  background-color: rgba(224, 205, 169, 0.15);
  border-color: transparent;
  backdrop-filter: blur(2px);
}

/* --- 點擊狀態特效 --- */
.cursor-ring.click {
  width: 20px;
  height: 20px;
  background-color: rgba(224, 205, 169, 0.4);
}

@media (max-width: 768px) {
  .desktop-only {
    display: none !important;
  }
}
</style>