<template>
  <template v-if="route.path === '/login' || route.path === '/public-trace'">
    <router-view />
  </template>

  <el-container v-else class="app-wrapper">
    <el-aside width="240px" class="ocean-sidebar">
      <div class="logo-zone">
        <div class="logo-icon">🌊</div>
        <div class="logo-text">
          <h2>Ocean Trace</h2>
          <p>全产业链溯源中台</p>
        </div>
      </div>

      <el-menu 
        :default-active="route.path" 
        router 
        class="ocean-menu" 
        background-color="transparent" 
        text-color="#94a3b8" 
        active-text-color="#ffffff">
        <el-menu-item index="/dashboard">
          <el-icon><Monitor /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <div class="menu-group-title">商业流转</div>
        <el-menu-item index="/order"><el-icon><Briefcase /></el-icon><span>零产：订单与客户</span></el-menu-item>
        
        <div class="menu-group-title">生产溯源</div>
        <el-menu-item index="/farm"><el-icon><Coordinate /></el-icon><span>一产：海洋牧场</span></el-menu-item>
        <el-menu-item index="/process"><el-icon><Cpu /></el-icon><span>二产：加工车间</span></el-menu-item>
        
        <div class="menu-group-title">大宗与出海</div>
        <el-menu-item index="/inventory"><el-icon><Box /></el-icon><span>仓储：动态库存 WMS</span></el-menu-item>
        <el-menu-item index="/export"><el-icon><Ship /></el-icon><span>三产：出口装柜</span></el-menu-item>
        
        <div class="menu-group-title">合规与清算</div>
        <el-menu-item index="/finance"><el-icon><DataLine /></el-icon><span>财务：成本利润核算</span></el-menu-item>
        <el-menu-item index="/receivable"><el-icon><Wallet /></el-icon><span>财务：资金风控放单</span></el-menu-item>
        <el-menu-item index="/documents"><el-icon><Document /></el-icon><span>单证：数字单据中枢</span></el-menu-item>
      </el-menu>
      
      <div class="sidebar-footer">
        <div class="user-info">
          <el-avatar :size="36" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" />
          <div class="user-desc">
            <strong>Admin</strong>
            <span>超级架构师</span>
          </div>
        </div>
      </div>
    </el-aside>

    <el-container class="main-container">
      <el-header class="glass-header">
        <div class="header-breadcrumb">
          <el-icon class="mr-2"><Guide /></el-icon>
          <span style="font-weight: 600; color: #1e293b; letter-spacing: 1px;">全球供应链流转节点监控</span>
        </div>
        <div class="header-actions">
          <el-tag type="info" effect="plain" round class="pulse-tag">🟢 局域网服务器运行中</el-tag>
          <el-button type="danger" plain round size="small" @click="handleLogout" class="logout-btn">
            <el-icon style="margin-right:4px;"><SwitchButton /></el-icon> 退出系统
          </el-button>
        </div>
      </el-header>

      <el-main class="ocean-main-bg">
        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'  
import { Guide, SwitchButton, Monitor, Briefcase, Coordinate, Cpu, Box, Ship, Money, Document,DataLine, Wallet } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const handleLogout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style>
/* 1. 锁死最外层：占满全屏，绝对不准外溢 */
.app-wrapper {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  display: flex;
}

/* 2. 锁死侧边栏：宽度固定，绝不缩水，内容多了自己滚动 */
.ocean-sidebar {
  height: 100vh;
  flex-shrink: 0; 
  overflow-y: auto;
  /* 你的背景色和边框样式可以保留在下面 */
  background-color: #0f172a; 
}

/* 3. 锁死右侧大容器：垂直排列，高度等于屏幕高度 */
.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden; /* 头部不准动 */
}

/* 4. 🚨 最关键的一步：右侧主内容区（你的图表和表格都在这里） */
.ocean-main-bg {
  flex: 1; /* 撑满头部以下的所有剩余空间 */
  overflow-y: auto; /* 只要内容超出屏幕，立马出现内部滚动条，绝对不去挤压别人！ */
  overflow-x: hidden;
  padding: 20px;
  box-sizing: border-box;
}

/* 美化一下右侧的滚动条，让它更有高级感 */
.ocean-main-bg::-webkit-scrollbar {
  width: 8px;
}
.ocean-main-bg::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}
/* =========================================================
   🌊 Ocean Trace 8.0 (修复完整版) - 顶级高保真·深海流体美学
   核心理念：深海沉浸感、水晶拟物光影、最高权重锁死背景！
   ========================================================= */
:root {
  /* 全局背景：极浅的冰蓝色，带来清透的海洋呼吸感 */
  --ocean-bg: #e8f0f8;
}

