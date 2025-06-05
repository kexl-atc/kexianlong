import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { useUserStore } from '@/store/user'

// 创建axios实例
const request = axios.create({
  baseURL: import.meta.env.VUE_APP_API_BASE_URL || '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 从localStorage获取token
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    
    // 添加时间戳防止缓存
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now()
      }
    }
    
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    // 如果响应有success字段，检查是否成功
    const res = response.data
    
    if (Object.prototype.hasOwnProperty.call(res, 'success') && !res.success) {
      ElMessage({
        message: res.message || '操作失败',
        type: 'error',
        duration: 3000
      })
      return Promise.reject(new Error(res.message || 'Error'))
    }
    
    return response
  },
  error => {
    console.error('Response error:', error)
    
    // 获取错误信息
    let message = error.message || '网络错误'
    
    if (error.response) {
      const { status, data } = error.response
      
      // 根据状态码处理
      switch (status) {
        case 401:{
          message = data.message || '登录已过期，请重新登录'
          // 清除用户信息
          const userStore = useUserStore()
          userStore.logout()
          // 跳转到登录页
          if (router.currentRoute.value.path !== '/login') {
            router.push({
              path: '/login',
              query: { redirect: router.currentRoute.value.fullPath }
            })
          }
          break
        }  
        case 403:
          message = data.message || '没有权限执行此操作'
          break
          
        case 404:
          message = data.message || '请求的资源不存在'
          break
          
        case 400:
        case 422:
          message = data.message || '请求参数错误'
          break
          
        case 500:
          message = data.message || '服务器内部错误'
          break
          
        default:
          message = data.message || `请求失败(${status})`
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      message = '网络连接失败，请检查网络'
    }
    
    // 显示错误消息
    ElMessage({
      message,
      type: 'error',
      duration: 3000
    })
    
    return Promise.reject(error)
  }
)

export default request