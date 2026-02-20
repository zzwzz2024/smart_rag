<template>
  <div class="api-auth-container">
    <div class="api-auth-header">
      <h2>API授权管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        <span>创建授权</span>
      </el-button>
    </div>

    <!-- 创建授权对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="dialogTitle"
      width="600px"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-form-item label="供应商名称" prop="vendor_name">
          <el-input v-model="formData.vendor_name" placeholder="请输入供应商名称" />
        </el-form-item>
        <el-form-item label="供应商负责人" prop="vendor_contact">
          <el-input v-model="formData.vendor_contact" placeholder="请输入供应商负责人" />
        </el-form-item>
        <el-form-item label="联系电话" prop="contact_phone">
          <el-input v-model="formData.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="授权IP地址">
          <el-input 
            v-model="formData.authorized_ips" 
            placeholder="请输入授权IP地址，多个IP以逗号分隔"
            type="textarea"
            :rows="2"
          />
        </el-form-item>
        <el-form-item label="授权知识库" prop="knowledge_base_ids">
          <el-select
            v-model="formData.knowledge_base_ids"
            multiple
            placeholder="请选择授权知识库"
            style="width: 100%"
          >
            <el-option
              v-for="kb in knowledgeBases"
              :key="kb.id"
              :label="kb.name"
              :value="kb.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="授权开始时间" prop="start_time">
          <el-date-picker
            v-model="formData.start_time"
            type="datetime"
            placeholder="选择开始时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="授权结束时间" prop="end_time">
          <el-date-picker
            v-model="formData.end_time"
            type="datetime"
            placeholder="选择结束时间"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="saveAuthorization">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 授权列表 -->
    <div class="api-auth-list">
      <el-table v-loading="loading" :data="authorizations" style="width: 100%">
        <el-table-column prop="vendor_name" label="供应商名称" width="180" />
        <el-table-column prop="vendor_contact" label="负责人" width="150" />
        <el-table-column prop="contact_phone" label="联系电话" width="150" />
        <el-table-column label="授权知识库" width="200">
          <template #default="scope">
            <el-tooltip :content="scope.row.knowledge_base_names.join(', ')">
              <div class="kb-tags">
                <el-tag v-for="name in scope.row.knowledge_base_names.slice(0, 2)" :key="name" size="small">
                  {{ name }}
                </el-tag>
                <el-tag v-if="scope.row.knowledge_base_names.length > 2" size="small" type="info">
                  +{{ scope.row.knowledge_base_names.length - 2 }}
                </el-tag>
              </div>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="授权码" width="300">
          <template #default="scope">
            <el-tooltip content="点击复制">
              <span class="auth-code" @click="copyAuthCode(scope.row.auth_code)">
                {{ scope.row.auth_code }}
              </span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="有效期" width="200">
          <template #default="scope">
            <div>
              <div>{{ formatDate(scope.row.start_time) }}</div>
              <div>{{ formatDate(scope.row.end_time) }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="isAuthorizationValid(scope.row) ? 'success' : 'danger'">
              {{ isAuthorizationValid(scope.row) ? '有效' : '无效' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="editAuthorization(scope.row)">
              <el-icon><Edit /></el-icon>
              <span>编辑</span>
            </el-button>
            <el-button size="small" type="danger" @click="deleteAuthorization(scope.row.id)">
              <el-icon><Delete /></el-icon>
              <span>删除</span>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="api-auth-pagination">
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Search, Refresh } from '@element-plus/icons-vue'
import { useKbStore } from '../stores/kb'
import request from '../api/request'
import type { KnowledgeBase } from '../types'

// API 接口
const apiAuthApi = {
  // 获取授权列表
  getAuthorizations(params?: any) {
    return request({
      url: '/api-auth',
      method: 'get',
      params
    })
  },
  
  // 创建授权
  createAuthorization(data: any) {
    return request({
      url: '/api-auth',
      method: 'post',
      data
    })
  },
  
  // 更新授权
  updateAuthorization(id: string, data: any) {
    return request({
      url: `/api-auth/${id}`,
      method: 'put',
      data
    })
  },
  
  // 删除授权
  deleteAuthorization(id: string) {
    return request({
      url: `/api-auth/${id}`,
      method: 'delete'
    })
  }
}

// 数据
const authorizations = ref<any[]>([])
const knowledgeBases = ref<KnowledgeBase[]>([])
const loading = ref(false)
const showCreateDialog = ref(false)
const dialogTitle = ref('创建授权')
const currentAuthorizationId = ref<string>('')

// 表单数据
const formData = ref({
  vendor_name: '',
  vendor_contact: '',
  contact_phone: '',
  authorized_ips: '',
  knowledge_base_ids: [] as string[],
  start_time: new Date(),
  end_time: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) // 默认30天后
})

// 表单验证规则
const formRules = ref({
  vendor_name: [{ required: true, message: '请输入供应商名称', trigger: 'blur' }],
  vendor_contact: [{ required: true, message: '请输入供应商负责人', trigger: 'blur' }],
  contact_phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
  knowledge_base_ids: [{ required: true, message: '请选择授权知识库', trigger: 'change' }],
  start_time: [{ required: true, message: '请选择授权开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择授权结束时间', trigger: 'change' }]
})

// 分页
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 表单引用
const formRef = ref()

// 加载授权列表
const loadAuthorizations = async () => {
  loading.value = true
  try {
    const response = await apiAuthApi.getAuthorizations({
      skip: (pagination.value.currentPage - 1) * pagination.value.pageSize,
      limit: pagination.value.pageSize
    })
    authorizations.value = response.data || response
    pagination.value.total = authorizations.value.length
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || '获取授权列表失败'
    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
  }
}

// 加载知识库列表
const loadKnowledgeBases = async () => {
  try {
    await useKbStore().getKnowledgeBases()
    knowledgeBases.value = useKbStore().knowledgeBases
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || '获取知识库列表失败'
    ElMessage.error(errorMessage)
  }
}

// 保存授权
const saveAuthorization = async () => {
  if (!formRef.value) return
  
  formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      loading.value = true
      try {
        if (currentAuthorizationId.value) {
          // 更新授权
          await apiAuthApi.updateAuthorization(currentAuthorizationId.value, formData.value)
          ElMessage.success('更新授权成功')
        } else {
          // 创建授权
          await apiAuthApi.createAuthorization(formData.value)
          ElMessage.success('创建授权成功')
        }
        showCreateDialog.value = false
        await loadAuthorizations()
        resetForm()
      } catch (error: any) {
        const errorMessage = error.response?.data?.detail || '保存授权失败'
        ElMessage.error(errorMessage)
      } finally {
        loading.value = false
      }
    }
  })
}

