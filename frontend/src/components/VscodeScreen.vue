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
  "// --------------------------------",
  "//  Auto-generating Portfolio...   ",
  "// --------------------------------",
  "import { Experience } from 'data';",
  "",
  "const developer = {",
  "  name: 'Mikey Wang',",
  "  role: 'Frontend Engineer',",
  "  skills: ['Vue', 'Three.js', 'Python'],",
  "  status: 'Ready to code 🚀'",
  "};",
  "",
  "function initWorld() {",
  "  console.log('Hello World!');",
  "  return <Portfolio />;",
  "}",
  "",
  "// Status: 200 OK",
  "// Waiting for user input..."
];

// === VS Code Dark+ Theme Colors ===
const colors = {
  bg: '#1e1e1e',
  sideBar: '#252526', // 左側行號區背景
  titleBar: '#2d2d2d', // 上方標題列
  tabActive: '#1e1e1e', // 啟動的分頁
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

const drawInterface = (ctx: CanvasRenderingContext2D) => {
  // 1. 主背景
  ctx.fillStyle = colors.bg;
  ctx.fillRect(0, 0, width, height);

  // 2. 行號區 (Gutter)
  ctx.fillStyle = colors.sideBar;
  ctx.fillRect(0, 0, 120, height);

  // 3. 標題欄 (Title Bar / Tabs)
  ctx.fillStyle = colors.titleBar; // Tab Bar Background
  ctx.fillRect(0, 0, width, 80);

  // 4. 繪製 "App.tsx" 分頁標籤
  ctx.fillStyle = colors.tabActive; // Active Tab Background
  ctx.fillRect(0, 0, 300, 80);
  
  // 分頁上方的藍色線條
  ctx.fillStyle = '#007acc';
  ctx.fillRect(0, 0, 300, 3);

  // 分頁文字 "App.tsx"
  ctx.font = 'bold 36px "Segoe UI", Arial, sans-serif';
  ctx.fillStyle = '#ffffff';
  ctx.textAlign = 'left';
  ctx.fillText('⚛️ App.tsx', 40, 50);
  
  // 其他分頁 (暗淡)
  ctx.fillStyle = '#969696';
  ctx.fillText('main.py', 340, 50);
  ctx.fillText('style.css', 550, 50);

  // 5. 底部狀態列
  ctx.fillStyle = '#007acc';
  ctx.fillRect(0, height - 60, width, 60);
  ctx.fillStyle = 'white';
  ctx.font = '30px Arial';
  ctx.fillText('main', 40, height - 20);
  ctx.textAlign = 'right';
  ctx.fillText('TypeScript React', width - 40, height - 20);
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