<template>
  <div class="h5-container">
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading" :size="40" color="#10b981"><Loading /></el-icon>
      <p>正在从区块链及数据库读取溯源档案...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <el-icon :size="60" color="#ef4444"><WarningFilled /></el-icon>
      <h2>溯源失败</h2>
      <p>抱歉，未找到该批次金鲳鱼的合规流转记录，或该商品未经授权。</p>
    </div>

    <div v-else-if="traceData" class="trace-content">
      <div class="header-banner">
        <div class="trust-badge">
          <el-icon><CircleCheckFilled /></el-icon> 官方认证 · 全链路追溯
        </div>
        <h1>深海优选金鲳鱼</h1>
        <p class="sn-text">防伪溯源码：{{ traceData.trace_sn }}</p>
      </div>

      <div class="timeline-card">
        <h3 class="section-title"><el-icon><Compass /></el-icon> 追溯时间轴</h3>
        <el-timeline>
          
          <el-timeline-item type="success" size="large" icon="OfficeBuilding" :timestamp="'加工工厂：' + traceData.process_info.factory">
            <div class="node-box">
              <h4>冷链加工与合规检测</h4>
              <p>加工批次：{{ traceData.process_info.process_id }}</p>
              <p>核心温控：<span class="highlight-green">{{ traceData.process_info.temp_control }}</span></p>
              <el-tag size="small" type="success" effect="dark" class="mt-2">海关出口级检测合格</el-tag>
            </div>
          </el-timeline-item>

          <el-timeline-item type="warning" size="large" icon="Ship" :timestamp="'起捕日期：' + traceData.harvest_info.harvest_date">
            <div class="node-box">
              <h4>科学出笼与起捕</h4>
              <p>起捕单号：{{ traceData.harvest_info.harvest_id }}</p>
              <p>起捕重量：{{ traceData.harvest_info.quantity }} kg</p>
            </div>
          </el-timeline-item>

          <el-timeline-item type="primary" size="large" icon="Location" :timestamp="'入海日期：' + traceData.farm_info.stocking_date">
            <div class="node-box">
              <h4>深海生态网箱养殖</h4>
              <p>养殖批次：{{ traceData.farm_info.batch_id }}</p>
              <p>海域单元：{{ traceData.farm_info.unit }}</p>
              <p>责任人：{{ traceData.farm_info.responsible_person }}</p>
            </div>
          </el-timeline-item>
          
        </el-timeline>
      </div>

      <div class="footer-endorsement">
        <div class="stamp-icon">🛡️</div>
        <p>本数据由金鲳鱼 ERP 溯源引擎与合规放行网关 (Gate C) 联合担保，数据不可篡改。</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { Loading, WarningFilled, CircleCheckFilled, Compass, OfficeBuilding, Ship, Location } from '@element-plus/icons-vue'

const route = useRoute()
const traceData = ref(null)
const loading = ref(true)
const error = ref(false)

onMounted(() => {
  // 从网址中获取 ?sn=PROC-XXX 的查询参数
  const sn = route.query.sn
  if (!sn) {
    loading.value = false
    error.value = true
    return
  }

  // 呼叫后端的溯源接口 (直接利用咱们之前写好的 get_trace_report 接口)
  axios.get(`http://127.0.0.1:8000/api/trace/${sn}/`)
    .then(res => {
      traceData.value = res.data.data
    })
    .catch(() => {
      error.value = true
    })
    .finally(() => {
      // 为了让加载动画显示一下，故意延迟0.5秒
      setTimeout(() => { loading.value = false }, 500)
    })
})
</script>

<style scoped>
/* 针对手机端设计的 H5 专属样式 */
.h5-container {
  max-width: 480px; /* 模拟手机屏幕宽度 */
  margin: 0 auto;
  min-height: 100vh;
  background-color: #f3f4f6;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  overflow-x: hidden;
}

.loading-state, .error-state {
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 20px;
  color: #6b7280;
}

.header-banner {
  background: linear-gradient(135deg, #047857 0%, #10b981 100%);
  color: white;
  padding: 40px 20px 30px;
  text-align: center;
  border-bottom-left-radius: 20px;
  border-bottom-right-radius: 20px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.trust-badge {
  display: inline-block;
  background: rgba(255,255,255,0.2);
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  width: max-content;
  margin: 0 auto 15px;
}

.header-banner h1 { margin: 0 0 10px; font-size: 24px; letter-spacing: 1px; }
.sn-text { font-family: monospace; font-size: 13px; opacity: 0.9; margin: 0; background: rgba(0,0,0,0.1); padding: 4px 10px; border-radius: 4px; display: inline-block;}

.timeline-card {
  background: white;
  margin: -15px 15px 20px;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
  position: relative;
  z-index: 10;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1f2937;
  font-size: 16px;
  margin-bottom: 25px;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 10px;
}

.node-box {
  background: #f9fafb;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #f3f4f6;
  margin-top: 5px;
}

.node-box h4 { margin: 0 0 8px; font-size: 14px; color: #374151; }
.node-box p { margin: 4px 0; font-size: 12px; color: #6b7280; }
.highlight-green { color: #059669; font-weight: bold; }
.mt-2 { margin-top: 8px; }

.footer-endorsement {
  text-align: center;
  padding: 20px;
  color: #9ca3af;
  font-size: 11px;
  line-height: 1.6;
  padding-bottom: 40px;
}
.stamp-icon { font-size: 24px; margin-bottom: 5px; opacity: 0.5; }
</style>