<template>
  <div class="finance-container">
    <div class="header-banner">
      <h2><el-icon><DataLine /></el-icon> 全链路成本与利润核算中心</h2>
      <el-button type="success" size="large" @click="handleCalculate" :loading="isCalculating">
        <el-icon class="mr-1"><Coin /></el-icon> 启动智能核算引擎
      </el-button>
    </div>

    <div class="dashboard-grid">
      <div class="dash-card bg-blue">
        <div class="title">全球总营收 (Revenue)</div>
        <div class="number">${{ totalRevenue.toLocaleString() }}</div>
      </div>
      <div class="dash-card bg-orange">
        <div class="title">三产总成本 (Total Costs)</div>
        <div class="number">-${{ totalCosts.toLocaleString() }}</div>
      </div>
      <div class="dash-card bg-green">
        <div class="title">系统净利润 (Net Profit)</div>
        <div class="number profit-text">+${{ totalProfit.toLocaleString() }}</div>
        <el-progress :percentage="profitMargin" color="#ffffff" :stroke-width="10" :show-text="false" class="mt-2" />
        <div class="text-xs text-white mt-1">综合利润率: {{ profitMargin }}%</div>
      </div>
    </div>

    <el-card shadow="never">
      <el-table :data="ledgerList" style="width: 100%" class="finance-table">
        <el-table-column prop="order_id" label="贸易订单号" min-width="150" />
        <el-table-column prop="customer_name" label="采购商" min-width="160" />
        
        <el-table-column label="营收总额" min-width="120">
          <template #default="scope"><span class="text-blue-600 font-bold">${{ scope.row.revenue }}</span></template>
        </el-table-column>
        
        <el-table-column label="一产成本(养殖)" min-width="130">
          <template #default="scope"><span class="cost-text">-${{ scope.row.farm_cost }}</span></template>
        </el-table-column>
        
        <el-table-column label="二产成本(加工)" min-width="130">
          <template #default="scope"><span class="cost-text">-${{ scope.row.process_cost }}</span></template>
        </el-table-column>
        
        <el-table-column label="三产成本(报关)" min-width="130">
          <template #default="scope"><span class="cost-text">-${{ scope.row.export_cost }}</span></template>
        </el-table-column>
        
        <el-table-column label="单笔净利润" min-width="140" fixed="right">
          <template #default="scope">
            <span :class="scope.row.net_profit >= 0 ? 'profit-positive' : 'profit-negative'">${{ scope.row.net_profit }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="calcVisible" title="智能财务核算引擎 (Financial Engine)" width="500px">
      <el-form label-width="120px" class="mt-4">
        <el-form-item label="选择贸易订单">
          <el-select v-model="selectedOrderId" placeholder="请选择要核算的订单" style="width: 100%">
            <el-option
              v-for="order in availableOrders"
              :key="order.id"
              :label="order.order_id + ' (采购商: ' + (order.customer_detail ? order.customer_detail.name : '未知') + ')'"
              :value="order.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <el-alert 
        title="引擎将自动追溯该订单对应的：出海报关单 -> 加工冷链批次 -> 养殖饲料记录，进行全成本利润核算。" 
        type="info" 
        show-icon 
        :closable="false" 
        class="mt-4"
      />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="calcVisible = false">取消</el-button>
          <el-button type="success" @click="submitCalculation" :loading="isCalculating">
            <el-icon class="mr-1"><Coin /></el-icon> 提取成本并平账
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
// 🚨 删除了 Lock, Unlock, Money 等与风控相关的图标
import { DataLine, Coin } from '@element-plus/icons-vue'
// 🚨 删除了 ElMessageBox
import { ElMessage } from 'element-plus' 

const ledgerList = ref([])
const isCalculating = ref(false)

const calcVisible = ref(false)
const availableOrders = ref([])
const selectedOrderId = ref(null)

const totalRevenue = computed(() => ledgerList.value.reduce((sum, item) => sum + parseFloat(item.revenue), 0))
const totalCosts = computed(() => ledgerList.value.reduce((sum, item) => sum + parseFloat(item.farm_cost) + parseFloat(item.process_cost) + parseFloat(item.export_cost), 0))
const totalProfit = computed(() => ledgerList.value.reduce((sum, item) => sum + parseFloat(item.net_profit), 0))
const profitMargin = computed(() => totalRevenue.value === 0 ? 0 : Math.round((totalProfit.value / totalRevenue.value) * 100))

const fetchLedgers = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/gtm/finance/')
    ledgerList.value = res.data
  } catch (error) {
    ElMessage.error('无法读取财务明细账单！')
  }
}

onMounted(() => fetchLedgers())

const handleCalculate = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/gtm/sales-orders/')
    availableOrders.value = res.data 
    selectedOrderId.value = null     
    calcVisible.value = true         
  } catch (error) {
    ElMessage.error('无法连接后端读取订单列表！')
  }
}

const submitCalculation = async () => {
  if (!selectedOrderId.value) {
    return ElMessage.warning('请先在下拉框中选择一个订单！')
  }
  
  isCalculating.value = true
  try {
    await axios.post('http://127.0.0.1:8000/api/gtm/finance/run-calc/', {
      order_id: selectedOrderId.value
    })
    ElMessage.success('核算成功！全链路成本已提取入账。')
    calcVisible.value = false 
    fetchLedgers() 
  } catch (e) {
    if (e.response && e.response.data.error) {
      ElMessage.error(`核算阻断：${e.response.data.error}`)
    } else {
      ElMessage.error('核算失败：未找到订单或底层溯源数据链条断裂！')
    }
  } finally {
    isCalculating.value = false
  }
}

// 🚨 删除了 handleRelease 函数（已移交到 ReceivableManage 页面）

</script>

<style scoped>
.finance-container { padding: 10px; }
.header-banner { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding: 15px 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.header-banner h2 { margin: 0; color: #1e293b; display: flex; align-items: center; gap: 10px; }

.dashboard-grid { display: grid; grid-template-columns: 1fr 1fr 2fr; gap: 20px; margin-bottom: 20px; }
.dash-card { padding: 25px; border-radius: 12px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.1); display: flex; flex-direction: column; justify-content: center; }
.bg-blue { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
.bg-orange { background: linear-gradient(135deg, #f97316, #c2410c); }
.bg-green { background: linear-gradient(135deg, #10b981, #047857); }

.dash-card .title { font-size: 15px; opacity: 0.9; margin-bottom: 8px; }
.dash-card .number { font-size: 36px; font-weight: 900; }
.profit-text { text-shadow: 0 2px 4px rgba(0,0,0,0.2); }

.text-blue-600 { color: #2563eb; }
.cost-text { color: #ef4444; font-weight: 500; }
.profit-positive { color: #10b981; font-weight: bold; font-size: 16px; }
.profit-negative { color: #ef4444; font-weight: bold; font-size: 16px; }
</style>