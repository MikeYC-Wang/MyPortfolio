<script setup lang="ts">
import { ref, onMounted, onUnmounted, defineExpose } from 'vue';

// === 高解析度設定 (2K) ===
const width = 2048;
const height = 1024; // 2:1 寬螢幕比例
const padding = { x: 60, y: 120 }; // y 從 120 開始，保留給上方標題欄
const lineHeight = 60; // 字體變大
const fontSize = 'bold 42px "Menlo", "Monaco", "Courier New", monospace';

// === 程式碼內容 ===
const codeLines = [

  "import { Experience } from 'data';",
  "",
  "const developer = {",
  "  name: 'Mike Wang',",
  "  role: 'Frontend Engineer',",
  "  skills: ['Vue', 'Vite', 'Python', 'HTML', 'CSS', 'JavaScript'],",
  "  'ASP.NET Webform', 'ASP.NET Core', 'C#'],",
  "};",
  "",
  "async function startDay() {",
  "  console.log('🌞 早安！系統啟動中...');",
  "  ",
  "  try {",
  "    await Coffee.drink(); // 關鍵步驟",
  "    mike.mood = 'Ready to code 🚀';",
  "    ",
  "    // 嘗試修復昨天的 Bug...",
  "    // const bug = null; // 假裝沒看見",
  "    ",
  "    return createApp(Portfolio).mount('#app');",
  "  } catch (err) {",
  "    console.error('😱 崩潰啦：', err);",
  "    return '去睡覺吧';",
  "  }",
  "}",
  "",
  "// Status: 200 OK",
  "// Waiting for inspiration..."
];

// === VS Code Dark+ Theme Colors ===
const colors = {
  bg: '#1e1e1e',
  sideBar: '#252526', // 左側行號區背景
  titleBar: '#2d2d2d', // 上方標題列
  tabActive: '#1e1e1e', // 啟動的分頁
  tabInactive: '#2d2d2d', // 未啟動的分頁
  text: '#d4d4d4',
  keyword: '#569cd6',   // pink/purple
  string: '#ce9178',    // orange
  comment: '#6a9955',   // green
  func: '#dcdcaa',      // yellow
  number: '#b5cea8',    // light green
  lineNum: '#858585',
  cursor: '#d4d4d4'
};

const canvasRef = ref<HTMLCanvasElement | null>(null);

// 動畫狀態
let currentLineIndex = 0;
let currentCharIndex = 0;
let displayedLines: string[] = [];
let cursorVisible = true;
let typingTimer: any = null;
let blinkTimer: any = null;

// === 圖示載入輔助函式 ===
// 注意：這裡使用 font-awesome 的 unicode 或者是直接繪製簡單圖形來模擬 icon 會比較快
// 為了最佳效果，這裡我們使用 Emoji 或簡單的文字顏色來代表 Logo
const drawInterface = (ctx: CanvasRenderingContext2D) => {
  // 1. 主背景
  ctx.fillStyle = colors.bg;
  ctx.fillRect(0, 0, width, height);

  // 2. 行號區 (Gutter)
  ctx.fillStyle = colors.sideBar;
  ctx.fillRect(0, 0, 120, height);

  // 3. 標題欄 (Title Bar / Tabs Background)
  ctx.fillStyle = colors.titleBar;
  ctx.fillRect(0, 0, width, 80);

  // === 分頁繪製設定 ===
  const tabWidth = 350; // 每個分頁的寬度
  const tabHeight = 80;
  
  // -- Tab 1: App.vue (Active) --
  ctx.fillStyle = colors.tabActive; 
  ctx.fillRect(0, 0, tabWidth, tabHeight);
  
  // 頂部綠色線條 (Vue Green - Active Indicator)
  ctx.fillStyle = '#42b883'; 
  ctx.fillRect(0, 0, tabWidth, 3);

  // Vue Logo (使用 Emoji 替代或繪製簡單圖形) - 這裡用 V 作為 Logo 示意
  ctx.font = 'bold 36px "Segoe UI", Arial, sans-serif';
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';
  ctx.fillStyle = '#42b883'; // Vue Green
  ctx.fillText('V', 40, tabHeight / 2); // 簡單的 V 代表 Vue

  // 檔名文字
  ctx.font = 'bold 36px "Segoe UI", Arial, sans-serif';
  ctx.fillStyle = '#ffffff'; // Active Text White
  ctx.fillText('App.vue', 80, tabHeight / 2);
  
  // 關閉按鈕 (x)
  ctx.fillStyle = '#ffffff';
  ctx.font = '28px Arial';
  ctx.fillText('×', tabWidth - 40, tabHeight / 2);


  // -- Tab 2: main.py (Inactive) --
  const tab2X = tabWidth;
  ctx.fillStyle = colors.tabInactive; 
  // 繪製分隔線
  ctx.strokeStyle = '#1e1e1e';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(tab2X, 15);
  ctx.lineTo(tab2X, 65);
  ctx.stroke();

  // Python Logo (🐍) - 模擬
  ctx.font = '36px "Segoe UI Emoji", "Segoe UI", Arial, sans-serif';
  ctx.fillStyle = '#3776AB'; // Python Blue/Yellow mixed visual
  ctx.fillText('🐍', tab2X + 30, tabHeight / 2);

  // 檔名文字
  ctx.font = '36px "Segoe UI", Arial, sans-serif'; // Inactive use regular weight
  ctx.fillStyle = '#969696'; // Inactive Text Grey
  ctx.fillText('main.py', tab2X + 80, tabHeight / 2);


  // -- Tab 3: index.ts (Inactive) --
  const tab3X = tabWidth * 2;
  // 繪製分隔線
  ctx.beginPath();
  ctx.moveTo(tab3X, 15);
  ctx.lineTo(tab3X, 65);
  ctx.stroke();

  // TS Logo (TS)
  ctx.font = 'bold 28px "Segoe UI", Arial, sans-serif';
  ctx.fillStyle = '#3178C6'; // TS Blue
  ctx.fillText('TS', tab3X + 30, tabHeight / 2);

  // 檔名文字
  ctx.font = '36px "Segoe UI", Arial, sans-serif';
  ctx.fillStyle = '#969696';
  ctx.fillText('index.ts', tab3X + 80, tabHeight / 2);


  // 5. 底部狀態列 (保持不變)
  ctx.fillStyle = '#007acc';
  ctx.fillRect(0, height - 60, width, 60);
  ctx.fillStyle = 'white';
  ctx.font = '30px Arial';
  ctx.textBaseline = 'bottom'; // 恢復基準線設定，以免影響 drawCode
  ctx.fillText('main', 40, height - 20);
  ctx.textAlign = 'right';
  ctx.fillText('Vue TypeScript', width - 40, height - 20); // 更改為 Vue TypeScript
  ctx.fillText('Ln 12, Col 42', width - 350, height - 20);
};

