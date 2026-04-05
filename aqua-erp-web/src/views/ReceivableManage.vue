<template>
  <div class="receivable-container">
    <div class="header-banner">
      <h2><el-icon><Wallet /></el-icon> 资金风控与单证放行台</h2>
    </div>

    <el-card shadow="never">
      <el-alert title="风控铁律：在全额尾款到账前，严禁解除任何订单的物权单证锁定。" type="error" show-icon class="mb-4" :closable="false" />
      
      <el-table :data="orderList" style="width: 100%" border>
        <el-table-column prop="order_id" label="贸易订单号" width="180" />
        <el-table-column prop="customer_name" label="海外采购商" min-width="150" />
        
        <el-table-column label="资金锁定状态" min-width="150" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.financial_status === '已结清/放行' ? 'success' : 'danger'" effect="dark" size="large">
              <el-icon class="mr-1" v-if="scope.row.financial_status !== '已结清/放行'"><Lock /></el-icon>
              <el-icon class="mr-1" v-else><Unlock /></el-icon>
              {{ scope.row.financial_status || '待收尾款' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="风控操作" width="200" align="center">
          <template #default="scope">
            <el-button 
              v-if="scope.row.financial_status !== '已结清/放行'" 
              type="danger" 
              @click="handleRelease(scope.row)"
            >
              <el-icon class="mr-1"><Money /></el-icon> 确认收款并解锁
            </el-button>
            <el-button v-else type="success" disabled plain>
              已放行单证
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Wallet, Lock, Unlock, Money } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const orderList = ref([])

const fetchOrders = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/gtm/finance/')
    orderList.value = res.data
  } catch (error) {
    ElMessage.error('无法读取风控列表！')
  }
}

onMounted(() => fetchOrders())

const handleRelease = (row) => {
  ElMessageBox.confirm(
    `请确认已收到订单 ${row.order_id} 的全额尾款。放行后，客户将可直接下载正本提单！`,
    '⚠️ 资金风控高危操作',
    { confirmButtonText: '款项已核实入账', cancelButtonText: '取消', type: 'error' }
  ).then(async () => {
    try {
      // 呼叫后端 API
      await axios.post(`http://127.0.0.1:8000/api/orders/${row.id}/release_finance/`)
      ElMessage.success('资金风控已解除！单证中心同步放行。')
      fetchOrders() // 刷新列表
    } catch (error) {
      ElMessage.error('操作失败，请检查网络！')
    }
  }).catch(() => {})
}
</script>

<style scoped>
.receivable-container { padding: 20px; }
.header-banner { margin-bottom: 20px; padding: 15px 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.header-banner h2 { margin: 0; display: flex; align-items: center; gap: 10px; }
</style>