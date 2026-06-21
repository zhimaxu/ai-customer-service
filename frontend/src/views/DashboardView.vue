<template>
  <div class="dashboard-view">
    <div class="dashboard-toolbar">
      <h2 class="page-title">数据分析</h2>
      <div class="toolbar-right">
        <el-select v-model="period" size="default" @change="loadData" class="dark-select">
          <el-option label="今天" value="day" />
          <el-option label="本周" value="week" />
          <el-option label="本月" value="month" />
        </el-select>
        <el-button :icon="SwitchButton" @click="handleLogout" text class="logout-link">退出</el-button>
      </div>
    </div>

    <div class="dashboard-content">
      <!-- Overview Cards -->
      <div class="overview-grid">
        <div class="stat-card" v-for="card in statCards" :key="card.label">
          <div class="stat-icon" :style="{ background: card.gradient }">
            <el-icon :size="20"><component :is="card.icon" /></el-icon>
          </div>
          <div class="stat-value">{{ card.value }}</div>
          <div class="stat-label">{{ card.label }}</div>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="charts-row">
        <DarkCard>
          <template #header>对话趋势</template>
          <div ref="trendChartRef" class="chart-container"></div>
        </DarkCard>
        <DarkCard>
          <template #header>满意度分布</template>
          <div ref="satChartRef" class="chart-container"></div>
        </DarkCard>
      </div>

      <!-- Efficiency Row -->
      <DarkCard>
        <template #header>效率指标</template>
        <div class="efficiency-grid">
          <div class="eff-item">
            <div class="eff-value">{{ efficiency.avg_first_response_time || '--' }}<span class="eff-unit">s</span></div>
            <div class="eff-label">首次响应时间</div>
          </div>
          <div class="eff-divider"></div>
          <div class="eff-item">
            <div class="eff-value">{{ efficiency.avg_response_time || '--' }}<span class="eff-unit">s</span></div>
            <div class="eff-label">平均响应时间</div>
          </div>
          <div class="eff-divider"></div>
          <div class="eff-item">
            <div class="eff-value">{{ overview.resolution_rate }}<span class="eff-unit">%</span></div>
            <div class="eff-label">解决率</div>
          </div>
          <div class="eff-divider"></div>
          <div class="eff-item">
            <div class="eff-value">{{ overview.total_messages }}</div>
            <div class="eff-label">消息总数</div>
          </div>
        </div>
      </DarkCard>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { SwitchButton, DataBoard, Connection, Star, TrendCharts } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { getOverview, getChatStats, getSatisfactionStats, getEfficiencyStats } from '../api/stats'
import DarkCard from '../components/DarkCard.vue'
import * as echarts from 'echarts'

const router = useRouter()
const authStore = useAuthStore()
const period = ref('day')
const trendChartRef = ref(null)
const satChartRef = ref(null)

const overview = reactive({
  total_sessions: 0,
  active_sessions: 0,
  avg_satisfaction: 0,
  resolution_rate: 0,
  total_messages: 0,
})

const efficiency = reactive({
  avg_first_response_time: null,
  avg_response_time: null,
  resolution_rate: 0,
  total_messages: 0,
})

const statCards = [
  {
    label: '总会话数',
    value: '0',
    icon: 'Connection',
    gradient: 'linear-gradient(135deg, #FF6B35, #FF8F66)',
  },
  {
    label: '活跃会话',
    value: '0',
    icon: 'TrendCharts',
    gradient: 'linear-gradient(135deg, #34D399, #6EE7B7)',
  },
  {
    label: '平均满意度',
    value: '0/5',
    icon: 'Star',
    gradient: 'linear-gradient(135deg, #7C5CFC, #9B82FC)',
  },
  {
    label: '解决率',
    value: '0%',
    icon: 'DataBoard',
    gradient: 'linear-gradient(135deg, #FBBF24, #FCD34D)',
  },
]

let trendChart = null
let satChart = null

const CHART_COLORS = {
  coral: '#FF6B35',
  coralLight: '#FF8F66',
  purple: '#7C5CFC',
  green: '#34D399',
  warning: '#FBBF24',
  danger: '#EF4444',
  grid: 'rgba(255, 255, 255, 0.06)',
  axis: 'rgba(255, 255, 255, 0.3)',
  text: '#9CA3AF',
}

