<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
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

// === 1. 設定預設圖表類型為 'donut' (圓餅圖) ===
const currentType = ref<ChartType>('donut'); 

// === 🎨 配色變數 (用於漸層) ===
const COLORS = ['#00FFFF', '#FFD700', '#00E396', '#775DD0', '#FF4560', '#546E7A', '#26a69a', '#D10CE8'];
// 深色模式下的漸變高亮色 (科技感)
const GRADIENT_COLORS_DARK = ['#00C9FF', '#92FE9D', '#FF5F6D', '#7474BF', '#FF8D7E', '#78909C', '#4DB6AC', '#E040FB']; 
// 淺色模式下的漸變暗色
const GRADIENT_COLORS_LIGHT = ['#0077B6', '#1E8449', '#CB4335', '#5DADE2', '#C0392B', '#455A64', '#00695C', '#8E24AA']; 

// 根據主題取得文字顏色
const textColor = computed(() => props.isDark ? '#e0cda9' : '#5d4037');

// ------------------------------------
// 核心：根據不同圖表類型產生對應的 Series 數據
// ------------------------------------
const series = computed(() => {
  if (skills.value.length === 0) return [];

  if (currentType.value === 'bar') {
    // GitHub 風格堆疊長條圖 (每個技能是一個獨立 Series)
    return skills.value.map(skill => ({
      name: skill.category,
      data: [skill.score]
    }));
  } else {
    // 圓餅圖 / 徑向圖：Series 是一個單純的數字陣列
    return skills.value.map(skill => skill.score);
  }
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
    colors: COLORS, // 基礎色盤
    legend: {
      position: 'bottom',
      labels: { colors: isDark ? '#fff' : '#333' },
      itemMargin: { horizontal: 10, vertical: 5 }
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
    },
    // === 全域漸層設定 (主要針對圓餅圖生效) ===
    fill: {
        type: currentType.value === 'donut' ? 'gradient' : 'solid',
        gradient: {
          shade: isDark ? 'dark' : 'light',
          type: 'horizontal',
          shadeIntensity: 0.5,
          gradientToColors: isDark ? GRADIENT_COLORS_DARK : GRADIENT_COLORS_LIGHT,
          inverseColors: true,
          opacityFrom: 1,
          opacityTo: 1,
          stops: [0, 100]
        }
    }
  };

  // === 1. 圓餅圖 (Donut) ===
  if (currentType.value === 'donut') {
    return {
      ...baseOptions,
      chart: { type: 'donut' },
      labels: skills.value.map(s => s.category),
      stroke: {
        show: true,
        colors: [isDark ? '#1a1a1a' : '#fff'], // 區塊間的間隔線
        width: 2
      },
      plotOptions: {
        pie: {
          donut: {
            size: '65%', // 中空大小
            labels: {
              show: true,
              name: { color: isDark ? '#fff' : '#333' },
              value: { color: isDark ? '#e0cda9' : '#5d4037' },
              total: {
                show: true,
                label: 'Skills',
                color: isDark ? '#fff' : '#333',
                formatter: () => `${skills.value.length} 項`
              }
            }
          }
        }
      }
    };
  }

  // === 2. GitHub 風格堆疊長條圖 (Bar) ===
  if (currentType.value === 'bar') {
    return {
      ...baseOptions,
      chart: {
        type: 'bar',
        stacked: true, 
        stackType: '100%', 
        toolbar: { show: false }
      },
      plotOptions: {
        bar: {
          horizontal: true, 
          borderRadius: 8, 
          barHeight: '40%', 
        }
      },
      xaxis: {
        categories: ['Skill Distribution'], 
        labels: { show: false }, 
        axisBorder: { show: false },
        axisTicks: { show: false }
      },
      yaxis: { show: false },
      grid: {
        show: false, 
        padding: { top: 0, bottom: 0, left: 0, right: 0 }
      },
      stroke: {
        width: 1,
        colors: [isDark ? '#2c2c2c' : '#fff'] 
      },
      fill: { type: 'solid' } // 長條圖通常用實色比較好看
    };
  }
  
  // === 3. 徑向圖 (RadialBar) ===
  if (currentType.value === 'radialBar') {
     return {
      ...baseOptions,
      chart: { type: 'radialBar' },
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
      },
      fill: { type: 'gradient' } // 徑向圖也適合漸層
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
      <h3 :style="{ color: textColor }">
        <i class="fa-solid fa-chart-pie" style="margin-right: 8px;"></i> 技能分佈分析
      </h3>
      
      <div class="controls">
        <button 
          @click="setType('donut')" 
          :class="{ active: currentType === 'donut' }"
          title="圓餅圖"
        >
          <span class="icon"><i class="fa-solid fa-circle-notch"></i></span> Donut
        </button>
        <button 
          @click="setType('bar')" 
          :class="{ active: currentType === 'bar' }"
          title="堆疊長條圖"
        >
          <span class="icon"><i class="fa-solid fa-chart-bar"></i></span> Bar
        </button>
        <button 
          @click="setType('radialBar')" 
          :class="{ active: currentType === 'radialBar' }"
          title="徑向圖"
        >
          <span class="icon"><i class="fa-solid fa-bullseye"></i></span> Radial
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <p><i class="fa-solid fa-spinner fa-spin"></i> 正在載入數據...</p>
    </div>

    <div v-else class="chart-wrapper">
      <VueApexCharts
        :key="currentType"
        :type="currentType === 'radialBar' ? 'radialBar' : (currentType === 'bar' ? 'bar' : 'donut')"
        height="320"
        :options="chartOptions"
        :series="series"
      />
    </div>
  </div>
</template>

<style scoped>
.chart-container {
  width: 100%;
  max-width: 600px;
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
  display: flex;
  align-items: center;
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
  gap: 6px;
}

.controls button .icon {
  font-size: 0.9rem;
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
  min-height: 320px;
  width: 100%;
  display: flex;
  justify-content: center;
}

.loading-state {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
  gap: 10px;
}

/* 深色模式適配 */
:deep(.apexcharts-legend-text) {
  font-family: inherit !important;
}
</style>