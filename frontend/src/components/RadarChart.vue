<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue';
import VueApexCharts from 'vue3-apexcharts';
import axios from 'axios';
import type { ApexOptions } from 'apexcharts';

// 介面定義
interface Skill {
  category: string;
  score: number;
}

// 支援的圖表類型
type ChartType = 'bar' | 'donut' | 'radialBar';

const props = defineProps<{
  isDark: boolean;
}>();

const skills = ref<Skill[]>([]);
const loading = ref(true);
const currentType = ref<ChartType>('bar'); // 預設使用長條圖 (GitHub 風格)

// === 🎨 配色變數 ===
const COLOR_PRIMARY_DARK = '#e0cda9';
const COLOR_PRIMARY_LIGHT = '#5d4037';
const COLORS = ['#FFD700', '#FF4560', '#00E396', '#008FFB', '#775DD0', '#546E7A', '#26a69a', '#D10CE8'];

// 根據主題取得文字顏色
const textColor = computed(() => props.isDark ? '#e0cda9' : '#5d4037');

// ------------------------------------
// 核心：根據不同圖表類型產生對應的 Series 數據
// ------------------------------------
const series = computed(() => {
  if (skills.value.length === 0) return [];

  if (currentType.value === 'bar') {
    // === GitHub 風格堆疊長條圖 ===
    // 每個技能是一個獨立的 Series，每個 Series 只有一個數據點 (橫向堆疊)
    return skills.value.map(skill => ({
      name: skill.category,
      data: [skill.score]
    }));
  } else if (currentType.value === 'donut' || currentType.value === 'radialBar') {
    // === 圓餅圖 / 徑向圖 ===
    // Series 是一個單純的數字陣列
    return skills.value.map(skill => skill.score);
  }
  return [];
});

// ------------------------------------
// 核心：根據不同圖表類型產生 ApexOptions
// ------------------------------------
const chartOptions = computed<ApexOptions>(() => {
  const isDark = props.isDark;
  
  // 共用設定
  const baseOptions: ApexOptions = {
    chart: {
      background: 'transparent',
      toolbar: { show: false },
      animations: { enabled: true }
    },
    theme: {
      mode: isDark ? 'dark' : 'light',
      palette: 'palette1' 
    },
    colors: COLORS, // 使用自訂多彩色系
    legend: {
      position: 'bottom',
      labels: { colors: isDark ? '#fff' : '#333' }
    },
    dataLabels: {
      style: {
        fontSize: '12px',
        fontWeight: 'bold',
      },
      dropShadow: { enabled: false }
    },
    tooltip: {
      theme: isDark ? 'dark' : 'light'
    }
  };

  // === 1. GitHub 風格堆疊長條圖 (Stacked Bar) ===
  if (currentType.value === 'bar') {
    return {
      ...baseOptions,
      chart: {
        type: 'bar',
        stacked: true, // 開啟堆疊
        stackType: '100%', // 設定為 100% 佔比模式
        toolbar: { show: false },
        background: 'transparent'
      },
      plotOptions: {
        bar: {
          horizontal: true, // 橫向
          borderRadius: 8, // 圓角
          barHeight: '40%', // 調整條狀高度，讓它看起來像進度條
        }
      },
      xaxis: {
        categories: ['Skill Distribution'], // 只有一個分類
        labels: { show: false }, // 隱藏 X 軸標籤
        axisBorder: { show: false },
        axisTicks: { show: false }
      },
      yaxis: {
        show: false // 隱藏 Y 軸
      },
      grid: {
        show: false, // 隱藏格線
        padding: { top: 0, bottom: 0, left: 0, right: 0 }
      },
      stroke: {
        width: 1,
        colors: [isDark ? '#2c2c2c' : '#fff'] // 堆疊區塊間的間隔線
      }
    };
  }

  // === 2. 圓餅圖 (Donut) ===
  if (currentType.value === 'donut') {
    return {
      ...baseOptions,
      chart: {
        type: 'donut',
      },
      labels: skills.value.map(s => s.category),
      plotOptions: {
        pie: {
          donut: {
            size: '65%',
            labels: {
              show: true,
              total: {
                show: true,
                label: 'Total Skills',
                color: isDark ? '#fff' : '#333',
              }
            }
          }
        }
      },
      stroke: {
        show: true,
        colors: [isDark ? '#1a1a1a' : '#fff'],
        width: 2
      }
    };
  }
  
  // === 3. 徑向圖 (RadialBar) ===
  if (currentType.value === 'radialBar') {
     return {
      ...baseOptions,
      chart: {
        type: 'radialBar',
      },
      labels: skills.value.map(s => s.category),
      plotOptions: {
        radialBar: {
          hollow: { size: '50%' },
          track: {
            background: isDark ? '#444' : '#e0e0e0',
          },
          dataLabels: {
            name: { color: isDark ? '#fff' : '#333' },
            value: { color: isDark ? '#e0cda9' : '#333' }
          }
        }
      }
    };
  }

  return baseOptions;
});

