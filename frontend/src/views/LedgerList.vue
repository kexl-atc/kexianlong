<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>台账管理系统</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item>首页</el-breadcrumb-item>
          <el-breadcrumb-item>台账列表</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-icon><User /></el-icon>
            {{ userStore && userStore.currentUsername ? userStore.currentUsername : '' }}
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人信息</el-dropdown-item>
              <el-dropdown-item command="password">修改密码</el-dropdown-item>
              <el-dropdown-item v-if="userStore.isAdmin" command="user-management">用户管理</el-dropdown-item>
              <el-dropdown-item v-if="userStore.isAdmin" command="admin-logs">系统日志</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <!-- 搜索和操作栏 -->
    <div class="search-bar">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="省份">
          <el-select
            v-model="searchForm.province"
            placeholder="全部省份"
            clearable
            filterable
            allow-create
            @change="handleProvinceChange"
            style="width: 150px"
          >
            <el-option
              v-for="item in provinceList"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="项目名称">
          <el-autocomplete
            v-model="searchForm.project_name"
            :fetch-suggestions="handleProjectInput"
            :loading="projectSuggestionsLoading"
            placeholder="请输入项目名称"
            clearable
            style="width: 100%"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
            <template #default="{ item }">
              <span v-html="highlightKeyword(item.value, searchForm.project_name)"></span>
            </template>
            <template #empty>
              <span v-if="projectSuggestionsLoading">正在加载...</span>
              <span v-else>无匹配结果</span>
            </template>
          </el-autocomplete>
        </el-form-item>
        <el-form-item label="开会地点">
          <el-autocomplete
            v-model="searchForm.location"
            :fetch-suggestions="handleLocationInput"
            :loading="locationSuggestionsLoading"
            placeholder="请输入开会地点"
            clearable
            style="width: 100%"
            @select="handleLocationSelect"
          >
            <template #prefix>
              <el-icon><Location /></el-icon>
            </template>
            <template #default="{ item }">
              <span v-html="highlightKeyword(item.value, searchForm.location)" />
              <span v-if="item.group" style="color:#aaa;font-size:12px;margin-left:8px;">{{ item.group }}</span>
            </template>
            <template #empty>
              <span v-if="locationSuggestionsLoading">正在加载...</span>
              <span v-else>无匹配结果</span>
            </template>
          </el-autocomplete>
        </el-form-item>
        <el-form-item label="录入人员">
          <el-select
            v-model="searchForm.recorder"
            placeholder="全部人员"
            clearable
            filterable
            style="width: 150px"
          >
            <el-option
              v-for="user in recorderList"
              :key="user"
              :label="user"
              :value="user"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleDateChange"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="handleSearch">搜索</el-button>
          <el-button icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <div class="action-buttons">
        <el-button type="primary" icon="Plus" @click="handleAdd">新增台账</el-button>
        <el-dropdown @command="handleExportFormat" :disabled="exportLoading">
          <el-button icon="Download" :loading="exportLoading">
            导出数据 <el-icon><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="csv">导出 CSV</el-dropdown-item>
              <el-dropdown-item command="excel">导出 Excel</el-dropdown-item>
              <el-dropdown-item command="word">导出 Word</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <!-- 数据表格 -->
    <el-table
      v-loading="loading"
      :data="tableData"
      border
      stripe
      style="width: 100%"
      @sort-change="handleSortChange"
    >
      <el-table-column type="index" label="序号" width="60" :index="getIndex" />
      <el-table-column prop="recorder" label="录入人员" width="100" />
      <el-table-column prop="province" label="省份" width="100" />
      <el-table-column prop="project_name" label="项目名称" min-width="150" show-overflow-tooltip />
      <el-table-column prop="date" label="日期" width="110" sortable="custom" />
      <el-table-column prop="location" label="开会地点" min-width="120" show-overflow-tooltip />
      <el-table-column prop="personnel" label="涉及人员" min-width="150" show-overflow-tooltip />
      <el-table-column prop="nature" label="性质" width="120" />
      
      <!-- 长文本字段使用Tooltip -->
      <el-table-column prop="specific_matters" label="具体事项" min-width="200">
        <template #default="{ row }">
          <el-tooltip
            :content="row.specific_matters"
            placement="top"
            :disabled="!row.specific_matters || row.specific_matters.length < 50"
          >
            <div class="text-truncate">
              {{ row.specific_matters }}
            </div>
          </el-tooltip>
        </template>
      </el-table-column>
      
      <el-table-column prop="follow_up_points" label="后续要点" min-width="200">
        <template #default="{ row }">
          <el-tooltip
            :content="row.follow_up_points"
            placement="top"
            :disabled="!row.follow_up_points || row.follow_up_points.length < 50"
          >
            <div class="text-truncate">
              {{ row.follow_up_points || '-' }}
            </div>
          </el-tooltip>
        </template>
      </el-table-column>
      
      <el-table-column prop="created_at" label="创建时间" width="160" sortable="custom">
        <template #default="{ row }">
          {{ formatDateOnly(row.created_at) }}
        </template>
      </el-table-column>
      
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button
            v-if="canEdit(row)"
            type="primary"
            size="small"
            link
            @click="handleEdit(row)"
          >
            编辑
          </el-button>
          <el-button
            v-if="canDelete(row)"
            type="danger"
            size="small"
            link
            @click="handleDelete(row)"
          >
            删除
          </el-button>
          <el-button
            type="info"
            size="small"
            link
            @click="handleView(row)"
          >
            查看
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="[10, 20, 50, 100]"
      :total="total"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      class="pagination"
    />
    
    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="修改密码"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="原密码" prop="oldPassword">
          <el-input
            v-model="passwordForm.oldPassword"
            type="password"
            placeholder="请输入原密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            placeholder="请输入新密码（至少6位）"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="passwordLoading" @click="handleChangePassword">
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
import { getLedgerList, deleteLedgerEntry, getProvinces, exportLedger, getProjectSuggestions } from '@/api/ledger'
import { changePassword } from '@/api/auth'
import debounce from 'lodash/debounce'
import axios from 'axios'
import { ArrowDown } from '@element-plus/icons-vue'

