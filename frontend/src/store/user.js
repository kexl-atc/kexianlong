import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    // 从localStorage恢复数据
    token: localStorage.getItem('token') || null,
    userInfo: JSON.parse(localStorage.getItem('userInfo') || '{}')
  }),
  
  getters: {
    // 是否已认证
    isAuthenticated: (state) => !!state.token,
    
    // 当前用户信息
    currentUser: (state) => state.userInfo,
    
    // 用户ID
    currentUserId: (state) => state.userInfo?.id || null,
    
    // 用户名
    currentUsername: (state) => state.userInfo?.username || '未知用户',
    
    // 用户角色
    currentRole: (state) => state.userInfo?.role || 'user',
    
    // 是否是管理员
    isAdmin: (state) => state.userInfo?.role === 'admin',
    
    // 是否是高级用户
    isPowerUser: (state) => state.userInfo?.role === 'power_user',
    
    // 是否是普通用户
    isUser: (state) => state.userInfo?.role === 'user'
  },
  
  actions: {
    // 登录成功
    loginSuccess(token, userInfo) {
      this.token = token
      this.userInfo = userInfo
      
      // 持久化到localStorage
      localStorage.setItem('token', token)
      localStorage.setItem('userInfo', JSON.stringify(userInfo))
    },
    
    // 更新用户信息
    updateUserInfo(userInfo) {
      this.userInfo = { ...this.userInfo, ...userInfo }
      localStorage.setItem('userInfo', JSON.stringify(this.userInfo))
    },
    
    // 登出
    logout() {
      this.token = null
      this.userInfo = {}
      
      // 清除localStorage
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
    }
  }
})