<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

// === 高解析度設定 (FHD) ===
const width = 1920;
const height = 1080;
const padding = { x: 60, y: 120 };
const lineHeight = 60;
const fontSize = 'bold 42px "Menlo", "Monaco", "Courier New", monospace';

// ... (codeLines 與 colors 設定保持不變，為了版面整潔這裡省略，請保留原本的內容) ...
const codeLines = [
  "import { Experience } from 'data';",
  "",
  "const developer = {",
  "  name: 'Mike Wang',",
  "  role: 'Frontend Engineer',",
  "  skills: [",
  "    'Vue', 'Vite', 'Python', 'HTML', 'CSS', 'JavaScript',",
  "    'ASP.NET Webform', 'ASP.NET Core', 'C#'",
  "  ],",
  "};",
  "",
  "async function startDay() {",
  "  console.log('☀ 早安！系統啟動中...');",
  "  ",
  "  try {",
  "    await Coffee.drink(); // 關鍵步驟",
  "    developer.mood = 'Ready to code ✎... ';",
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

const colors = {
  bg: '#1e1e1e',
  sideBar: '#252526',
  titleBar: '#2d2d2d',
  tabActive: '#1e1e1e',
  tabInactive: '#2d2d2d',
  text: '#d4d4d4',
  keyword: '#569cd6',
  string: '#ce9178',
  comment: '#6a9955',
  func: '#dcdcaa',
  number: '#b5cea8',
  lineNum: '#858585',
  cursor: '#d4d4d4'
};

const canvasRef = ref<HTMLCanvasElement | null>(null);
const pythonIcon = new Image();
pythonIcon.src = '/python-logo.png';
let isPythonIconLoaded = false;

pythonIcon.onload = () => {
  isPythonIconLoaded = true;
  if (isPoweredOn) {
    cacheBackground();
    isDirty = true;
  }
};

// 動畫狀態
let currentLineIndex = 0;
let currentCharIndex = 0;
let displayedLines: string[] = [];
let cursorVisible = true;
let typingTimer: any = null;
let blinkTimer: any = null;
let isPoweredOn = false;
let bgCanvas: HTMLCanvasElement | null = null;
let isDirty = false;
let rafId: number;

const cacheBackground = () => {
  bgCanvas = document.createElement('canvas');
  bgCanvas.width = width;
  bgCanvas.height = height;
  const ctx = bgCanvas.getContext('2d');
  if (ctx) drawInterface(ctx);
};

// === 繪製介面 (保留原本的 drawInterface 函式) ===
const drawInterface = (ctx: CanvasRenderingContext2D) => {
    // ... (保留原本的 drawInterface 內容) ...
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

    // Vue Logo (V)
    ctx.font = 'bold 36px "Segoe UI", Arial, sans-serif';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#42b883'; // Vue Green
    ctx.fillText('V', 40, tabHeight / 2);

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

    // Python Logo (Py)
if (isPythonIconLoaded) {
    const iconSize = 36;
    const iconY = (tabHeight - iconSize) / 2; 
    ctx.drawImage(pythonIcon, tab2X + 25, iconY, iconSize, iconSize);
  } else {
    ctx.font = '36px "Segoe UI Emoji", "Segoe UI", Arial, sans-serif';
    ctx.fillStyle = '#3776AB'; 
    ctx.fillText('Py', tab2X + 30, tabHeight / 2);
  }

    // 檔名文字
    ctx.font = '36px "Segoe UI", Arial, sans-serif'; 
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

    // 5. 底部狀態列
    ctx.fillStyle = '#007acc';
    ctx.fillRect(0, height - 60, width, 60);
    ctx.fillStyle = 'white';
    ctx.font = '30px Arial';
    ctx.textBaseline = 'bottom'; 
    ctx.textAlign = 'left';
    ctx.fillText('main', 40, height - 20);
    ctx.textAlign = 'right';
    ctx.fillText('Vue TypeScript', width - 40, height - 20);
    ctx.fillText('Ln 12, Col 42', width - 350, height - 20);
};

// === 繪製程式碼內容 (保留原本的 drawCode 函式) ===
const drawCode = (ctx: CanvasRenderingContext2D) => {
    // ... (保留原本的 drawCode 內容) ...
    ctx.font = fontSize;
    ctx.textBaseline = 'top';

    let y = padding.y;
    
    // 捲動邏輯 (當內容超過畫面時向上捲動)
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
    } else if (line.includes('import') || line.includes('const') || line.includes('function') || line.includes('return') || line.includes('async') || line.includes('await') || line.includes('try') || line.includes('catch')) {
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

    // 確保游標只在可視區域內繪製
    if (cursorY >= 80 && cursorY < height - 60) {
        ctx.fillStyle = colors.cursor;
        ctx.fillRect(cursorX + 5, cursorY, 4, 50); // 加粗游標
    }
    }
};

