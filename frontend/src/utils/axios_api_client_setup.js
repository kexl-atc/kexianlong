import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 创建 Axios 实例
const ApiClient = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  }
})

// 请求拦截器
ApiClient.interceptors.request.use(
  config => {
    console.log('Request:', config.url, config.method, config.data)
    // 从 localStorage 获取 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求发送失败:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
ApiClient.interceptors.response.use(
  response => {
    console.log('Response:', response.config.url, response.status, response.data)
    return response
  },
  error => {
    console.error('API请求出错:', error.response || error.message)
    
    const errorMessage = error.response?.data?.message || error.message || '未知错误'
    
    if (error.response) {
      switch (error.response.status) {
        case 401:
          ElMessage.error('登录状态已过期，请重新登录')
          localStorage.removeItem('token')
          localStorage.removeItem('userInfo')
          if (router.currentRoute.value.path !== '/login') {
            router.push('/login')
          }
          break
        case 403:
          ElMessage.error(errorMessage || '您没有权限执行此操作')
          break
        case 404:
          ElMessage.warning(errorMessage || '请求的资源不存在')
          break
        case 422:
          ElMessage.warning(errorMessage || '请求参数验证失败')
          break
        case 400:
          ElMessage.warning(errorMessage)
          break
        case 500:
          ElMessage.error(errorMessage || '服务器发生内部错误')
          break
        default:
          ElMessage.error(`请求失败 (${error.response.status}): ${errorMessage}`)
      }
    } else if (error.request) {
      ElMessage.error('网络请求失败，请检查您的网络连接')
      console.error('Network error:', error.request)
    } else {
      ElMessage.error('请求配置错误')
      console.error('Request config error:', error.message)
    }
    
    return Promise.reject(error)
  }
)

// 导出配置好的 ApiClient 实例
export default ApiClient