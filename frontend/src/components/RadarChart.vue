<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import * as echarts from 'echarts';
import axios from '@/api';

const props = defineProps<{ isDark: boolean }>();
const chartContainer = ref<HTMLElement | null>(null);
let myChart: echarts.ECharts | null = null;
let resizeObserver: ResizeObserver | null = null;
const loading = ref(true);

// 🎨 擴充到 15 種獨立漸層色盤 (確保項目再多也夠用！)
const getGradientColors = () => [
  new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#00f2fe' }, { offset: 1, color: '#4facfe' }]), // 亮藍
  new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#fa709a' }, { offset: 1, color: '#fee140' }]), // 粉橘
  new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#43e97b' }, { offset: 1, color: '#38f9d7' }]), // 螢光綠
  new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#b224ef' }, { offset: 1, color: '#7579ff' }]), // 炫紫
  new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#f83600' }, { offset: 1, color: '#f9d423' }]), // 烈焰橘
  new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#ff0844' }, { offset: 1, color: '#ffb199' }]), // 烈火紅
  new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#00c6ff' }, { offset: 1, color: '#0072ff' }]), // 深海藍
  new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#16a085' }, { offset: 1, color: '#f4d03f' }]), // 藍綠轉黃
  new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#667eea' }, { offset: 1, color: '#764ba2' }]), // 靛紫
  new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#11998e' }, { offset: 1, color: '#38ef7d' }]), // 薄荷綠
  new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#ff758c' }, { offset: 1, color: '#ff7eb3' }]), // 芭比粉
  new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#13547a' }, { offset: 1, color: '#80d0c7' }]), // 青鈦色
  new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#f77062' }, { offset: 1, color: '#fe5196' }]), // 珊瑚紅
  new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#a18cd1' }, { offset: 1, color: '#fbc2eb' }]), // 柔和紫
  new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: '#00b09b' }, { offset: 1, color: '#96c93d' }]), // 青檸綠
];

const initChart = async (data: any[]) => {
  await nextTick();
  if (!chartContainer.value) return;
  
  if (!myChart) {
    myChart = echarts.init(chartContainer.value);
  }

  const chartData = data.length > 0 
    ? data.map(s => ({ value: s.score, name: s.category }))
    : [
        { value: 35, name: 'Vue.js / 前端' },
        { value: 25, name: '.NET / C#' },
        { value: 15, name: 'JavaScript / TS' },
        { value: 15, name: 'Python' },
        { value: 10, name: 'SQL / 資料庫' }
      ];

  const option = {
    backgroundColor: 'transparent',
    color: getGradientColors(),
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(13, 17, 23, 0.9)',
      borderColor: '#007bff',
      textStyle: { color: '#fff', fontFamily: 'monospace' },
      formatter: '{b} : 專案使用 {c} 次 ({d}%)' // 滑鼠懸停顯示次數與自動換算的百分比
    },
    legend: {
      type: 'scroll', 
      bottom: '2%',
      left: 'center',
      textStyle: { 
        color: props.isDark ? '#e0cda9' : '#5d4037',
        fontFamily: '"Fira Code", monospace',
        fontWeight: 'bold',
        fontSize: 11
      },
      itemWidth: 14,
      itemHeight: 14,
      icon: 'circle',
      pageIconColor: '#007bff', // 翻頁按鈕的顏色
      pageIconInactiveColor: '#555',
      pageTextStyle: { color: props.isDark ? '#fff' : '#333' }
    },
    series: [
      {
        name: '技術佔比',
        type: 'pie',
        radius: ['40%', '65%'], // 稍微縮小半徑，留空間給旁邊密集的標籤
        center: ['50%', '42%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 6,
          borderColor: props.isDark ? '#1e1e1e' : '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{d}%', 
          color: props.isDark ? '#e0cda9' : '#5d4037',
          fontFamily: '"Fira Code", monospace',
          fontWeight: 'bold',
          lineHeight: 16,
          fontSize: 12
        },
        labelLine: {
          length: 10,
          length2: 15,
          smooth: true,
          lineStyle: {
            width: 2,
            color: props.isDark ? 'rgba(224, 205, 169, 0.4)' : 'rgba(93, 64, 55, 0.4)'
          }
        },
        emphasis: {
          label: { show: true, fontSize: 14, fontWeight: 'bold' },
          itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' }
        },
        data: chartData
      }
    ]
  };

  myChart.setOption(option);
};

const fetchSkills = async () => {
  try {
    const res = await axios.get('/api/skills');
    await initChart(res.data); 
  } catch (error) {
    console.error('無法取得技能數據', error);
    await initChart([]); 
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchSkills();
  if (chartContainer.value) {
    resizeObserver = new ResizeObserver(() => {
      if (myChart) myChart.resize();
    });
    resizeObserver.observe(chartContainer.value);
  }
});

onUnmounted(() => {
  if (resizeObserver && chartContainer.value) {
    resizeObserver.unobserve(chartContainer.value);
    resizeObserver.disconnect();
  }
  if (myChart) myChart.dispose();
});

watch(() => props.isDark, () => { fetchSkills(); });
</script>

<template>
  <div class="chart-container">
    <h3>
      <i class="fa-solid fa-chart-pie"></i> 技術棧佔比分析
    </h3>

    <div v-if="loading" class="loading-state">
      <i class="fa-solid fa-spinner fa-spin"></i> 正在分析專案數據...
    </div>

    <div ref="chartContainer" class="echarts-wrapper" :class="{ hidden: loading }"></div>
  </div>
</template>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--card-bg, rgba(44, 44, 44, 0.7));
  border: 1px solid var(--card-border, rgba(255, 255, 255, 0.1));
  border-radius: 16px;
  padding: 30px;
  box-shadow: var(--card-shadow, 0 4px 6px rgba(0,0,0,0.3));
  transition: all 0.4s ease;
  box-sizing: border-box;
}

.chart-container:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 242, 255, 0.15);
  border-color: #007bff;
}

h3 {
  margin-top: 0;
  border-bottom: 2px solid #007bff;
  padding-bottom: 10px;
  margin-bottom: 20px;
  display: inline-block;
  color: var(--text-color);
  font-size: 1.17em;
}

h3 i {
  margin-right: 8px;
}

.echarts-wrapper {
  width: 100%;
  flex-grow: 1;
  min-height: 400px;
  position: relative;
  overflow: hidden;
}

.echarts-wrapper::before {
  content: '';
  position: absolute;
  top: 42%; 
  left: 50%;
  transform: translate(-50%, -50%);
  width: 230px; 
  height: 230px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0, 242, 255, 0.1) 0%, transparent 70%);
  border: 1px dashed rgba(0, 242, 255, 0.3);
  animation: slow-spin 20s linear infinite;
  pointer-events: none;
  z-index: 0;
}

@keyframes slow-spin {
  0% { transform: translate(-50%, -50%) rotate(0deg); }
  100% { transform: translate(-50%, -50%) rotate(360deg); }
}

:deep(div[style*="z-index"]) {
  z-index: 1 !important;
}

.hidden { display: none; }
.loading-state {
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
  font-family: 'Fira Code', monospace;
}

@media (max-width: 768px) {
  .echarts-wrapper::before {
    width: 160px;
    height: 160px;
  }
}
</style>