// ------------------------------------
// 數據獲取
// ------------------------------------
const fetchSkills = async () => {
  loading.value = true;
  try {
    // 模擬數據 (如果沒有 API)
    // const mockData = [
    //   { category: 'JavaScript', score: 90 },
    //   { category: 'Vue.js', score: 85 },
    //   { category: 'CSS', score: 80 },
    //   { category: 'HTML', score: 95 },
    //   { category: 'TypeScript', score: 70 }
    // ];
    // skills.value = mockData;

    const response = await axios.get('/api/skills');
    skills.value = response.data;
  } catch (error) {
    console.error('無法取得技能數據：', error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchSkills();
});

// 輔助函數：切換圖表
const setType = (type: ChartType) => {
  currentType.value = type;
};
</script>

<template>
  <div class="chart-container">
    <div class="header">
      <h3 :style="{ color: textColor }">技能分佈分析</h3>
      
      <!-- 圖表切換按鈕 -->
      <div class="controls">
        <button 
          @click="setType('bar')" 
          :class="{ active: currentType === 'bar' }"
          title="堆疊長條圖"
        >
          <span class="icon">📊</span> Bar
        </button>
        <button 
          @click="setType('donut')" 
          :class="{ active: currentType === 'donut' }"
          title="圓餅圖"
        >
          <span class="icon">🍩</span> Donut
        </button>
        <button 
          @click="setType('radialBar')" 
          :class="{ active: currentType === 'radialBar' }"
          title="徑向圖"
        >
          <span class="icon">🎯</span> Radial
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <p>正在載入數據...</p>
    </div>

    <div v-else class="chart-wrapper">
      <!-- 
        重要：當切換圖表類型時，ApexCharts 有時需要重新 mounting
        這裡使用 :key="currentType" 強制 Vue 重新渲染元件 
      -->
      <VueApexCharts
        :key="currentType"
        :type="currentType === 'radialBar' ? 'radialBar' : (currentType === 'bar' ? 'bar' : 'donut')"
        height="300"
        :options="chartOptions"
        :series="series"
      />
    </div>
  </div>
</template>

<style scoped>
.chart-container {
  width: 100%;
  max-width: 600px; /* 加寬一點以適應橫條圖 */
  margin: 0 auto;
  background: var(--card-bg, rgba(255, 255, 255, 0.1));
  backdrop-filter: blur(10px);
  border: 1px solid var(--card-border, rgba(255, 255, 255, 0.2));
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.controls {
  display: flex;
  background: rgba(0, 0, 0, 0.05);
  padding: 4px;
  border-radius: 8px;
  gap: 4px;
}

.controls button {
  border: none;
  background: transparent;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  color: var(--text-color, #888);
  font-weight: 500;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 4px;
}

.controls button:hover {
  background: rgba(0, 0, 0, 0.05);
}

.controls button.active {
  background: var(--card-bg, #fff);
  color: var(--primary-color, #333);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chart-wrapper {
  min-height: 300px;
  width: 100%;
}

.loading-state {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
}

/* 深色模式適配 (如果父元件有傳入變數) */
:deep(.apexcharts-legend-text) {
  font-family: inherit !important;
}
</style>