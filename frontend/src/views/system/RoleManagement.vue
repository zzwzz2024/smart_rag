<template>
  <div class="role-management-container">
    <div class="role-management-header">
      <h3>角色管理</h3>
      <el-button type="primary" @click="showAddRoleDialog = true">
        <el-icon><Plus /></el-icon>
        <span>添加角色</span>
      </el-button>
    </div>
    
    <!-- 搜索表单 -->
    <div class="role-search-form">
      <el-form :model="searchForm" class="role-form">
        <el-form-item label="角色名称">
          <el-input v-model="searchForm.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchRoles">
            <el-icon><Search /></el-icon>
            <span>查询</span>
          </el-button>
          <el-button @click="resetSearch">
            <el-icon><Refresh /></el-icon>
            <span>重置</span>
          </el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 角色列表 -->
    <div class="role-list">
      <el-table :data="roles" style="width: 100%" border>
        <el-table-column prop="id" label="ID" width="100" />
        <el-table-column prop="name" label="角色名称" width="180" />
        <el-table-column prop="description" label="角色描述" />
        <el-table-column prop="createdAt" label="创建时间" width="200" />
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="editRole(scope.row)">
              <el-icon><Edit /></el-icon>
              <span>编辑</span>
            </el-button>
            <el-button size="small" @click="setPermissions(scope.row)">
              <el-icon><Lock /></el-icon>
              <span>权限设置</span>
            </el-button>
            <el-button size="small" type="danger" @click="deleteRole(scope.row.id)">
              <el-icon><Delete /></el-icon>
              <span>删除</span>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 分页 -->
    <div class="role-pagination">
      <el-pagination
        v-model:current-page="pagination.currentPage"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="pagination.total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 添加/编辑角色对话框 -->
    <el-dialog
      v-model="showAddRoleDialog"
      :title="dialogTitle"
      width="500px"
    >
      <el-form :model="roleForm" :rules="roleRules" ref="roleFormRef" label-width="100px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="roleForm.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色描述" prop="description">
          <el-input v-model="roleForm.description" placeholder="请输入角色描述" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddRoleDialog = false">取消</el-button>
          <el-button type="primary" @click="saveRole">保存</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 权限设置对话框 -->
    <el-dialog
      v-model="showPermissionDialog"
      title="权限设置"
      width="600px"
    >
      <div class="permission-setting">
        <el-tree
          v-model="selectedPermissions"
          :data="permissionTree"
          show-checkbox
          node-key="id"
          default-expand-all
        />
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showPermissionDialog = false">取消</el-button>
          <el-button type="primary" @click="savePermissions">保存权限</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, Edit, Delete, Lock } from '@element-plus/icons-vue'
import { roleApi, permissionApi } from '../../api/system'
import type { Role, Permission } from '../../types/system'

// 数据
const roles = ref<Role[]>([])
const permissions = ref<Permission[]>([])
const permissionTree = ref<any[]>([])
const loading = ref(false)

// 搜索表单
const searchForm = ref({
  name: ''
})

// 分页
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 对话框
const showAddRoleDialog = ref(false)
const dialogTitle = ref('添加角色')
const roleForm = ref({
  id: '',
  name: '',
  description: ''
})
const roleFormRef = ref()

// 权限设置
const showPermissionDialog = ref(false)
const selectedPermissions = ref<string[]>([])
const currentRole = ref<Role | null>(null)

// 表单验证规则
const roleRules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入角色描述', trigger: 'blur' }
  ]
}

// 加载角色列表
const loadRoles = async () => {
  loading.value = true
  try {
    const response = await roleApi.getRoles({
      skip: (pagination.value.currentPage - 1) * pagination.value.pageSize,
      limit: pagination.value.pageSize
    })
    roles.value = response
    // 假设后端返回总数
    pagination.value.total = response.total || response.length
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
    // 构建权限树
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

// 搜索角色
const searchRoles = async () => {
  loading.value = true
  try {
    // 这里可以根据搜索条件调用API
    // 暂时使用本地过滤
    const filteredRoles = roles.value.filter(role => 
      role.name.includes(searchForm.value.name)
    )
    roles.value = filteredRoles
    pagination.value.total = filteredRoles.length
    ElMessage.success('搜索成功')
  } catch (error) {
    console.error('搜索角色失败:', error)
    ElMessage.error('搜索角色失败')
  } finally {
    loading.value = false
  }
}

// 重置搜索
const resetSearch = () => {
  searchForm.value = {
    name: ''
  }
  loadRoles()
}

// 编辑角色
const editRole = (role: Role) => {
  roleForm.value = { ...role }
  dialogTitle.value = '编辑角色'
  showAddRoleDialog.value = true
}

// 设置权限
const setPermissions = async (role: Role) => {
  currentRole.value = role
  showPermissionDialog.value = true
  // 这里可以加载角色现有的权限
  selectedPermissions.value = []
}

// 删除角色
const deleteRole = (roleId: string) => {
  ElMessageBox.confirm(
    '确定要删除这个角色吗？',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'danger'
    }
  ).then(async () => {
    try {
      await roleApi.deleteRole(roleId)
      ElMessage.success('角色删除成功')
      loadRoles()
    } catch (error) {
      console.error('删除角色失败:', error)
      ElMessage.error('删除角色失败')
    }
  }).catch(() => {
    // 取消删除
  })
}

// 保存角色
const saveRole = async () => {
  if (!roleFormRef.value) return
  
  roleFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        if (roleForm.value.id) {
          // 编辑角色
          await roleApi.updateRole(roleForm.value.id, {
            name: roleForm.value.name,
            description: roleForm.value.description
          })
          ElMessage.success('角色更新成功')
        } else {
          // 添加角色
          await roleApi.createRole({
            name: roleForm.value.name,
            description: roleForm.value.description
          })
          ElMessage.success('角色添加成功')
        }
        showAddRoleDialog.value = false
        loadRoles()
      } catch (error) {
        console.error('保存角色失败:', error)
        ElMessage.error('保存角色失败')
      }
    }
  })
}

// 保存权限
const savePermissions = async () => {
  if (!currentRole.value) return
  
  try {
    await roleApi.assignPermissions(currentRole.value.id, selectedPermissions.value)
    ElMessage.success('权限保存成功')
    showPermissionDialog.value = false
  } catch (error) {
    console.error('保存权限失败:', error)
    ElMessage.error('保存权限失败')
  }
}

// 分页处理
const handleSizeChange = (size: number) => {
  pagination.value.pageSize = size
  loadRoles()
}

const handleCurrentChange = (current: number) => {
  pagination.value.currentPage = current
  loadRoles()
}

// 初始化
onMounted(async () => {
  await loadRoles()
  await loadPermissions()
})
</script>

<style scoped>
.role-management-container {
  padding: 20px 0;
}

.role-management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.role-management-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.role-search-form {
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

.role-list {
  margin-bottom: 20px;
}

.role-pagination {
  display: flex;
  justify-content: flex-end;
}

.permission-setting {
  max-height: 400px;
  overflow-y: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .role-form {
    flex-direction: column;
    align-items: stretch;
  }
  
  .role-management-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>