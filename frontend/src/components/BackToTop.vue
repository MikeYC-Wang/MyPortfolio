<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const isVisible = ref(false);

// 監聽滾動事件，超過 300px 就顯示按鈕
const checkScroll = () => {
  isVisible.value = window.scrollY > 300;
};

// 點擊後平滑滾動到最上方
const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  });
};

onMounted(() => {
  // 加上 passive: true 提升滾動效能
  window.addEventListener('scroll', checkScroll, { passive: true });
});

onUnmounted(() => {
  window.removeEventListener('scroll', checkScroll);
});
</script>

<template>
  <Transition name="fade">
    <button v-show="isVisible" class="back-to-top" @click="scrollToTop" title="回到頂部">
      <i class="fa-solid fa-arrow-up"></i>
    </button>
  </Transition>
</template>

<style scoped>
.back-to-top {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--milk-tea, #e6ccb2) 0%, var(--milk-tea-dark, #d4b595) 100%);
  color: #121212;
  border: none;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.2rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  z-index: 999; /* 確保它在最上層，不會被 Footer 蓋住 */
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.back-to-top:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 20px rgba(212, 181, 149, 0.5);
}

/* 淡入淡出動畫 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

@media (max-width: 768px) {
  .back-to-top {
    bottom: 20px;
    right: 20px;
    width: 45px;
    height: 45px;
  }
}
</style>