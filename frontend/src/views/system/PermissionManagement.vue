<template>
  <div class="permission-management-container">
    <div class="permission-management-header">
      <h3>权限设置</h3>
    </div>
    
    <!-- 角色选择 -->
    <div class="role-selector">
      <el-form :model="roleForm" class="role-form">
        <el-form-item label="选择角色">
          <el-select v-model="roleForm.roleId" placeholder="请选择角色" @change="handleRoleChange">
            <el-option
              v-for="role in roles"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="currentRole">
          <div class="permission-actions-top">
            <el-button size="small" @click="selectAll">全选</el-button>
            <el-button size="small" @click="selectInverse">反选</el-button>
          </div>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 权限树 -->
    <div class="permission-tree" v-if="currentRole">
      <el-tree
        ref="permissionTreeRef"
        :data="permissionTree"
        show-checkbox
        node-key="id"
        default-expand-all
        :default-checked-keys="selectedPermissions"
        @check="handleCheck"
      />
    </div>
    
    <!-- 保存按钮 -->
    <div class="permission-actions" v-if="currentRole">
      <el-button type="primary" @click="savePermissions">
        <el-icon><Check /></el-icon>
        <span>保存权限</span>
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Check } from '@element-plus/icons-vue'
import { roleApi, permissionApi, menuApi } from '../../api/system'
import type { Role, Permission, Menu } from '../../types/system'

// 数据
const roles = ref<Role[]>([])
const permissions = ref<Permission[]>([])
const menus = ref<Menu[]>([])
const permissionTree = ref<any[]>([])
const loading = ref(false)

// 角色表单
const roleForm = ref({
  roleId: ''
})

// 当前角色
const currentRole = ref<Role | null>(null)

// 选中的权限
const selectedPermissions = ref<string[]>([])

// 权限树引用
const permissionTreeRef = ref<any>(null)

// 加载角色列表
const loadRoles = async () => {
  loading.value = true
  try {
    const response = await roleApi.getRoles()
    roles.value = response
  } catch (error) {
    console.error('加载角色列表失败:', error)
    ElMessage.error('加载角色列表失败')
  } finally {
    loading.value = false
  }
}

// 加载菜单列表
const loadMenus = async () => {
  try {
    const response = await menuApi.getMenus()
    menus.value = response
  } catch (error) {
    console.error('加载菜单列表失败:', error)
    ElMessage.error('加载菜单列表失败')
  }
}

// 加载权限列表
const loadPermissions = async () => {
  try {
    const response = await permissionApi.getPermissions()
    permissions.value = response
    await loadMenus()
    buildPermissionTree()
  } catch (error) {
    console.error('加载权限列表失败:', error)
    ElMessage.error('加载权限列表失败')
  }
}

// 构建菜单树
const buildMenuTree = (menus: Menu[]): any[] => {
  const menuMap: Record<string, any> = {}
  const tree: any[] = []

  // 首先将所有菜单转换为树节点格式
  menus.forEach(menu => {
    menuMap[menu.id] = {
      id: menu.id,
      label: menu.name,
      children: [],
      isMenu: true
    }
  })

  // 构建菜单树结构
  menus.forEach(menu => {
    if (menu.parent_id) {
      // 如果有父菜单，添加到父菜单的children中
      if (menuMap[menu.parent_id]) {
        menuMap[menu.parent_id].children.push(menuMap[menu.id])
      }
    } else {
      // 如果没有父菜单，直接添加到树中
      tree.push(menuMap[menu.id])
    }
  })

  return tree
}

// 构建权限树
const buildPermissionTree = () => {
  try {
    // 先构建菜单树
    const menuTree = buildMenuTree(menus.value)

    // 确保 menuTree 是数组
    if (!Array.isArray(menuTree)) {
      console.error('menuTree 不是数组:', menuTree)
      permissionTree.value = []
      return
    }

    // 将权限添加到对应的菜单节点下
    permissions.value.forEach(permission => {
      if (permission && permission.menu_id) {
        // 查找对应的菜单节点
        const findMenuNode = (nodes: any[]): any => {
          if (!Array.isArray(nodes)) return null
          
          for (const node of nodes) {
            if (node && node.id === permission.menu_id) {
              return node
            }
            if (node && node.children && Array.isArray(node.children) && node.children.length > 0) {
              const found = findMenuNode(node.children)
              if (found) {
                return found
              }
            }
          }
          return null
        }

        const menuNode = findMenuNode(menuTree)
        if (menuNode && menuNode.children && Array.isArray(menuNode.children)) {
          // 添加权限作为菜单的子节点
          menuNode.children.push({
            id: permission.id,
            label: permission.name,
            isMenu: false
          })
        }
      } else if (permission) {
        // 如果没有menu_id，直接添加到根节点
        menuTree.push({
          id: permission.id,
          label: permission.name,
          isMenu: false
        })
      }
    })

    permissionTree.value = menuTree
  } catch (error) {
    console.error('构建权限树失败:', error)
    permissionTree.value = []
  }
}

