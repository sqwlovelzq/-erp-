<template>
  <div class="app-container">
    <el-row :gutter="20" class="dashboard-cards">
      <el-col :span="8"><el-card shadow="hover" class="data-card primary-card"><div class="card-content"><div class="card-icon">🌊</div><div class="card-info"><div class="card-title">累计养殖批次</div><div class="card-value">{{ tableData.length }} <span class="unit">批</span></div></div></div></el-card></el-col>
      <el-col :span="8"><el-card shadow="hover" class="data-card warning-card"><div class="card-content"><div class="card-icon">🐟</div><div class="card-info"><div class="card-title">活跃网箱单元</div><div class="card-value">{{ uniqueUnits }} <span class="unit">个</span></div></div></div></el-card></el-col>
      <el-col :span="8"><el-card shadow="hover" class="data-card success-card"><div class="card-content"><div class="card-icon">🛡️</div><div class="card-info"><div class="card-title">品控安全状态</div><div class="card-value">100 <span class="unit">% 合规</span></div></div></div></el-card></el-col>
    </el-row>

    <el-card class="main-workspace" shadow="never">
      <template #header>
        <div class="workspace-header">
          <div class="header-left">
            <span class="title-icon">📊</span>
            <span class="title-text">养殖与起捕调度台</span>
          </div>
          
          <div class="header-actions">
            <el-input 
              v-model="searchKeyword" 
              placeholder="搜批次号或网箱..." 
              class="search-box" 
              clearable 
              @keyup.enter="handleSearch"
              @clear="handleSearch">
              <template #append><el-button @click="handleSearch"><el-icon><Search /></el-icon></el-button></template>
            </el-input>

            <el-button type="primary" size="large" class="action-btn" @click="openAddDialog">
              <el-icon style="margin-right: 5px;"><Plus /></el-icon> 新增养殖批次
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredTableData" style="width: 100%" v-loading="loading" :header-cell-style="{background:'#f8fafc', color:'#475569', fontWeight: 'bold'}">
        <el-table-column prop="farm_batch_id" label="养殖批次号" min-width="140">
          <template #default="scope"><span class="batch-id">{{ scope.row.farm_batch_id }}</span></template>
        </el-table-column>
        <el-table-column prop="breeding_unit" label="养殖单元" min-width="120">
          <template #default="scope"><el-tag effect="light" type="info"><el-icon><Location /></el-icon> {{ scope.row.breeding_unit }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="stocking_date" label="放养日期" min-width="110" />
        <el-table-column prop="target_spec" label="目标规格" min-width="100" />
        <el-table-column prop="responsible_person" label="责任人" min-width="100">
          <template #default="scope"><div class="person-cell"><el-icon><Avatar /></el-icon> {{ scope.row.responsible_person }}</div></template>
        </el-table-column>
        
        <el-table-column label="现场与数据操作" width="280" align="center" fixed="right">
          <template #default="scope">
            <div style="display: flex; gap: 8px; justify-content: center; align-items: center;">
              <el-button size="small" type="warning" class="hover-elevate" @click="openHarvestDialog(scope.row)">🚢 起捕</el-button>
              
              <el-upload action="http://127.0.0.1:8000/api/upload/" :data="{ farm_id: scope.row.farm_batch_id, file_type: '养殖水质报告' }" :show-file-list="false" :on-success="handleUploadSuccess" :on-error="handleUploadError" name="file">
                <el-button size="small" type="success" plain class="hover-elevate">📎 报告</el-button>
              </el-upload>

              <el-button size="small" type="primary" plain circle @click="openEditDialog(scope.row)" title="编辑档案">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button size="small" type="danger" plain circle @click="handleDelete(scope.row.farm_batch_id)" title="作废批次">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="addDialogVisible" :title="isEditMode ? '✏️ 修改养殖档案' : '🌱 新增养殖批次'" width="600px">
      <el-form :model="newBatchForm" label-width="120px">
        <el-form-item label="养殖批次号">
          <el-input v-model="newBatchForm.farm_batch_id" :disabled="isEditMode" placeholder="如：FARM-2026-001" />
        </el-form-item>
        <el-form-item label="养殖单元">
          <el-input v-model="newBatchForm.breeding_unit" placeholder="如：1号外海网箱" />
        </el-form-item>
        <el-form-item label="放养日期">
          <el-date-picker v-model="newBatchForm.stocking_date" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" :disabled="isEditMode" />
        </el-form-item>
        <el-form-item label="目标规格">
          <el-input v-model="newBatchForm.target_spec" placeholder="如：500g-700g" />
        </el-form-item>
        <el-form-item label="责任人">
          <el-input v-model="newBatchForm.responsible_person" />
        </el-form-item>
        <el-form-item label="饲料/药物记录">
          <el-input v-model="newBatchForm.feed_med_logs" type="textarea" :rows="3" placeholder="记录日常投喂和水质传感器巡检情况" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitNewBatch" :loading="submitting">{{ isEditMode ? '确认修正' : '确认下苗' }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="harvestDialogVisible" title="起捕流转 (Gate A 拦截门)" width="500px">
      <div style="margin-bottom: 20px; color: #e6a23c; font-size: 13px; background: #fdf6ec; padding: 10px; border-radius: 4px;">
        <el-icon><Warning /></el-icon> 注意：按出口合规要求，起捕重量必须大于等于 1000kg 才能放行。
      </div>
      <el-form :model="harvestForm" label-width="120px">
        <el-form-item label="关联批次"><el-input v-model="harvestForm.parent_farm_id" disabled /></el-form-item>
        <el-form-item label="起捕数量(kg)"><el-input v-model="harvestForm.quantity" type="number" placeholder="输入起捕重量" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="harvestDialogVisible = false">取消</el-button>
        <el-button type="warning" @click="submitHarvest" :loading="submitting">确认起捕</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import { Plus, Location, Avatar, Warning, Search, Edit, Delete } from '@element-plus/icons-vue'

