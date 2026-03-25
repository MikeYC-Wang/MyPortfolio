<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import * as echarts from 'echarts';
// import axios from 'axios';
import axios from '@/api';
import SiteFooter from '@/components/SiteFooter.vue';

// === 圖表 1: 伺服器監控 ===
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

// === 圖表 2: API 流量監控 ===
const apiChartContainer = ref<HTMLElement | null>(null);
let apiChart: echarts.ECharts | null = null;

const fetchApiStats = async () => {
  try {
    const res = await axios.get('/api/stats/api-calls');
    const dates = res.data.map((d: any) => d.date);
    const counts = res.data.map((d: any) => d.count);
    
    if (apiChart) {
      apiChart.setOption({
        xAxis: { data: dates },
        series: [{ data: counts }]
      });
    }
  } catch (error) {
    console.error('無法取得 API 數據:', error);
  }
};

// === 圖表 3: 真實 GitHub 貢獻度熱力圖 ===
const heatmapContainer = ref<HTMLElement | null>(null);
let heatmapChart: echarts.ECharts | null = null;

const fetchGithubData = async () => {
  try {
    const res = await axios.get('/api/github_contributions');
    if (res.data && res.data.length > 0) {
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
    pollingTimer = window.setInterval(fetchSystemStatus, 1000); 
  }

  // --- 初始化圖表 2 (API 流量監控) ---
  if (apiChartContainer.value) {
    apiChart = echarts.init(apiChartContainer.value);
    const apiOption = {
      backgroundColor: 'transparent',
      title: { 
        text: 'API TRAFFIC (LAST 7 DAYS)', 
        textStyle: { color: '#e2a6ff', fontSize: 16, fontWeight: 'bold', fontFamily: 'monospace' }, 
        left: '20px', top: '20px' 
      },
      tooltip: { 
        trigger: 'axis', 
        backgroundColor: 'rgba(13, 17, 23, 0.9)', 
        borderColor: '#e2a6ff', 
        textStyle: { color: '#fff', fontFamily: 'monospace' } 
      },
      grid: { left: '4%', right: '4%', bottom: '5%', top: '25%', containLabel: true },
      xAxis: { 
        type: 'category', 
        boundaryGap: false, 
        data: [], 
        axisLine: { lineStyle: { color: '#e2a6ff' } }, 
        axisLabel: { color: '#888', fontFamily: 'monospace' } 
      },
      yAxis: { 
        type: 'value', 
        name: 'Requests',
        nameTextStyle: { color: '#888' },
        axisLine: { lineStyle: { color: '#888' } }, 
        splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.05)', type: 'dashed' } }, 
        axisLabel: { color: '#888', fontFamily: 'monospace' } 
      },
      series: [
        {
          name: 'API Calls',
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          itemStyle: { color: '#e2a6ff' },
          lineStyle: { width: 3, shadowColor: 'rgba(226, 166, 255, 0.5)', shadowBlur: 10 },
          areaStyle: { 
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(226, 166, 255, 0.5)' }, 
              { offset: 1, color: 'rgba(226, 166, 255, 0.02)' }
            ]) 
          },
          data: []
        }
      ]
    };
    apiChart.setOption(apiOption);
    await fetchApiStats();
  }

  // --- 初始化圖表 3 (GitHub 熱力圖) ---
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
        appendToBody: true,
        extraCssText: 'z-index: 9999;',
        formatter: function (p: any) {
          const format = echarts.time.format(p.data[0], '{yyyy}-{MM}-{dd}', false);
          return `${format} <br/> 貢獻指標: <span style="color:#e6ccb2; font-weight:bold;">${p.data[1]}</span>`;
        }
      },
      visualMap: {
        min: 0, max: 10, calculable: true, orient: 'horizontal', left: 'center', bottom: '0',
        textStyle: { color: '#888' },
        inRange: { color: ['rgba(230, 204, 178, 0.1)', '#e6ccb2', '#d4b595', '#a1887f', '#5d4037'] }
      },
      calendar: [{
        top: 30, bottom: 60, left: 45, right: 30,
        range: [echarts.time.format(start, '{yyyy}-{MM}-{dd}', false), echarts.time.format(end, '{yyyy}-{MM}-{dd}', false)],
        cellSize: ['auto', 20], 
        itemStyle: { color: 'rgba(255, 255, 255, 0.02)', borderWidth: 2, borderColor: 'transparent' },
        splitLine: { show: false }, yearLabel: { show: false }, 
        dayLabel: { color: '#888', nameMap: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'] },
        monthLabel: { color: '#888', nameMap: 'EN' }
      }],
      series: [{ type: 'heatmap', coordinateSystem: 'calendar', data: [], itemStyle: { borderRadius: 4, borderColor: 'transparent', borderWidth: 2 } }]
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
  if (apiChart) apiChart.dispose();
  if (heatmapChart) heatmapChart.dispose();
});

const handleResize = () => {
  if (myChart) myChart.resize();
  if (apiChart) apiChart.resize();
  if (heatmapChart) heatmapChart.resize();
};
</script>

<template>
  <div>
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

        <div class="monitor-card mb-4">
          <div ref="apiChartContainer" class="echarts-box api-echarts-box"></div>
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
    <SiteFooter />
  </div>
</template>

<style scoped>
 @import '@/assets/css/dashboard.css';
</style>