// 编辑授权
const editAuthorization = (authorization: any) => {
  currentAuthorizationId.value = authorization.id
  dialogTitle.value = '编辑授权'
  formData.value = {
    vendor_name: authorization.vendor_name,
    vendor_contact: authorization.vendor_contact,
    contact_phone: authorization.contact_phone,
    authorized_ips: authorization.authorized_ips,
    knowledge_base_ids: authorization.knowledge_base_ids,
    start_time: new Date(authorization.start_time),
    end_time: new Date(authorization.end_time)
  }
  showCreateDialog.value = true
}

// 删除授权
const deleteAuthorization = (id: string) => {
  ElMessageBox.confirm(
    '确定要删除这个授权吗？删除后将无法恢复。',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      loading.value = true
      try {
        await apiAuthApi.deleteAuthorization(id)
        ElMessage.success('删除授权成功')
        await loadAuthorizations()
      } catch (error: any) {
        const errorMessage = error.response?.data?.detail || '删除授权失败'
        ElMessage.error(errorMessage)
      } finally {
        loading.value = false
      }
    })
    .catch(() => {
      // 用户取消删除
    })
}

// 复制授权码
const copyAuthCode = (authCode: string) => {
  navigator.clipboard.writeText(authCode).then(() => {
    ElMessage.success('授权码已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败，请手动复制')
  })
}

// 重置表单
const resetForm = () => {
  currentAuthorizationId.value = ''
  formData.value = {
    vendor_name: '',
    vendor_contact: '',
    contact_phone: '',
    authorized_ips: '',
    knowledge_base_ids: [],
    start_time: new Date(),
    end_time: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
  }
  dialogTitle.value = '创建授权'
}

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 判断授权是否有效
const isAuthorizationValid = (authorization: any) => {
  // 首先检查is_active状态
  if (!authorization.is_active) {
    return false
  }
  
  // 然后检查有效期
  const now = new Date()
  const startTime = new Date(authorization.start_time)
  const endTime = new Date(authorization.end_time)
  
  return now >= startTime && now <= endTime
}

// 分页处理
const handleSizeChange = (size: number) => {
  pagination.value.pageSize = size
  loadAuthorizations()
}

const handleCurrentChange = (current: number) => {
  pagination.value.currentPage = current
  loadAuthorizations()
}

// 初始化
onMounted(async () => {
  await Promise.all([
    loadKnowledgeBases(),
    loadAuthorizations()
  ])
})
</script>

<style scoped>
.api-auth-container {
  padding: 20px 0;
}

.api-auth-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.api-auth-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.api-auth-list {
  margin-bottom: 20px;
}

.api-auth-pagination {
  display: flex;
  justify-content: flex-end;
}

.auth-code {
  cursor: pointer;
  color: #409EFF;
  text-decoration: underline;
}

.kb-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .api-auth-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
