<template>
  <div class="gtm-export-container">
    <div class="action-bar">
      <el-input v-model="searchQuery" placeholder="搜索报关单号或目的地..." prefix-icon="Search" class="search-input" />
      <el-button type="primary" size="large" @click="simulateComplianceCheck">
        <el-icon class="mr-2"><Ship /></el-icon> 创建出境报关单
      </el-button>
    </div>

    <el-card class="table-card" shadow="never">
      <el-table :data="exportList" style="width: 100%" class="gtm-table">
        <el-table-column prop="customs_id" label="海关申报号 (Customs No.)" min-width="180" />
        <el-table-column prop="destination" label="目的港 (POD)" min-width="150" />
        <el-table-column prop="bol_number" label="提单号 (B/L)" min-width="150" />
        <el-table-column label="报关状态 (Status)" min-width="160">
          <template #default="scope">
            <el-tag :type="getCustomsType(scope.row.customs_status)" effect="dark" round class="status-tag">
              <el-icon class="mr-1">
                <Loading v-if="scope.row.customs_status === '海关查验中'" />
                <CircleCheck v-else-if="scope.row.customs_status === '海关已放行'" />
                <Warning v-else />
              </el-icon>
              {{ scope.row.customs_status || '未知状态' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="无纸化单证 (Documents)" min-width="180" align="center">
          <template #default="scope">
            <el-button size="small" type="primary" plain round @click="openDocCenter(scope.row)">
              <el-icon class="mr-1"><DocumentCopy /></el-icon> 单证控制台
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="140" align="center">
          <template #default="scope">
             <el-button 
               size="small" 
               type="success" 
               plain 
               round 
               v-if="scope.row.customs_status === '草稿/待申报'"
               @click="handleSubmit(scope.row)" 
             >
               <el-icon><Position /></el-icon> 提交申报
             </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="createVisible" title="录入出境报关单 (新增记录)" width="550px">
      <el-form :model="exportForm" label-width="130px" class="mt-4">
        <el-form-item label="出口批次号">
          <el-input v-model="exportForm.export_id" placeholder="例如: EXP-2026-001" />
        </el-form-item>
        <el-form-item label="目的港 (POD)">
          <el-input v-model="exportForm.destination" placeholder="例如: 奥克兰港" />
        </el-form-item>
        <el-form-item label="提单号 (B/L)">
          <el-input v-model="exportForm.bol_number" placeholder="例如: BOL-998877" />
        </el-form-item>
        <el-form-item label="装柜时间">
          <el-date-picker v-model="exportForm.loading_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        
        <el-divider>底层数据关联 (填入系统ID数字)</el-divider>
        <el-form-item label="关联加工批次 ID">
          <el-input v-model="exportForm.process_batch" placeholder="填入数字，如: 1" type="number" />
        </el-form-item>
        <el-form-item label="关联销售订单 ID">
          <el-input v-model="exportForm.sales_order" placeholder="填入数字，如: 1" type="number" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createVisible = false">取消</el-button>
          <el-button type="primary" @click="submitExport" :loading="isSubmitting">确认提交入库</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog v-model="docVisible" title="数字单证引擎 (Digital Document Engine)" width="700px" class="doc-dialog">
      <div class="doc-header mb-4">
        <div class="doc-info">
          <strong>申报号：{{ currentDocOrder.customs_id }}</strong>
          <span class="ml-4 text-gray-500">目的港：{{ currentDocOrder.destination }}</span>
        </div>
        <el-tag type="info" effect="plain">国际通用标准 EDI</el-tag>
      </div>
      <el-alert title="系统已关联底层 ERP 数据，支持一键生成符合国际标准的 PDF 报关单证。" type="success" :closable="false" class="mb-4" />
      <div class="doc-grid">
        <div class="doc-card">
          <div class="doc-icon invoice"><el-icon><Money /></el-icon></div>
          <div class="doc-detail">
            <h4>商业发票 (Commercial Invoice)</h4>
            <p v-if="docStatus.invoice">已关联真实交易额</p><p v-else class="warning-text">待生成</p>
          </div>
          <div class="doc-action">
            <el-button v-if="docStatus.invoice" type="primary" size="small" plain>下载 PDF</el-button>
            <el-button v-else type="primary" size="small" :loading="isGenerating.invoice" @click="generateDoc('invoice')">一键生成</el-button>
          </div>
        </div>
        <div class="doc-card">
          <div class="doc-icon origin"><el-icon><MapLocation /></el-icon></div>
          <div class="doc-detail">
            <h4>原产地证 (Cert of Origin)</h4>
            <p v-if="docStatus.origin">已获海关数字签名</p><p v-else class="warning-text">待提取溯源数据</p>
          </div>
          <div class="doc-action">
            <el-button v-if="docStatus.origin" type="primary" size="small" plain>下载 PDF</el-button>
            <el-button v-else type="warning" size="small" :loading="isGenerating.origin" @click="generateDoc('origin')">提取数据</el-button>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { Search, Ship, DocumentCopy, Position, Loading, CircleCheck, Warning, Money, Box, MapLocation } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const searchQuery = ref('')
const docVisible = ref(false)
const createVisible = ref(false) // 控制新增表单的显示
const isSubmitting = ref(false)
const currentDocOrder = ref({})
const exportList = ref([])

// 🚨 表单绑定的数据模型
const exportForm = reactive({
  export_id: '',
  destination: '',
  bol_number: '',
  loading_date: '',
  process_batch: null,
  sales_order: null
})

// 拉取列表
const fetchRealExports = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/gtm/exports/')
    exportList.value = response.data.map(exp => ({
      customs_id: exp.export_id,
      destination: exp.destination,
      bol_number: exp.bol_number || '待分配',
      customs_status: exp.customs_status,
      rawExportData: exp
    }))
  } catch (error) {
    ElMessage.error('无法连接到后端接口！')
  }
}

