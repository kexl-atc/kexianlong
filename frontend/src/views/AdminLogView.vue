<template>
    <div class="page-container">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-left">
          <h2>系统日志</h2>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>系统管理</el-breadcrumb-item>
            <el-breadcrumb-item>系统日志</el-breadcrumb-item>
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
      
      <!-- 日志内容 -->
      <div v-else class="content-container">
        <!-- 搜索栏 -->
        <div class="search-bar">
          <el-form :inline="true" :model="searchForm" class="search-form">
            <el-form-item label="日志级别">
              <el-select
                v-model="searchForm.level"
                placeholder="全部级别"
                clearable
                style="width: 120px"
              >
                <el-option label="INFO" value="INFO" />
                <el-option label="WARNING" value="WARNING" />
                <el-option label="ERROR" value="ERROR" />
              </el-select>
            </el-form-item>
            <el-form-item label="操作用户">
              <el-select
                v-model="searchForm.user_id"
                placeholder="全部用户"
                clearable
                filterable
                style="width: 150px"
              >
                <el-option
                  v-for="user in userList"
                  :key="user.id"
                  :label="user.username"
                  :value="user.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="时间范围">
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
            <el-button icon="DataAnalysis" @click="showStatistics">系统统计</el-button>
            <el-dropdown @command="handleExportFormat" :disabled="exportLoading">
              <el-button icon="Download" :loading="exportLoading">
                导出日志 <el-icon><ArrowDown /></el-icon>
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
        
        <!-- 日志表格 -->
        <el-table
          v-loading="loading"
          :data="tableData"
          border
          stripe
          style="width: 100%"
        >
          <el-table-column type="index" label="序号" width="60" :index="getIndex" />
          <el-table-column prop="timestamp" label="时间" width="180">
            <template #default="{ row }">
              {{ formatTimestamp(row.timestamp) }}
            </template>
          </el-table-column>
          <el-table-column prop="level" label="级别" width="100">
            <template #default="{ row }">
              <el-tag
                :type="getLevelType(row.level)"
                size="small"
              >
                {{ row.level }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="username" label="操作用户" width="120" />
          <el-table-column prop="message" label="日志消息" min-width="300" show-overflow-tooltip />
          <el-table-column prop="ip_address" label="IP地址" width="140" />
          <el-table-column prop="details" label="详情" width="100">
            <template #default="{ row }">
              <el-button
                v-if="row.details"
                type="primary"
                size="small"
                link
                @click="showDetails(row)"
              >
                查看
              </el-button>
              <span v-else>-</span>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页 -->
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          class="pagination"
        />
      </div>
      
      <!-- 详情对话框 -->
      <el-dialog
        v-model="detailsDialogVisible"
        title="日志详情"
        width="600px"
      >
        <el-descriptions :column="1" border>
          <el-descriptions-item label="时间">
            {{ formatTimestamp(currentLog.timestamp) }}
          </el-descriptions-item>
          <el-descriptions-item label="级别">
            <el-tag :type="getLevelType(currentLog.level)" size="small">
              {{ currentLog.level }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="用户">
            {{ currentLog.username || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="IP地址">
            {{ currentLog.ip_address || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="消息">
            {{ currentLog.message }}
          </el-descriptions-item>
          <el-descriptions-item label="详细信息" v-if="currentLog.details">
            <pre style="margin: 0; white-space: pre-wrap;">{{ currentLog.details }}</pre>
          </el-descriptions-item>
        </el-descriptions>
      </el-dialog>
      
      <!-- 系统统计对话框 -->
      <el-dialog
        v-model="statisticsDialogVisible"
        title="系统统计"
        width="800px"
      >
        <div v-loading="statisticsLoading" class="statistics-container">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card>
                <template #header>
                  <span>用户统计</span>
                </template>
                <el-descriptions :column="1">
                  <el-descriptions-item label="总用户数">
                    {{ statistics.users?.total || 0 }}
                  </el-descriptions-item>
                  <el-descriptions-item label="管理员">
                    {{ statistics.users?.by_role?.admin || 0 }}
                  </el-descriptions-item>
                  <el-descriptions-item label="高级用户">
                    {{ statistics.users?.by_role?.power_user || 0 }}
                  </el-descriptions-item>
                  <el-descriptions-item label="普通用户">
                    {{ statistics.users?.by_role?.user || 0 }}
                  </el-descriptions-item>
                </el-descriptions>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <template #header>
                  <span>台账统计</span>
                </template>
                <el-descriptions :column="1">
                  <el-descriptions-item label="总台账数">
                    {{ statistics.entries?.total || 0 }}
                  </el-descriptions-item>
                  <el-descriptions-item label="最近7天新增">
                    {{ statistics.entries?.recent_7_days || 0 }}
                  </el-descriptions-item>
                </el-descriptions>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-dialog>
    </div>
  </template>
  
  <script>
  import { defineComponent, ref, reactive, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import { useUserStore } from '@/store/user'
  import { getActivityLogs, getUserList, getStatistics } from '@/api/admin'
  import axios from 'axios'
  import { ArrowDown } from '@element-plus/icons-vue'
  
  export default defineComponent({
    name: 'AdminLogView',
    setup() {
      const router = useRouter()
      const userStore = useUserStore()
      
      // 搜索表单
      const searchForm = reactive({
        level: '',
        user_id: '',
        start_date: '',
        end_date: ''
      })
      
      const dateRange = ref(null)
      const userList = ref([])
      
      // 表格数据
      const tableData = ref([])
      const loading = ref(false)
      const currentPage = ref(1)
      const pageSize = ref(20)
      const total = ref(0)
      
      // 当前查看的日志
      const currentLog = ref({})
      const detailsDialogVisible = ref(false)
      
      // 统计信息
      const statistics = ref({})
      const statisticsDialogVisible = ref(false)
      const statisticsLoading = ref(false)
      
      // 导出相关
      const exportLoading = ref(false)
      
      // 获取表格序号
      const getIndex = (index) => {
        return (currentPage.value - 1) * pageSize.value + index + 1
      }
      
      // 获取级别标签类型
      const getLevelType = (level) => {
        const typeMap = {
          'INFO': 'success',
          'WARNING': 'warning',
          'ERROR': 'danger'
        }
        return typeMap[level] || 'info'
      }
      
      // 格式化时间戳
      const formatTimestamp = (timestamp) => {
        if (!timestamp) return '-'
        return new Date(timestamp).toLocaleString('zh-CN')
      }
      
      // 获取日志数据
      const fetchLogs = async () => {
        loading.value = true
        try {
          const params = {
            page: currentPage.value,
            limit: pageSize.value,
            ...searchForm
          }
          
          const res = await getActivityLogs(params)
          if (res.data.code === 0) {
            const data = res.data.data
            tableData.value = data.logs
            total.value = data.total_logs
          } else {
            ElMessage.error(res.data.message || '获取日志失败')
          }
        } catch (error) {
          console.error('获取日志失败:', error)
        } finally {
          loading.value = false
        }
      }
      
      // 获取用户列表
      const fetchUserList = async () => {
        try {
          const res = await getUserList({ pageSize: 100 })
          if (res.data.code === 0) {
            userList.value = res.data.data.users
          } else {
            ElMessage.error(res.data.message || '获取用户列表失败')
          }
        } catch (error) {
          console.error('获取用户列表失败:', error)
        }
      }
      
      // 搜索
      const handleSearch = () => {
        currentPage.value = 1
        fetchLogs()
      }
      
      // 重置
      const handleReset = () => {
        searchForm.level = ''
        searchForm.user_id = ''
        searchForm.start_date = ''
        searchForm.end_date = ''
        dateRange.value = null
        currentPage.value = 1
        fetchLogs()
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
      
      // 分页变化
      const handleSizeChange = () => {
        currentPage.value = 1
        fetchLogs()
      }
      
      const handleCurrentChange = () => {
        fetchLogs()
      }
      
      // 查看详情
      const showDetails = (row) => {
        currentLog.value = row
        detailsDialogVisible.value = true
      }
      
      // 返回
      const goBack = () => {
        router.push('/ledger/list')
      }
      
      // 显示统计信息
      const showStatistics = async () => {
        statisticsDialogVisible.value = true
        statisticsLoading.value = true
        try {
          const res = await getStatistics()
          if (res.data.code === 0) {
            statistics.value = res.data.data
          } else {
            ElMessage.error(res.data.message || '获取统计信息失败')
          }
        } catch (error) {
          console.error('获取统计信息失败:', error)
        } finally {
          statisticsLoading.value = false
        }
      }
      
      // 导出日志
      const handleExportFormat = async (format) => {
        exportLoading.value = true
        try {
          const params = {
            ...searchForm,
            start_date: dateRange.value?.[0],
            end_date: dateRange.value?.[1],
            format
          }
          const res = await axios.get('/admin/export/logs', {
            params,
            responseType: format === 'csv' ? 'blob' : 'arraybuffer'
          })
          let fileName = 'logs_export'
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
      
      // 初始化
      onMounted(() => {
        if (!userStore.isAuthenticated || !userStore.isAdmin) {
          router.replace({ path: '/not-permission' })
        } else {
          fetchUserList()
          fetchLogs()
        }
      })
      
      return {
        userStore,
        searchForm,
        dateRange,
        userList,
        tableData,
        loading,
        currentPage,
        pageSize,
        total,
        currentLog,
        detailsDialogVisible,
        statistics,
        statisticsDialogVisible,
        statisticsLoading,
        exportLoading,
        getIndex,
        getLevelType,
        formatTimestamp,
        handleSearch,
        handleReset,
        handleDateChange,
        handleSizeChange,
        handleCurrentChange,
        showDetails,
        goBack,
        showStatistics,
        handleExportFormat,
        ArrowDown
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
  
  .statistics-container {
    min-height: 300px;
  }
  
  :deep(.el-breadcrumb) {
    font-size: 14px;
  }
  
  :deep(.el-card) {
    margin-bottom: 20px;
  }
  </style>