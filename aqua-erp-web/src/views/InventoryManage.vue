<template>
  <div class="app-container">
    <div class="wms-header">
      <div class="header-left">
        <el-icon class="title-icon" :size="28"><Box /></el-icon>
        <h2>WMS 动态实时库存大屏</h2>
      </div>
      <el-tag type="info" effect="plain" round>
        <el-icon><Clock /></el-icon> 数据实时联动：根据起捕与出库单自动推算，账实100%相符
      </el-tag>
    </div>

    <div v-if="loading" class="loading-box">
      <el-skeleton :rows="5" animated />
    </div>

    <el-row :gutter="30" v-else class="inventory-row">
      <el-col :span="8">
        <el-card class="stock-card raw-stock" shadow="hover">
          <div class="card-top">
            <span class="stock-title">🌊 待加工活鱼 (原料仓)</span>
            <el-tag size="small" effect="dark" color="#0284c7" style="border:none;">Gate A 拦水坝</el-tag>
          </div>
          <div class="card-middle">
            <el-progress type="dashboard" :percentage="calcPercentage(inventory.raw_stock_kg)" :color="rawColors">
              <template #default>
                <span class="percentage-value">{{ inventory.raw_stock_kg }}<span class="unit">kg</span></span>
              </template>
            </el-progress>
          </div>
          <div class="card-bottom">
            <p>当前滞留批次：<strong>{{ inventory.raw_count }}</strong> 批</p>
            <p class="desc-text">提示：请尽快安排送往加工厂，避免鲜度下降。</p>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="stock-card finished-stock" shadow="hover">
          <div class="card-top">
            <span class="stock-title">❄️ -18℃ 冻品 (成品仓)</span>
            <el-tag size="small" effect="dark" color="#0f766e" style="border:none;">Gate B 保鲜库</el-tag>
          </div>
          <div class="card-middle">
            <el-progress type="dashboard" :percentage="calcPercentage(inventory.finished_stock_kg)" :color="finishedColors">
              <template #default>
                <span class="percentage-value">{{ inventory.finished_stock_kg }}<span class="unit">kg</span></span>
              </template>
            </el-progress>
          </div>
          <div class="card-bottom">
            <p>当前囤货批次：<strong>{{ inventory.finished_count }}</strong> 批</p>
            <p class="desc-text">提示：等待客户打全款后，即可装柜发往海关。</p>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="stock-card export-stock" shadow="hover">
          <div class="card-top">
            <span class="stock-title">🚢 累计已装柜 (已出库)</span>
            <el-tag size="small" effect="dark" color="#be123c" style="border:none;">Gate C 出口关</el-tag>
          </div>
          <div class="card-middle">
            <div class="export-data-display">
              <span class="export-value">{{ inventory.exported_kg }}</span>
              <span class="export-unit">kg</span>
            </div>
          </div>
          <div class="card-bottom">
            <p>累计流转批次：<strong>{{ inventory.exported_count }}</strong> 批</p>
            <p class="desc-text">提示：数据已全部上链，进入全球溯源体系。</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Box, Clock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const loading = ref(true)
const inventory = ref({ raw_stock_kg: 0, raw_count: 0, finished_stock_kg: 0, finished_count: 0, exported_kg: 0, exported_count: 0 })

// 假设我们的单一仓库最大承载量是 50,000 kg，用来计算环形进度条的百分比
const MAX_CAPACITY = 50000 
const calcPercentage = (val) => {
  if (!val) return 0
  let pct = (Number(val) / MAX_CAPACITY) * 100
  return pct > 100 ? 100 : Number(pct.toFixed(1))
}

// 动态颜色：越多越红（快爆仓了）
const rawColors = [ { color: '#38bdf8', percentage: 20 }, { color: '#0284c7', percentage: 60 }, { color: '#0369a1', percentage: 80 }, { color: '#e11d48', percentage: 100 } ]
const finishedColors = [ { color: '#2dd4bf', percentage: 20 }, { color: '#0f766e', percentage: 60 }, { color: '#115e59', percentage: 80 }, { color: '#e11d48', percentage: 100 } ]

const fetchInventory = () => {
  axios.get('http://127.0.0.1:8000/api/inventory/')
    .then(res => {
      inventory.value = res.data.data
    })
    .catch(() => {
      ElMessage.error('获取实时仓储数据失败')
    })
    .finally(() => {
      loading.value = false
    })
}

onMounted(() => { fetchInventory() })
</script>

<style scoped>
.app-container { padding: 30px; background-color: #f1f5f9; min-height: 100vh; }
.wms-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
.header-left { display: flex; align-items: center; gap: 10px; color: #1e293b; }
.header-left h2 { margin: 0; font-size: 24px; letter-spacing: 1px; }

.inventory-row { margin-top: 20px; }
.stock-card { border-radius: 16px; border: none; height: 380px; display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.3s ease; }
.stock-card:hover { transform: translateY(-5px); }

.raw-stock { background: linear-gradient(180deg, #ffffff 0%, #f0f9ff 100%); border-top: 4px solid #0284c7; }
.finished-stock { background: linear-gradient(180deg, #ffffff 0%, #f0fdfa 100%); border-top: 4px solid #0f766e; }
.export-stock { background: linear-gradient(180deg, #ffffff 0%, #fff1f2 100%); border-top: 4px solid #be123c; }

.card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.stock-title { font-size: 16px; font-weight: bold; color: #334155; }

.card-middle { flex: 1; display: flex; justify-content: center; align-items: center; margin-bottom: 20px; }
.percentage-value { font-size: 32px; font-weight: 900; color: #1e293b; }
.unit { font-size: 14px; font-weight: normal; color: #64748b; margin-left: 4px; }

.export-data-display { text-align: center; background: #fff1f2; padding: 40px; border-radius: 50%; border: 8px solid #ffe4e6; }
.export-value { font-size: 42px; font-weight: 900; color: #be123c; }
.export-unit { font-size: 16px; font-weight: bold; color: #f43f5e; margin-left: 5px; }

.card-bottom { border-top: 1px dashed #cbd5e1; padding-top: 15px; }
.card-bottom p { margin: 5px 0; font-size: 15px; color: #475569; }
.desc-text { font-size: 12px !important; color: #94a3b8 !important; margin-top: 8px !important; }
</style>