const draw = () => {
  isDirty = true;
};

const renderLoop = () => {
  if (isDirty && isPoweredOn) {
    const canvas = canvasRef.value;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        if (bgCanvas) {
          ctx.drawImage(bgCanvas, 0, 0); 
        } else {
          drawInterface(ctx);
        }

        drawCode(ctx);
      }
    }
    isDirty = false; // 畫完就清除標記
  }
  rafId = requestAnimationFrame(renderLoop);
};

// 打字機邏輯 (保留不變)
const typeStep = () => {
  if (!isPoweredOn) return; // 如果沒開機就不執行

  if (currentLineIndex >= codeLines.length) {
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
    
    let speed = Math.random() * 30 + 20;
    if (char === ' ') speed = 10;
    typingTimer = setTimeout(typeStep, speed);
  } else {
    currentLineIndex++;
    currentCharIndex = 0;
    draw();
    typingTimer = setTimeout(typeStep, 150);
  }
};

const blinkCursor = () => {
  if (isPoweredOn) {
    cursorVisible = !cursorVisible;
    draw();
  }
  blinkTimer = setTimeout(blinkCursor, 500);
};

// === 新增：開機動畫與邏輯 ===
const turnOn = async () => {
    if (isPoweredOn) return;
    
    const canvas = canvasRef.value;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // 1. 播放 BIOS / Loading 動畫
    let progress = 0;
    
    const drawBoot = () => {
        // 背景全黑
        ctx.fillStyle = '#000000';
        ctx.fillRect(0, 0, width, height);

        // 文字資訊
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 40px "Courier New", monospace';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'top';
        
        ctx.fillText('PORTFOLIO BIOS v1.0.2', 50, 50);
        ctx.fillText('CPU: M1 Neural Engine @ 3.2GHz', 50, 110);
        ctx.fillText('Memory: 64GB Unified', 50, 170);
        ctx.fillText('Checking Peripherals...', 50, 230);
        
        if (progress > 30) ctx.fillText('  - Keyboard: OK', 50, 290);
        if (progress > 60) ctx.fillText('  - Mouse: OK', 50, 350);
        if (progress > 80) ctx.fillText('  - Graphics: OK', 50, 410);

        // Loading Bar
        const barWidth = 800;
        const barHeight = 20;
        const barX = (width - barWidth) / 2;
        const barY = height / 2 + 100;

        // 外框
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 4;
        ctx.strokeRect(barX, barY, barWidth, barHeight);

        // 填充
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(barX + 5, barY + 5, (barWidth - 10) * (progress / 100), barHeight - 10);
        
        ctx.textAlign = 'center';
        ctx.fillText(`LOADING SYSTEM... ${Math.floor(progress)}%`, width / 2, barY + 50);
    };

    return new Promise<void>((resolve) => {
        const interval = setInterval(() => {
            progress += 1.5; // 控制載入速度
            drawBoot();

            if (progress >= 100) {
                clearInterval(interval);
                isPoweredOn = true;
                cacheBackground(); 
                isDirty = true; 
                typeStep();
                resolve();
            }
        }, 16); // 60FPS
    });
};

onMounted(() => {
  const canvas = canvasRef.value;
  if (canvas) {
    const ctx = canvas.getContext('2d');
    if (ctx) {
        ctx.fillStyle = '#0a0a0a'; 
        ctx.fillRect(0, 0, width, height);
    }
  }
  
  blinkCursor();
  rafId = requestAnimationFrame(renderLoop);
});

onUnmounted(() => {
  clearTimeout(typingTimer);
  clearTimeout(blinkTimer);
  cancelAnimationFrame(rafId);
});

// 公開方法給父元件
defineExpose({ canvasRef, turnOn, isPoweredOn });
</script>

<template>
  <canvas ref="canvasRef" :width="width" :height="height" style="display: none;"></canvas>
</template>