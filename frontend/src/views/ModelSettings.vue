<template>
  <div class="model-settings-container">
    <h2>模型管理</h2>
    
    <!-- 模型类型切换 -->
    <div class="model-type-tabs">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="Embedding 模型" name="embedding">
          <div class="model-actions">
            <el-button type="primary" @click="showAddModelDialog('embedding')">
              <el-icon><Plus /></el-icon>
              添加 Embedding 模型
            </el-button>
          </div>
          <el-table :data="filteredModels" style="width: 100%" border>
            <el-table-column prop="name" label="模型标识" width="180" />
            <el-table-column prop="model" label="模型名称" />
            <el-table-column prop="vendorName" label="模型厂商" width="150" />
            <el-table-column prop="apiKey" label="API Key" width="150">
              <template #default="scope">
                {{ scope.row.apiKey ? '已设置' : '未设置' }}
              </template>
            </el-table-column>
            <el-table-column prop="baseUrl" label="基础 URL" width="200" />
            <el-table-column label="状态" width="120">
              <template #default="scope">
                <el-switch
                  v-model="scope.row.isActive"
                  active-text=""
                  inactive-text=""
                  @change="handleStatusChange(scope.row)"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="showEditModelDialog(scope.row)">
                  编辑
                </el-button>
                <el-button 
                  size="small" 
                  type="primary" 
                  :disabled="scope.row.isDefault"
                  @click="setDefaultModel(scope.row.id)"
                >
                  {{ scope.row.isDefault ? '默认模型' : '设为默认' }}
                </el-button>
                <el-button size="small" type="danger" @click="confirmDeleteModel(scope.row.id)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="聊天模型" name="chat">
          <div class="model-actions">
            <el-button type="primary" @click="showAddModelDialog('chat')">
              <el-icon><Plus /></el-icon>
              添加聊天模型
            </el-button>
          </div>
          <el-table :data="filteredModels" style="width: 100%" border>
            <el-table-column prop="name" label="模型名称" width="180" />
            <el-table-column prop="model" label="模型标识" />
            <el-table-column prop="vendorName" label="模型厂商" width="150" />
            <el-table-column prop="apiKey" label="API Key" width="160">
              <template #default="scope">
                {{ scope.row.apiKey ? '已设置' : '未设置' }}
              </template>
            </el-table-column>
            <el-table-column prop="baseUrl" label="基础 URL" width="200" />
            <el-table-column label="状态" width="120">
              <template #default="scope">
                <el-switch
                  v-model="scope.row.isActive"
                  active-text=""
                  inactive-text=""
                  @change="handleStatusChange(scope.row)"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="240" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="showEditModelDialog(scope.row)">
                  编辑
                </el-button>
                <el-button 
                  size="small" 
                  type="primary" 
                  :disabled="scope.row.isDefault"
                  @click="setDefaultModel(scope.row.id)"
                >
                  {{ scope.row.isDefault ? '默认模型' : '设为默认' }}
                </el-button>
                <el-button size="small" type="danger" @click="confirmDeleteModel(scope.row.id)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="Rerank 模型" name="rerank">
          <div class="model-actions">
            <el-button type="primary" @click="showAddModelDialog('rerank')">
              <el-icon><Plus /></el-icon>
              添加 Rerank 模型
            </el-button>
          </div>
          <el-table :data="filteredModels" style="width: 100%" border>
            <el-table-column prop="name" label="模型名称" width="180" />
            <el-table-column prop="model" label="模型标识" />
            <el-table-column prop="vendorName" label="模型厂商" width="150" />
            <el-table-column prop="apiKey" label="API Key" width="200">
              <template #default="scope">
                {{ scope.row.apiKey ? '已设置' : '未设置' }}
              </template>
            </el-table-column>
            <el-table-column prop="baseUrl" label="基础 URL" width="200" />
            <el-table-column label="状态" width="120">
              <template #default="scope">
                <el-switch
                  v-model="scope.row.isActive"
                  active-text="启用"
                  inactive-text="停用"
                  @change="handleStatusChange(scope.row)"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="showEditModelDialog(scope.row)">
                  编辑
                </el-button>
                <el-button 
                  size="small" 
                  type="primary" 
                  :disabled="scope.row.isDefault"
                  @click="setDefaultModel(scope.row.id)"
                >
                  {{ scope.row.isDefault ? '默认模型' : '设为默认' }}
                </el-button>
                <el-button size="small" type="danger" @click="confirmDeleteModel(scope.row.id)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </div>
    
    <!-- 添加/编辑模型对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
    >
      <el-form :model="modelForm" :rules="modelRules" ref="modelFormRef" label-width="100px">
        <el-form-item label="模型标识" prop="name">
          <el-input v-model="modelForm.name" placeholder="请输入模型标识" />
        </el-form-item>
        <el-form-item label="模型名称" prop="model">
          <el-input v-model="modelForm.model" placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item label="模型厂商">
          <el-select v-model="modelForm.vendorId" placeholder="请选择模型厂商" style="width: 100%">
            <el-option
              v-for="vendor in vendors"
              :key="vendor.id"
              :label="vendor.name"
              :value="vendor.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="API Key" prop="apiKey">
          <el-input v-model="modelForm.apiKey" placeholder="请输入 API Key" type="password" />
        </el-form-item>
        <el-form-item label="基础 URL" prop="baseUrl">
          <el-input v-model="modelForm.baseUrl" placeholder="请输入基础 URL" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="modelForm.description" placeholder="请输入模型描述" type="textarea" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="modelForm.isActive" active-text="" inactive-text="" />
        </el-form-item>
        <el-form-item label="默认">
          <el-switch v-model="modelForm.isDefault" active-text="" inactive-text="" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveModel">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import modelApi, { ModelCreate, ModelUpdate, ModelResponse } from '../api/model'