body {
  background-color: var(--ocean-bg);
  /* 注入海洋波纹般的微光背景 */
  background-image: radial-gradient(at 50% 0%, rgba(2, 132, 199, 0.05) 0px, transparent 50vw),
                    radial-gradient(at 100% 100%, rgba(16, 185, 129, 0.05) 0px, transparent 50vw);
}

/* ✨ 全局卡片底座 */
.el-card {
  border-radius: 20px !important;
  border: 1px solid rgba(255, 255, 255, 0.9) !important;
  background: rgba(255, 255, 255, 0.85) !important;
  backdrop-filter: blur(20px) !important;
  box-shadow:
    0 10px 30px -10px rgba(2, 132, 199, 0.08),
    inset 0 1px 0 0 rgba(255, 255, 255, 0.8) !important;
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
}

/* =========================================================
   🚨 核心重构：顶部数据看板（高权重锁死背景，绝对防白板！）
   ========================================================= */
.dashboard-cards .el-card {
  padding: 20px !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  position: relative;
  overflow: hidden;
  /* 先强行清空可能残留的白色背景 */
  background-color: transparent !important; 
}

/* ✨ 水晶反光层 */
.dashboard-cards .el-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 100%;
  background: linear-gradient(180deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0) 40%);
  pointer-events: none;
}

/* 🌊 1. 深海之心 (主色) - 注意这里加了 .el-card 提升权重 */
.dashboard-cards .el-card.primary-card {
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 50%, #082f49 100%) !important;
  box-shadow: 0 15px 35px -10px rgba(2, 132, 199, 0.5) !important;
}

