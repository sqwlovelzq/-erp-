import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import router from './router' // 👈 新增：引入路由

const app = createApp(App)
app.use(ElementPlus)
app.use(router) // 👈 新增：使用路由
app.mount('#app')