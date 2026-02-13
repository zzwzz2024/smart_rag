import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../views/Layout.vue'
import Login from '../views/Login.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/chat'
    },
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/',
      component: Layout,
      children: [
        {
          path: 'chat',
          name: 'Chat',
          component: () => import('../views/Chat.vue')
        },
        {
          path: 'knowledge-base',
          name: 'KnowledgeBase',
          component: () => import('../views/KnowledgeBase.vue')
        },
        {
          path: 'documents',
          name: 'Documents',
          component: () => import('../views/Documents.vue')
        },
        {
          path: 'evaluation',
          name: 'Evaluation',
          component: () => import('../views/Evaluation.vue')
        },
        {
          path: 'settings',
          name: 'Settings',
          component: () => import('../views/Settings.vue')
        }
      ]
    }
  ]
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router