/* 🌅 2. 破晓之辉 (警告) - 彻底修复这张卡片的白板问题！ */
.dashboard-cards .el-card.warning-card {
  background: linear-gradient(135deg, #f59e0b 0%, #ea580c 50%, #7c2d12 100%) !important;
  box-shadow: 0 15px 35px -10px rgba(234, 88, 12, 0.5) !important;
}

/* 🌿 3. 浅滩绿洲 (成功) */
.dashboard-cards .el-card.success-card {
  background: linear-gradient(135deg, #10b981 0%, #059669 50%, #064e3b 100%) !important;
  box-shadow: 0 15px 35px -10px rgba(16, 185, 129, 0.5) !important;
}

/* 🐚 4. 深渊珍珠 (信息) */
.dashboard-cards .el-card.info-card {
  background: linear-gradient(135deg, #64748b 0%, #475569 50%, #0f172a 100%) !important;
  box-shadow: 0 15px 35px -10px rgba(71, 85, 105, 0.5) !important;
}

/* 数据排版 */
.dashboard-cards .card-content {
  display: flex !important;
  align-items: center !important;
  padding: 0 !important;
  gap: 20px !important;
  position: relative; 
  z-index: 2;
}

/* 🧊 拟物化水晶图标底座 */
.dashboard-cards .card-icon {
  font-size: 34px !important;
  width: 72px !important;
  height: 72px !important;
  border-radius: 20px !important;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.4) !important;
  box-shadow: inset 0 2px 4px rgba(255, 255, 255, 0.3), 0 8px 16px rgba(0,0,0,0.1) !important;
  backdrop-filter: blur(10px) !important;
  color: #ffffff !important;
  display: flex !important; justify-content: center !important; align-items: center !important;
  margin: 0 !important; flex-shrink: 0 !important;
}

/* 🚨 强制文字发光防吞 */
.dashboard-cards .card-info { flex: 1 !important; display: flex !important; flex-direction: column !important; }

.dashboard-cards .card-title {
  font-size: 14px !important;
  font-weight: bold !important;
  color: rgba(255, 255, 255, 0.9) !important;
  margin-bottom: 6px !important;
  letter-spacing: 1px !important;
  text-transform: uppercase;
  text-shadow: 0 2px 5px rgba(0,0,0,0.4) !important;
}

.dashboard-cards .card-value {
  font-size: 40px !important;
  font-weight: 900 !important;
  color: #ffffff !important;
  line-height: 1 !important;
  text-shadow: 0 3px 8px rgba(0,0,0,0.5) !important; 
  display: flex !important;
  align-items: baseline !important;
}

.dashboard-cards .card-value .unit {
  font-size: 15px !important;
  font-weight: bold !important;
  color: rgba(255, 255, 255, 0.75) !important;
  margin-left: 8px !important;
  text-shadow: none !important;
}

/* ================== 其他区域全局优化 ================== */
.main-workspace { background: rgba(255, 255, 255, 0.95) !important; }
.el-table th.el-table__cell { 
  background: linear-gradient(to right, #f0f9ff, #e0f2fe) !important; 
  color: #0369a1 !important; 
  font-weight: 800 !important; 
  border-bottom: 2px solid #bae6fd !important;
}

/* 操作按钮 */
.el-button { border-radius: 10px !important; font-weight: bold !important; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important; }

.el-button--primary:not(.is-plain) {
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
  border: 1px solid #0ea5e9 !important;
  box-shadow: 0 4px 10px rgba(2, 132, 199, 0.3), inset 0 2px 0 rgba(255,255,255,0.2) !important;
}
.el-button--primary:not(.is-plain):hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(2, 132, 199, 0.4), inset 0 2px 0 rgba(255,255,255,0.3) !important; }

/* 表格内小按钮 */
.el-button.is-plain.is-circle {
  border-radius: 50% !important; padding: 8px !important;
  background: rgba(255,255,255,0.8) !important;
  backdrop-filter: blur(4px) !important;
}
.el-button--primary.is-plain { border: 1px solid #7dd3fc !important; color: #0284c7 !important; }
.el-button--primary.is-plain:hover { background: #e0f2fe !important; color: #0369a1 !important; transform: scale(1.1); }
.el-button--danger.is-plain { border: 1px solid #fecdd3 !important; color: #e11d48 !important; }
.el-button--danger.is-plain:hover { background: #ffe4e6 !important; color: #be123c !important; transform: scale(1.1); }
</style>

<style scoped>
/* =========================================================
   本页面的骨架专属样式 (侧边栏与顶部导航)
   ========================================================= */
.app-wrapper { height: 100vh; overflow: hidden; }

/* 侧边栏：深海拟物化 */
.ocean-sidebar {
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: 4px 0 15px rgba(0,0,0,0.1);
  z-index: 10;
}

.logo-zone { padding: 25px 20px; display: flex; align-items: center; gap: 15px; border-bottom: 1px solid rgba(255,255,255,0.05); }
.logo-icon { font-size: 32px; background: rgba(2, 132, 199, 0.2); width: 45px; height: 45px; display: flex; justify-content: center; align-items: center; border-radius: 12px; }
.logo-text h2 { margin: 0; color: #ffffff; font-size: 20px; font-weight: 900; letter-spacing: 1px; }
.logo-text p { margin: 4px 0 0 0; color: #38bdf8; font-size: 12px; font-weight: bold; text-transform: uppercase; letter-spacing: 1.5px; }

.ocean-menu { flex: 1; border-right: none; padding: 15px 10px; overflow-y: auto; }
.menu-group-title { color: #475569; font-size: 11px; font-weight: 900; text-transform: uppercase; letter-spacing: 2px; margin: 20px 0 10px 15px; }

/* 菜单项悬浮与激活效果 */
.ocean-sidebar :deep(.el-menu-item) {
  border-radius: 10px;
  margin-bottom: 5px;
  height: 45px;
  line-height: 45px;
  transition: all 0.3s ease;
}
.ocean-sidebar :deep(.el-menu-item:hover) { background-color: rgba(255, 255, 255, 0.05) !important; color: #ffffff !important; transform: translateX(5px); }
.ocean-sidebar :deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(2, 132, 199, 0.2) 0%, rgba(2, 132, 199, 0.05) 100%) !important;
  color: #38bdf8 !important;
  border-left: 4px solid #38bdf8;
  font-weight: bold;
}

.sidebar-footer { padding: 20px; background: rgba(0, 0, 0, 0.2); border-top: 1px solid rgba(255,255,255,0.05); }
.user-info { display: flex; align-items: center; gap: 12px; }
.user-desc { display: flex; flex-direction: column; }
.user-desc strong { color: white; font-size: 14px; }
.user-desc span { color: #10b981; font-size: 12px; font-weight: bold; }

/* 顶部导航：毛玻璃效果 */
.glass-header { background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(12px); border-bottom: 1px solid rgba(255, 255, 255, 0.3); display: flex; justify-content: space-between; align-items: center; padding: 0 30px; z-index: 5; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02); }
.header-breadcrumb { display: flex; align-items: center; font-size: 18px; }
.header-actions { display: flex; align-items: center; gap: 20px; }
.logout-btn { border-color: #fca5a5 !important; color: #be123c !important; background: transparent !important; }
.logout-btn:hover { background: #fff1f2 !important; border-color: #f43f5e !important; }

/* 主区域背景 */
.ocean-main-bg { background-color: var(--ocean-bg); padding: 20px 30px; position: relative; overflow-y: auto; }

/* 页面切换动画 */
.fade-transform-enter-active, .fade-transform-leave-active { transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); }
.fade-transform-enter-from { opacity: 0; transform: translateY(20px) scale(0.98); }
.fade-transform-leave-to { opacity: 0; transform: translateY(-20px) scale(0.98); }
</style>

