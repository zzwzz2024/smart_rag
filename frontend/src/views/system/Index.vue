<template>
  <div class="system-container">
    <div class="system-header">
      <h2>系统管理</h2>
    </div>
    
    <div class="system-nav">
      <el-menu
        :default-active="activeSubMenu"
        class="system-menu"
        mode="horizontal"
        @select="handleSubMenuSelect"
      >
        <el-menu-item index="users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="roles">
          <el-icon><Position /></el-icon>
          <span>角色管理</span>
        </el-menu-item>
        <el-menu-item index="menus">
          <el-icon><Menu /></el-icon>
          <span>菜单管理</span>
        </el-menu-item>
        <el-menu-item index="permissions">
          <el-icon><Lock /></el-icon>
          <span>权限设置</span>
        </el-menu-item>
        <el-menu-item index="dictionaries">
          <el-icon><Grid /></el-icon>
          <span>字典管理</span>
        </el-menu-item>
      </el-menu>
    </div>
    
    <div class="system-content">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { User, Position, Menu, Lock, Grid } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 计算当前激活的子菜单
const activeSubMenu = computed(() => {
  const path = route.path
  if (path.includes('/system/users')) return 'users'
  if (path.includes('/system/roles')) return 'roles'
  if (path.includes('/system/menus')) return 'menus'
  if (path.includes('/system/permissions')) return 'permissions'
  if (path.includes('/system/dictionaries')) return 'dictionaries'
  return 'users'
})

// 处理子菜单选择
const handleSubMenuSelect = (index: string) => {
  router.push(`/system/${index}`)
}

// 初始化
onMounted(() => {
  // 如果当前路径是/system但没有子路径，重定向到/system/users
  if (route.path === '/system') {
    router.push('/system/users')
  }
})
</script>

<style scoped>
.system-container {
  padding: 20px 0;
}

.system-header {
  margin-bottom: 24px;
}

.system-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.system-nav {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.system-menu {
  border-bottom: none;
}

.system-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 24px;
  min-height: 600px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .system-menu {
    flex-wrap: wrap;
  }
  
  .system-content {
    padding: 16px;
  }
}
</style>