const tableData = ref([])
const loading = ref(false)
const addDialogVisible = ref(false)
const harvestDialogVisible = ref(false)
const submitting = ref(false)

const searchKeyword = ref('')
const isEditMode = ref(false)

const uniqueUnits = computed(() => new Set(tableData.value.map(item => item.breeding_unit)).size)

// 前端过滤搜索（养殖模块数据通常不太多，前端搜足够快）
const filteredTableData = computed(() => {
  if (!searchKeyword.value) return tableData.value
  const lowerKeyword = searchKeyword.value.toLowerCase()
  return tableData.value.filter(item => 
    item.farm_batch_id.toLowerCase().includes(lowerKeyword) || 
    item.breeding_unit.toLowerCase().includes(lowerKeyword)
  )
})

const newBatchForm = reactive({ farm_batch_id: '', breeding_unit: '', stocking_date: '', target_spec: '', responsible_person: '', feed_med_logs: '' })
const harvestForm = reactive({ parent_farm_id: '', harvest_id: '', harvest_date: '', quantity: '' })

const fetchData = () => {
  loading.value = true
  axios.get('http://127.0.0.1:8000/api/batches/').then(res => { tableData.value = res.data; loading.value = false })
}

const handleSearch = () => { /* 触发计算属性重新渲染即可 */ }

const openAddDialog = () => {
  isEditMode.value = false
  Object.assign(newBatchForm, { farm_batch_id: `FARM-${new Date().getFullYear()}-`, breeding_unit: '', stocking_date: new Date().toISOString().split('T')[0], target_spec: '', responsible_person: '', feed_med_logs: '' })
  addDialogVisible.value = true
}

const openEditDialog = (row) => {
  isEditMode.value = true
  Object.assign(newBatchForm, { 
    farm_batch_id: row.farm_batch_id, breeding_unit: row.breeding_unit, 
    stocking_date: row.stocking_date, target_spec: row.target_spec, 
    responsible_person: row.responsible_person, feed_med_logs: row.feed_med_logs || '' 
  })
  addDialogVisible.value = true
}

