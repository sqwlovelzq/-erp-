<template>
  <div class="gtm-order-container">
    <div class="action-bar">
      <el-input 
        v-model="searchQuery" 
        placeholder="搜索订单号..." 
        prefix-icon="Search"
        class="search-input"
        clearable 
      />
      <el-button type="primary" size="large" class="glow-btn" @click="handleCreate">
        <el-icon class="mr-2"><Plus /></el-icon> 录入跨国订单
      </el-button>
    </div>

    <el-card class="table-card" shadow="never">
      <el-table :data="orderList" style="width: 100%" class="gtm-table">
        <el-table-column prop="order_id" label="国际贸易单号" min-width="160" />
        
        <el-table-column label="采购商 (Buyer)" min-width="180">
          <template #default="scope">
            <div class="customer-link" @click="openCRM(scope.row.rawCustomerData)">
              <el-avatar :size="24" :src="scope.row.avatar" class="mr-2" />
              <span class="customer-name">{{ scope.row.customer }}</span>
              <el-icon class="link-icon"><TopRight /></el-icon>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="amount" label="总金额 (FOB)" min-width="140">
          <template #default="scope">
            <span class="money-text">${{ scope.row.amount }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="生产履约状态" min-width="140">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" effect="light" round>
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="单证与追踪" min-width="150">
          <template #default="scope">
            <el-button size="small" type="primary" plain round @click="openTracking(scope.row)">
              <el-icon class="mr-1"><Location /></el-icon> 链路追踪
            </el-button>
          </template>
        </el-table-column>

        <el-table-column label="操作" min-width="120" align="center">
          <template #default>
            <el-button size="small" type="primary" plain circle><el-icon><Edit /></el-icon></el-button>
            <el-button size="small" type="danger" plain circle><el-icon><Delete /></el-icon></el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-drawer
      v-model="crmVisible"
      :title="'客户深度画像：' + (currentCustomer.name || '未知')"
      direction="rtl"
      size="400px"
      class="crm-drawer"
    >
      <div class="crm-content" v-if="currentCustomer.name">
        <div class="crm-header">
          <el-avatar :size="64" :src="currentCustomer.avatar" />
          <div class="crm-title">
            <h3>{{ currentCustomer.name }}</h3>
            <el-tag :type="currentCustomer.credit === 'A级 (极佳)' ? 'success' : 'warning'" effect="dark">
              信用评级：{{ currentCustomer.credit || '未评级' }}
            </el-tag>
          </div>
        </div>
        
        <el-divider>全球贸易风控指标</el-divider>
        <div class="data-grid">
          <div class="data-box">
            <span class="data-label">累计交易额</span>
            <span class="data-value">${{ currentCustomer.total_trade || '0.00' }}</span>
          </div>
          <div class="data-box">
            <span class="data-label">历史违约率</span>
            <span class="data-value" style="color: #10b981;">0.00%</span>
          </div>
        </div>

        <el-alert 
          v-if="currentCustomer.credit === 'A级 (极佳)'"
          title="系统合规建议：允许最高 $50,000 的信用赊销放行。" 
          type="success" 
          show-icon 
          class="mt-4" 
          :closable="false"
        />
      </div>
    </el-drawer>

    <el-dialog v-model="trackingVisible" title="全球供应链追踪网" width="600px">
      <p>正在拉取单号 {{ currentTrackOrder.order_id }} 的底层溯源数据...</p>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Search, Plus, Edit, Delete, TopRight, Location } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const searchQuery = ref('')
const crmVisible = ref(false)
const trackingVisible = ref(false)
const currentCustomer = ref({})
const currentTrackOrder = ref({})
const orderList = ref([])

// 拉取真实数据
const fetchRealOrders = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/gtm/sales-orders/')
    orderList.value = response.data.map(order => ({
      order_id: order.order_id,
      customer: order.customer_detail ? order.customer_detail.name : '未关联客户',
      avatar: `https://api.dicebear.com/7.x/initials/svg?seed=${order.customer_detail ? order.customer_detail.name : 'NA'}`,
      amount: order.total_amount,
      status: order.status,
      rawCustomerData: order.customer_detail // 核心风控数据包
    }))
  } catch (error) {
    ElMessage.error('无法连接到后端服务器！')
  }
}

onMounted(() => {
  fetchRealOrders()
})

const getStatusType = (status) => {
  if (!status) return 'info'
  if (status.includes('生产')) return 'warning'
  if (status.includes('报关') || status.includes('装柜')) return 'danger'
  if (status.includes('完结') || status.includes('结清')) return 'success'
  return 'info'
}

// 打开真实数据的 CRM 抽屉
const openCRM = (rawCustomerData) => {
  if (!rawCustomerData) {
    ElMessage.warning('该订单未在后端关联客户风控档案')
    return
  }
  currentCustomer.value = {
    name: rawCustomerData.name,
    avatar: `https://api.dicebear.com/7.x/initials/svg?seed=${rawCustomerData.name}`,
    credit: rawCustomerData.credit_rating,
    total_trade: rawCustomerData.total_trade_volume
  }
  crmVisible.value = true
}

const openTracking = (order) => {
  currentTrackOrder.value = order
  trackingVisible.value = true
}

const handleCreate = () => {
  ElMessage.info('未来接入订单创建弹窗')
}
</script>

<style scoped>
.gtm-order-container { padding: 5px; }
.action-bar { display: flex; justify-content: space-between; margin-bottom: 20px; }
.search-input { width: 350px; }

.customer-link { display: flex; align-items: center; cursor: pointer; padding: 4px 8px; border-radius: 6px; transition: all 0.2s ease; }
.customer-link:hover { background: #e0f2fe; }
.customer-name { color: #0284c7; font-weight: bold; margin-right: 5px; }
.link-icon { font-size: 12px; color: #0284c7; }
.money-text { font-weight: 900; font-size: 15px; color: #0f172a; }

.crm-header { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
.crm-title h3 { margin: 0 0 5px 0; color: #0f172a; font-size: 20px; }
.data-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }
.data-box { background: #f8fafc; padding: 15px; border-radius: 12px; display: flex; flex-direction: column; }
.data-label { font-size: 12px; color: #64748b; margin-bottom: 5px; }
.data-value { font-size: 20px; font-weight: 900; color: #0f172a; }
</style>