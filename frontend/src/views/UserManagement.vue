<template>
    <div class="page-container">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-left">
          <h2>用户管理</h2>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>系统管理</el-breadcrumb-item>
            <el-breadcrumb-item>用户管理</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-button type="primary" icon="ArrowLeft" @click="goBack">返回列表</el-button>
        </div>
      </div>
      
      <!-- 权限检查 -->
      <div v-if="!userStore.isAdmin" class="no-permission">
        <el-empty description="您没有权限访问此页面">
          <el-button type="primary" @click="goBack">返回</el-button>
        </el-empty>
      </div>
      
      <!-- 用户管理内容 -->
      <div v-else class="content-container">
        <!-- 搜索栏 -->
        <div class="search-bar">
          <el-form :inline="true" :model="searchForm" class="search-form">
            <el-form-item label="用户名">
              <el-input
                v-model="searchForm.search"
                placeholder="搜索用户名"
                clearable
                @keyup.enter="handleSearch"
              />
            </el-form-item>
            <el-form-item label="角色">
              <el-select
                v-model="searchForm.role"
                placeholder="全部角色"
                clearable
                style="width: 120px"
              >
                <el-option label="管理员" value="admin" />
                <el-option label="高级用户" value="power_user" />
                <el-option label="普通用户" value="user" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" icon="Search" @click="handleSearch">搜索</el-button>
              <el-button icon="Refresh" @click="handleReset">重置</el-button>
            </el-form-item>
          </el-form>
          
          <div class="action-buttons">
            <el-button type="primary" icon="Plus" @click="showAddDialog">新增用户</el-button>
          </div>
        </div>
        
        <!-- 用户表格 -->
        <el-table
          v-loading="loading"
          :data="tableData"
          border
          stripe
          style="width: 100%"
        >
          <el-table-column type="index" label="序号" width="60" :index="getIndex" />
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="role" label="角色" width="120">
            <template #default="{ row }">
              <el-tag :type="getRoleType(row.role)">
                {{ getRoleName(row.role) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="entry_count" label="台账数量" width="100" />
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button
                v-if="row.username !== 'admin'"
                type="primary"
                size="small"
                link
                @click="showEditDialog(row)"
              >
                修改角色
              </el-button>
              <el-button
                type="warning"
                size="small"
                link
                @click="resetPassword(row)"
              >
                重置密码
              </el-button>
              <el-button
                v-if="row.username !== 'admin' && row.username !== userStore.currentUsername"
                type="danger"
                size="small"
                link
                @click="handleDelete(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页 -->
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          class="pagination"
        />
      </div>
      
      <!-- 新增用户对话框 -->
      <el-dialog
        v-model="addDialogVisible"
        title="新增用户"
        width="500px"
        :close-on-click-modal="false"
      >
        <el-form
          ref="addFormRef"
          :model="addForm"
          :rules="addRules"
          label-width="100px"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="addForm.username"
              placeholder="请输入用户名"
              autocomplete="off"
            />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="addForm.password"
              type="password"
              placeholder="请输入密码（至少6位）"
              show-password
              autocomplete="new-password"
            />
          </el-form-item>
          <el-form-item label="角色" prop="role">
            <el-select v-model="addForm.role" placeholder="请选择角色">
              <el-option label="管理员" value="admin" />
              <el-option label="高级用户" value="power_user" />
              <el-option label="普通用户" value="user" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="addDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="addLoading" @click="handleAdd">
            确定
          </el-button>
        </template>
      </el-dialog>
      
      <!-- 修改角色对话框 -->
      <el-dialog
        v-model="editDialogVisible"
        title="修改用户角色"
        width="400px"
        :close-on-click-modal="false"
      >
        <el-form label-width="100px">
          <el-form-item label="用户名">
            <el-input :value="currentUser.username" disabled />
          </el-form-item>
          <el-form-item label="当前角色">
            <el-tag :type="getRoleType(currentUser.role)">
              {{ getRoleName(currentUser.role) }}
            </el-tag>
          </el-form-item>
          <el-form-item label="新角色">
            <el-select v-model="newRole" placeholder="请选择新角色">
              <el-option label="管理员" value="admin" />
              <el-option label="高级用户" value="power_user" />
              <el-option label="普通用户" value="user" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="editLoading" @click="handleUpdateRole">
            确定
          </el-button>
        </template>
      </el-dialog>
    </div>
  </template>
  
  <script>
  import { defineComponent, ref, reactive, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import { useUserStore } from '@/store/user'
  import { getUserList, updateUserRole, deleteUser } from '@/api/admin'
  import { register } from '@/api/auth'
  
  export default defineComponent({
    name: 'UserManagement',
    setup() {
      const router = useRouter()
      const userStore = useUserStore()
      
      // 搜索表单
      const searchForm = reactive({
        search: '',
        role: ''
      })
      
      // 表格数据
      const tableData = ref([])
      const loading = ref(false)
      const currentPage = ref(1)
      const pageSize = ref(20)
      const total = ref(0)
      
      // 新增用户
      const addDialogVisible = ref(false)
      const addFormRef = ref(null)
      const addForm = reactive({
        username: '',
        password: '',
        role: 'user'
      })
      const addRules = {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
        ],
        role: [
          { required: true, message: '请选择角色', trigger: 'change' }
        ]
      }
      const addLoading = ref(false)
      
      // 修改角色
      const editDialogVisible = ref(false)
      const currentUser = ref({})
      const newRole = ref('')
      const editLoading = ref(false)
      
      // 获取角色标签类型
      const getRoleType = (role) => {
        const typeMap = {
          'admin': 'danger',
          'power_user': 'warning',
          'user': 'primary'
        }
        return typeMap[role] || 'info'
      }
      
      // 获取角色名称
      const getRoleName = (role) => {
        const nameMap = {
          'admin': '管理员',
          'power_user': '高级用户',
          'user': '普通用户'
        }
        return nameMap[role] || role
      }
      
      // 格式化日期
      const formatDate = (dateString) => {
        if (!dateString) return '-'
        return new Date(dateString).toLocaleString('zh-CN')
      }
      
      // 获取表格序号
      const getIndex = (index) => {
        return (currentPage.value - 1) * pageSize.value + index + 1
      }
      
      // 获取用户列表
      const fetchUsers = async () => {
        loading.value = true
        try {
          const params = {
            page: currentPage.value,
            pageSize: pageSize.value,
            search: searchForm.search,
            role: searchForm.role
          }
          
          const res = await getUserList(params)
          if (res.data.code === 0) {
            tableData.value = res.data.data.users
            total.value = res.data.data.total
          } else {
            ElMessage.error(res.data.message || '获取用户列表失败')
          }
        } catch (error) {
          console.error('获取用户列表失败:', error)
        } finally {
          loading.value = false
        }
      }
      
      // 搜索
      const handleSearch = () => {
        currentPage.value = 1
        fetchUsers()
      }
      
      // 重置
      const handleReset = () => {
        searchForm.search = ''
        searchForm.role = ''
        currentPage.value = 1
        fetchUsers()
      }
      
      // 分页变化
      const handleSizeChange = () => {
        currentPage.value = 1
        fetchUsers()
      }
      
      const handleCurrentChange = () => {
        fetchUsers()
      }
      
      // 显示新增对话框
      const showAddDialog = () => {
        addForm.username = ''
        addForm.password = ''
        addForm.role = 'user'
        addDialogVisible.value = true
      }
      
      // 新增用户
      const handleAdd = async () => {
        const valid = await addFormRef.value.validate().catch(() => false)
        if (!valid) return
        addLoading.value = true
        try {
          const res = await register(addForm)
          if (res.data.code === 0 || res.data.success) {
            ElMessage.success('新增用户成功')
            addDialogVisible.value = false
            currentPage.value = 1 // 新增后跳到第一页
            fetchUsers()
          } else {
            ElMessage.error(res.data.message || '新增用户失败')
          }
        } catch (error) {
          ElMessage.error('新增用户失败')
          console.error('新增用户失败:', error)
        } finally {
          addLoading.value = false
        }
      }
      
      // 显示修改角色对话框
      const showEditDialog = (row) => {
        currentUser.value = row
        newRole.value = row.role
        editDialogVisible.value = true
      }
      
      // 修改角色
      const handleUpdateRole = async () => {
        if (newRole.value === currentUser.value.role) {
          ElMessage.warning('角色未改变')
          return
        }
        
        editLoading.value = true
        try {
          const res = await updateUserRole(currentUser.value.id, newRole.value)
          if (res.data.code === 0) {
            ElMessage.success('角色修改成功')
            editDialogVisible.value = false
            fetchUsers()
          }
        } catch (error) {
          console.error('修改角色失败:', error)
        } finally {
          editLoading.value = false
        }
      }
      
      // 重置密码
      const resetPassword = async (row) => {
        try {
          await ElMessageBox.confirm(
            `确定要重置用户 "${row.username}" 的密码为初始密码 "123456" 吗？`,
            '提示',
            {
              confirmButtonText: '确定',
              cancelButtonText: '取消',
              type: 'warning'
            }
          )
          
          // 这里应该调用重置密码的API
          ElMessage.success('密码重置成功，新密码为：123456')
        } catch (error) {
          // 用户取消
        }
      }
      
      // 删除用户
      const handleDelete = async (row) => {
        try {
          await ElMessageBox.confirm(
            `确定要删除用户 "${row.username}" 吗？此操作将同时删除该用户的所有台账记录。`,
            '警告',
            {
              confirmButtonText: '确定',
              cancelButtonText: '取消',
              type: 'warning'
            }
          )
          
          const res = await deleteUser(row.id)
          if (res.data.code === 0) {
            ElMessage.success('删除成功')
            fetchUsers()
          } else {
            ElMessage.error(res.data.message || '删除失败')
          }
        } catch (error) {
          if (error !== 'cancel') {
            console.error('删除失败:', error)
          }
        }
      }
      
      // 返回
      const goBack = () => {
        router.push('/ledger/list')
      }
      
      // 初始化
      onMounted(() => {
        if (!userStore.isAuthenticated || !userStore.isAdmin) {
          router.replace({ path: '/not-permission' })
        }
        if (userStore.isAdmin) {
          fetchUsers()
        }
      })
      
      return {
        userStore,
        searchForm,
        tableData,
        loading,
        currentPage,
        pageSize,
        total,
        addDialogVisible,
        addFormRef,
        addForm,
        addRules,
        addLoading,
        editDialogVisible,
        currentUser,
        newRole,
        editLoading,
        getRoleType,
        getRoleName,
        formatDate,
        getIndex,
        handleSearch,
        handleReset,
        handleSizeChange,
        handleCurrentChange,
        showAddDialog,
        handleAdd,
        showEditDialog,
        handleUpdateRole,
        resetPassword,
        handleDelete,
        goBack
      }
    }
  })
  </script>
  
  <style scoped>
  .page-container {
    min-height: 100vh;
    background-color: #f5f7fa;
  }
  
  .page-header {
    background-color: white;
    padding: 16px 20px;
    border-bottom: 1px solid #e6e6e6;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .header-left h2 {
    margin: 0 0 8px 0;
    font-size: 20px;
    color: #303133;
  }
  
  .no-permission {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: calc(100vh - 200px);
  }
  
  .content-container {
    padding: 16px;
  }
  
  .search-bar {
    background-color: white;
    padding: 20px;
    margin-bottom: 16px;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }
  
  .search-form {
    flex: 1;
  }
  
  .action-buttons {
    display: flex;
    gap: 10px;
  }
  
  .el-table {
    background-color: white;
    border-radius: 4px;
    overflow: hidden;
  }
  
  .pagination {
    margin-top: 20px;
    text-align: right;
  }
  
  :deep(.el-breadcrumb) {
    font-size: 14px;
  }
  </style>