const submitNewBatch = () => {
  if (!newBatchForm.farm_batch_id || !newBatchForm.breeding_unit) return ElMessage.warning('请填写批次号与网箱')
  submitting.value = true
  
  const url = isEditMode.value ? `http://127.0.0.1:8000/api/batches/update/${newBatchForm.farm_batch_id}/` : 'http://127.0.0.1:8000/api/batches/'
  const method = isEditMode.value ? 'put' : 'post'

  axios[method](url, newBatchForm).then(res => {
    ElMessage.success(res.data.message)
    addDialogVisible.value = false
    fetchData() 
  }).catch(err => {
    ElMessage.error(err.response?.data?.message || '操作失败')
  }).finally(() => { submitting.value = false })
}

const handleDelete = (farm_id) => {
  ElMessageBox.confirm(`确认要作废清退养殖批次【${farm_id}】吗? 传感器数据也将被解绑。`, '高危操作', {
    confirmButtonText: '确认作废', cancelButtonText: '取消', type: 'error'
  }).then(() => {
    axios.delete(`http://127.0.0.1:8000/api/batches/delete/${farm_id}/`).then(res => {
      ElMessage.success(res.data.message)
      fetchData()
    }).catch(err => {
      ElMessage.error(err.response?.data?.message || '删除失败，可能是该批次已起捕流转。')
    })
  }).catch(() => {})
}

const openHarvestDialog = (row) => {
  harvestForm.parent_farm_id = row.farm_batch_id
  harvestForm.harvest_id = 'H-' + Date.now()
  harvestForm.quantity = ''
  harvestForm.harvest_date = new Date().toISOString().split('T')[0]
  harvestDialogVisible.value = true
}

const submitHarvest = () => {
  submitting.value = true
  axios.post('http://127.0.0.1:8000/api/harvests/', harvestForm).then(res => {
    ElMessage.success(res.data.message)
    harvestDialogVisible.value = false
  }).catch(err => {
    if (err.response && err.response.status === 403) { ElMessage({ message: err.response.data.message, type: 'error', duration: 5000 }) }
  }).finally(() => { submitting.value = false })
}

const handleUploadSuccess = (response) => { ElNotification({ title: '证据链归档成功', message: response.message, type: 'success' }) }
const handleUploadError = () => { ElMessage.error('上传失败，请检查后端！') }

onMounted(() => { fetchData() })
</script>

<style scoped>
/* 样式与原版高度一致，仅增加搜索区排版 */
.app-container { padding: 24px; min-height: 100vh; }
.dashboard-cards { margin-bottom: 24px; }
.data-card { border-radius: 12px; border: none; }
.card-content { display: flex; align-items: center; padding: 10px; }
.card-icon { font-size: 42px; margin-right: 20px; background: rgba(255,255,255,0.2); width: 70px; height: 70px; display: flex; justify-content: center; align-items: center; border-radius: 50%; }
.card-info { flex: 1; }
.card-title { font-size: 14px; opacity: 0.9; margin-bottom: 8px; }
.card-value { font-size: 28px; font-weight: bold; }
.unit { font-size: 14px; font-weight: normal; margin-left: 4px; }

.primary-card { background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: white; }
.warning-card { background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%); color: white; }
.success-card { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; }

.main-workspace { border-radius: 12px; border: none; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }

/* ✨ 搜索区排版 ✨ */
.workspace-header { display: flex; justify-content: space-between; align-items: center; }
.header-left { display: flex; align-items: center; }
.title-icon { font-size: 22px; margin-right: 10px; }
.title-text { font-size: 18px; font-weight: 600; color: #1e293b; }
.header-actions { display: flex; gap: 15px; align-items: center; }
.search-box { width: 280px; }

.action-btn { border-radius: 8px; font-weight: bold; }
.batch-id { font-family: 'Courier New', Courier, monospace; font-weight: bold; color: #0284c7; background: #e0f2fe; padding: 4px 8px; border-radius: 4px; }
.person-cell { display: flex; align-items: center; gap: 8px; color: #475569; font-weight: 500; }
.hover-elevate { transition: all 0.2s ease; }
.hover-elevate:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
</style>