async function loadData() {
  try {
    const [overviewData, chatData, satData, effData] = await Promise.all([
      getOverview(),
      getChatStats(period.value),
      getSatisfactionStats(),
      getEfficiencyStats(),
    ])

    Object.assign(overview, {
      total_sessions: overviewData.total_sessions,
      active_sessions: overviewData.active_sessions,
      avg_satisfaction: overviewData.avg_satisfaction,
      resolution_rate: overviewData.resolution_rate,
      total_messages: overviewData.total_messages,
    })

    Object.assign(efficiency, effData)

    statCards[0].value = overview.total_sessions.toLocaleString()
    statCards[1].value = overview.active_sessions.toLocaleString()
    statCards[2].value = `${overview.avg_satisfaction}/5`
    statCards[3].value = `${overview.resolution_rate}%`

    if (trendChartRef.value) {
      if (!trendChart) trendChart = echarts.init(trendChartRef.value)
      trendChart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(26, 29, 39, 0.95)',
          borderColor: 'rgba(255,255,255,0.1)',
          textStyle: { color: '#EAEAEA' },
        },
        legend: {
          data: ['总计', '活跃', '已关闭'],
          textStyle: { color: CHART_COLORS.text },
          top: 0,
        },
        grid: { left: 40, right: 20, top: 40, bottom: 24 },
        xAxis: {
          type: 'category',
          data: chatData.trend.map((t) => t.date),
          axisLine: { lineStyle: { color: CHART_COLORS.grid } },
          axisLabel: { color: CHART_COLORS.text },
          axisTick: { show: false },
        },
        yAxis: {
          type: 'value',
          axisLine: { show: false },
          axisLabel: { color: CHART_COLORS.text },
          splitLine: { lineStyle: { color: CHART_COLORS.grid } },
        },
        series: [
          {
            name: '总计',
            type: 'line',
            smooth: true,
            data: chatData.trend.map((t) => t.total),
            itemStyle: { color: CHART_COLORS.coral },
            lineStyle: { width: 2.5 },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(255, 107, 53, 0.3)' },
                { offset: 1, color: 'rgba(255, 107, 53, 0.02)' },
              ]),
            },
          },
          {
            name: '活跃',
            type: 'line',
            smooth: true,
            data: chatData.trend.map((t) => t.active),
            itemStyle: { color: CHART_COLORS.green },
            lineStyle: { width: 2 },
          },
          {
            name: '已关闭',
            type: 'line',
            smooth: true,
            data: chatData.trend.map((t) => t.closed),
            itemStyle: { color: CHART_COLORS.warning },
            lineStyle: { width: 2 },
          },
        ],
      })
    }

    if (satChartRef.value) {
      if (!satChart) satChart = echarts.init(satChartRef.value)
      const dist = satData.distribution
      satChart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(26, 29, 39, 0.95)',
          borderColor: 'rgba(255,255,255,0.1)',
          textStyle: { color: '#EAEAEA' },
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          textStyle: { color: CHART_COLORS.text },
        },
        series: [
          {
            name: '满意度',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['60%', '50%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 6,
              borderColor: 'rgba(15, 17, 23, 0.8)',
              borderWidth: 2,
            },
            label: {
              show: true,
              formatter: '{b}: {c}',
              color: CHART_COLORS.text,
            },
            data: [
              { value: dist['5'] || 0, name: '5 星', itemStyle: { color: CHART_COLORS.coral } },
              { value: dist['4'] || 0, name: '4 星', itemStyle: { color: CHART_COLORS.coralLight } },
              { value: dist['3'] || 0, name: '3 星', itemStyle: { color: CHART_COLORS.warning } },
              { value: dist['2'] || 0, name: '2 星', itemStyle: { color: '#F87171' } },
              { value: dist['1'] || 0, name: '1 星', itemStyle: { color: CHART_COLORS.danger } },
            ],
          },
        ],
      })
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

function handleLogout() {
  authStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', () => {
    trendChart?.resize()
    satChart?.resize()
  })
})
</script>

<style scoped>
.dashboard-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-deep);
}

.dashboard-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-5) var(--space-6);
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-surface);
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.logout-link {
  color: var(--text-muted) !important;
  font-size: 13px;
}

.logout-link:hover {
  color: var(--danger) !important;
}

:deep(.dark-select .el-input__wrapper) {
  background-color: var(--bg-input) !important;
  border-color: var(--border-subtle) !important;
  box-shadow: none !important;
  border-radius: var(--radius-md) !important;
}

:deep(.dark-select .el-input__inner) {
  color: var(--text-primary) !important;
}

:deep(.dark-select .el-input__wrapper.is-focus) {
  border-color: var(--coral-primary) !important;
}

:deep(.dark-select .el-select__placeholder) {
  color: var(--text-primary) !important;
}

:deep(.dark-select .el-input__suffix-icon) {
  color: var(--text-muted) !important;
}

.dashboard-content {
  flex: 1;
  padding: var(--space-6);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
}

.stat-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  transition: all var(--transition-base);
}

.stat-card:hover {
  border-color: var(--border-medium);
  box-shadow: var(--shadow-card-hover);
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 2px;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.chart-container {
  height: 300px;
}

.efficiency-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-6);
  padding: var(--space-4) 0;
}

.eff-item {
  text-align: center;
}

.eff-value {
  font-size: 36px;
  font-weight: 700;
  color: var(--coral-primary);
  line-height: 1.2;
}

.eff-unit {
  font-size: 16px;
  font-weight: 400;
  color: var(--text-muted);
  margin-left: 2px;
}

.eff-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: var(--space-2);
}

.eff-divider {
  width: 1px;
  background: var(--border-subtle);
  align-self: stretch;
}
</style>
