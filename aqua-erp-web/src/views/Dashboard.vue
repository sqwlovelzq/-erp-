<template>
  <div class="dashboard-container">
    <div class="header-banner">
      <h2><el-icon><Monitor /></el-icon> Ocean Trace</h2>
      <el-tag type="success" effect="dark" round>实时数据已连通后端</el-tag>
    </div>

    <el-row :gutter="20" style="margin-bottom: 24px;">
      <el-col :span="8">
        <el-card shadow="hover" class="kpi-card">
          <div class="kpi-title">累计核算订单数</div>
          <div class="kpi-value">{{ orderCount }} <span class="text-sm text-gray-400">单</span></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="kpi-card">
          <div class="kpi-title">系统总净利润 (Net Profit)</div>
          <div class="kpi-value text-green-500">+${{ totalProfit.toLocaleString() }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="kpi-card">
          <div class="kpi-title">综合利润率</div>
          <div class="kpi-value text-blue-500">{{ profitMargin }}%</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="14">
        <el-card shadow="never" class="chart-card">
          <h3>单笔贸易营收与利润走势</h3>
          <div ref="barChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
      
      <el-col :span="10">
        <el-card shadow="never" class="chart-card">
          <h3>三产成本结构占比 (Cost Breakdown)</h3>
          <div ref="pieChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { Monitor } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// DOM 引用
const barChartRef = ref(null)
const pieChartRef = ref(null)

// 响应式数据
const orderCount = ref(0)
const totalProfit = ref(0)
const profitMargin = ref(0)

// ECharts 实例
let barChart = null
let pieChart = null

// 从后端拉取真实的财务数据并渲染图表
const fetchAndRenderData = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/gtm/finance/')
    const data = res.data

    if (data.length === 0) return // 如果没数据就不渲染了

    // 1. 计算顶部 KPI
    orderCount.value = data.length
    const totalRev = data.reduce((sum, item) => sum + parseFloat(item.revenue), 0)
    totalProfit.value = data.reduce((sum, item) => sum + parseFloat(item.net_profit), 0)
    profitMargin.value = totalRev === 0 ? 0 : Math.round((totalProfit.value / totalRev) * 100)

    // 2. 准备柱状图数据 (X轴订单号，Y轴营收和利润)
    const orderIds = data.map(item => item.order_id)
    const revenues = data.map(item => parseFloat(item.revenue))
    const profits = data.map(item => parseFloat(item.net_profit))

    // 3. 准备饼图数据 (累加一、二、三产总成本)
    const totalFarm = data.reduce((sum, item) => sum + parseFloat(item.farm_cost), 0)
    const totalProcess = data.reduce((sum, item) => sum + parseFloat(item.process_cost), 0)
    const totalExport = data.reduce((sum, item) => sum + parseFloat(item.export_cost), 0)

    // 绘制图表
    renderBarChart(orderIds, revenues, profits)
    renderPieChart(totalFarm, totalProcess, totalExport)

  } catch (error) {
    ElMessage.error('驾驶舱无法连接底层财务数据源！')
  }
}

// 渲染柱状图配置 (优化版)
const renderBarChart = (xData, revData, profitData) => {
  barChart = echarts.init(barChartRef.value)
  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    // 🚨 修复 1：把图例移到最顶部，绝对不和底部文字打架
    legend: { top: '0%', textStyle: { color: '#334155', fontWeight: 'bold' } }, 
    // 🚨 修复 2：给上下左右留出充足的呼吸空间
    grid: { top: '15%', left: '3%', right: '4%', bottom: '5%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: xData,
      axisLabel: { color: '#64748b' } // X轴文字颜色调淡一点更高级
    },
    yAxis: { 
      type: 'value', 
      name: '金额 (USD)',
      nameTextStyle: { color: '#64748b', padding: [0, 0, 0, 20] }
    },
    series: [
      { 
        name: '总营收(FOB)', 
        type: 'bar', 
        data: revData, 
        // 🚨 修复 3：给柱子减肥！最大宽度不超过 60 像素，加上圆角
        barMaxWidth: 60, 
        itemStyle: { color: '#3b82f6', borderRadius: [6, 6, 0, 0] } 
      },
      { 
        name: '净利润(Profit)', 
        type: 'line', 
        data: profitData, 
        itemStyle: { color: '#10b981' }, 
        smooth: true, 
        symbolSize: 10,
        lineStyle: { width: 3, shadowColor: 'rgba(16, 185, 129, 0.3)', shadowBlur: 10 } // 加点高级的发光特效
      }
    ]
  }
  barChart.setOption(option)
}

// 渲染饼图配置
const renderPieChart = (farm, process, exportCost) => {
  pieChart = echarts.init(pieChartRef.value)
  const option = {
    tooltip: { trigger: 'item', formatter: '{a} <br/>{b}: ${c} ({d}%)' },
    legend: { bottom: '0%', left: 'center' },
    series: [
      {
        name: '成本结构',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        label: { show: false, position: 'center' },
        emphasis: { label: { show: true, fontSize: 20, fontWeight: 'bold' } },
        labelLine: { show: false },
        data: [
          { value: farm, name: '一产(养殖/饲料)', itemStyle: { color: '#f59e0b' } },
          { value: process, name: '二产(加工/冷链)', itemStyle: { color: '#8b5cf6' } },
          { value: exportCost, name: '三产(报关/海运)', itemStyle: { color: '#06b6d4' } }
        ]
      }
    ]
  }
  pieChart.setOption(option)
}

// 监听窗口大小变化，让图表自适应缩放
const handleResize = () => {
  if (barChart) barChart.resize()
  if (pieChart) pieChart.resize()
}

onMounted(() => {
  fetchAndRenderData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (barChart) barChart.dispose()
  if (pieChart) pieChart.dispose()
})
</script>

<style scoped>
/* 🚨 加上 border-box 和 hidden，绝对防止内容溢出重叠到侧边栏 */
.dashboard-container { 
  padding: 20px; 
  background: #f8fafc; 
  width: 100%; 
  box-sizing: border-box; 
  overflow-x: hidden; 
}

.header-banner { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 20px; 
  padding: 15px 20px; 
  background: white; 
  border-radius: 8px; 
  box-shadow: 0 2px 10px rgba(0,0,0,0.05); 
}
.header-banner h2 { margin: 0; color: #0f172a; display: flex; align-items: center; gap: 10px; }

.kpi-card { text-align: center; border-radius: 12px; border: none; }
.kpi-title { font-size: 14px; color: #64748b; margin-bottom: 10px; font-weight: bold; }
.kpi-value { font-size: 32px; font-weight: 900; color: #0f172a; }

.chart-card { 
  border-radius: 12px; 
  border: none; 
  height: 100%; 
  margin-bottom: 24px; 
}
.chart-card { border-radius: 12px; border: none; height: 100%; }
.chart-card h3 { margin: 0 0 15px 0; font-size: 16px; color: #334155; padding-bottom: 10px; border-bottom: 1px solid #e2e8f0; }

/* 🚨 强制图表盒子在父元素内部渲染，绝不跑出去 */
.chart-box { 
  width: 100%; 
  height: 320px; 
  position: relative;
  overflow: hidden; 
}
</style>