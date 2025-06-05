<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>{{ pageTitle }}</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/ledger/list' }">台账列表</el-breadcrumb-item>
          <el-breadcrumb-item>{{ pageTitle }}</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
    </div>
    
    <!-- 表单内容 -->
    <div class="form-container">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        :disabled="isView"
        label-width="120px"
        class="ledger-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="录入人员">
              <el-input v-model="userStore.currentUsername" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="录入时间" v-if="isEdit || isView">
              <el-input :value="formatDate(formData.created_at)" disabled />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="省份" prop="province">
              <el-select
                v-model="formData.province"
                placeholder="请选择或输入省份"
                filterable
                allow-create
                default-first-option
                style="width: 100%"
              >
                <el-option
                  v-for="item in provinceList"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="项目名称" prop="project_name">
              <el-autocomplete
                v-model="formData.project_name"
                :fetch-suggestions="queryProjectSuggestions"
                placeholder="请输入项目名称"
                :trigger-on-focus="false"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="日期" prop="date">
              <el-date-picker
                v-model="formData.date"
                type="date"
                placeholder="请选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="地点" prop="location">
              <el-input
                v-model="formData.location"
                placeholder="请输入地点"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="涉及人员" prop="personnel">
              <el-input
                v-model="formData.personnel"
                placeholder="请输入涉及人员，多人用逗号分隔"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性质" prop="nature">
              <el-select
                v-model="formData.nature"
                placeholder="请选择性质"
                style="width: 100%"
              >
                <el-option
                  v-for="item in natureOptions"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="具体事项记录" prop="specific_matters">
          <el-input
            v-model="formData.specific_matters"
            type="textarea"
            :rows="6"
            placeholder="请输入具体事项记录"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="后续落实要点" prop="follow_up_points">
          <el-input
            v-model="formData.follow_up_points"
            type="textarea"
            :rows="4"
            placeholder="请输入后续需要落实的要点（选填）"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item v-if="!isView">
          <el-button type="primary" :loading="loading" @click="handleSubmit">
            {{ isEdit ? '保存修改' : '提交' }}
          </el-button>
          <el-button @click="handleCancel">取消</el-button>
          <el-button v-if="isEdit" type="warning" @click="handleReset">重置</el-button>
        </el-form-item>
        
        <el-form-item v-else>
          <el-button type="primary" @click="handleEdit">编辑</el-button>
          <el-button @click="handleBack">返回</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import { 
  getLedgerEntry, 
  createLedgerEntry, 
  updateLedgerEntry,
  getProvinces,
  getProjectSuggestions,
  getNatureOptions
} from '@/api/ledger'
import debounce from 'lodash/debounce'

