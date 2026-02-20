<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';

const chartContainer = ref<HTMLElement | null>(null);
let myChart: echarts.ECharts | null = null;
let pollingTimer: number | null = null;

const MAX_POINTS = 30; 
const timeData = ref<string[]>([]);
const cpuData = ref<number[]>([]);
const ramData = ref<number[]>([]);
const gpuData = ref<number[]>([]); // ✨ 新增 GPU 陣列

const fetchSystemStatus = async () => {
  try {
    const res = await axios.get('/api/system_status');
    const { cpu, ram, gpu } = res.data; // ✨ 接收 GPU 數據
    
    const now = new Date();
    const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;

    timeData.value.push(timeStr);
    cpuData.value.push(cpu);
    ramData.value.push(ram);
    gpuData.value.push(gpu); // ✨ 存入 GPU 陣列

    if (timeData.value.length > MAX_POINTS) {
      timeData.value.shift();
      cpuData.value.shift();
      ramData.value.shift();
      gpuData.value.shift(); // ✨ 同步剔除最舊的 GPU 數據
    }

    if (myChart) {
      myChart.setOption({
        xAxis: { data: timeData.value },
        series: [
          { data: cpuData.value }, 
          { data: ramData.value },  
          { data: gpuData.value }  // ✨ 對應第三個 series (GPU)
        ]
      });
    }
  } catch (error) {
    console.error('無法取得系統數據:', error);
  }
};

onMounted(async () => {
  if (chartContainer.value) {
    myChart = echarts.init(chartContainer.value); 

    const option = {
      // ✨ 加入第三種顏色：青色(CPU), 紫色(RAM), 駭客綠(GPU)
      color: ['#00f2ff', '#bd00ff', '#00ff41'], 
      backgroundColor: 'transparent',
      title: {
        text: 'SERVER PERFORMANCE MONITOR',
        textStyle: { color: '#00f2ff', fontSize: 16, fontWeight: 'bold', fontFamily: 'monospace' },
        left: '20px',
        top: '20px'
      },
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(13, 17, 23, 0.8)',
        borderColor: '#00f2ff',
        textStyle: { color: '#fff', fontFamily: 'monospace' },
        axisPointer: {
          type: 'cross',
          label: { backgroundColor: '#00f2ff', color: '#000' },
          lineStyle: { color: '#00f2ff', type: 'dashed' }
        }
      },
      legend: {
        // ✨ 圖例加入 GPU
        data: ['CPU Usage (%)', 'RAM Usage (%)', 'GPU Usage (%)'], 
        textStyle: { color: '#888' },
        top: '60px',
        right: '30px'
      },
      grid: {
        left: '4%', right: '4%', bottom: '5%', top: '25%', containLabel: true,
        show: false 
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: [], 
        axisLine: { lineStyle: { color: '#00f2ff' } },
        axisLabel: { color: '#888', fontFamily: 'monospace' },
        axisTick: { show: false },
        splitLine: { 
            show: true, 
            lineStyle: { color: 'rgba(0, 242, 255, 0.1)', type: 'dashed' } 
        }
      },
      yAxis: [
        {
          type: 'value',
          name: 'Usage (%)', // ✨ 將 Y 軸名稱統整為 Usage
          min: 0, max: 100,
          axisLine: { lineStyle: { color: '#888' } },
          axisLabel: { color: '#888', formatter: '{value} %' },
          splitLine: { lineStyle: { color: 'rgba(136, 136, 136, 0.2)', type: 'dashed' } },
          nameTextStyle: { color: '#888' }
        }
      ],
      series: [
        // CPU
        {
          name: 'CPU Usage (%)',
          type: 'line',
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 3, shadowColor: 'rgba(0, 242, 255, 0.5)', shadowBlur: 10, shadowOffsetY: 5 },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(0, 242, 255, 0.5)' },
              { offset: 1, color: 'rgba(0, 242, 255, 0.05)' }
            ])
          },
          data: [] 
        },
        // RAM
        {
          name: 'RAM Usage (%)', 
          type: 'line',
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 3, shadowColor: 'rgba(189, 0, 255, 0.5)', shadowBlur: 10, shadowOffsetY: 5 },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(189, 0, 255, 0.5)' },
              { offset: 1, color: 'rgba(189, 0, 255, 0.05)' }
            ])
          },
          data: [] 
        },
        // ✨ GPU (駭客綠)
        {
          name: 'GPU Usage (%)', 
          type: 'line',
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 3, shadowColor: 'rgba(0, 255, 65, 0.5)', shadowBlur: 10, shadowOffsetY: 5 },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(0, 255, 65, 0.5)' },
              { offset: 1, color: 'rgba(0, 255, 65, 0.05)' }
            ])
          },
          data: [] 
        }
      ]
    };

    myChart.setOption(option);
    window.addEventListener('resize', handleResize);

    await fetchSystemStatus(); 
    pollingTimer = window.setInterval(fetchSystemStatus, 10000); 
  }
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (pollingTimer) window.clearInterval(pollingTimer);
  if (myChart) myChart.dispose();
});

const handleResize = () => {
  if (myChart) myChart.resize();
};
</script>

<template>
  <div class="dashboard-page">
    <div class="dashboard-wrapper">
      
      <div class="header-actions">
        <h1 class="page-title">
          <i class="fa-solid fa-gauge"></i> 系統監控控制台 </h1>
        
        <RouterLink to="/" class="back-btn">
          <i class="fa-solid fa-arrow-left"></i> 返回首頁
        </RouterLink>
      </div>

      <div class="monitor-card">
        <div ref="chartContainer" class="echarts-box"></div>
        <div class="scan-line"></div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* 頁面外層，維持滿版，文字顏色吃全域設定 */
.dashboard-page {
  min-height: 100vh;
  padding: 80px 20px 40px; 
  display: flex;
  justify-content: center;
}

.dashboard-wrapper {
  width: 100%;
  max-width: 1200px;
}

/* 標題與按鈕的排版 */
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 15px;
}

/* 套用漸層文字與 FontAwesome */
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

/* 統一使用 Theme.css 的按鈕變數 */
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

/* 讓圖表外框完全吃 Theme.css 的卡片設定 */
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
  height: 65vh;
  min-height: 450px;
}

/* 輕微的科技感掃描線 */
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
</style>