<template>
  <div class="layout-container">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ 'collapsed': appStore.sidebarCollapsed }">
      <div class="sidebar-header">
        <h1 class="logo">ZZWZZ RAG</h1>
        <button class="toggle-btn" @click="appStore.toggleSidebar">
          {{ appStore.sidebarCollapsed ? '展开' : '收起' }}
        </button>
      </div>
      <nav class="sidebar-nav">
        <ul>
          <li>
            <router-link to="/chat" @click="appStore.setCurrentView('chat')">
              <i class="icon">💬</i>
              <span>聊天</span>
            </router-link>
          </li>
          <li>
            <router-link to="/knowledge-base" @click="appStore.setCurrentView('knowledge-base')">
              <i class="icon">📚</i>
              <span>知识库</span>
            </router-link>
          </li>
          <li>
            <router-link to="/documents" @click="appStore.setCurrentView('documents')">
              <i class="icon">📄</i>
              <span>文档</span>
            </router-link>
          </li>
          <li>
            <router-link to="/evaluation" @click="appStore.setCurrentView('evaluation')">
              <i class="icon">📊</i>
              <span>评估</span>
            </router-link>
          </li>
          <li>
            <router-link to="/settings" @click="appStore.setCurrentView('settings')">
              <i class="icon">⚙️</i>
              <span>设置</span>
            </router-link>
          </li>
          <li>
            <router-link to="/model-settings" @click="appStore.setCurrentView('model-settings')">
              <i class="icon">🤖</i>
              <span>模型设置</span>
            </router-link>
          </li>
          <li>
            <router-link to="/system/users" @click="appStore.setCurrentView('system')">
              <i class="icon">🛠️</i>
              <span>系统设置</span>
            </router-link>
          </li>
        </ul>
      </nav>
      <div class="sidebar-footer">
        <div class="user-info">
          <span class="username">{{ userStore.user?.username || '未登录' }}</span>
        </div>
        <button class="logout-btn" @click="handleLogout">
          <i class="icon">🚪</i>
          <span>退出登录</span>
        </button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <header class="main-header">
        <div class="header-left">
          <h2>{{ currentViewTitle }}</h2>
        </div>
        <div class="header-right">
          <button class="btn btn-secondary" @click="appStore.toggleDarkMode">
            {{ appStore.isDarkMode ? '切换到亮色模式' : '切换到暗色模式' }}
          </button>
        </div>
      </header>
      <div class="content-wrapper">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'
import { useUserStore } from '../stores/user'

const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

// 当前视图标题
const currentViewTitle = computed(() => {
  const viewMap: Record<string, string> = {
    'chat': '智能聊天',
    'knowledge-base': '知识库管理',
    'documents': '文档管理',
    'evaluation': '系统评估',
    'settings': '系统设置',
    'model-settings': '模型设置',
    'system': '系统管理'
  }
  return viewMap[appStore.currentView] || 'ZZWZZ RAG 系统'
})

// 处理退出登录
const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

// 加载用户信息和深色模式设置
onMounted(async () => {
  appStore.loadDarkMode()
  try {
    await userStore.getCurrentUser()
  } catch (error) {
    console.error('获取用户信息失败:', error)
    // 如果获取用户信息失败，跳转到登录页
    router.push('/login')
  }
})
</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* 侧边栏样式 */
.sidebar {
  width: 250px;
  background-color: #2c3e50;
  color: white;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
}

.sidebar.collapsed {
  width: 60px;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #34495e;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 18px;
  font-weight: bold;
  margin: 0;
}

.sidebar.collapsed .logo {
  display: none;
}

.toggle-btn {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.toggle-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.sidebar-nav {
  flex: 1;
  padding: 20px 0;
}

.sidebar-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-nav li {
  margin-bottom: 8px;
}

.sidebar-nav a {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: white;
  text-decoration: none;
  transition: background-color 0.2s ease;
  border-radius: 0 4px 4px 0;
}

.sidebar-nav a:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.sidebar-nav a.router-link-active {
  background-color: #4CAF50;
  color: white;
}

.sidebar-nav .icon {
  margin-right: 12px;
  font-size: 16px;
}

.sidebar.collapsed .sidebar-nav span {
  display: none;
}

.sidebar.collapsed .sidebar-nav .icon {
  margin-right: 0;
  text-align: center;
  width: 100%;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid #34495e;
}

.user-info {
  margin-bottom: 16px;
}

.username {
  font-size: 14px;
  font-weight: 500;
}

.sidebar.collapsed .username {
  display: none;
}

.logout-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.logout-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.logout-btn .icon {
  margin-right: 8px;
}

.sidebar.collapsed .logout-btn span {
  display: none;
}

.sidebar.collapsed .logout-btn .icon {
  margin-right: 0;
}

/* 主内容区样式 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #f5f5f5;
}

.main-header {
  padding: 0 30px;
  height: 60px;
  background-color: white;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.main-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: #333;
}

.header-right {
  display: flex;
  align-items: center;
}

.content-wrapper {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 1000;
  }

  .sidebar.collapsed {
    left: -250px;
    width: 250px;
  }

  .main-content {
    margin-left: 0;
  }

  .content-wrapper {
    padding: 20px;
  }
}
</style>