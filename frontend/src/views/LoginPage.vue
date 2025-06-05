<template>
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <h1>台账管理系统</h1>
          <p>请登录您的账号</p>
        </div>
        
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="login-form"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              prefix-icon="User"
              size="large"
              clearable
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              @click="handleLogin"
              style="width: 100%"
            >
              {{ loading ? '登录中...' : '登 录' }}
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="login-footer">
          <el-link type="primary" @click="showRegisterDialog">注册新账号</el-link>
        </div>
      </div>
      
      <!-- 注册对话框 -->
      <el-dialog
        v-model="registerDialogVisible"
        title="注册新账号"
        width="400px"
        :close-on-click-modal="false"
      >
        <el-form
          ref="registerFormRef"
          :model="registerForm"
          :rules="registerRules"
          label-width="80px"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="registerForm.username"
              placeholder="请输入用户名"
              clearable
            />
          </el-form-item>
          
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="请输入密码（至少6位）"
              show-password
            />
          </el-form-item>
          
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input
              v-model="registerForm.confirmPassword"
              type="password"
              placeholder="请再次输入密码"
              show-password
            />
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="registerDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="registerLoading" @click="handleRegister">
            {{ registerLoading ? '注册中...' : '注册' }}
          </el-button>
        </template>
      </el-dialog>
    </div>
  </template>
  
  <script>
  import { defineComponent, ref, reactive } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import { useUserStore } from '@/store/user'
  import { login, register } from '@/api/auth'
  
  export default defineComponent({
    name: 'LoginPage',
    setup() {
      const router = useRouter()
      const route = useRoute()
      const userStore = useUserStore()
      
      // 登录表单
      const loginFormRef = ref(null)
      const loginForm = reactive({
        username: '',
        password: ''
      })
      
      const loginRules = {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
        ]
      }
      
      const loading = ref(false)
      
      // 处理登录
      const handleLogin = async () => {
        const valid = await loginFormRef.value.validate().catch(() => false)
        if (!valid) return
        
        loading.value = true
        try {
          const res = await login(loginForm)
          
          if (res.data.success) {
            // 保存用户信息
            const userInfo = {
              id: res.data.user_id,
              username: res.data.username,
              role: res.data.role
            }
            userStore.loginSuccess(res.data.access_token, userInfo)
            
            ElMessage.success('登录成功')
            
            // 跳转到原目标页面或首页
            const redirect = route.query.redirect || '/ledger/list'
            router.push(redirect)
          }
        } catch (error) {
          console.error('Login error:', error)
        } finally {
          loading.value = false
        }
      }
      
      // 注册相关
      const registerDialogVisible = ref(false)
      const registerFormRef = ref(null)
      const registerForm = reactive({
        username: '',
        password: '',
        confirmPassword: ''
      })
      
      const validateConfirmPassword = (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      }
      
      const registerRules = {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请再次输入密码', trigger: 'blur' },
          { validator: validateConfirmPassword, trigger: 'blur' }
        ]
      }
      
      const registerLoading = ref(false)
      
      const showRegisterDialog = () => {
        registerForm.username = ''
        registerForm.password = ''
        registerForm.confirmPassword = ''
        registerDialogVisible.value = true
      }
      
      const handleRegister = async () => {
        const valid = await registerFormRef.value.validate().catch(() => false)
        if (!valid) return
        
        registerLoading.value = true
        try {
          const res = await register({
            username: registerForm.username,
            password: registerForm.password
          })
          
          if (res.data.success) {
            ElMessage.success('注册成功，请登录')
            registerDialogVisible.value = false
            
            // 自动填充登录表单
            loginForm.username = registerForm.username
            loginForm.password = ''
          }
        } catch (error) {
          console.error('Register error:', error)
        } finally {
          registerLoading.value = false
        }
      }
      
      return {
        loginFormRef,
        loginForm,
        loginRules,
        loading,
        handleLogin,
        registerDialogVisible,
        registerFormRef,
        registerForm,
        registerRules,
        registerLoading,
        showRegisterDialog,
        handleRegister
      }
    }
  })
  </script>
  
  <style scoped>
  .login-container {
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
  
  .login-card {
    width: 400px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
    padding: 40px;
  }
  
  .login-header {
    text-align: center;
    margin-bottom: 40px;
  }
  
  .login-header h1 {
    font-size: 28px;
    color: #303133;
    margin-bottom: 10px;
  }
  
  .login-header p {
    font-size: 14px;
    color: #909399;
  }
  
  .login-form {
    margin-bottom: 20px;
  }
  
  .login-footer {
    text-align: center;
  }
  
  :deep(.el-input__inner) {
    height: 48px;
  }
  
  :deep(.el-button) {
    height: 48px;
    font-size: 16px;
  }
  </style>