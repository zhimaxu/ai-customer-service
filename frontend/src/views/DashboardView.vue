<template>
  <div class="dashboard-view">
    <div class="top-bar">
      <span class="logo">Analytics Dashboard</span>
      <div class="nav-tabs">
        <router-link to="/" class="nav-tab">Chat</router-link>
        <router-link to="/agent" class="nav-tab">Agent</router-link>
        <router-link to="/dashboard" class="nav-tab active">Dashboard</router-link>
      </div>
      <div class="top-actions">
        <el-select v-model="period" size="small" style="width: 100px" @change="loadData">
          <el-option label="Today" value="day" />
          <el-option label="Week" value="week" />
          <el-option label="Month" value="month" />
        </el-select>
        <el-button :icon="SwitchButton" @click="handleLogout">Logout</el-button>
      </div>
    </div>

    <div class="dashboard-content">
      <div class="overview-cards">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ overview.total_sessions }}</div>
          <div class="stat-label">Total Sessions</div>
        </el-card>
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ overview.active_sessions }}</div>
          <div class="stat-label">Active Sessions</div>
        </el-card>
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ overview.avg_satisfaction }}/5</div>
          <div class="stat-label">Avg Satisfaction</div>
        </el-card>
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ overview.resolution_rate }}%</div>
          <div class="stat-label">Resolution Rate</div>
        </el-card>
      </div>

      <div class="charts-row">
        <el-card shadow="hover" class="chart-card">
          <template #header>Chat Trend</template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
        <el-card shadow="hover" class="chart-card">
          <template #header>Satisfaction Distribution</template>
          <div ref="satChartRef" class="chart-container"></div>
        </el-card>
      </div>

      <div class="charts-row">
        <el-card shadow="hover" class="chart-card wide">
          <template #header>Efficiency Metrics</template>
          <div class="efficiency-grid">
            <div class="eff-item">
              <div class="eff-value">{{ efficiency.avg_first_response_time || '--' }}s</div>
              <div class="eff-label">Avg First Response</div>
            </div>
            <div class="eff-item">
              <div class="eff-value">{{ efficiency.avg_response_time || '--' }}s</div>
              <div class="eff-label">Avg Response Time</div>
            </div>
            <div class="eff-item">
              <div class="eff-value">{{ efficiency.resolution_rate }}%</div>
              <div class="eff-label">Resolution Rate</div>
            </div>
            <div class="eff-item">
              <div class="eff-value">{{ efficiency.total_messages }}</div>
              <div class="eff-label">Total Messages</div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { SwitchButton } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { getOverview, getChatStats, getSatisfactionStats, getEfficiencyStats } from '../api/stats'
import * as echarts from 'echarts'

const router = useRouter()
const authStore = useAuthStore()
const period = ref('day')
const trendChartRef = ref(null)
const satChartRef = ref(null)
const overview = ref({ total_sessions: 0, active_sessions: 0, avg_satisfaction: 0, resolution_rate: 0 })
const efficiency = ref({ avg_first_response_time: 0, avg_response_time: 0, resolution_rate: 0, total_messages: 0 })

let trendChart = null
let satChart = null

async function loadData() {
  try {
    const [overviewData, chatData, satData, effData] = await Promise.all([
      getOverview(),
      getChatStats(period.value),
      getSatisfactionStats(),
      getEfficiencyStats(),
    ])

    overview.value = {
      total_sessions: overviewData.total_sessions,
      active_sessions: overviewData.active_sessions,
      avg_satisfaction: overviewData.avg_satisfaction,
      resolution_rate: overviewData.resolution_rate,
    }

    efficiency.value = effData

    if (trendChartRef.value) {
      if (!trendChart) trendChart = echarts.init(trendChartRef.value)
      trendChart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: chatData.trend.map((t) => t.date) },
        yAxis: { type: 'value' },
        series: [
          { name: 'Total', type: 'line', smooth: true, data: chatData.trend.map((t) => t.total), itemStyle: { color: '#409EFF' } },
          { name: 'Active', type: 'line', smooth: true, data: chatData.trend.map((t) => t.active), itemStyle: { color: '#67C23A' } },
          { name: 'Closed', type: 'line', smooth: true, data: chatData.trend.map((t) => t.closed), itemStyle: { color: '#E6A23C' } },
        ],
      })
    }

    if (satChartRef.value) {
      if (!satChart) satChart = echarts.init(satChartRef.value)
      const dist = satData.distribution
      satChart.setOption({
        tooltip: { trigger: 'item' },
        legend: { orient: 'vertical', left: 'left' },
        series: [
          {
            name: 'Satisfaction',
            type: 'pie',
            radius: '50%',
            data: [
              { value: dist['5'] || 0, name: '5 stars' },
              { value: dist['4'] || 0, name: '4 stars' },
              { value: dist['3'] || 0, name: '3 stars' },
              { value: dist['2'] || 0, name: '2 stars' },
              { value: dist['1'] || 0, name: '1 star' },
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
  ElMessage.success('Logged out')
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
  background: #f5f7fa;
}
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 48px;
  background: #4a148c;
  color: white;
}
.logo { font-size: 18px; font-weight: bold; }
.nav-tabs { display: flex; gap: 16px; }
.nav-tab {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  padding: 4px 12px;
  border-radius: 4px;
}
.nav-tab:hover,
.nav-tab.active {
  color: white;
  background: rgba(255, 255, 255, 0.15);
}
.dashboard-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
.overview-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}
.stat-card .stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}
.stat-card .stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 4px;
}
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}
.chart-card.wide {
  grid-column: span 2;
}
.chart-container {
  height: 300px;
}
.efficiency-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 20px 0;
}
.eff-item {
  text-align: center;
}
.eff-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
}
.eff-label {
  font-size: 14px;
  color: #999;
  margin-top: 8px;
}
</style>