onMounted(() => fetchRealExports())

const getCustomsType = (status) => {
  if (status === '海关已放行') return 'success'
  if (status === '海关查验中') return 'warning'
  return 'info'
}

// 🌟 核心改动：合规扫描通过后，打开新增表单！
const simulateComplianceCheck = () => {
  ElMessageBox.confirm(
    '系统即将验证下游订单信息与上游加工数据...',
    '🚨 全球贸易合规网关',
    { confirmButtonText: '启动扫描', cancelButtonText: '取消', type: 'warning' }
  ).then(() => {
    ElMessage({ message: '✅ 合规通过！已开启录入通道。', type: 'success' })
    createVisible.value = true // 打开表单弹窗
  })
}

// 🌟 核心改动：真正把数据 POST 给 Django 后端
const submitExport = async () => {
  isSubmitting.value = true
  try {
    await axios.post('http://127.0.0.1:8000/api/gtm/exports/', exportForm)
    ElMessage.success('报关单成功写入数据库！')
    createVisible.value = false // 关掉弹窗
    fetchRealExports() // 重新刷新表格
  } catch (error) {
    console.error(error)
    ElMessage.error('写入失败！请确保你填入的【加工批次 ID】和【订单 ID】在数据库中真实存在！')
  } finally {
    isSubmitting.value = false
  }
}

const handleSubmit = async (row) => {
  try {
    // 呼叫后端刚刚写的那个特殊 action 接口
    // 注意：URL 格式是 /api/gtm/exports/{id}/submit_declaration/
    await axios.post(`http://127.0.0.1:8000/api/gtm/exports/${row.rawExportData.id}/submit_declaration/`)
    
    ElMessage.success(`报关单 ${row.customs_id} 已成功推送到海关系统！`)
    
    // 💡 这里的逻辑很巧妙：我们不需要刷新整页，直接改前端数据，让按钮消失
    row.customs_status = '海关查验中' 
    
    // 模拟 3 秒后海关自动放行（为了让你看到效果）
    setTimeout(async () => {
        // 这里你可以选择真的再发一次请求改状态，或者只是前端演示
        ElMessage({ message: `🎊 报关单 ${row.customs_id} 海关查验通过，已放行！`, type: 'success' })
        row.customs_status = '海关已放行'
    }, 5000)

  } catch (error) {
    // 🚨 加上这几行“吐真剂”代码
    console.error("1. 完整的错误对象:", error)
    if (error.response) {
      console.error("2. 后端拒绝的状态码 (比如 404, 500):", error.response.status)
      console.error("3. 后端给出的具体原因:", error.response.data)
    } else {
      console.error("后端根本没回话，可能是地址错了或者没启动")
    }
    
    ElMessage.error('申报提交失败，请检查网络或后端接口！')
  }
}

const docStatus = reactive({ invoice: false, packing: false, origin: false })
const isGenerating = reactive({ invoice: false, packing: false, origin: false })
const openDocCenter = (row) => { currentDocOrder.value = row; docVisible.value = true }
const generateDoc = (type) => {
  isGenerating[type] = true
  setTimeout(() => { isGenerating[type] = false; docStatus[type] = true; ElMessage.success('数字单证生成成功！') }, 1500)
}
</script>

<style scoped>
/* 样式保持不变 */
.gtm-export-container { padding: 5px; }
.action-bar { display: flex; justify-content: space-between; margin-bottom: 20px; }
.search-input { width: 350px; }
.status-tag { min-width: 110px; justify-content: center; font-weight: bold; }
.doc-header { background: #f8fafc; padding: 15px; border-radius: 8px; border-left: 4px solid #3b82f6; display: flex; justify-content: space-between; align-items: center; }
.doc-grid { display: flex; flex-direction: column; gap: 15px; }
.doc-card { display: flex; align-items: center; padding: 15px 20px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.02); transition: all 0.3s ease; }
.doc-card:hover { border-color: #bae6fd; box-shadow: 0 4px 15px rgba(2,132,199,0.08); }
.doc-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; justify-content: center; align-items: center; font-size: 24px; margin-right: 20px; color: white; }
.doc-icon.invoice { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
.doc-icon.origin { background: linear-gradient(135deg, #f59e0b, #b45309); }
.doc-detail { flex: 1; }
.doc-detail h4 { margin: 0 0 5px 0; font-size: 15px; color: #0f172a; }
.doc-detail p { margin: 0; font-size: 13px; color: #64748b; }
.doc-detail .warning-text { color: #e11d48; font-weight: bold; }
.doc-action { margin-left: 20px; }
</style>