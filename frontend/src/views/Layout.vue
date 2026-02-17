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
            <router-link to="/chat" @click="handleMenuClick('/chat', 'chat', '聊天')">
              <i class="icon">💬</i>
              <span>聊天</span>
            </router-link>
          </li>
          <li class="has-submenu" :class="{ 'open': openSubmenu === 'knowledge' }">
            <div class="submenu-title" @click="toggleSubmenu('knowledge')">
              <i class="icon">📚</i>
              <span>知识库</span>
              <i class="submenu-arrow">{{ openSubmenu === 'knowledge' ? '▼' : '▶' }}</i>
            </div>
            <ul class="submenu">
              <li>
                <router-link to="/knowledge-base" @click="handleMenuClick('/knowledge-base', 'knowledge-base', '知识库管理')">
                  <i class="icon">📚</i>
                  <span>知识库管理</span>
                </router-link>
              </li>
              <li>
                <router-link to="/documents" @click="handleMenuClick('/documents', 'documents', '文档管理')">
                  <i class="icon">📄</i>
                  <span>文档管理</span>
                </router-link>
              </li>
              <li>
                <router-link to="/evaluation" @click="handleMenuClick('/evaluation', 'evaluation', '知识库评估')">
                  <i class="icon">📊</i>
                  <span>知识库评估</span>
                </router-link>
              </li>
            </ul>
          </li>
          <li>
            <router-link to="/model-settings" @click="handleMenuClick('/model-settings', 'model-settings', '模型设置')">
              <i class="icon">🤖</i>
              <span>模型管理</span>
            </router-link>
          </li>
          <li class="has-submenu" :class="{ 'open': openSubmenu === 'system' }">
            <div class="submenu-title" @click="toggleSubmenu('system')">
              <i class="icon">🛠️</i>
              <span>系统设置</span>
              <i class="submenu-arrow">{{ openSubmenu === 'system' ? '▼' : '▶' }}</i>
            </div>
            <ul class="submenu">
              <li>
                <router-link to="/system/users" @click="handleMenuClick('/system/users', 'system', '用户管理')">
                  <i class="icon">👤</i>
                  <span>用户管理</span>
                </router-link>
              </li>
              <li>
                <router-link to="/system/roles" @click="handleMenuClick('/system/roles', 'system', '角色管理')">
                  <i class="icon">🎭</i>
                  <span>角色管理</span>
                </router-link>
              </li>
              <li>
                <router-link to="/system/menus" @click="handleMenuClick('/system/menus', 'system', '菜单管理')">
                  <i class="icon">📋</i>
                  <span>菜单管理</span>
                </router-link>
              </li>
              <li>
                <router-link to="/system/permissions" @click="handleMenuClick('/system/permissions', 'system', '权限设置')">
                  <i class="icon">🔒</i>
                  <span>权限设置</span>
                </router-link>
              </li>
              <li>
                <router-link to="/system/dictionaries" @click="handleMenuClick('/system/dictionaries', 'system', '字典管理')">
                  <i class="icon">📖</i>
                  <span>字典管理</span>
                </router-link>
              </li>
            </ul>
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
<!--        <div class="header-right">
          <button class="btn btn-secondary" @click="toggleDarkMode">
            {{ appStore.isDarkMode ? '切换到亮色模式' : '切换到暗色模式' }}
          </button>
        </div>-->
      </header>
      
      <!-- 页签区域 -->
      <div class="tabs-container" v-if="tabsStore.tabsList.length > 0">
        <div class="tabs-wrapper">
          <div 
            v-for="(tab, index) in tabsStore.tabsList" 
            :key="tab.path"
            class="tab-item"
            :class="{ 'active': tabsStore.activeTab === tab.path }"
            @click="handleTabClick(tab.path)"
            @contextmenu.prevent="showContextMenu($event, tab, index)"
          >
            <span class="tab-title">{{ tab.title }}</span>
            <button 
              class="tab-close-btn"
              @click.stop="handleTabClose(tab.path)"
              title="关闭标签"
            >
              ×
            </button>
          </div>
        </div>
      </div>
      
      <!-- 右键菜单 -->
      <div 
        v-if="contextMenu.visible" 
        class="context-menu"
        :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
        @click.stop
      >
        <ul>
          <li @click="handleContextMenuAction('closeCurrent')">
            关闭当前标签
          </li>
          <li @click="handleContextMenuAction('closeOther')">
            关闭其他标签
          </li>
          <li @click="handleContextMenuAction('closeAll')">
            关闭全部标签
          </li>
          <li @click="handleContextMenuAction('closeLeft')">
            关闭左侧标签
          </li>
          <li @click="handleContextMenuAction('closeRight')">
            关闭右侧标签
          </li>
        </ul>
      </div>
      
      <div class="content-wrapper">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../stores/app'
