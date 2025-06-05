<template>
  <el-menu
    :default-active="activeMenu"
    class="sidebar-menu"
    :collapse="isCollapse"
    router
  >
    <el-menu-item index="/ledger/list">
      <el-icon><Document /></el-icon>
      <template #title>台账列表</template>
    </el-menu-item>

    <el-menu-item index="/ledger/new">
      <el-icon><Plus /></el-icon>
      <template #title>新增台账</template>
    </el-menu-item>

    <template v-if="userStore.isAdmin">
      <el-menu-item index="/admin/users">
        <el-icon><User /></el-icon>
        <template #title>用户管理</template>
      </el-menu-item>

      <el-menu-item index="/admin/logs">
        <el-icon><List /></el-icon>
        <template #title>系统日志</template>
      </el-menu-item>
    </template>

    <template v-if="userStore.isAdmin || userStore.isPowerUser">
      <el-menu-item index="/statistics">
        <el-icon><DataLine /></el-icon>
        <template #title>系统统计</template>
      </el-menu-item>
    </template>
  </el-menu>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/store/user'
import {
  Document,
  Plus,
  User,
  List,
  DataLine
} from '@element-plus/icons-vue'

const route = useRoute()
const userStore = useUserStore()

// 当前激活的菜单项
const activeMenu = computed(() => route.path)

// 是否折叠侧边栏
const isCollapse = computed(() => false) // 可以根据需要设置为响应式变量
</script>

<style scoped>
.sidebar-menu {
  height: 100%;
  border-right: none;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 200px;
}
</style> 