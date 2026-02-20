<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';

// === 圖表 1: 伺服器監控 (保持原樣) ===
const chartContainer = ref<HTMLElement | null>(null);
let myChart: echarts.ECharts | null = null;
let pollingTimer: number | null = null;

const MAX_POINTS = 30; 
const timeData = ref<string[]>([]);
const cpuData = ref<number[]>([]);
const ramData = ref<number[]>([]);
const gpuData = ref<number[]>([]); 

const fetchSystemStatus = async () => {
  try {
    const res = await axios.get('/api/system_status');
    const { cpu, ram, gpu } = res.data; 
    
    const now = new Date();
    const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;

    timeData.value.push(timeStr);
    cpuData.value.push(cpu);
    ramData.value.push(ram);
    gpuData.value.push(gpu); 

    if (timeData.value.length > MAX_POINTS) {
      timeData.value.shift();
      cpuData.value.shift();
      ramData.value.shift();
      gpuData.value.shift(); 
    }

    if (myChart) {
      myChart.setOption({
        xAxis: { data: timeData.value },
        series: [
          { data: cpuData.value }, 
          { data: ramData.value },  
          { data: gpuData.value }  
        ]
      });
    }
  } catch (error) {
    console.error('無法取得系統數據:', error);
  }
};

// === 圖表 2: 真實 GitHub 貢獻度熱力圖 ===
const heatmapContainer = ref<HTMLElement | null>(null);
let heatmapChart: echarts.ECharts | null = null;

const fetchGithubData = async () => {
  try {
    const res = await axios.get('/api/github_contributions');
    if (res.data && res.data.length > 0) {
      // 拿到真實數據後，更新熱力圖
      if (heatmapChart) {
        heatmapChart.setOption({
          series: [{ data: res.data }]
        });
      }
    }
  } catch (error) {
    console.error('無法取得 GitHub 數據:', error);
  }
};