// 模型厂商类型定义
interface ModelVendor {
  id: string
  name: string
  description?: string
}

// 模型类型定义
interface Model extends ModelResponse {
  vendorId?: string
  vendorName?: string
  isActive?: boolean
  isDefault?: boolean
  createdAt?: string
  updatedAt?: string
}

// 模型类型
const ModelType = {
  EMBEDDING: 'embedding' as const,
  CHAT: 'chat' as const,
  RERANK: 'rerank' as const
}

// 响应式数据
const activeTab = ref<'embedding' | 'chat' | 'rerank'>('embedding')
const dialogVisible = ref(false)
const dialogTitle = ref('')
const modelForm = ref<Partial<Model>>({
  type: 'embedding',
  name: '',
  model: '',
  vendorId: '',
  apiKey: '',
  baseUrl: '',
  description: '',
  isActive: true,
  isDefault: false
})
const modelFormRef = ref()
const models = ref<Model[]>([])
const vendors = ref<ModelVendor[]>([])

// 表单验证规则
const modelRules = {
  name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' }
  ],
  model: [
    { required: true, message: '请输入模型标识', trigger: 'blur' }
  ]
}

// 过滤当前类型的模型
const filteredModels = computed(() => {
  return models.value.filter(model => model.type === activeTab.value)
})

// 处理标签页切换
const handleTabChange = (tab: string) => {
  activeTab.value = tab as 'embedding' | 'chat' | 'rerank'
  modelForm.value.type = activeTab.value
  loadModels()
}

// 显示添加模型对话框
const showAddModelDialog = (type: 'embedding' | 'chat' | 'rerank') => {
  modelForm.value = {
    type,
    name: '',
    model: '',
    vendorId: '',
    apiKey: '',
    baseUrl: '',
    description: '',
    isActive: true,
    isDefault: false
  }
  dialogTitle.value = `添加 ${getModelTypeName(type)}`
  dialogVisible.value = true
}

// 显示编辑模型对话框
const showEditModelDialog = (model: Model) => {
  modelForm.value = { ...model }
  dialogTitle.value = `编辑 ${model.name}`
  dialogVisible.value = true
}

// 确认删除模型
const confirmDeleteModel = (modelId: string) => {
  ElMessageBox.confirm(
    '确定要删除这个模型吗？',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 调用删除模型API
    deleteModel(modelId)
  }).catch(() => {
    // 取消删除
  })
}

// 删除模型
const deleteModel = async (modelId: string) => {
  try {
    await modelApi.deleteModel(modelId)
    models.value = models.value.filter(model => model.id !== modelId)
    ElMessage.success('模型删除成功')
  } catch (error: any) {
    console.error('删除模型失败:', error)
    // 提取详细错误信息
    const errorMessage = error.response?.data?.detail || '删除模型失败'
    ElMessage.error(errorMessage)
  }
}

