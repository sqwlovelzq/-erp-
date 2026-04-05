<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <div class="logo-icon">🌊</div>
        <h2>金鲳鱼全产业链 ERP</h2>
        <p>数字溯源与合规放单系统 V1.0</p>
      </div>

      <el-form :model="form" class="login-form" @keyup.enter="handleLogin">
        <el-form-item>
          <el-input 
            v-model="form.username" 
            placeholder="请输入您的专属账号" 
            size="large"
            clearable>
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="请输入安全密码" 
            size="large" 
            show-password>
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-button 
          type="primary" 
          class="submit-btn" 
          size="large" 
          :loading="loading" 
          @click="handleLogin">
          {{ loading ? '安 全 验 证 中...' : '登 录 系 统' }}
        </el-button>
      </el-form>
      
      <div class="login-footer">
        技术支持：系统架构部 | 工业级数据审计驱动
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue' // 👈 引入酷炫的图标

const router = useRouter()
const form = reactive({ username: '', password: '' })
const loading = ref(false)

const handleLogin = () => {
  if (!form.username || !form.password) {
    return ElMessage.warning('账号和密码不能为空！')
  }
  
  loading.value = true
  axios.post('http://127.0.0.1:8000/api/login/', form)
    .then(res => {
      // 登录成功，把钥匙存起来
      localStorage.setItem('erp_token', res.data.token)
      localStorage.setItem('erp_role', res.data.role)
      ElMessage.success({ message: res.data.message, duration: 2000 })
      
      // 根据角色智能跳转 (如果是业务员去出口，如果是财务去财务室)
      setTimeout(() => {
        if (res.data.role === '记录员') {
          router.push('/export')
        } else {
          router.push('/farm') // 厂长或管理员默认去一产养殖
        }
      }, 500)
    })
    .catch(err => {
      ElMessage.error(err.response?.data?.message || '服务器连接失败')
    })
    .finally(() => {
      loading.value = false
    })
}
</script>

<style scoped>
/* 终极深海渐变背景 */
.login-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
  overflow: hidden;
}

/* 磨砂玻璃质感的登录卡片 */
.login-box {
  width: 420px;
  background: rgba(255, 255, 255, 0.95);
  padding: 40px 40px 30px;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
}

.login-header {
  text-align: center;
  margin-bottom: 35px;
}

.logo-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.login-header h2 {
  margin: 0;
  font-size: 24px;
  color: #2c3e50;
  letter-spacing: 1px;
}

.login-header p {
  margin: 8px 0 0;
  font-size: 13px;
  color: #7f8c8d;
  letter-spacing: 2px;
}

.login-form {
  margin-bottom: 20px;
}

/* 深度定制 Element Plus 的输入框圆角 */
:deep(.el-input__wrapper) {
  border-radius: 8px;
  padding: 4px 11px;
}

.submit-btn {
  width: 100%;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  letter-spacing: 4px;
  background: linear-gradient(to right, #1d976c, #93f9b9); /* 成功放行的翠绿色调 */
  border: none;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(29, 151, 108, 0.4);
}

.login-footer {
  text-align: center;
  font-size: 12px;
  color: #bdc3c7;
  border-top: 1px solid #ecf0f1;
  padding-top: 15px;
}
</style>