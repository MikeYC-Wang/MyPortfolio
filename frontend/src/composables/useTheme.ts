// src/composables/useTheme.ts
import { ref } from 'vue';

// 建立一個全域的狀態，預設為 true (深色)
const isDark = ref(true);

export function useTheme() {
  
  // 初始化：檢查目前的 DOM 狀態同步到變數
  const initTheme = () => {
    if (typeof document !== 'undefined') {
      // 如果 body 已經有 theme-light，就設為 false，否則預設 true
      isDark.value = !document.body.classList.contains('theme-light');
      updateDom(); // 確保一開始的 class 是正確掛上的
    }
  };

  // 切換主題的函數
  const toggleTheme = () => {
    isDark.value = !isDark.value;
    updateDom();
  };

  // 強制設定主題 (例如一開始載入時)
  const setDark = (value: boolean) => {
    isDark.value = value;
    updateDom();
  };

  // 同步到 DOM (body class)
  const updateDom = () => {
    if (typeof document !== 'undefined') {
      if (isDark.value) {
        document.body.classList.add('theme-dark');
        document.body.classList.remove('theme-light');
      } else {
        document.body.classList.add('theme-light');  
        document.body.classList.remove('theme-dark'); 
      }
    }
  };

  return {
    isDark,
    toggleTheme,
    initTheme,
    setDark
  };
}