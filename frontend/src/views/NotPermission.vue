<template>
  <div class="not-permission-container">
    <div class="content">
      <div class="error-code">403</div>
      <h2>无权限访问</h2>
      <p>抱歉，您没有权限访问此页面</p>
      <div class="actions">
        <el-button type="primary" icon="House" @click="goHome">
          返回首页
        </el-button>
      </div>
    </div>
    <div class="header-right">
      <el-button type="primary" icon="ArrowLeft" @click="goBack">返回列表</el-button>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { useRouter } from 'vue-router'

export default defineComponent({
  name: 'NotPermission',
  setup() {
    const router = useRouter()
    const goHome = () => {
      router.push('/')
    }
    const goBack = () => {
      router.back()
    }
    return { goHome, goBack }
  }
})
</script>

<style scoped>
.not-permission-container {
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
  color: #e6a23c;
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
.header-right {
  position: absolute;
  top: 10px;
  right: 10px;
}
</style> 