export default defineComponent({
  name: 'LedgerList',
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    
    // 搜索表单
    const searchForm = reactive({
      project_name: '',
      location: '',
      province: '',
      recorder: '',
      start_date: '',
      end_date: ''
    })
    
    const dateRange = ref(null)
    const provinceList = ref([])
    const recorderList = ref([]) // 录入人员列表
    const currentProvinceData = ref([]) // 当前省份的数据
    
    // 表格数据
    const tableData = ref([])
    const loading = ref(false)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = ref(0)
    const sortProp = ref('')
    const sortOrder = ref('')
    
    // 获取表格序号
    const getIndex = (index) => {
      return (currentPage.value - 1) * pageSize.value + index + 1
    }
    
    // 权限判断
    const canEdit = (row) => {
      return userStore.isAdmin || userStore.isPowerUser || 
        (userStore.isUser && row.user_id === userStore.currentUserId)
    }
    
    const canDelete = (row) => {
      return userStore.isAdmin || userStore.isPowerUser || 
        (userStore.isUser && row.user_id === userStore.currentUserId)
    }
    
    // 获取数据
    const fetchData = async () => {
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          pageSize: pageSize.value,
          ...searchForm
        }
        
        // 添加排序参数
        if (sortProp.value) {
          params.sort = sortProp.value
          params.order = sortOrder.value === 'ascending' ? 'asc' : 'desc'
        }
        
        // 清理空字符串参数
        Object.keys(params).forEach(key => {
          if (params[key] === '') delete params[key]
        })
        
        const res = await getLedgerList(params)
        if (res.data.code === 0) {
          tableData.value = res.data.data.items
          total.value = res.data.data.total
          
          // 提取录入人员列表（去重）
          const recorders = new Set()
          res.data.data.items.forEach(item => {
            if (item.recorder) {
              recorders.add(item.recorder)
            }
          })
          recorderList.value = Array.from(recorders).sort()
        } else {
          ElMessage.error(res.data.message || '获取数据失败')
        }
      } catch (error) {
        console.error('获取数据失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    // 获取省份列表
    const fetchProvinces = async () => {
      try {
        const res = await getProvinces()
        if (res.data.code === 0) {
          provinceList.value = res.data.data
        } else {
          ElMessage.error(res.data.message || '获取省份列表失败')
        }
      } catch (error) {
        console.error('获取省份列表失败:', error)
      }
    }
    
    // 省份变化时的处理
    const handleProvinceChange = (value) => {
      // 当选择省份后，保存当前省份的数据用于后续搜索建议
      if (value) {
        currentProvinceData.value = tableData.value.filter(item => item.province === value)
      } else {
        currentProvinceData.value = tableData.value
      }
    }
    
    // 项目名称搜索建议（防抖）
    const fetchProjectSuggestions = async (query) => {
      if (!query) return []
      try {
        const params = { query }
        if (searchForm.province) params.province = searchForm.province
        const res = await getProjectSuggestions(params)
        // 按 value 出现频率排序（如果后端返回有 count 字段可用，否则前端统计）
        let suggestions = res.data.data || []
        if (suggestions.length > 0 && suggestions[0].count !== undefined) {
          suggestions = suggestions.sort((a, b) => b.count - a.count)
        }
        return suggestions
      } catch (error) {
        console.error('获取项目建议失败:', error)
        return []
      }
    }
    const debouncedFetchProjectSuggestions = debounce(fetchProjectSuggestions, 300)
    const projectSuggestionsLoading = ref(false)
    const projectSuggestions = ref([])
    const handleProjectInput = async (value) => {
      projectSuggestionsLoading.value = true
      projectSuggestions.value = await debouncedFetchProjectSuggestions(value)
      projectSuggestionsLoading.value = false
    }
    
    // 地点搜索建议（防抖）
    const fetchLocationSuggestions = async (query) => {
      if (!query) return []
      try {
        const params = { query }
        if (searchForm.province) params.province = searchForm.province
        if (searchForm.project_name) params.project_name = searchForm.project_name
        const res = await axios.get('/meta/suggestions/locations', { params })
        let suggestions = res.data.data || []
        // 分组：常用（高频）、历史（本地）、全部
        const history = (JSON.parse(localStorage.getItem('location_history') || '[]') || [])
          .filter(h => h.includes(query))
          .map(h => ({ value: h, group: '历史' }))
        const common = suggestions.slice(0, 5).map(s => ({ ...s, group: '常用' }))
        const all = suggestions.slice(5).map(s => ({ ...s, group: '全部' }))
        return [...history, ...common, ...all]
      } catch (error) {
        console.error('获取地点建议失败:', error)
        return []
      }
    }
    const debouncedFetchLocationSuggestions = debounce(fetchLocationSuggestions, 300)
    const locationSuggestionsLoading = ref(false)
    const locationSuggestions = ref([])
    const handleLocationInput = async (value) => {
      locationSuggestionsLoading.value = true
      locationSuggestions.value = await debouncedFetchLocationSuggestions(value)
      locationSuggestionsLoading.value = false
    }
    
    // 搜索
    const handleSearch = () => {
      currentPage.value = 1
      fetchData()
    }
    
    // 重置
    const handleReset = () => {
      searchForm.project_name = ''
      searchForm.location = ''
      searchForm.province = ''
      searchForm.recorder = ''
      searchForm.start_date = ''
      searchForm.end_date = ''
      dateRange.value = null
      currentPage.value = 1
      fetchData()
    }
    
    // 日期范围变化
    const handleDateChange = (value) => {
      if (value) {
        searchForm.start_date = value[0]
        searchForm.end_date = value[1]
      } else {
        searchForm.start_date = ''
        searchForm.end_date = ''
      }
    }
    
    // 排序变化
    const handleSortChange = ({ prop, order }) => {
      sortProp.value = prop
      sortOrder.value = order
      fetchData()
    }
    
    // 分页变化
    const handleSizeChange = () => {
      currentPage.value = 1
      fetchData()
    }
    
    const handleCurrentChange = () => {
      fetchData()
    }
    
    // 新增
    const handleAdd = () => {
      router.push('/ledger/new')
    }
    
    // 编辑
    const handleEdit = (row) => {
      router.push(`/ledger/edit/${row.id}`)
    }
    
    // 查看
    const handleView = (row) => {
      router.push(`/ledger/edit/${row.id}?view=true`)
    }
    
    // 删除
    const handleDelete = async (row) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除"${row.project_name}"吗？`,
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        const res = await deleteLedgerEntry(row.id)
        if (res.data.success) {
          ElMessage.success('删除成功')
          fetchData()
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除失败:', error)
        }
      }
    }
    
    // 导出
    const exportLoading = ref(false)
    
    const handleExportFormat = async (format) => {
      exportLoading.value = true
      try {
        const params = {
          ...searchForm,
          start_date: dateRange.value?.[0],
          end_date: dateRange.value?.[1],
          format
        }
        const res = await exportLedger(params)
        let fileName = 'ledger_export'
        let mimeType = ''
        if (format === 'csv') {
          fileName += '.csv'
          mimeType = 'text/csv'
        } else if (format === 'excel') {
          fileName += '.xlsx'
          mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        } else if (format === 'word') {
          fileName += '.docx'
          mimeType = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        const blob = new Blob([res.data], { type: mimeType })
        const link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob)
        link.download = fileName
        link.click()
        window.URL.revokeObjectURL(link.href)
        ElMessage.success('导出成功')
      } catch (e) {
        ElMessage.error('导出失败')
      } finally {
        exportLoading.value = false
      }
    }
    
    // 下拉菜单命令
    const handleCommand = (command) => {
      switch (command) {
        case 'profile':
          ElMessage.info('个人信息功能开发中')
          break
        case 'password':
          showPasswordDialog()
          break
        case 'user-management':
          router.push('/admin/users')
          break
        case 'admin-logs':
          router.push('/admin/logs')
          break
        case 'logout':
          handleLogout()
          break
      }
    }
    
    // 退出登录
    const handleLogout = async () => {
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        userStore.logout()
        router.push('/login')
        ElMessage.success('已退出登录')
      } catch (error) {
        // 用户取消
      }
    }
    
    // 修改密码
    const passwordDialogVisible = ref(false)
    const passwordFormRef = ref(null)
    const passwordForm = reactive({
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
    
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== passwordForm.newPassword) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    
    const passwordRules = {
      oldPassword: [
        { required: true, message: '请输入原密码', trigger: 'blur' }
      ],
      newPassword: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请再次输入新密码', trigger: 'blur' },
        { validator: validateConfirmPassword, trigger: 'blur' }
      ]
    }
    
    const passwordLoading = ref(false)
    
    const showPasswordDialog = () => {
      passwordForm.oldPassword = ''
      passwordForm.newPassword = ''
      passwordForm.confirmPassword = ''
      passwordDialogVisible.value = true
    }
    
    const handleChangePassword = async () => {
      const valid = await passwordFormRef.value.validate().catch(() => false)
      if (!valid) return
      
      passwordLoading.value = true
      try {
        const res = await changePassword({
          old_password: passwordForm.oldPassword,
          new_password: passwordForm.newPassword
        })
        
        if (res.data.code === 0) {
          ElMessage.success('密码修改成功，请重新登录')
          passwordDialogVisible.value = false
          
          // 清除登录状态，跳转到登录页
          setTimeout(() => {
            userStore.logout()
            router.push('/login')
          }, 1000)
        } else {
          ElMessage.error(res.data.message || '密码修改失败')
        }
      } catch (error) {
        console.error('修改密码失败:', error)
      } finally {
        passwordLoading.value = false
      }
    }
    
    // 在 script setup 里添加 formatDateOnly 方法
    const formatDateOnly = (dateString) => {
      if (!dateString) return ''
      const d = new Date(dateString)
      if (isNaN(d)) return dateString
      return d.toISOString().slice(0, 10)
    }
    
    // 高亮建议项关键字
    const highlightKeyword = (text, keyword) => {
      if (!keyword) return text
      // 转义正则特殊字符
      const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
      return text.replace(new RegExp(escaped, 'gi'), match => `<span style="color:#3A7AFE;font-weight:bold">${match}</span>`)
    }
    
    const handleLocationSelect = (val) => {
      let history = JSON.parse(localStorage.getItem('location_history') || '[]')
      if (!history.includes(val)) {
        history.unshift(val)
        if (history.length > 10) history = history.slice(0, 10)
        localStorage.setItem('location_history', JSON.stringify(history))
      }
    }
    
    // 初始化
    onMounted(() => {
      if (!userStore.isAuthenticated) {
        router.replace({ path: '/login' })
      }
      fetchProvinces()
      fetchData()
    })
    
    return {
      userStore,
      searchForm,
      dateRange,
      provinceList,
      recorderList,
      tableData,
      loading,
      currentPage,
      pageSize,
      total,
      getIndex,
      canEdit,
      canDelete,
      fetchData,
      handleSearch,
      handleReset,
      handleDateChange,
      handleProvinceChange,
      handleSortChange,
      handleSizeChange,
      handleCurrentChange,
      handleAdd,
      handleEdit,
      handleView,
      handleDelete,
      handleExportFormat,
      handleCommand,
      passwordDialogVisible,
      passwordFormRef,
      passwordForm,
      passwordRules,
      passwordLoading,
      handleChangePassword,
      exportLoading,
      formatDateOnly,
      projectSuggestionsLoading,
      projectSuggestions,
      handleProjectInput,
      locationSuggestionsLoading,
      locationSuggestions,
      handleLocationInput,
      highlightKeyword,
      handleLocationSelect,
      ArrowDown
    }
  }
})
</script>

<style scoped>
:root {
  --primary-color: #3A7AFE;
  --secondary-bg: #F5F7FA;
  --card-bg: #FFFFFF;
  --border-radius: 10px;
  --shadow: 0 4px 24px 0 rgba(58,122,254,0.08);
  --table-header-bg: #F0F2F5;
  --table-header-color: #222;
  --text-color: #222;
  --muted-color: #888;
}

.page-container {
  min-height: 100vh;
  background: var(--secondary-bg);
  padding: 0;
}

.page-header {
  background: var(--card-bg);
  padding: 24px 32px 12px 32px;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
  box-shadow: var(--shadow);
}

.header-left h2 {
  margin: 0 0 8px 0;
  font-size: 26px;
  color: var(--primary-color);
  font-weight: 700;
  letter-spacing: 1px;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: var(--text-color);
  font-size: 16px;
  padding: 6px 16px;
  border-radius: var(--border-radius);
  transition: background 0.2s, color 0.2s;
}
.user-info:hover {
  background: var(--primary-color);
  color: #fff;
}

.search-bar {
  background: var(--card-bg);
  padding: 24px 32px 12px 32px;
  margin: 24px 24px 0 24px;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 16px;
  border-left: 4px solid #3A7AFE;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: 16px 24px;
  margin-bottom: 0;
  flex: 1;
}

.action-buttons {
  display: flex;
  gap: 14px;
  align-items: center;
}

.el-button {
  border-radius: var(--border-radius);
  font-weight: 500;
  transition: background 0.2s, color 0.2s, box-shadow 0.2s;
}
.el-button--primary {
  background: linear-gradient(90deg, #3A7AFE 0%, #005bea 100%);
  border-color: #3A7AFE;
  color: #fff;
  box-shadow: 0 2px 8px 0 rgba(58,122,254,0.10);
}
.el-button--primary:hover, .el-button--primary:focus {
  background: linear-gradient(90deg, #2556c7 0%, #005bea 100%);
  border-color: #2556c7;
}
.el-button--success {
  background: linear-gradient(90deg, #34d399 0%, #059669 100%);
  border-color: #34d399;
  color: #fff;
}
.el-button--success:hover, .el-button--success:focus {
  background: linear-gradient(90deg, #059669 0%, #34d399 100%);
  border-color: #059669;
}
.el-button--info {
  background: #f0f2f5;
  color: var(--primary-color);
  border: none;
}
.el-button--info:hover {
  background: #e6f0ff;
  color: #2556c7;
}
.el-button--default {
  background: #fff;
  color: var(--primary-color);
  border: 1px solid #dbeafe;
}
.el-button--default:hover {
  background: #f0f6ff;
  color: #2556c7;
}

.el-select, .el-autocomplete, .el-date-picker, .el-input {
  border-radius: var(--border-radius) !important;
}

.el-table {
  margin: 24px;
  background: var(--card-bg);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  overflow: hidden;
}

:deep(.el-table__header th) {
  background: var(--table-header-bg) !important;
  color: var(--table-header-color) !important;
  font-weight: 600;
  font-size: 15px;
}
:deep(.el-table__body td) {
  color: var(--text-color);
  font-size: 14px;
}
:deep(.el-table__row:hover) {
  background: #f4f8ff !important;
}

.text-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pagination {
  margin: 32px 24px 24px 24px;
  text-align: right;
}

:deep(.el-pagination__total),
:deep(.el-pagination__sizes),
:deep(.el-pagination__jump) {
  color: var(--muted-color);
}

:deep(.el-breadcrumb) {
  font-size: 15px;
  color: var(--muted-color);
}

:deep(.el-dropdown-menu__item--divided) {
  border-top: 1px solid #e6e6e6;
}

@media (max-width: 900px) {
  .page-header, .search-bar {
    padding: 16px 8px 8px 8px;
  }
  .el-table, .pagination {
    margin: 8px;
  }
}

@media (max-width: 600px) {
  .search-bar, .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  .action-buttons {
    justify-content: flex-end;
  }
}

/* 搜索栏按钮样式优化 */
.el-button--primary {
  background: linear-gradient(90deg, #3A7AFE 0%, #005bea 100%);
  border-color: #3A7AFE;
  color: #fff;
  box-shadow: 0 2px 8px 0 rgba(58,122,254,0.10);
}
.el-button--primary:hover, .el-button--primary:focus {
  background: linear-gradient(90deg, #2556c7 0%, #005bea 100%);
  border-color: #2556c7;
}
.el-button--success {
  background: linear-gradient(90deg, #34d399 0%, #059669 100%);
  border-color: #34d399;
  color: #fff;
}
.el-button--success:hover, .el-button--success:focus {
  background: linear-gradient(90deg, #059669 0%, #34d399 100%);
  border-color: #059669;
}
.el-button--info {
  background: #f0f2f5;
  color: var(--primary-color);
  border: none;
}
.el-button--info:hover {
  background: #e6f0ff;
  color: #2556c7;
}
.el-button--default {
  background: #fff;
  color: var(--primary-color);
  border: 1px solid #dbeafe;
}
.el-button--default:hover {
  background: #f0f6ff;
  color: #2556c7;
}

/* 搜索栏背景和分隔 */
.search-bar {
  background: var(--card-bg);
  padding: 24px 32px 12px 32px;
  margin: 24px 24px 0 24px;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 16px;
  border-left: 4px solid #3A7AFE;
}

/* 搜索输入高亮 */
.el-form-item .el-input__wrapper {
  box-shadow: 0 2px 8px 0 rgba(58,122,254,0.06);
  border-radius: 6px;
}

/* 新增台账按钮更突出 */
.action-buttons .el-button--primary {
  font-weight: 600;
  letter-spacing: 1px;
  font-size: 16px;
  padding: 0 24px;
  background: linear-gradient(90deg, #3A7AFE 0%, #005bea 100%);
  border: none;
  box-shadow: 0 4px 16px 0 rgba(58,122,254,0.12);
}

/* 搜索/重置按钮主次分明 */
.search-form .el-button--primary {
  background: linear-gradient(90deg, #3A7AFE 0%, #005bea 100%);
  border: none;
  color: #fff;
}
.search-form .el-button {
  font-size: 15px;
  min-width: 80px;
}
.search-form .el-button.icon-Refresh {
  color: #3A7AFE;
  background: #f0f6ff;
  border: 1px solid #dbeafe;
}
</style>