import { useUserStore } from '../stores/user'
import { useTabsStore } from '../stores/tabs'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const userStore = useUserStore()
const tabsStore = useTabsStore()

// 右键菜单状态
const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
  currentTab: null as any,
  currentIndex: -1
})

// 侧边栏子菜单状态
const openSubmenu = ref<string | null>(null)

// 当前视图标题
const currentViewTitle = computed(() => {
  const viewMap: Record<string, string> = {
    'chat': '智能聊天',
    'knowledge-base': '知识库管理',
    'documents': '文档管理',
    'evaluation': '知识库评估',
    'settings': '系统管理',
    'model-settings': '模型管理',
    'system': '系统管理'
  }
  return viewMap[appStore.currentView] || 'ZZWZZ RAG 系统'
})

// 处理菜单点击
const handleMenuClick = (path: string, view: string, title: string) => {
  // 点击其他菜单时，收起相应的子菜单
  if (view !== 'system' && view !== 'knowledge-base' && view !== 'evaluation' && view !== 'documents') {
    openSubmenu.value = null
  }
  // 点击知识库相关菜单时，保持知识库子菜单打开
  if (view === 'knowledge-base' || view === 'evaluation' || view === 'documents') {
    openSubmenu.value = 'knowledge'
  }
  appStore.setCurrentView(view)
  tabsStore.addTab({
    path,
    name: view,
    title
  })
}

// 切换子菜单
const toggleSubmenu = (submenu: string) => {
  if (openSubmenu.value === submenu) {
    // 收起菜单
    openSubmenu.value = null
  } else {
    // 展开菜单
    openSubmenu.value = submenu
    // 系统设置菜单展开时，默认选中第一个子菜单（用户管理）
    if (submenu === 'system') {
      // 检查当前是否已经在系统设置页面
      if (!route.path.includes('/system/')) {
        router.push('/system/users')
        handleMenuClick('/system/users', 'system', '用户管理')
      }
    }
  }
}

// 处理页签点击
const handleTabClick = (path: string) => {
  router.push(path)
  tabsStore.setActiveTab(path)
}

// 处理页签关闭
const handleTabClose = (path: string) => {
  tabsStore.removeTab(path)
}

// 显示右键菜单
const showContextMenu = (event: MouseEvent, tab: any, index: number) => {
  contextMenu.value = {
    visible: true,
    x: event.clientX,
    y: event.clientY,
    currentTab: tab,
    currentIndex: index
  }
}

// 隐藏右键菜单
const hideContextMenu = () => {
  contextMenu.value.visible = false
}

// 处理右键菜单操作
const handleContextMenuAction = (action: string) => {
  const { currentTab, currentIndex } = contextMenu.value
  
  switch (action) {
    case 'closeCurrent':
      if (currentTab) {
        handleTabClose(currentTab.path)
      }
      break
    case 'closeOther':
      if (currentTab) {
        tabsStore.closeOtherTabs(currentTab.path)
      }
      break
    case 'closeAll':
      tabsStore.closeAllTabs()
      break
    case 'closeLeft':
      if (currentIndex > 0) {
        const leftTabs = tabsStore.tabsList.slice(0, currentIndex)
        leftTabs.forEach(tab => {
          tabsStore.removeTab(tab.path)
        })
      }
      break
    case 'closeRight':
      if (currentIndex > -1 && currentIndex < tabsStore.tabsList.length - 1) {
        const rightTabs = tabsStore.tabsList.slice(currentIndex + 1)
        rightTabs.forEach(tab => {
          tabsStore.removeTab(tab.path)
        })
      }
      break
  }
  
  hideContextMenu()
}

