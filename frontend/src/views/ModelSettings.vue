<template>
  <div class="model-settings-container">
    <h2>{{ getPageTitle() }}</h2>
    
    <!-- 模型管理界面 -->
    <div class="model-actions">
      <el-button type="primary" @click="showAddModelDialog(currentModelType)">
        <el-icon><Plus /></el-icon>
        {{ getAddButtonText() }}
      </el-button>
    </div>
    <el-table :data="filteredModels" style="width: 100%" border>
      <el-table-column type="index" label="序号" width="80" />
      <el-table-column prop="name" :label="currentModelType === 'embedding' ? '模型标识' : '模型名称'" width="180" />
      <el-table-column prop="model" :label="currentModelType === 'embedding' ? '模型名称' : '模型标识'" />
      <el-table-column prop="vendorName" label="模型厂商" width="150" />
      <el-table-column prop="apiKey" label="API Key" width="150">
        <template #default="scope">
          {{ scope.row.apiKey ? '已设置' : '未设置' }}
        </template>
      </el-table-column>
      <el-table-column prop="baseUrl" label="基础 URL" width="200" />
      <!-- 只在聊天模型列表中显示参数列 -->
      <template v-if="currentModelType === 'chat'">
        <el-table-column label="Top K" width="100">
          <template #default="scope">
            {{ scope.row.topK || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="温度" width="100">
          <template #default="scope">
            {{ scope.row.temperature || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="Top P" width="100">
          <template #default="scope">
            {{ scope.row.topP || '-' }}
          </template>
        </el-table-column>
      </template>
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
    
    <!-- 添加/编辑模型对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
    >
      <el-form 
        :model="modelForm" 
        :rules="modelRules" 
        ref="modelFormRef" 
        label-width="80px"
        :inline="false"
        :label-position="'left'"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="模型标识" prop="name">
              <el-input v-model="modelForm.name" placeholder="请输入模型标识" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="模型名称" prop="model">
              <el-input v-model="modelForm.model" placeholder="请输入模型名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
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
          </el-col>
          <el-col :span="12">
            <el-form-item label="API Key" prop="apiKey">
              <el-input v-model="modelForm.apiKey" placeholder="请输入 API Key" type="password" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="基础 URL" prop="baseUrl">
              <el-input v-model="modelForm.baseUrl" placeholder="请输入基础 URL" />
            </el-form-item>
          </el-col>
          <!-- 只在聊天模型界面显示参数设置 -->
          <template v-if="modelForm.type === 'chat'">
            <el-col :span="12">
              <el-form-item label="Top K">
                <el-input-number v-model="modelForm.topK" :min="1" :max="50" :step="1" placeholder="请输入Top K值" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="温度">
                <el-input-number v-model="modelForm.temperature" :min="0" :max="2" :step="0.1" placeholder="请输入温度值" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Top P">
                <el-input-number v-model="modelForm.topP" :min="0" :max="1" :step="0.1" placeholder="请输入Top P值" />
              </el-form-item>
            </el-col>
          </template>
          <el-col :span="24">
            <el-form-item label="描述">
              <el-input v-model="modelForm.description" placeholder="请输入模型描述" type="textarea" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-switch v-model="modelForm.isActive" active-text="" inactive-text="" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="默认">
              <el-switch v-model="modelForm.isDefault" active-text="" inactive-text="" />
            </el-form-item>
          </el-col>
        </el-row>
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
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useRoute } from 'vue-router'
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
  topK?: number
  temperature?: number
  topP?: number
  createdAt?: string
  updatedAt?: string
}

// 模型类型
const ModelType = {
  EMBEDDING: 'embedding' as const,
  CHAT: 'chat' as const,
  RERANK: 'rerank' as const
}

// 路由
const route = useRoute()

// 响应式数据
const currentModelType = ref<'embedding' | 'chat' | 'rerank'>('embedding')
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
  isDefault: false,
  topK: 5,
  temperature: 0.7,
  topP: 0.9
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
  return models.value.filter(model => model.type === currentModelType.value)
})

// 获取页面标题
const getPageTitle = () => {
  const typeMap = {
    embedding: 'Embedding 模型管理',
    chat: '聊天模型管理',
    rerank: 'Rerank 模型管理'
  }
  return typeMap[currentModelType.value]
}

// 获取添加按钮文本
const getAddButtonText = () => {
  const typeMap = {
    embedding: '添加 Embedding 模型',
    chat: '添加聊天模型',
    rerank: '添加 Rerank 模型'
  }
  return typeMap[currentModelType.value]
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
    
    // 只在聊天模型中添加参数设置
    if (modelForm.value.type === 'chat') {
      modelData.topK = modelForm.value.topK || 5
      modelData.temperature = modelForm.value.temperature || 0.7
      modelData.topP = modelForm.value.topP || 0.9
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
    
    // 只在聊天模型中添加参数设置
    if (modelForm.value.type === 'chat') {
      modelData.topK = modelForm.value.topK
      modelData.temperature = modelForm.value.temperature
      modelData.topP = modelForm.value.topP
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
      type: currentModelType.value,
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

// 监听路由参数变化
watch(
  () => route.query.type,
  async (newType) => {
    if (newType && ['embedding', 'chat', 'rerank'].includes(newType as string)) {
      currentModelType.value = newType as 'embedding' | 'chat' | 'rerank'
      await loadModels()
    }
  }
)

// 初始化
onMounted(async () => {
  // 从URL查询参数中获取模型类型
  const typeParam = route.query.type as string
  if (typeParam && ['embedding', 'chat', 'rerank'].includes(typeParam)) {
    currentModelType.value = typeParam as 'embedding' | 'chat' | 'rerank'
  }
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