import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'

// 路由懒加载
const LoginPage = () => import('@/views/LoginPage.vue')
const LedgerList = () => import('@/views/LedgerList.vue')
const LedgerForm = () => import('@/views/LedgerForm.vue')
const AdminLogView = () => import('@/views/AdminLogView.vue')
const NotFound = () => import('@/views/NotFound.vue')
const UserManagement = () => import('@/views/UserManagement.vue')
const NotPermission = () => import('@/views/NotPermission.vue')
const MainLayout = () => import('@/layouts/MainLayout.vue')
const Statistics = () => import('@/views/Statistics.vue')

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { 
      title: '登录',
      requiresAuth: false 
    }
  },
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        redirect: to => {
          const userStore = useUserStore()
          return userStore.isAuthenticated ? '/ledger/list' : '/login'
        }
      },
      {
        path: 'ledger/list',
        name: 'LedgerList',
        component: LedgerList,
        meta: { 
          title: '台账列表',
          requiresAuth: true 
        }
      },
      {
        path: 'ledger/new',
        name: 'LedgerNew',
        component: LedgerForm,
        meta: { 
          title: '新增台账',
          requiresAuth: true 
        }
      },
      {
        path: 'ledger/edit/:id',
        name: 'LedgerEdit',
        component: LedgerForm,
        meta: { 
          title: '编辑台账',
          requiresAuth: true 
        }
      },
      {
        path: 'admin/users',
        name: 'UserManagement',
        component: UserManagement,
        meta: { 
          title: '用户管理',
          requiresAuth: true,
          requiresAdmin: true 
        }
      },
      {
        path: 'admin/logs',
        name: 'AdminLogs',
        component: AdminLogView,
        meta: { 
          title: '系统日志',
          requiresAuth: true,
          requiresAdmin: true 
        }
      },
      {
        path: 'statistics',
        name: 'Statistics',
        component: Statistics,
        meta: {
          requiresAuth: true,
          title: '系统统计'
        }
      }
    ]
  },
  {
    path: '/not-permission',
    name: 'NotPermission',
    component: NotPermission,
    meta: {
      title: '无权限访问'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: { 
      title: '页面不存在'
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  const title = to.meta.title ? `${to.meta.title} - 台账管理系统` : '台账管理系统'
  document.title = title
  
  const userStore = useUserStore()
  
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    if (!userStore.isAuthenticated) {
      ElMessage.warning('请先登录')
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }
    
    // 检查是否需要管理员权限
    if (to.meta.requiresAdmin && !userStore.isAdmin) {
      ElMessage.error('没有权限访问此页面')
      next(false)
      return
    }
  }
  
  // 已登录用户访问登录页，重定向到首页
  if (to.path === '/login' && userStore.isAuthenticated) {
    next('/ledger/list')
    return
  }
  
  next()
})

export default router