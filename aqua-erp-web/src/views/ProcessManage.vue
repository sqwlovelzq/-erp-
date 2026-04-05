<template>
  <div class="app-container">
    <el-row :gutter="20" class="dashboard-cards">
      <el-col :span="8"><el-card shadow="hover" class="data-card primary-card"><div class="card-content"><div class="card-icon">🏭</div><div class="card-info"><div class="card-title">累计加工批次</div><div class="card-value">{{ tableData.length }} <span class="unit">批</span></div></div></div></el-card></el-col>
      <el-col :span="8"><el-card shadow="hover" class="data-card warning-card"><div class="card-content"><div class="card-icon">❄️</div><div class="card-info"><div class="card-title">达标冷链记录</div><div class="card-value">{{ qualifiedCount }} <span class="unit">条</span></div></div></div></el-card></el-col>
      <el-col :span="8"><el-card shadow="hover" class="data-card info-card"><div class="card-content"><div class="card-icon">🏢</div><div class="card-info"><div class="card-title">协作加工厂</div><div class="card-value">{{ uniqueFactories }} <span class="unit">家</span></div></div></div></el-card></el-col>
    </el-row>

    <el-card class="main-workspace" shadow="never">
      <template #header>
        <div class="workspace-header">
          <div class="header-left">
            <span class="title-icon">⚙️</span>
            <span class="title-text">冷链加工与温控调度台</span>
          </div>
          
          <div class="header-actions">
            <el-input 
              v-model="searchKeyword" 
              placeholder="搜加工批次或工厂名..." 
              class="search-box" 
              clearable 
              @keyup.enter="handleSearch"
              @clear="handleSearch">
              <template #append><el-button @click="handleSearch"><el-icon><Search /></el-icon></el-button></template>
            </el-input>

            <el-button type="primary" size="large" class="action-btn" @click="openAddDialog">
              <el-icon style="margin-right: 5px;"><Plus /></el-icon> 新增加工入库
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredTableData" style="width: 100%" v-loading="loading" :header-cell-style="{background:'#f0fdfa', color:'#0f766e', fontWeight: 'bold'}">
        <el-table-column prop="process_id" label="加工批次号" min-width="140">
          <template #default="scope"><span class="batch-id">{{ scope.row.process_id }}</span></template>
        </el-table-column>
        <el-table-column prop="factory_name" label="加工厂名称" min-width="150">
          <template #default="scope"><div class="factory-cell"><el-icon><OfficeBuilding /></el-icon> {{ scope.row.factory_name }}</div></template>
        </el-table-column>
        <el-table-column prop="temp_control" label="核心温控记录" min-width="140" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.temp_control.includes('-18') ? 'success' : 'danger'" :effect="scope.row.temp_control.includes('-18') ? 'dark' : 'light'" round>
              <el-icon v-if="scope.row.temp_control.includes('-18')"><Check /></el-icon><el-icon v-else><Warning /></el-icon>
              {{ scope.row.temp_control }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sample_id" label="留样编号" min-width="120" align="center">
          <template #default="scope"><span style="color: #64748b; font-family: monospace;">{{ scope.row.sample_id || '未留样' }}</span></template>
        </el-table-column>
        
        <el-table-column label="归档与操作" width="280" align="center" fixed="right">
          <template #default="scope">
            <div style="display: flex; gap: 8px; justify-content: center; align-items: center;">
              <el-upload action="http://127.0.0.1:8000/api/upload/" :data="{ process_id: scope.row.process_id, file_type: '加工温控报告' }" :show-file-list="false" :on-success="handleUploadSuccess" :on-error="handleUploadError" name="file">
                <el-button size="small" type="primary" plain class="hover-elevate" title="传报告"><el-icon><Document /></el-icon></el-button>
              </el-upload>
              <el-upload action="http://127.0.0.1:8000/api/upload/" :data="{ process_id: scope.row.process_id, file_type: '外包装溯源标签' }" :show-file-list="false" :on-success="handleUploadSuccess" :on-error="handleUploadError" name="file">
                <el-button size="small" type="warning" plain class="hover-elevate" title="传标签"><el-icon><Ticket /></el-icon></el-button>
              </el-upload>

              <div style="width: 1px; height: 16px; background-color: #cbd5e1; margin: 0 4px;"></div>
              
              <el-button size="small" type="primary" plain circle @click="openEditDialog(scope.row)" title="修正档案">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button size="small" type="danger" plain circle @click="handleDelete(scope.row.process_id)" title="作废批次">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEditMode ? '✏️ 修改加工与温控记录' : '🏭 新增加工入库'" width="550px">
      <div style="margin-bottom: 20px; color: #b91c1c; font-size: 13px; background: #fef2f2; padding: 12px; border-radius: 6px; border: 1px solid #fca5a5;">
        <el-icon><WarningFilled /></el-icon> <strong>Gate B 合规警告：</strong><br/>
        海关硬性要求：冷链温控记录中必须明确包含 <strong>"-18"</strong> 字样。否则禁止装柜出口！
      </div>

      <el-form :model="form" label-width="120px">
        <el-form-item label="待加工起捕单" v-if="!isEditMode">
          <el-select v-model="form.harvest_id" placeholder="选择已起捕的货源" style="width: 100%">
            <el-option v-for="item in harvestList" :key="item.harvest_id" :label="item.harvest_id + ' (余 ' + item.quantity + 'kg)'" :value="item.harvest_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联起捕单" v-else>
          <el-input v-model="form.harvest_id" disabled />
        </el-form-item>

        <el-form-item label="加工批次号">
          <el-input v-model="form.process_id" :disabled="isEditMode" placeholder="如：PROC-2026-001" />
        </el-form-item>
        <el-form-item label="加工厂名称">
          <el-input v-model="form.factory_name" placeholder="如：湛江第一冷链加工厂" />
        </el-form-item>
        <el-form-item label="冷链温控记录">
          <el-input v-model="form.temp_control" placeholder="🚨 务必填写类似：全程-18度达标" />
        </el-form-item>
        <el-form-item label="品控留样编号">
          <el-input v-model="form.sample_id" placeholder="如：SMP-2026-001 (选填)" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitProcess" :loading="submitting">{{ isEditMode ? '确认修正' : '确认入库' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import { Plus, OfficeBuilding, Check, Warning, WarningFilled, Document, Ticket, Search, Edit, Delete } from '@element-plus/icons-vue'

const tableData = ref([])
const harvestList = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)

