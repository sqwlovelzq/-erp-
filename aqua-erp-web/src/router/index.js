import { createRouter, createWebHistory } from 'vue-router'
import FarmManage from '../views/FarmManage.vue'
import ProcessManage from '../views/ProcessManage.vue'
import ExportManage from '../views/ExportManage.vue'
import FinanceManage from '../views/FinanceManage.vue' 
import OrderManage from '../views/OrderManage.vue'
import Login from '../views/Login.vue' 
import TracePublic from '../views/TracePublic.vue' 
import InventoryManage from '../views/InventoryManage.vue'


const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: Login },
  { path: '/order', name: 'Order', component: OrderManage },
  { path: '/farm', name: 'Farm', component: FarmManage },
  { path: '/process', name: 'Process', component: ProcessManage },
  { path: '/export', name: 'Export', component: ExportManage },
  { path: '/finance', name: 'Finance', component: FinanceManage },
  { path: '/public-trace', name: 'PublicTrace', component: TracePublic } ,
  { path: '/inventory', name: 'Inventory', component: InventoryManage },
  {path: '/dashboard',name: 'Dashboard',component: () => import('../views/Dashboard.vue') },
  {path: '/documents',name: 'DocumentManage',component: () => import('../views/DocumentManage.vue')},
  {path: '/finance',name: 'FinanceManage',component: () => import('../views/FinanceManage.vue')},
  {path: '/receivable',name: 'ReceivableManage',component: () => import('../views/ReceivableManage.vue')},
  {path: '/documents',name: 'DocumentManage',component: () => import('../views/DocumentManage.vue')}
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