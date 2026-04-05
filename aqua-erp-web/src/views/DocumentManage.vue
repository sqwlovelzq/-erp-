<template>
  <div class="document-container">
    <div class="header-banner">
      <h2><el-icon><Document /></el-icon> 全球贸易单证中心 (Document Center)</h2>
      <el-button type="primary" size="large" @click="createVisible = true">
        <el-icon class="mr-1"><DocumentAdd /></el-icon> 签发新单证
      </el-button>
    </div>

    <el-card shadow="never" class="doc-card">
      <el-tabs v-model="activeTab" class="custom-tabs">
        <el-tab-pane label="全部单证 All" name="all"></el-tab-pane>
        <el-tab-pane label="发票 Invoice" name="发票"></el-tab-pane>
        <el-tab-pane label="提单 B/L" name="提单"></el-tab-pane>
        <el-tab-pane label="原产地证 C/O" name="原产地证"></el-tab-pane>
      </el-tabs>

      <el-table :data="filteredDocs" style="width: 100%" class="mt-4">
        <el-table-column label="单证类型" width="180">
          <template #default="scope">
            <div class="doc-type-box" :class="getDocColor(scope.row.doc_type)">
              <el-icon><Tickets /></el-icon> {{ scope.row.doc_type }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="doc_no" label="单证编号 (Doc No.)" min-width="160" />
        <el-table-column prop="order_id_display" label="关联订单号" min-width="150" />
        <el-table-column label="当前状态" min-width="120">
          <template #default="scope">
            <el-tag :type="scope.row.status === '已生效' ? 'success' : 'warning'" effect="light" round>
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="单证操作" min-width="150" fixed="right">
          <template #default>
            <el-button size="small" type="primary" plain><el-icon><View /></el-icon> 预览</el-button>
            <el-button size="small" type="success" plain><el-icon><Download /></el-icon> 下载 PDF</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="createVisible" title="签发国际贸易单证" width="500px">
      <el-form :model="docForm" label-width="100px">
        <el-form-item label="单证类型">
          <el-select v-model="docForm.doc_type" placeholder="请选择类型" style="width: 100%">
            <el-option label="商业发票 (Invoice)" value="发票" />
            <el-option label="海运提单 (B/L)" value="提单" />
            <el-option label="原产地证 (Origin)" value="原产地证" />
            <el-option label="装箱单 (Packing)" value="装箱单" />
            <el-option label="销售合同 (Contract)" value="合同" />
          </el-select>
        </el-form-item>
        <el-form-item label="单证编号">
          <el-input v-model="docForm.doc_no" placeholder="例如: INV-2026-001" />
        </el-form-item>
        <el-form-item label="关联订单 ID">
          <el-input v-model="docForm.order" placeholder="填入系统关联的订单数字ID" type="number" />
        </el-form-item>
        <el-form-item label="初始状态">
          <el-radio-group v-model="docForm.status">
            <el-radio label="待签发">草稿待签</el-radio>
            <el-radio label="已生效">正式生效</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" @click="submitDoc">确认签发入库</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { Document, DocumentAdd, Tickets, View, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('all')
const createVisible = ref(false)
const docList = ref([])
const docForm = ref({ doc_no: '', doc_type: '发票', order: null, status: '已生效' })

const fetchDocs = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/gtm/documents/')
    docList.value = res.data
  } catch (e) {
    ElMessage.error('无法连接单证数据库！')
  }
}

onMounted(() => fetchDocs())

const filteredDocs = computed(() => {
  if (activeTab.value === 'all') return docList.value
  return docList.value.filter(doc => doc.doc_type === activeTab.value)
})

const submitDoc = async () => {
  try {
    await axios.post('http://127.0.0.1:8000/api/gtm/documents/', docForm.value)
    ElMessage.success('单证签发成功！')
    createVisible.value = false
    fetchDocs()
  } catch (e) {
    ElMessage.error('签发失败，请检查订单ID是否存在！')
  }
}

const getDocColor = (type) => {
  const colorMap = {
    '发票': 'bg-blue-100 text-blue-600',
    '提单': 'bg-green-100 text-green-600',
    '原产地证': 'bg-orange-100 text-orange-600',
    '装箱单': 'bg-purple-100 text-purple-600',
    '合同': 'bg-gray-100 text-gray-700'
  }
  return colorMap[type] || 'bg-gray-100 text-gray-600'
}
</script>

<style scoped>
.document-container { padding: 20px; box-sizing: border-box; }
.header-banner { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding: 15px 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.header-banner h2 { margin: 0; color: #0f172a; display: flex; align-items: center; gap: 10px; }
.doc-card { border-radius: 12px; }
.doc-type-box { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 6px; font-weight: bold; font-size: 13px; }

/* 颜色辅助类 */
.bg-blue-100 { background-color: #dbeafe; } .text-blue-600 { color: #2563eb; }
.bg-green-100 { background-color: #dcfce3; } .text-green-600 { color: #16a34a; }
.bg-orange-100 { background-color: #ffedd5; } .text-orange-600 { color: #ea580c; }
.bg-purple-100 { background-color: #f3e8ff; } .text-purple-600 { color: #9333ea; }
.bg-gray-100 { background-color: #f1f5f9; } .text-gray-700 { color: #334155; }
</style>