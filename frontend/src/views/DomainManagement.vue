<template>
  <div class="domain-management">
    <h2>领域管理</h2>
    
    <!-- 操作按钮 -->
    <div class="action-buttons">
      <el-button type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon>
        新建领域
      </el-button>
    </div>
    
    <!-- 领域列表 -->
    <el-table :data="domains" style="width: 100%">
      <el-table-column prop="name" label="领域名称" width="180" />
      <el-table-column prop="description" label="描述" />
      <el-table-column label="创建时间" width="200">
        <template #default="scope">
          {{ formatDateTime(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="scope">
          <el-switch
            v-model="scope.row.is_active"
            active-text="启用"
            inactive-text="停用"
            @change="toggleDomainStatus(scope.row)"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button size="small" @click="showUpdateDialog(scope.row)" style="margin-right: 8px;">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button size="small" type="danger" @click="confirmDelete(scope.row.id)">
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <div class="pagination">
      <Pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 创建领域对话框 -->
    <el-dialog v-model="createDialogVisible" title="创建领域">
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="领域名称">
          <el-input v-model="createForm.name" placeholder="请输入领域名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="createForm.description" placeholder="请输入领域描述" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createDomain">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 更新领域对话框 -->
    <el-dialog v-model="updateDialogVisible" title="编辑领域">
      <el-form :model="updateForm" label-width="80px">
        <el-form-item label="领域名称">
          <el-input v-model="updateForm.name" placeholder="请输入领域名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="updateForm.description" placeholder="请输入领域描述" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="updateDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="updateDomain">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { domainApi } from '../api/domain'
import Pagination from '../components/Pagination.vue'

// 领域列表
const domains = ref<any[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// 对话框状态
const createDialogVisible = ref(false)
const updateDialogVisible = ref(false)

// 表单数据
const createForm = ref({
  name: '',
  description: ''
})

const updateForm = ref({
  id: '',
  name: '',
  description: ''
})

// 获取领域列表
const getDomains = async () => {
  try {
    const skip = (currentPage.value - 1) * pageSize.value
    const response = await domainApi.getDomains(skip, pageSize.value)
    console.log(response)
    // 检查响应格式
    if (response.items) {
      // 后端返回了分页格式
      domains.value = response.items
      total.value = response.total
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '获取领域列表失败')
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  createForm.value = {
    name: '',
    description: ''
  }
  createDialogVisible.value = true
}

// 显示更新对话框
const showUpdateDialog = (domain: any) => {
  updateForm.value = {
    id: domain.id,
    name: domain.name,
    description: domain.description
  }
  updateDialogVisible.value = true
}

// 创建领域
const createDomain = async () => {
  try {
    await domainApi.createDomain(createForm.value)
    ElMessage.success('领域创建成功')
    createDialogVisible.value = false
    getDomains()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '创建领域失败')
  }
}

// 更新领域
const updateDomain = async () => {
  try {
    await domainApi.updateDomain(updateForm.value.id, updateForm.value)
    ElMessage.success('领域更新成功')
    updateDialogVisible.value = false
    getDomains()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '更新领域失败')
  }
}

// 格式化日期时间
const formatDateTime = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 切换领域状态
const toggleDomainStatus = async (domain: any) => {
  try {
    await domainApi.updateDomain(domain.id, { is_active: domain.is_active })
    ElMessage.success(domain.is_active ? '领域已启用' : '领域已停用')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '更新领域状态失败')
    // 恢复原来的状态
    domain.is_active = !domain.is_active
  }
}

// 确认删除
const confirmDelete = (domainId: string) => {
  ElMessageBox.confirm('确定要删除这个领域吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await domainApi.deleteDomain(domainId)
      ElMessage.success('领域删除成功')
      getDomains()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '删除领域失败')
    }
  }).catch(() => {
    // 取消删除
  })
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  getDomains()
}

const handleCurrentChange = (current: number) => {
  currentPage.value = current
  getDomains()
}

// 初始化
onMounted(() => {
  getDomains()
})
</script>

<style scoped>
.domain-management {
  padding: 20px;
}

.action-buttons {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  text-align: right;
}
</style>
