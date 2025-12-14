import { ref } from 'vue';

// 建立一個全域的狀態，預設為 true (深色)
const isDark = ref(true);

export function useTheme() {
  
  // 初始化：檢查目前的 DOM 狀態同步到變數
  const initTheme = () => {
    if (typeof document !== 'undefined') {
      isDark.value = document.body.classList.contains('theme-dark');
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
      } else {
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