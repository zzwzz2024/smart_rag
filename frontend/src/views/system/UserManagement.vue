<template>
  <div class="user-management-container">
    <div class="user-management-header">
      <h3>用户管理</h3>
      <el-button type="primary" @click="showAddUserDialog = true">
        <el-icon><Plus /></el-icon>
        <span>添加用户</span>
      </el-button>
    </div>
    
    <!-- 搜索表单 -->
    <div class="user-search-form">
      <el-form :model="searchForm" class="user-form">
        <el-form-item label="用户名">
          <el-input v-model="searchForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="searchForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="searchForm.roleId" placeholder="请选择角色">
            <el-option
              v-for="role in roles"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchUsers">
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
    
    <!-- 用户列表 -->
    <div class="user-list">
      <el-table v-loading="loading" :data="users" style="width: 100%" border>
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column prop="username" label="用户名" width="180" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="roleName" label="角色" width="150" />
        <el-table-column prop="createdAt" label="创建时间" width="200" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="editUser(scope.row)">
              <el-icon><Edit /></el-icon>
              <span>编辑</span>
            </el-button>
            <el-button size="small" type="danger" @click="deleteUser(scope.row.id)">
              <el-icon><Delete /></el-icon>
              <span>删除</span>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 分页 -->
    <div class="user-pagination">
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
    
    <!-- 添加/编辑用户对话框 -->
    <el-dialog
      v-model="showAddUserDialog"
      :title="dialogTitle"
      width="500px"
    >
      <el-form :model="userForm" :rules="userRules" ref="userFormRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码" :prop="userForm.id ? '' : 'password'">
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="角色" prop="roleId">
          <el-select v-model="userForm.roleId" placeholder="请选择角色">
            <el-option
              v-for="role in roles"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddUserDialog = false">取消</el-button>
          <el-button type="primary" @click="saveUser">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import {ref, onMounted, watch} from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, Edit, Delete } from '@element-plus/icons-vue'
import { userApi, roleApi } from '../../api/system'
import type { User } from '../../types/system'
import {useRoute} from "vue-router";

// 数据
const users = ref<any[]>([])
const roles = ref<any[]>([])
const loading = ref(false)

// 搜索表单
const searchForm = ref({
  username: '',
  email: '',
  roleId: ''
})

// 分页
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 对话框
const showAddUserDialog = ref(false)
const dialogTitle = ref('添加用户')
const userForm = ref({
  id: '',
  username: '',
  email: '',
  password: '',
  roleId: ''
})
const userFormRef = ref()

// 表单验证规则
const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ],
  roleId: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

// 加载用户列表
const loadUsers = async () => {
  loading.value = true
  try {
    const response = await userApi.getUsers({
      skip: (pagination.value.currentPage - 1) * pagination.value.pageSize,
      limit: pagination.value.pageSize
    })
    // 处理响应数据，添加roleName字段
    users.value = response.map((user: any) => {
      const role = roles.value.find(r => r.id === user.role_id)
      return {
        ...user,
        roleName: role ? role.name : user.role,
        roleId: user.role_id,
        createdAt: user.created_at
      }
    })
    pagination.value.total = response.total || response.length
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

// 加载角色列表
const loadRoles = async () => {
  try {
    const response = await roleApi.getRoles()
    roles.value = response
  } catch (error) {
    console.error('加载角色列表失败:', error)
    ElMessage.error('加载角色列表失败')
  }
}

// 搜索用户
const searchUsers = async () => {
  loading.value = true
  try {
    // 这里可以根据搜索条件调用API
    // 暂时使用模拟搜索
    const filteredUsers = users.value.filter(user => {
      return (
        (searchForm.value.username ? user.username.includes(searchForm.value.username) : true) &&
        (searchForm.value.email ? user.email.includes(searchForm.value.email) : true) &&
        (searchForm.value.roleId ? user.roleId === searchForm.value.roleId : true)
      )
    })
    users.value = filteredUsers
    pagination.value.total = filteredUsers.length
    ElMessage.success('搜索成功')
  } catch (error) {
    console.error('搜索用户失败:', error)
    ElMessage.error('搜索用户失败')
  } finally {
    loading.value = false
  }
}

// 重置搜索
const resetSearch = () => {
  searchForm.value = {
    username: '',
    email: '',
    roleId: ''
  }
  loadUsers()
}

// 编辑用户
const editUser = (user: any) => {
  userForm.value = {
    id: user.id,
    username: user.username,
    email: user.email,
    roleId: user.roleId
  }
  dialogTitle.value = '编辑用户'
  showAddUserDialog.value = true
}

// 删除用户
const deleteUser = (userId: string) => {
  ElMessageBox.confirm(
    '确定要删除这个用户吗？',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'danger'
    }
  ).then(async () => {
    try {
      await userApi.deleteUser(userId)
      ElMessage.success('用户删除成功')
      loadUsers()
    } catch (error) {
      console.error('删除用户失败:', error)
      ElMessage.error('删除用户失败')
    }
  }).catch(() => {
    // 取消删除
  })
}

// 保存用户
const saveUser = async () => {
  if (!userFormRef.value) return
  
  userFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        if (userForm.value.id) {
          // 编辑用户
          await userApi.updateUser(userForm.value.id, {
            username: userForm.value.username,
            email: userForm.value.email,
            role_id: userForm.value.roleId
          })
          if (userForm.value.password) {
            // 如果填写了密码，更新密码
            await userApi.updateUser(userForm.value.id, {
              password: userForm.value.password
            })
          }
          ElMessage.success('用户更新成功')
        } else {
          // 添加用户
          await userApi.createUser({
            username: userForm.value.username,
            email: userForm.value.email,
            password: userForm.value.password,
            role_id: userForm.value.roleId,
            is_active: true
          })
          ElMessage.success('用户添加成功')
        }
        showAddUserDialog.value = false
        loadUsers()
      } catch (error) {
        console.error('保存用户失败:', error)
        ElMessage.error('保存用户失败')
      }
    }
  })
}

// 分页处理
const handleSizeChange = (size: number) => {
  pagination.value.pageSize = size
  loadUsers()
}

const handleCurrentChange = (current: number) => {
  pagination.value.currentPage = current
  loadUsers()
}

// 初始化
onMounted(async () => {
  await loadRoles()
  await loadUsers()
})

const route = useRoute()
watch(
  () => route.query._refresh,  // 直接监听 _refresh 查询参数
  async (newValue) => {
    if (newValue) {
      await Promise.all([
         await loadRoles(),
         await loadUsers()
      ])
    }
  },
  { immediate: false }
)
</script>

<style scoped>
.user-management-container {
  padding: 20px 0;
}

.user-management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.user-management-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.user-search-form {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
}

.user-form {
  display: flex;
  align-items: end;
  gap: 16px;
  flex-wrap: wrap;
}

.user-list {
  margin-bottom: 20px;
}

.user-pagination {
  display: flex;
  justify-content: flex-end;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-form {
    flex-direction: column;
    align-items: stretch;
  }
  
  .user-management-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>