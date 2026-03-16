<template>
  <div class="tag-management">
    <h2>标签管理</h2>
    
    <!-- 操作按钮 -->
    <div class="action-buttons">
      <el-button type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon>
        新建标签
      </el-button>
    </div>
    
    <!-- 标签列表 -->
    <el-table :data="tags" style="width: 100%">
      <el-table-column prop="name" label="标签名称" width="180" />
      <el-table-column prop="color" label="颜色" width="120">
        <template #default="scope">
          <div class="color-preview" :style="{ backgroundColor: scope.row.color }"></div>
          <span>{{ scope.row.color }}</span>
        </template>
      </el-table-column>
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
            @change="toggleTagStatus(scope.row)"
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
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 创建标签对话框 -->
    <el-dialog v-model="createDialogVisible" title="创建标签">
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="标签名称">
          <el-input v-model="createForm.name" placeholder="请输入标签名称" />
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="createForm.color" show-alpha />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createTag">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 更新标签对话框 -->
    <el-dialog v-model="updateDialogVisible" title="编辑标签">
      <el-form :model="updateForm" label-width="80px">
        <el-form-item label="标签名称">
          <el-input v-model="updateForm.name" placeholder="请输入标签名称" />
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="updateForm.color" show-alpha />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="updateDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="updateTag">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { tagApi } from '../api/tag'

// 标签列表
const tags = ref<any[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// 对话框状态
const createDialogVisible = ref(false)
const updateDialogVisible = ref(false)

// 表单数据
const createForm = ref({
  name: '',
  color: '#4CAF50'
})

const updateForm = ref({
  id: '',
  name: '',
  color: ''
})

// 获取标签列表
const getTags = async () => {
  try {
    const skip = (currentPage.value - 1) * pageSize.value
    const response = await tagApi.getTags(skip, pageSize.value)
    console.log(response)
    // 检查响应格式
    if (response.items) {
      // 后端返回了分页格式
      tags.value = response.items
      total.value = response.total
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '获取标签列表失败')
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  createForm.value = {
    name: '',
    color: '#4CAF50'
  }
  createDialogVisible.value = true
}

// 显示更新对话框
const showUpdateDialog = (tag: any) => {
  updateForm.value = {
    id: tag.id,
    name: tag.name,
    color: tag.color
  }
  updateDialogVisible.value = true
}

// 创建标签
const createTag = async () => {
  try {
    await tagApi.createTag(createForm.value)
    ElMessage.success('标签创建成功')
    createDialogVisible.value = false
    getTags()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '创建标签失败')
  }
}

// 更新标签
const updateTag = async () => {
  try {
    await tagApi.updateTag(updateForm.value.id, updateForm.value)
    ElMessage.success('标签更新成功')
    updateDialogVisible.value = false
    getTags()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '更新标签失败')
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

// 切换标签状态
const toggleTagStatus = async (tag: any) => {
  try {
    await tagApi.updateTag(tag.id, { is_active: tag.is_active })
    ElMessage.success(tag.is_active ? '标签已启用' : '标签已停用')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '更新标签状态失败')
    // 恢复原来的状态
    tag.is_active = !tag.is_active
  }
}

// 确认删除
const confirmDelete = (tagId: string) => {
  ElMessageBox.confirm('确定要删除这个标签吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await tagApi.deleteTag(tagId)
      ElMessage.success('标签删除成功')
      getTags()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '删除标签失败')
    }
  }).catch(() => {
    // 取消删除
  })
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  getTags()
}

const handleCurrentChange = (current: number) => {
  currentPage.value = current
  getTags()
}

// 初始化
onMounted(() => {
  getTags()
})
</script>

<style scoped>
.tag-management {
  padding: 20px;
}

.action-buttons {
  margin-bottom: 20px;
}

.color-preview {
  display: inline-block;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  margin-right: 8px;
  vertical-align: middle;
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
