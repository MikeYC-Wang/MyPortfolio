<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const codeLines = [
  "// ---------------------------------------------",
  "<span class='comment'>// Auto-generating Portfolio Content...</span>",
  "// ---------------------------------------------",
  "<span class='keyword'>import</span> { Experience, Project } <span class='keyword'>from</span> <span class='string'>'data/portfolio'</span>;",
  "",
  "<span class='const'>const</span> name = <span class='string'>'Mikey Wang'</span>;",
  "<span class='const'>const</span> isReady = <span class='boolean'>true</span>;",
  "",
  "<span class='function'>function</span> <span class='func-name'>renderProjects</span>(p: Project[]) {",
  "  <span class='keyword'>return</span> p.<span class='method'>map</span>(proj => (",
  "    <span class='tag-name'>&lt;div</span> <span class='attr-name'>key</span>={proj.<span class='property'>id</span>}<span class='tag-name'>&gt;</span>",
  "      <span class='property'>proj</span>.<span class='property'>title</span>",
  "    <span class='tag-name'>&lt;/div&gt;</span>",
  "  ));",
  "}",
  "",
  "<span class='comment'>// Connecting to web 3.0 via WebGL...</span>",
  "<span class='comment'>// Status: 200 OK</span>",
];

const animatedCode = ref('');
let lineIndex = 0;
let charIndex = 0;
let isTyping = true;
let animationTimer: number | null = null;

const startTypingAnimation = () => {
  if (!isTyping) return;

  // 檢查並重置索引
  if (lineIndex >= codeLines.length) {
     lineIndex = 0;
     charIndex = 0;
     isTyping = true;
  }

  // 使用非空斷言符 '!' 解決 TypeScript 警告
  const currentLine = codeLines[lineIndex]!; 
  const rawLength = currentLine.length;

  if (charIndex < rawLength) {
    let nextChar = currentLine.substring(charIndex, charIndex + 1);
    let advance = 1;

    // 處理 HTML 標籤
    if (nextChar === '<') {
      const tagEnd = currentLine.indexOf('>', charIndex);
      if (tagEnd !== -1) {
        nextChar = currentLine.substring(charIndex, tagEnd + 1);
        advance = tagEnd - charIndex + 1;
      }
    }

    animatedCode.value += nextChar;
    charIndex += advance;
    
    // 加速跳過標籤
    const delay = advance > 1 ? 0 : 30; 
    animationTimer = setTimeout(startTypingAnimation, delay);

  } else {
    // 換行
    animatedCode.value += '<br>';
    lineIndex++;
    charIndex = 0;

    if (lineIndex >= codeLines.length) {
      isTyping = false;
      // 重複打字動畫
      animationTimer = setTimeout(() => {
        animatedCode.value = '';
        lineIndex = 0;
        isTyping = true;
        startTypingAnimation();
      }, 5000); 
      return;
    }

    animationTimer = setTimeout(startTypingAnimation, 100);
  }
};

onMounted(() => {
  startTypingAnimation();
});

onUnmounted(() => {
  if (animationTimer !== null) {
    clearTimeout(animationTimer);
  }
});
</script>

<template>
  <div id="vscode-screen-source" class="vscode-theme">
    <div class="editor">
      <div class="line-numbers">
        <span v-for="n in 17" :key="n">{{ n }}</span>
      </div>
      <div class="code-area" v-html="animatedCode"></div>
      <div class="cursor" v-if="isTyping"></div>
    </div>
    <div class="status-bar">
      <span>&#x2705; Ready</span>
      <span>Vue(TSX)</span>
      <span>UTF-8</span>
    </div>
  </div>
</template>

<style scoped>
/* 確保元件隱藏在視圖外，但仍能被 DOM 渲染 */
#vscode-screen-source {
  position: absolute;
  top: 0;
  left: -9999px; 
  width: 1024px; 
  height: 768px; 
  color: #D4D4D4; 
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 32px; 
  overflow: hidden;
  box-sizing: border-box;
}

.vscode-theme {
  background-color: #1e1e1e;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.editor {
  flex-grow: 1;
  display: flex;
  padding-top: 10px;
  overflow-y: hidden;
  position: relative;
}

.line-numbers {
  display: flex;
  flex-direction: column;
  color: #858585;
  text-align: right;
  padding: 0 15px;
  user-select: none;
  line-height: 1.5;
}

.line-numbers span {
  counter-increment: linenumber;
  height: 1.5em;
}

.code-area {
  flex-grow: 1;
  white-space: nowrap;
  line-height: 1.5;
}

/* 游標模擬 */
.cursor {
  position: absolute;
  left: 310px; 
  top: 320px; 
  width: 2px;
  height: 1.5em;
  background-color: #D4D4D4;
  animation: blink 0.7s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* 狀態列 */
.status-bar {
  height: 40px;
  background-color: #007ACC;
  color: white;
  font-size: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 10px;
}

/* 語法高亮模擬 */
.code-area :deep(.comment) { color: #6a9955; }
.code-area :deep(.keyword) { color: #569cd6; } 
.code-area :deep(.const) { color: #4fc08d; }
.code-area :deep(.string) { color: #ce9178; } 
.code-area :deep(.tag-name) { color: #569cd6; } 
.code-area :deep(.attr-name) { color: #9cdcfe; } 
.code-area :deep(.property) { color: #d4d4d4; } 
.code-area :deep(.function) { color: #dcdcaa; } 
.code-area :deep(.method) { color: #dcdcaa; } 
.code-area :deep(.func-name) { color: #4ec9b0; } 
.code-area :deep(.boolean) { color: #569cd6; }
</style>