const searchKeyword = ref('')
const isEditMode = ref(false)

const form = reactive({ harvest_id: '', process_id: '', factory_name: '', temp_control: '', sample_id: '' })

const qualifiedCount = computed(() => tableData.value.filter(item => item.temp_control.includes('-18')).length)
const uniqueFactories = computed(() => new Set(tableData.value.map(item => item.factory_name)).size)

const filteredTableData = computed(() => {
  if (!searchKeyword.value) return tableData.value
  const lower = searchKeyword.value.toLowerCase()
  return tableData.value.filter(item => 
    item.process_id.toLowerCase().includes(lower) || 
    item.factory_name.toLowerCase().includes(lower)
  )
})

const fetchData = () => {
  loading.value = true
  axios.get('http://127.0.0.1:8000/api/process-list/').then(res => { tableData.value = res.data; loading.value = false })
}

const handleSearch = () => { /* 触发 computed 重新计算 */ }

const openAddDialog = () => {
  isEditMode.value = false
  axios.get('http://127.0.0.1:8000/api/harvest-list/').then(res => {
    harvestList.value = res.data
    Object.assign(form, { harvest_id: '', process_id: `PROC-${new Date().getFullYear()}-`, factory_name: '', temp_control: '', sample_id: '' })
    dialogVisible.value = true
  })
}

const openEditDialog = (row) => {
  isEditMode.value = true
  Object.assign(form, { 
    harvest_id: row.harvest_batch__harvest_id || '已绑定', 
    process_id: row.process_id, 
    factory_name: row.factory_name, 
    temp_control: row.temp_control, 
    sample_id: row.sample_id || '' 
  })
  dialogVisible.value = true
}

const submitProcess = () => {
  if (!form.process_id || !form.factory_name) return ElMessage.warning('请填写完整的批次信息')
  submitting.value = true
  
  const url = isEditMode.value ? `http://127.0.0.1:8000/api/process/update/${form.process_id}/` : 'http://127.0.0.1:8000/api/process/'
  const method = isEditMode.value ? 'put' : 'post'

  axios[method](url, form).then(res => {
    ElMessage.success(res.data.message)
    dialogVisible.value = false
    fetchData()
  }).catch(err => {
    ElMessage.error(err.response?.data?.message || '操作失败')
  }).finally(() => { submitting.value = false })
}

const handleDelete = (process_id) => {
  ElMessageBox.confirm(`确认要作废加工批次【${process_id}】吗? 关联的留样编号与温控附件将失效。`, '高危操作', {
    confirmButtonText: '确认作废', cancelButtonText: '取消', type: 'error'
  }).then(() => {
    axios.delete(`http://127.0.0.1:8000/api/process/delete/${process_id}/`).then(res => {
      ElMessage.success(res.data.message)
      fetchData()
    }).catch(err => {
      ElMessage.error(err.response?.data?.message || '删除失败，该批次可能已装柜出口。')
    })
  }).catch(() => {})
}

const handleUploadSuccess = (response) => { ElNotification({ title: '品控文件已归档', message: response.message, type: 'success' }) }
const handleUploadError = () => { ElMessage.error('上传失败，请检查后端网络') }

onMounted(() => { fetchData() })
</script>

<style scoped>
.app-container { padding: 24px; min-height: 100vh; }
.dashboard-cards { margin-bottom: 24px; }
.data-card { border-radius: 12px; border: none; }
.card-content { display: flex; align-items: center; padding: 10px; }
.card-icon { font-size: 42px; margin-right: 20px; background: rgba(255,255,255,0.2); width: 70px; height: 70px; display: flex; justify-content: center; align-items: center; border-radius: 50%; }
.card-info { flex: 1; }
.card-title { font-size: 14px; opacity: 0.9; margin-bottom: 8px; }
.card-value { font-size: 28px; font-weight: bold; }
.unit { font-size: 14px; font-weight: normal; margin-left: 4px; }

.primary-card { background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%); color: white; }
.warning-card { background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%); color: white; }
.info-card { background: linear-gradient(135deg, #475569 0%, #334155 100%); color: white; }
.main-workspace { border-radius: 12px; border: none; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }

/* ✨ 搜索区排版 ✨ */
.workspace-header { display: flex; justify-content: space-between; align-items: center; }
.header-left { display: flex; align-items: center; }
.title-icon { font-size: 22px; margin-right: 10px; }
.title-text { font-size: 18px; font-weight: 600; color: #0f766e; }
.header-actions { display: flex; gap: 15px; align-items: center; }
.search-box { width: 280px; }

.action-btn { border-radius: 8px; font-weight: bold; }
.batch-id { font-family: 'Courier New', Courier, monospace; font-weight: bold; color: #0f766e; background: #ccfbf1; padding: 4px 8px; border-radius: 4px; }
.factory-cell { display: flex; align-items: center; gap: 8px; color: #334155; font-weight: 500; }
.hover-elevate { transition: all 0.2s ease; }
.hover-elevate:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
</style>