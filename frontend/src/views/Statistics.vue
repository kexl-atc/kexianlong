<template>
  <div class="statistics-container">
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>台账录入统计</span>
          <el-select v-model="timeRange" placeholder="选择时间范围" @change="fetchStats">
            <el-option label="最近7天" :value="7" />
            <el-option label="最近30天" :value="30" />
            <el-option label="最近90天" :value="90" />
          </el-select>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="用户台账数量" name="total">
          <v-chart class="chart" :option="totalChartOption" autoresize />
        </el-tab-pane>
        <el-tab-pane label="月度趋势" name="trend">
          <v-chart class="chart" :option="trendChartOption" autoresize />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { getLedgerStatsByUser } from '@/api/statistics'
import { ElMessage } from 'element-plus'

// 注册 ECharts 组件
use([
  CanvasRenderer,
  BarChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

// 状态
const timeRange = ref(30)
const activeTab = ref('total')
const totalChartOption = ref({})
const trendChartOption = ref({})

// 获取统计数据
const fetchStats = async () => {
  try {
    const res = await getLedgerStatsByUser({ days: timeRange.value })
    if (res.success) {
      updateCharts(res.data)
    } else {
      ElMessage.error(res.message || '获取统计数据失败')
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败')
  }
}

// 更新图表
const updateCharts = (data) => {
  // 更新总数图表
  totalChartOption.value = {
    title: {
      text: '各用户台账录入数量',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: data.total.map(item => item.username),
      axisLabel: {
        interval: 0,
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      name: '台账数量'
    },
    series: [{
      data: data.total.map(item => item.count),
      type: 'bar',
      showBackground: true,
      backgroundStyle: {
        color: 'rgba(180, 180, 180, 0.2)'
      }
    }]
  }

  // 更新趋势图表
  const months = [...new Set(data.trend.flatMap(item => 
    item.records.map(record => record.month)
  ))].sort()

  trendChartOption.value = {
    title: {
      text: '用户台账录入趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: data.trend.map(item => item.username),
      top: 30
    },
    xAxis: {
      type: 'category',
      data: months,
      axisLabel: {
        interval: 0,
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      name: '台账数量'
    },
    series: data.trend.map(item => ({
      name: item.username,
      type: 'line',
      data: months.map(month => {
        const record = item.records.find(r => r.month === month)
        return record ? record.count : 0
      }),
      smooth: true
    }))
  }
}

// 初始化
onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.statistics-container {
  padding: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart {
  height: 400px;
  width: 100%;
}
</style> 