export default defineComponent({
  name: 'LedgerForm',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const userStore = useUserStore()
    
    // 页面模式
    const entryId = computed(() => route.params.id)
    const isEdit = computed(() => !!entryId.value && !route.query.view)
    const isView = computed(() => !!route.query.view)
    const pageTitle = computed(() => {
      if (isView.value) return '查看台账'
      return isEdit.value ? '编辑台账' : '新增台账'
    })
    
    // 表单数据
    const formRef = ref(null)
    const formData = reactive({
      province: '',
      project_name: '',
      date: '',
      location: '',
      personnel: '',
      nature: '',
      specific_matters: '',
      follow_up_points: '',
      created_at: ''
    })
    
    // 原始数据备份（用于重置）
    const originalData = ref({})
    
    // 表单验证规则
    const formRules = {
      province: [
        { required: true, message: '请选择省份', trigger: 'change' }
      ],
      project_name: [
        { required: true, message: '请输入项目名称', trigger: 'blur' },
        { max: 200, message: '项目名称不能超过200个字符', trigger: 'blur' }
      ],
      date: [
        { required: true, message: '请选择日期', trigger: 'change' }
      ],
      location: [
        { required: true, message: '请输入地点', trigger: 'blur' },
        { max: 200, message: '地点不能超过200个字符', trigger: 'blur' }
      ],
      personnel: [
        { required: true, message: '请输入涉及人员', trigger: 'blur' },
        { max: 500, message: '涉及人员不能超过500个字符', trigger: 'blur' }
      ],
      nature: [
        { required: true, message: '请选择性质', trigger: 'change' }
      ],
      specific_matters: [
        { required: true, message: '请输入具体事项记录', trigger: 'blur' }
      ]
    }
    
    // 选项数据
    const provinceList = ref([])
    const natureOptions = ref([])
    const loading = ref(false)
    
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
    
    // 获取性质选项
    const fetchNatureOptions = async () => {
      try {
        const res = await getNatureOptions()
        if (res.data.code === 0) {
          natureOptions.value = res.data.data
        } else {
          ElMessage.error(res.data.message || '获取性质选项失败')
        }
      } catch (error) {
        console.error('获取性质选项失败:', error)
        // 使用默认选项
        natureOptions.value = [
          '会议纪要',
          '工作安排',
          '问题反馈',
          '临时任务',
          '研讨交流',
          '资料交接',
          '人员对接',
          '常规项目工作',
          '其他'
        ]
      }
    }
    
    // 获取台账详情
    const fetchLedgerEntry = async () => {
      if (!entryId.value) return
      
      loading.value = true
      try {
        const res = await getLedgerEntry(entryId.value)
        if (res.data.code === 0) {
          const data = res.data.data
          Object.keys(formData).forEach(key => {
            if (Object.prototype.hasOwnProperty.call(data, key)) {
              formData[key] = data[key]
            }
          })
          // 保存原始数据
          originalData.value = { ...formData }
        } else {
          ElMessage.error(res.data.message || '获取台账详情失败')
          router.push('/ledger/list')
        }
      } catch (error) {
        console.error('获取台账详情失败:', error)
        ElMessage.error('获取台账详情失败')
        router.push('/ledger/list')
      } finally {
        loading.value = false
      }
    }
    
    // 项目名称搜索建议
    const queryProjectSuggestions = debounce(async (queryString, cb) => {
      if (!queryString) {
        cb([])
        return
      }
      
      try {
        const res = await getProjectSuggestions(queryString)
        if (res.data.code === 0) {
          cb(res.data.data)
        } else {
          cb([])
        }
      } catch (error) {
        console.error('获取搜索建议失败:', error)
        cb([])
      }
    }, 300)
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }
    
    // 提交表单
    const handleSubmit = async () => {
      const valid = await formRef.value.validate().catch(() => false)
      if (!valid) return
      
      loading.value = true
      try {
        let res
        if (isEdit.value) {
          res = await updateLedgerEntry(entryId.value, formData)
        } else {
          res = await createLedgerEntry(formData)
        }
        
        if (res.data.code === 0) {
          ElMessage.success(isEdit.value ? '修改成功' : '创建成功')
          router.push('/ledger/list')
        } else {
          ElMessage.error(res.data.message || '提交失败')
        }
      } catch (error) {
        console.error('提交失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    // 取消
    const handleCancel = () => {
      router.push('/ledger/list')
    }
    
    // 重置表单
    const handleReset = () => {
      if (isEdit.value && originalData.value) {
        Object.keys(originalData.value).forEach(key => {
          formData[key] = originalData.value[key]
        })
        ElMessage.success('已重置为原始数据')
      }
    }
    
    // 返回列表
    const handleBack = () => {
      router.push('/ledger/list')
    }
    
    // 编辑按钮（查看模式下）
    const handleEdit = () => {
      router.push(`/ledger/edit/${entryId.value}`)
    }
    
    // 初始化
    onMounted(() => {
      fetchProvinces()
      fetchNatureOptions()
      if (entryId.value) {
        fetchLedgerEntry()
      }
    })
    
    return {
      userStore,
      pageTitle,
      isEdit,
      isView,
      formRef,
      formData,
      formRules,
      provinceList,
      natureOptions,
      loading,
      queryProjectSuggestions,
      formatDate,
      handleSubmit,
      handleCancel,
      handleReset,
      handleBack,
      handleEdit
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
}

.header-left h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #303133;
}

.form-container {
  max-width: 1000px;
  margin: 20px auto;
  padding: 30px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.ledger-form {
  margin-top: 20px;
}

:deep(.el-breadcrumb) {
  font-size: 14px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-textarea__inner) {
  font-family: inherit;
  line-height: 1.5;
}
</style>