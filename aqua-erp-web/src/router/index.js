import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
  { path: '/order', name: 'Order', component: () => import('../views/OrderManage.vue') },
  { path: '/farm', name: 'Farm', component: () => import('../views/FarmManage.vue') },
  { path: '/process', name: 'Process', component: () => import('../views/ProcessManage.vue') },
  { path: '/export', name: 'Export', component: () => import('../views/ExportManage.vue') },
  { path: '/finance', name: 'Finance', component: () => import('../views/FinanceManage.vue') },
  { path: '/receivable', name: 'ReceivableManage', component: () => import('../views/ReceivableManage.vue') },
  { path: '/documents', name: 'DocumentManage', component: () => import('../views/DocumentManage.vue') },
  { path: '/inventory', name: 'Inventory', component: () => import('../views/InventoryManage.vue') },
  { path: '/public-trace', name: 'PublicTrace', component: () => import('../views/TracePublic.vue') }
]
const router = createRouter({history: createWebHistory(),routes})

// 登录拦截守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('erp_token')
  
  // 🚨 核心修改：如果是去 /login 或者去 /public-trace，都不需要拦截！直接放行！
  if (to.path !== '/login' && to.path !== '/public-trace' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router