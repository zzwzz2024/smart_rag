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
      </el-form>
    </div>
    
    <!-- 权限树 -->
    <div class="permission-tree" v-if="currentRole">
      <h4>{{ currentRole.name }} 的权限设置</h4>
      <el-tree
        v-model="selectedPermissions"
        :data="permissionTree"
        show-checkbox
        node-key="id"
        default-expand-all
        @check-change="handleCheckChange"
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
import { roleApi, permissionApi } from '../../api/system'
import type { Role, Permission } from '../../types/system'

// 数据
const roles = ref<Role[]>([])
const permissions = ref<Permission[]>([])
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

// 加载权限列表
const loadPermissions = async () => {
  try {
    const response = await permissionApi.getPermissions()
    permissions.value = response
    buildPermissionTree()
  } catch (error) {
    console.error('加载权限列表失败:', error)
    ElMessage.error('加载权限列表失败')
  }
}

// 构建权限树
const buildPermissionTree = () => {
  // 这里需要根据实际的权限数据结构构建树
  // 暂时使用简化的实现
  permissionTree.value = permissions.value.map(permission => ({
    id: permission.id,
    label: permission.name,
    children: []
  }))
}

// 处理角色选择
const handleRoleChange = async () => {
  if (roleForm.value.roleId) {
    currentRole.value = roles.value.find(role => role.id === roleForm.value.roleId)
    // 加载角色现有的权限
    try {
      const roleWithPermissions = await roleApi.getRoleById(roleForm.value.roleId)
      selectedPermissions.value = roleWithPermissions.permissions?.map(p => p.id) || []
    } catch (error) {
      console.error('加载角色权限失败:', error)
      selectedPermissions.value = []
    }
  } else {
    currentRole.value = null
    selectedPermissions.value = []
  }
}

// 处理权限勾选变化
const handleCheckChange = (data: any, checked: boolean, indeterminate: boolean) => {
  console.log('权限变化:', data, checked, indeterminate)
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
.permission-management-container {
  padding: 20px 0;
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

.permission-tree {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 24px;
}

.permission-tree h4 {
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 600;
}

.permission-actions {
  display: flex;
  justify-content: flex-start;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .role-form {
    flex-direction: column;
    align-items: stretch;
  }
  
  .permission-tree {
    padding: 16px;
  }
  
  .permission-actions {
    justify-content: center;
  }
}
</style>