const drawCode = (ctx: CanvasRenderingContext2D) => {
  ctx.font = fontSize;
  ctx.textBaseline = 'top';

  let y = padding.y;
  
  // 捲動邏輯
  const totalHeight = displayedLines.length * lineHeight;
  const maxCodeHeight = height - padding.y - 80; // 扣掉底部狀態列
  let scrollOffset = 0;
  
  if (totalHeight > maxCodeHeight) {
    scrollOffset = totalHeight - maxCodeHeight;
  }

  displayedLines.forEach((line, index) => {
    const drawY = y - scrollOffset;
    
    // 超出繪圖區域不繪製
    if (drawY < 80 || drawY > height - 60) {
      y += lineHeight;
      return; 
    }

    // 繪製行號
    ctx.fillStyle = colors.lineNum;
    ctx.textAlign = 'right';
    ctx.fillText((index + 1).toString(), 100, drawY);

    // 繪製程式碼內容
    ctx.textAlign = 'left';
    
    // 簡單語法高亮
    if (line.trim().startsWith('//')) {
      ctx.fillStyle = colors.comment;
    } else if (line.includes('import') || line.includes('const') || line.includes('function') || line.includes('return')) {
      ctx.fillStyle = colors.keyword;
    } else if (line.includes("'")) {
      ctx.fillStyle = colors.string;
    } else {
      ctx.fillStyle = colors.text;
    }
    
    ctx.fillText(line, 150, drawY);
    y += lineHeight;
  });

  // 繪製游標
  if (cursorVisible) {
    const lastLineIndex = displayedLines.length - 1;
    const lastLine = displayedLines[lastLineIndex] || '';
    
    // 計算游標位置
    ctx.font = fontSize; // 確保測量寬度時字型正確
    const textWidth = ctx.measureText(lastLine).width;
    
    const cursorX = 150 + textWidth;
    const cursorY = padding.y + (lastLineIndex * lineHeight) - scrollOffset;

    if (cursorY >= 80 && cursorY < height - 60) {
      ctx.fillStyle = colors.cursor;
      ctx.fillRect(cursorX + 5, cursorY, 4, 50); // 加粗游標
    }
  }
};

const draw = () => {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  drawInterface(ctx);
  drawCode(ctx);
};

const typeStep = () => {
  if (currentLineIndex >= codeLines.length) {
    // 重置循環
    typingTimer = setTimeout(() => {
      currentLineIndex = 0;
      currentCharIndex = 0;
      displayedLines = [];
      typeStep();
    }, 5000);
    return;
  }

  const currentFullLine = codeLines[currentLineIndex];
  if (currentFullLine === undefined) return;

  if (displayedLines.length <= currentLineIndex) {
    displayedLines.push('');
  }

  if (currentCharIndex < currentFullLine.length) {
    const char = currentFullLine[currentCharIndex] || '';
    if (displayedLines[currentLineIndex] !== undefined) {
      displayedLines[currentLineIndex] += char;
    }
    currentCharIndex++;
    draw();
    
    // 打字速度
    let speed = Math.random() * 30 + 20;
    if (char === ' ') speed = 10; // 空白鍵快一點
    typingTimer = setTimeout(typeStep, speed);
  } else {
    currentLineIndex++;
    currentCharIndex = 0;
    draw();
    typingTimer = setTimeout(typeStep, 150); // 換行停頓
  }
};

const blinkCursor = () => {
  cursorVisible = !cursorVisible;
  draw();
  blinkTimer = setTimeout(blinkCursor, 500);
};

onMounted(() => {
  draw();
  typeStep();
  blinkCursor();
});

onUnmounted(() => {
  clearTimeout(typingTimer);
  clearTimeout(blinkTimer);
});

defineExpose({ canvasRef });
</script>

<template>
  <canvas ref="canvasRef" :width="width" :height="height" style="display: none;"></canvas>
</template>