// === 生命週期 ===
onMounted(async () => {
  // --- 初始化圖表 1 (伺服器監控) ---
  if (chartContainer.value) {
    myChart = echarts.init(chartContainer.value); 
    const option = {
      color: ['#00f2ff', '#bd00ff', '#00ff41'], 
      backgroundColor: 'transparent',
      title: { text: 'SERVER PERFORMANCE MONITOR', textStyle: { color: '#00f2ff', fontSize: 16, fontWeight: 'bold', fontFamily: 'monospace' }, left: '20px', top: '20px' },
      tooltip: { trigger: 'axis', backgroundColor: 'rgba(13, 17, 23, 0.8)', borderColor: '#00f2ff', textStyle: { color: '#fff', fontFamily: 'monospace' }, axisPointer: { type: 'cross', label: { backgroundColor: '#00f2ff', color: '#000' }, lineStyle: { color: '#00f2ff', type: 'dashed' } } },
      legend: { data: ['CPU Usage (%)', 'RAM Usage (%)', 'GPU Usage (%)'], textStyle: { color: '#888' }, top: '60px', right: '30px' },
      grid: { left: '4%', right: '4%', bottom: '5%', top: '25%', containLabel: true, show: false },
      xAxis: { type: 'category', boundaryGap: false, data: [], axisLine: { lineStyle: { color: '#00f2ff' } }, axisLabel: { color: '#888', fontFamily: 'monospace' }, axisTick: { show: false }, splitLine: { show: true, lineStyle: { color: 'rgba(0, 242, 255, 0.1)', type: 'dashed' } } },
      yAxis: [{ type: 'value', name: 'Usage (%)', min: 0, max: 100, axisLine: { lineStyle: { color: '#888' } }, axisLabel: { color: '#888', formatter: '{value} %' }, splitLine: { lineStyle: { color: 'rgba(136, 136, 136, 0.2)', type: 'dashed' } }, nameTextStyle: { color: '#888' } }],
      series: [
        { name: 'CPU Usage (%)', type: 'line', smooth: true, symbol: 'none', lineStyle: { width: 3, shadowColor: 'rgba(0, 242, 255, 0.5)', shadowBlur: 10, shadowOffsetY: 5 }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(0, 242, 255, 0.5)' }, { offset: 1, color: 'rgba(0, 242, 255, 0.05)' }]) }, data: [] },
        { name: 'RAM Usage (%)', type: 'line', smooth: true, symbol: 'none', lineStyle: { width: 3, shadowColor: 'rgba(189, 0, 255, 0.5)', shadowBlur: 10, shadowOffsetY: 5 }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(189, 0, 255, 0.5)' }, { offset: 1, color: 'rgba(189, 0, 255, 0.05)' }]) }, data: [] },
        { name: 'GPU Usage (%)', type: 'line', smooth: true, symbol: 'none', lineStyle: { width: 3, shadowColor: 'rgba(0, 255, 65, 0.5)', shadowBlur: 10, shadowOffsetY: 5 }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(0, 255, 65, 0.5)' }, { offset: 1, color: 'rgba(0, 255, 65, 0.05)' }]) }, data: [] }
      ]
    };
    myChart.setOption(option);
    await fetchSystemStatus(); 
    pollingTimer = window.setInterval(fetchSystemStatus, 5000); 
  }

  // --- 初始化圖表 2 (GitHub 熱力圖) ---
  if (heatmapContainer.value) {
    heatmapChart = echarts.init(heatmapContainer.value);
    
    const end = new Date();
    const start = new Date();
    start.setFullYear(end.getFullYear() - 1);

    const heatmapOption = {
      backgroundColor: 'transparent',
      tooltip: {
        position: 'top',
        backgroundColor: 'rgba(44, 44, 44, 0.9)',
        borderColor: '#d4b595', 
        textStyle: { color: '#fff' },
        formatter: function (p: any) {
          const format = echarts.time.format(p.data[0], '{yyyy}-{MM}-{dd}', false);
          return `${format} <br/> 貢獻指標: <span style="color:#e6ccb2; font-weight:bold;">${p.data[1]}</span>`;
        }
      },
      visualMap: {
        min: 0,
        max: 10, // 最大值配合我們的 level_map 設定為 10
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: '0',
        textStyle: { color: '#888' },
        inRange: {
          color: ['rgba(230, 204, 178, 0.1)', '#e6ccb2', '#d4b595', '#a1887f', '#5d4037']
        }
      },
      calendar: [{
        top: 30, bottom: 60, left: 45, right: 30,
        range: [
          echarts.time.format(start, '{yyyy}-{MM}-{dd}', false),
          echarts.time.format(end, '{yyyy}-{MM}-{dd}', false)
        ],
        cellSize: ['auto', 20], 
        itemStyle: { color: 'rgba(255, 255, 255, 0.02)', borderWidth: 2, borderColor: 'transparent' },
        splitLine: { show: false }, yearLabel: { show: false }, 
        dayLabel: { color: '#888', nameMap: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'] },
        monthLabel: { color: '#888', nameMap: 'EN' }
      }],
      series: [{
        type: 'heatmap',
        coordinateSystem: 'calendar',
        data: [],
        itemStyle: { borderRadius: 4, borderColor: 'transparent', borderWidth: 2 }
      }]
    };
    heatmapChart.setOption(heatmapOption);
    
    await fetchGithubData();
  }

  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (pollingTimer) window.clearInterval(pollingTimer);
  if (myChart) myChart.dispose();
  if (heatmapChart) heatmapChart.dispose();
});

const handleResize = () => {
  if (myChart) myChart.resize();
  if (heatmapChart) heatmapChart.resize();
};
</script>

<template>
  <div class="dashboard-page">
    <div class="dashboard-wrapper">
      
      <div class="header-actions">
        <h1 class="page-title">
          <i class="fa-solid fa-server"></i> 系統監控與數據分析
        </h1>
        
        <RouterLink to="/" class="back-btn">
          <i class="fa-solid fa-arrow-left"></i> 返回首頁
        </RouterLink>
      </div>

      <div class="monitor-card mb-4">
        <div ref="chartContainer" class="echarts-box"></div>
        <div class="scan-line"></div>
      </div>

      <div class="monitor-card heatmap-card">
        <div class="card-header">
          <h2><i class="fa-brands fa-github"></i> 開發活躍度 (Contribution Heatmap)</h2>
          <span class="subtitle">近一年的程式碼提交紀錄</span>
        </div>
        
        <div class="heatmap-scroll-wrapper">
          <div ref="heatmapContainer" class="heatmap-box"></div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* --- 全域排版 --- */
.dashboard-page {
  min-height: 100vh;
  padding: 80px 20px 60px; 
  display: flex;
  justify-content: center;
}

.dashboard-wrapper {
  width: 100%;
  max-width: 1200px;
}

.mb-4 {
  margin-bottom: 30px;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 15px;
}

.page-title {
  margin: 0;
  font-size: 2rem;
  background: var(--gradient-text);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background-color: var(--btn-bg);
  color: var(--text-color);
  text-decoration: none;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  font-weight: bold;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background-color: var(--btn-hover);
  color: var(--link-active);
  transform: translateY(-2px);
}

/* --- 卡片共用樣式 --- */
.monitor-card {
  position: relative;
  background-color: var(--card-bg);
  border: 1px solid var(--card-border);
  box-shadow: var(--card-shadow);
  border-radius: 16px;
  padding: 20px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.monitor-card:hover {
  box-shadow: var(--card-hover-shadow);
}

.echarts-box {
  width: 100%;
  height: 55vh;
  min-height: 400px;
}

.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: rgba(0, 242, 255, 0.15);
  box-shadow: 0 0 10px rgba(0, 242, 255, 0.2);
  animation: scan 6s linear infinite;
  opacity: 0.8;
  pointer-events: none;
}

@keyframes scan {
  0% { top: -5%; }
  100% { top: 105%; }
}

/* --- 熱力圖專屬樣式 --- */
.heatmap-card {
  padding: 30px;
}

.card-header {
  margin-bottom: 10px;
  text-align: left;
}

.card-header h2 {
  margin: 0 0 5px 0;
  font-size: 1.4rem;
  color: var(--text-color);
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-header .subtitle {
  font-size: 0.9rem;
  color: #888;
}

.heatmap-scroll-wrapper {
  width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 10px; /* 給底部捲軸留一點空間 */
  
  /* Firefox 捲軸美化 */
  scrollbar-width: thin;
  scrollbar-color: var(--link-active) transparent;
}

.heatmap-scroll-wrapper::-webkit-scrollbar {
  height: 6px;
}
.heatmap-scroll-wrapper::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}
.heatmap-scroll-wrapper::-webkit-scrollbar-thumb {
  background: var(--link-active);
  border-radius: 4px;
}

.heatmap-box {
  width: 100%;
  min-width: 800px; 
  height: 250px; 
}

@media (max-width: 768px) {
  .heatmap-card {
    padding: 20px 15px;
  }

  .card-header {
    overflow-x: auto;
    scrollbar-width: none;
  }
  .card-header::-webkit-scrollbar {
    display: none;
  }

  .card-header h2 {
    font-size: 1.05rem;
    white-space: nowrap;
  }

  .card-header .subtitle {
    font-size: 0.8rem;
    white-space: nowrap;
    display: block;
  }

  .monitor-card {
    padding: 15px;
  }
}
</style>