// 处理角色选择
const handleRoleChange = async () => {
  if (roleForm.value.roleId) {
    // 查找角色信息
    currentRole.value = roles.value.find(role => role.id === roleForm.value.roleId)
    
    // 重新从后端加载角色的权限信息
    try {
      // 调用API获取角色详情，包括权限信息
      const roleWithPermissions = await roleApi.getRoleById(roleForm.value.roleId)
      
      // 更新选中的权限
      const permissionIds = roleWithPermissions.permissions?.map(p => p.id) || []
      selectedPermissions.value = permissionIds
      
      // 更新权限树的选中状态
      if (permissionTreeRef.value) {
        permissionTreeRef.value.setCheckedKeys(permissionIds)
      }
    } catch (error) {
      console.error('加载角色权限失败:', error)
      selectedPermissions.value = []
      if (permissionTreeRef.value) {
        permissionTreeRef.value.setCheckedKeys([])
      }
    }
  } else {
    currentRole.value = null
    selectedPermissions.value = []
    if (permissionTreeRef.value) {
      permissionTreeRef.value.setCheckedKeys([])
    }
  }
}

// 处理权限勾选变化
const handleCheck = (data: any, checked: any) => {
  selectedPermissions.value = checked.checkedKeys
}

// 全选功能
const selectAll = () => {
  // 收集所有节点的 ID
  const allNodes: string[] = []
  
  // 递归遍历所有节点
  const traverseNodes = (nodes: any[]) => {
    nodes.forEach(node => {
      if (node.id) {
        allNodes.push(node.id)
      }
      if (node.children && node.children.length > 0) {
        traverseNodes(node.children)
      }
    })
  }
  
  // 从根节点开始遍历
  traverseNodes(permissionTree.value)
  
  // 设置所有节点为选中状态
  selectedPermissions.value = allNodes
  if (permissionTreeRef.value) {
    permissionTreeRef.value.setCheckedKeys(allNodes)
  }
}

// 反选功能
const selectInverse = () => {
  // 收集所有节点的 ID
  const allNodes: string[] = []
  
  // 递归遍历所有节点
  const traverseNodes = (nodes: any[]) => {
    nodes.forEach(node => {
      if (node.id) {
        allNodes.push(node.id)
      }
      if (node.children && node.children.length > 0) {
        traverseNodes(node.children)
      }
    })
  }
  
  // 从根节点开始遍历
  traverseNodes(permissionTree.value)
  
  // 计算反选后的节点 ID
  const inverseNodes = allNodes.filter(id => !selectedPermissions.value.includes(id))
  
  // 设置反选后的节点为选中状态
  selectedPermissions.value = inverseNodes
  if (permissionTreeRef.value) {
    permissionTreeRef.value.setCheckedKeys(inverseNodes)
  }
}



// 保存权限
const savePermissions = async () => {
  if (!currentRole.value) return
  
  try {
    await roleApi.assignPermissions(currentRole.value.id, selectedPermissions.value)
    ElMessage.success('权限保存成功')
  } catch (error) {
    console.error('保存权限失败:', error)
    ElMessage.error('保存权限失败')
  }
}

// 初始化
onMounted(async () => {
  await loadRoles()
  await loadPermissions()
  
  // 默认选择第一个角色
  if (roles.value.length > 0) {
    roleForm.value.roleId = roles.value[0].id
    await handleRoleChange()
  }
})
</script>

<style scoped>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  overflow: hidden; /* 👈 隐藏最右侧全局滚动条 */
}

.permission-management-container {
  padding: 20px 0;
  height: 100vh;
  overflow: hidden;
  box-sizing: border-box;
}

.permission-management-header {
  margin-bottom: 24px;
}

.permission-management-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.role-selector {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
}

.role-form {
  display: flex;
  align-items: end;
  gap: 16px;
  flex-wrap: wrap;
}

.role-form .el-select {
  width: 200px;
}

.permission-tree {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 24px;
  max-height: 35vh;
  overflow-y: auto;
}



.permission-actions-top {
  display: flex;
  gap: 8px;
}

.permission-actions-top .el-button {
  font-size: 12px;
  padding: 4px 12px;
}

.tree-node-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tree-node-content .el-radio {
  margin-right: 0;
}

.tree-node-content span {
  flex: 1;
}

.permission-actions {
  display: flex;
  justify-content: flex-start;
  position: sticky;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: #f9f9f9;
  padding: 16px 0;
  margin-top: 16px;
  border-top: 1px solid #eaeaea;
  z-index: 10;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .role-form {
    flex-direction: column;
    align-items: stretch;
  }
  
  .permission-tree {
    padding: 16px;
    max-height: calc(100vh - 280px);
  }
  
  .permission-actions {
    justify-content: center;
  }
}

/* 主内容区域滚动条隐藏 */
:deep(.el-main) {
  overflow: hidden !important;
  height: 100% !important;
}

/* 侧边栏滚动条保留 */
:deep(.el-aside) {
  //overflow-y: auto;
}
</style>