// 保存模型
const saveModel = async () => {
  if (!modelFormRef.value) return
  
  await modelFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      if (modelForm.value.id) {
        // 编辑现有模型
        updateModel()
      } else {
        // 添加新模型
        createModel()
      }
    }
  })
}

// 创建模型
const createModel = async () => {
  try {
    const modelData: any = {
      type: modelForm.value.type as 'embedding' | 'chat' | 'rerank',
      name: modelForm.value.name || '',
      model: modelForm.value.model || '',
      vendorId: modelForm.value.vendorId,
      apiKey: modelForm.value.apiKey,
      baseUrl: modelForm.value.baseUrl,
      description: modelForm.value.description,
      isActive: modelForm.value.isActive !== false,
      isDefault: modelForm.value.isDefault === true
    }
    
    const response = await modelApi.createModel(modelData)
    models.value.push(response)
    ElMessage.success('模型添加成功')
    dialogVisible.value = false
  } catch (error: any) {
    console.error('创建模型失败:', error)
    // 提取详细错误信息
    const errorMessage = error.response?.data?.detail || '创建模型失败'
    ElMessage.error(errorMessage)
  }
}

// 更新模型
const updateModel = async () => {
  if (!modelForm.value.id) return
  
  try {
    const modelData: any = {
      name: modelForm.value.name,
      model: modelForm.value.model,
      vendorId: modelForm.value.vendorId,
      apiKey: modelForm.value.apiKey,
      baseUrl: modelForm.value.baseUrl,
      description: modelForm.value.description,
      isActive: modelForm.value.isActive,
      isDefault: modelForm.value.isDefault
    }
    
    const response = await modelApi.updateModel(modelForm.value.id, modelData)
    const index = models.value.findIndex(model => model.id === response.id)
    if (index !== -1) {
      models.value[index] = response
    }
    ElMessage.success('模型更新成功')
    dialogVisible.value = false
  } catch (error: any) {
    console.error('更新模型失败:', error)
    // 提取详细错误信息
    const errorMessage = error.response?.data?.detail || '更新模型失败'
    ElMessage.error(errorMessage)
  }
}

// 获取模型类型名称
const getModelTypeName = (type: 'embedding' | 'chat' | 'rerank') => {
  const typeNames = {
    embedding: 'Embedding 模型',
    chat: '聊天模型',
    rerank: 'Rerank 模型'
  }
  return typeNames[type]
}

// 加载模型厂商列表
const loadVendors = async () => {
  try {
    const response = await modelApi.getVendors()
    vendors.value = response.items
  } catch (error) {
    console.error('获取模型厂商列表失败:', error)
    ElMessage.error('获取模型厂商列表失败')
  }
}

// 加载模型列表
const loadModels = async () => {
  try {
    const response = await modelApi.getModels({
      type: activeTab.value,
      page: 1,
      page_size: 100 // 加载足够多的模型
    })
    models.value = response.items
  } catch (error) {
    console.error('获取模型列表失败:', error)
    ElMessage.error('获取模型列表失败')
  }
}

// 处理模型状态变更
const handleStatusChange = async (model: Model) => {
  try {
    await modelApi.updateModel(model.id, {
      isActive: model.isActive
    })
    ElMessage.success('模型状态更新成功')
  } catch (error) {
    console.error('更新模型状态失败:', error)
    ElMessage.error('更新模型状态失败')
    // 恢复原状态
    model.isActive = !model.isActive
  }
}

// 设置模型为默认
const setDefaultModel = async (modelId: string) => {
  try {
    await modelApi.setDefaultModel(modelId)
    ElMessage.success('模型已设置为默认')
    // 重新加载模型列表以更新默认状态
    await loadModels()
  } catch (error) {
    console.error('设置默认模型失败:', error)
    ElMessage.error('设置默认模型失败')
  }
}

// 初始化
onMounted(async () => {
  await loadVendors()
  await loadModels()
})
</script>

<style scoped>
.model-settings-container {
  padding: 20px 0;
}

.model-settings-container h2 {
  margin-bottom: 24px;
  font-size: 20px;
  font-weight: 600;
}

.model-type-tabs {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.model-actions {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-start;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .model-settings-container {
    padding: 10px 0;
  }
  
  .model-type-tabs {
    padding: 16px;
  }
  
  .model-actions {
    justify-content: center;
  }
}
</style>