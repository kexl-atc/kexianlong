<template>
    <div class="not-found-container">
      <div class="content">
        <div class="error-code">404</div>
        <h2>页面不存在</h2>
        <p>抱歉，您访问的页面不存在或已被移除</p>
        <div class="actions">
          <el-button type="primary" icon="House" @click="goHome">
            返回首页
          </el-button>
          <el-button icon="ArrowLeft" @click="goBack">
            返回上一页
          </el-button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { defineComponent } from 'vue'
  import { useRouter } from 'vue-router'
  
  export default defineComponent({
    name: 'NotFound',
    setup() {
      const router = useRouter()
      
      const goHome = () => {
        router.push('/')
      }
      
      const goBack = () => {
        router.back()
      }
      
      return {
        goHome,
        goBack
      }
    }
  })
  </script>
  
  <style scoped>
  .not-found-container {
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #f5f7fa;
  }
  
  .content {
    text-align: center;
    padding: 40px;
  }
  
  .error-code {
    font-size: 120px;
    font-weight: bold;
    color: #909399;
    margin-bottom: 20px;
    line-height: 1;
  }
  
  .content h2 {
    font-size: 24px;
    color: #303133;
    margin-bottom: 10px;
  }
  
  .content p {
    font-size: 16px;
    color: #606266;
    margin-bottom: 30px;
  }
  
  .actions {
    display: flex;
    justify-content: center;
    gap: 20px;
  }
  </style>