const toggleDarkMode = () => {
  const body = document.body
  body.classList.toggle('dark-mode')
  // 这里可以添加保存暗色模式设置的逻辑
  localStorage.setItem('darkMode', body.classList.contains('dark-mode') ? 'true' : 'false')
}

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
  
  // 初始化默认页签
  if (route.path !== '/login') {
    const titleMap: Record<string, string> = {
      '/chat': '聊天',
      '/knowledge-base': '知识库',
      '/documents': '文档管理',
      '/evaluation': '知识库评估',
      '/model-settings': '模型管理',
      '/system/users': '系统设置'
    }
    const title = titleMap[route.path] || 'ZZWZZ RAG 系统'
    tabsStore.addTab({
      path: route.path,
      name: route.name as string || 'home',
      title
    })
  }
  
  // 添加点击事件监听器，点击页面其他地方时隐藏右键菜单
  document.addEventListener('click', hideContextMenu)
  document.addEventListener('scroll', hideContextMenu)
})

onUnmounted(() => {
  // 移除事件监听器
  document.removeEventListener('click', hideContextMenu)
  document.removeEventListener('scroll', hideContextMenu)
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
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

/* 滚动条样式 */
.sidebar-nav::-webkit-scrollbar {
  width: 6px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
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

/* 子菜单样式 */
.has-submenu {
  position: relative;
}

.submenu-title {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 12px 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 0 4px 4px 0;
  text-align: left;
}

.submenu-title span {
  flex: 1;
  text-align: left;
}

.submenu-arrow {
  margin-left: auto;
  font-size: 12px;
  transition: transform 0.2s ease;
}

.submenu-title:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.submenu-arrow {
  font-size: 12px;
  transition: transform 0.2s ease;
}

.submenu {
  list-style: none;
  padding: 0;
  margin: 0;
  background-color: rgba(255, 255, 255, 0.05);
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
}

.has-submenu.open .submenu {
  max-height: 500px;
}

.submenu li {
  margin: 0;
}

.submenu li a {
  padding: 10px 20px 10px 40px;
  font-size: 14px;
}

.submenu li a:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.submenu li a.router-link-active {
  background-color: #4CAF50;
  color: white;
}

/* 折叠状态下的子菜单 */
.sidebar.collapsed .submenu-title {
  justify-content: center;
}

.sidebar.collapsed .submenu-title span,
.sidebar.collapsed .submenu-title .submenu-arrow {
  display: none;
}

.sidebar.collapsed .submenu {
  position: absolute;
  left: 100%;
  top: 0;
  width: 180px;
  background-color: #2c3e50;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  max-height: none;
  display: none;
}

.sidebar.collapsed .has-submenu:hover .submenu {
  display: block;
}

.sidebar.collapsed .submenu li a {
  padding: 10px 16px;
  white-space: nowrap;
}

.sidebar.collapsed .submenu li a .icon {
  margin-right: 8px;
  width: auto;
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

/* 页签样式 */
.tabs-container {
  background-color: white;
  border-bottom: 1px solid #e0e0e0;
  height: 40px;
  display: flex;
  align-items: center;
  overflow-x: auto;
  overflow-y: hidden;
}

.tabs-wrapper {
  display: flex;
  align-items: center;
  padding: 0 10px;
}

.tab-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  margin-right: 8px;
  background-color: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
  cursor: pointer;
  position: relative;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.tab-item:hover {
  background-color: #e3f2fd;
}

.tab-item.active {
  background-color: white;
  border-color: #2196f3;
  color: #2196f3;
}

.tab-title {
  margin-right: 8px;
  font-size: 14px;
}

.tab-close-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s ease;
}

.tab-close-btn:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

/* 右键菜单样式 */
.context-menu {
  position: fixed;
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 1000;
  min-width: 150px;
  overflow: hidden;
}

.context-menu ul {
  list-style: none;
  margin: 0;
  padding: 4px 0;
}

.context-menu li {
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease;
}

.context-menu li:hover {
  background-color: #f5f5f5;
}

body.dark-mode .context-menu {
  background-color: #343a40;
  border-color: #495057;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.3);
}

body.dark-mode .context-menu li {
  color: #e0e0e0;
}

body.dark-mode .context-menu li:hover {
  background-color: #495057;
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