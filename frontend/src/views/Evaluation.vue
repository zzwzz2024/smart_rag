<template>
  <div class="evaluation-container">
    <div class="evaluation-header">
      <div class="header-left">
        <h2>知识库评估</h2>
        <div class="filter-controls">
          <div class="filter-container">
            <label for="kb-filter">按知识库过滤:</label>
            <select 
              id="kb-filter" 
              v-model="selectedFilterKb" 
              class="form-control filter-select"
            >
              <option value="">全部知识库</option>
              <option 
                v-for="kb in kbStore.knowledgeBases" 
                :key="kb.id" 
                :value="kb.id"
              >
                {{ kb.name }}
              </option>
            </select>
          </div>
          <div class="filter-container">
            <label for="query-filter">按问题名称过滤:</label>
            <input 
              type="text" 
              id="query-filter" 
              v-model="queryFilter" 
              class="form-control filter-input"
              placeholder="输入问题关键词"
            >
          </div>
          <div class="filter-actions">
            <el-button type="primary" @click="filterEvaluations">
              <el-icon><Search /></el-icon>
              <span>查询</span>
            </el-button>
            <el-button @click="resetFilters">
              <el-icon><Refresh /></el-icon>
              <span>重置</span>
            </el-button>
          </div>
        </div>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showCreateModal = true">
          <el-icon><Plus /></el-icon>
          <span>创建评估</span>
        </el-button>
      </div>
    </div>

    <!-- 创建评估模态框 -->
    <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
      <div class="modal-content" @click.stop>
        <h3>创建评估</h3>
        <form @submit.prevent="createEvaluation">
          <div class="form-group">
            <label for="eval-query">测试问题</label>
            <input
              type="text"
              id="eval-query"
              v-model="newEvalQuery"
              required
              placeholder="请输入测试问题"
            />
          </div>
          <div class="form-group">
            <label for="eval-reference">参考答案</label>
            <textarea
              id="eval-reference"
              v-model="newEvalReference"
              rows="4"
              required
              placeholder="请输入参考答案"
            ></textarea>
          </div>
          <div class="form-group">
            <label for="eval-kb">选择知识库 <span style="color: red;">*</span></label>
            <select
              id="eval-kb"
              v-model="selectedKnowledgeBase"
              class="form-control"
              required
            >
              <option value="">请选择知识库</option>
              <option
                v-for="kb in kbStore.knowledgeBases"
                :key="kb.id"
                :value="kb.id"
              >
                {{ kb.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label for="eval-model">选择聊天模型 <span style="color: red;">*</span></label>
            <select
              id="eval-model"
              v-model="selectedModel"
              class="form-control"
              required
            >
              <option value="">请选择聊天模型</option>
              <option
                v-for="model in modelStore.chatModels"
                :key="model.id"
                :value="model.id"
              >
                {{ model.name }} ({{ model.vendorName }})
              </option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="showCreateModal = false">
              取消
            </button>
            <button type="submit" class="btn btn-primary" :disabled="isLoading">
              {{ isLoading ? '创建中...' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 编辑评估模态框 -->
    <div v-if="showEditModal" class="modal-overlay" @click="showEditModal = false">
      <div class="modal-content" @click.stop>
        <h3>编辑评估</h3>
        <form @submit.prevent="updateEvaluation">
          <div class="form-group">
            <label for="edit-eval-query">测试问题</label>
            <input
              type="text"
              id="edit-eval-query"
              v-model="editEvalQuery"
              required
              placeholder="请输入测试问题"
            />
          </div>
          <div class="form-group">
            <label for="edit-eval-reference">参考答案</label>
            <textarea
              id="edit-eval-reference"
              v-model="editEvalReference"
              rows="4"
              required
              placeholder="请输入参考答案"
            ></textarea>
          </div>
          <div class="form-group">
            <label for="edit-eval-kb">选择知识库 <span style="color: red;">*</span></label>
            <select
              id="edit-eval-kb"
              v-model="editSelectedKnowledgeBase"
              class="form-control"
              required
            >
              <option value="">请选择知识库</option>
              <option
                v-for="kb in kbStore.knowledgeBases"
                :key="kb.id"
                :value="kb.id"
              >
                {{ kb.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label for="edit-eval-model">选择聊天模型 <span style="color: red;">*</span></label>
            <select
              id="edit-eval-model"
              v-model="editSelectedModel"
              class="form-control"
              required
            >
              <option value="">请选择聊天模型</option>
              <option
                v-for="model in modelStore.chatModels"
                :key="model.id"
                :value="model.id"
              >
                {{ model.name }} ({{ model.vendorName }})
              </option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="showEditModal = false">
              取消
            </button>
            <button type="submit" class="btn btn-primary" :disabled="isLoading">
              {{ isLoading ? '重新评估中...' : '重新评估' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 评估列表 -->
    <div class="evaluation-list">
      <div
        v-for="evaluation in filteredEvaluations"
        :key="evaluation.id"
        class="evaluation-card"
      >
        <div class="evaluation-card-header">
          <h3>测试问题: {{ evaluation.query }}</h3>
          <div class="evaluation-score">
            <span class="score-label">评分:</span>
            <span class="score-value">{{ evaluation.score }}</span>
          </div>
        </div>
        <div class="evaluation-card-body">
          <div class="evaluation-item">
            <h4>参考答案:</h4>
            <p>{{ evaluation.reference_answer }}</p>
          </div>
          <div class="evaluation-item">
            <h4>AI 回答:</h4>
            <p>{{ evaluation.rag_answer }}</p>
          </div>
          <div class="evaluation-item">
            <h4>评估参数:</h4>
            <p>知识库: {{ getKnowledgeBaseName(evaluation.kb_id) }}</p>
            <p>模型: {{ getModelName(evaluation.model_id) }}</p>
          </div>
        </div>
        <div class="evaluation-card-footer">
          <span class="evaluation-time">{{ formatTime(evaluation.created_at) }}</span>
          <div class="evaluation-actions">
            <button class="btn btn-success btn-sm" @click="copyEvaluation(evaluation)">
              复制
            </button>
            <button class="btn btn-primary btn-sm" @click="editEvaluation(evaluation)">
              编辑
            </button>
            <button class="btn btn-danger btn-sm" @click="deleteEvaluation(evaluation.id)">
              删除
            </button>
          </div>
        </div>
      </div>
      <div v-if="filteredEvaluations.length === 0 && !isLoading" class="empty-state">
        <p>{{ selectedFilterKb ? '该知识库暂无评估记录' : '还没有创建评估' }}</p>
        <p>点击上方"创建评估"按钮开始创建</p>
      </div>
      <div v-if="isLoading" class="loading-state">
        <div class="loading"></div>
        <span>加载中...</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { evaluationApi } from '../api/evaluation'
import { useKbStore } from '../stores/kb'
import { useModelStore } from '../stores/model'
import { ElMessageBox, ElMessage, ElButton, ElIcon } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import type { Evaluation } from '../types'

const kbStore = useKbStore()
const modelStore = useModelStore()

const evaluations = ref<Evaluation[]>([])
const filteredEvaluations = ref<Evaluation[]>([])
const isLoading = ref(false)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const newEvalQuery = ref('')
const newEvalReference = ref('')
const selectedKnowledgeBase = ref<string>('')
const selectedModel = ref<string>('')
const selectedFilterKb = ref<string>('')
const queryFilter = ref('')
const editEvalQuery = ref('')
const editEvalReference = ref('')
const editSelectedKnowledgeBase = ref<string>('')
const editSelectedModel = ref<string>('')
const currentEditingEvaluation = ref<Evaluation | null>(null)

// 获取评估列表
const getEvaluations = async () => {
  isLoading.value = true
  try {
    // 构建查询参数
    const params: any = {}
    if (selectedFilterKb.value) {
      params.kb_id = selectedFilterKb.value
    }
    if (queryFilter.value) {
      params.query = queryFilter.value
    }
    const response = await evaluationApi.getEvaluations(params)
    evaluations.value = response.data || response
    filteredEvaluations.value = evaluations.value
  } catch (error: any) {
    // 提取详细错误信息
    const errorMessage = error.response?.data?.detail || '获取评估列表失败'
    ElMessage.error(errorMessage)
  } finally {
    isLoading.value = false
  }
}

// 过滤评估
const filterEvaluations = () => {
  // 重新从后端获取数据，使用过滤参数
  getEvaluations()
}

// 处理问题名称过滤
const handleQueryFilter = () => {
  // 使用防抖处理，避免频繁请求
  clearTimeout((window as any).queryFilterTimer)
  (window as any).queryFilterTimer = setTimeout(() => {
    getEvaluations()
  }, 300)
}

// 重置过滤条件
const resetFilters = () => {
  selectedFilterKb.value = ''
  queryFilter.value = ''
  getEvaluations()
}

// 创建评估
const createEvaluation = async () => {
  if (!newEvalQuery.value.trim() || !newEvalReference.value.trim() || !selectedKnowledgeBase.value || !selectedModel.value) {
    ElMessage.warning('请填写完整的评估信息')
    return
  }

  isLoading.value = true
  try {
    // 获取选中的知识库信息
    const selectedKB = kbStore.knowledgeBases.find(kb => kb.id === selectedKnowledgeBase.value)
    if (!selectedKB) {
      ElMessage.error('所选知识库不存在')
      return
    }
    
    // 获取选中的模型信息
    const selectedModelInfo = modelStore.chatModels.find(model => model.id === selectedModel.value)
    if (!selectedModelInfo) {
      ElMessage.error('所选模型不存在')
      return
    }
    
    console.log('Selected knowledge base:', selectedKB.name)
    console.log('Embedding model:', selectedKB.embedding_model_id)
    console.log('Rerank model:', selectedKB.rerank_model_id)
    console.log('Selected chat model:', selectedModelInfo.name)
    
    // 发送评估请求，包含知识库和模型信息
    const response = await evaluationApi.createEvaluation({
      query: newEvalQuery.value.trim(),
      reference_answer: newEvalReference.value.trim(),
      kb_ids: [selectedKnowledgeBase.value],
      model_id: selectedModel.value
    })
    const evaluation = response.data || response
    evaluations.value.push(evaluation)
    filterEvaluations()
    showCreateModal.value = false
    newEvalQuery.value = ''
    newEvalReference.value = ''
    selectedKnowledgeBase.value = ''
    selectedModel.value = ''
    ElMessage.success('创建评估成功')
  } catch (error: any) {
    // 提取详细错误信息
    const errorMessage = error.response?.data?.detail || '创建评估失败'
    ElMessage.error(errorMessage)
  } finally {
    isLoading.value = false
  }
}

// 编辑评估
const editEvaluation = (evaluation: Evaluation) => {
  currentEditingEvaluation.value = evaluation
  editEvalQuery.value = evaluation.query
  editEvalReference.value = evaluation.reference_answer
  // 预填充知识库和模型选择
  editSelectedKnowledgeBase.value = evaluation.kb_id
  editSelectedModel.value = evaluation.model_id
  showEditModal.value = true
}

// 复制评估方案
const copyEvaluation = (evaluation: Evaluation) => {
  // 预填充创建评估模态框的表单数据
  newEvalQuery.value = evaluation.query
  newEvalReference.value = evaluation.reference_answer
  selectedKnowledgeBase.value = evaluation.kb_id
  selectedModel.value = evaluation.model_id
  // 打开创建评估模态框
  showCreateModal.value = true
}

// 更新评估（重新评估）
const updateEvaluation = async () => {
  if (!editEvalQuery.value.trim() || !editEvalReference.value.trim() || !editSelectedKnowledgeBase.value || !editSelectedModel.value) {
    ElMessage.warning('请填写完整的评估信息')
    return
  }

  if (!currentEditingEvaluation.value) return

  isLoading.value = true
  try {
    // 获取选中的知识库信息
    const selectedKB = kbStore.knowledgeBases.find(kb => kb.id === editSelectedKnowledgeBase.value)
    if (!selectedKB) {
      ElMessage.error('所选知识库不存在')
      return
    }
    
    // 获取选中的模型信息
    const selectedModelInfo = modelStore.chatModels.find(model => model.id === editSelectedModel.value)
    if (!selectedModelInfo) {
      ElMessage.error('所选模型不存在')
      return
    }
    
    // 发送重新评估请求
    const response = await evaluationApi.updateEvaluation(currentEditingEvaluation.value.id, {
      query: editEvalQuery.value.trim(),
      reference_answer: editEvalReference.value.trim(),
      kb_ids: [editSelectedKnowledgeBase.value],
      model_id: editSelectedModel.value
    })
    const updatedEvaluation = response.data || response
    
    // 更新本地评估列表
    const index = evaluations.value.findIndex(evaluation => evaluation.id === currentEditingEvaluation.value?.id)
    if (index !== -1) {
      evaluations.value[index] = updatedEvaluation
    }
    
    filterEvaluations()
    showEditModal.value = false
    editEvalQuery.value = ''
    editEvalReference.value = ''
    editSelectedKnowledgeBase.value = ''
    editSelectedModel.value = ''
    currentEditingEvaluation.value = null
    ElMessage.success('重新评估成功')
  } catch (error: any) {
    // 提取详细错误信息
    const errorMessage = error.response?.data?.detail || '重新评估失败'
    ElMessage.error(errorMessage)
  } finally {
    isLoading.value = false
  }
}

// 删除评估
const deleteEvaluation = async (evalId: number) => {
  ElMessageBox.confirm(
    '确定要删除这个评估吗？删除后将无法恢复。',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        await evaluationApi.deleteEvaluation(evalId)
        evaluations.value = evaluations.value.filter(evaluation => evaluation.id !== evalId)
        filterEvaluations()
        ElMessage.success('删除评估成功')
      } catch (error: any) {
        // 提取详细错误信息
        const errorMessage = error.response?.data?.detail || '删除评估失败'
        ElMessage.error(errorMessage)
      }
    })
    .catch(() => {
      // 用户取消删除
    })
}

// 格式化时间
const formatTime = (timeString: string): string => {
  const date = new Date(timeString)
  return date.toLocaleString('zh-CN')
}

// 根据知识库ID获取名称
const getKnowledgeBaseName = (kbId: string): string => {
  const kb = kbStore.knowledgeBases.find(kb => kb.id === kbId)
  return kb ? kb.name : '未知知识库'
}

// 根据模型ID获取名称
const getModelName = (modelId: string): string => {
  const model = modelStore.chatModels.find(model => model.id === modelId)
  return model ? `${model.name} (${model.vendorName})` : '未知模型'
}

// 加载评估列表
onMounted(async () => {
  try {
    // 加载评估列表
    await getEvaluations()
    // 加载知识库列表
    await kbStore.getKnowledgeBases()
    // 加载模型列表
    await modelStore.getModels()
  } catch (error: any) {
    ElMessage.error('加载数据失败: ' + (error.message || '未知错误'))
  }
})

// 监听路由变化，检测 _refresh 参数触发重载
const route = useRoute()
watch(
  () => route.query._refresh,  // 直接监听 _refresh 查询参数
  async (newValue) => {
    if (newValue) {
      console.log('检测到 _refresh，重新加载授权列表和知识库...')
      await Promise.all([
        getEvaluations(),
        kbStore.getKnowledgeBases(),
        modelStore.getModels()
      ])
      // 可选：清除 _refresh 避免重复触发
      router.replace({ query: { ...route.query, _refresh: undefined } })
    }
  },
  { immediate: false }
)
</script>

<style scoped>
.evaluation-container {
  padding: 20px 0;
}

.evaluation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.evaluation-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

/* 创建评估模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  padding: 30px;
  width: 100%;
  max-width: 600px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-content h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

/* 表单控件样式 */
.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  margin-top: 4px;
  transition: border-color 0.2s ease;
}

.form-control:focus {
  border-color: #4CAF50;
  outline: none;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

/* 评估列表样式 */
.evaluation-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

/* 确保评估容器可以扩展并滚动 */
.evaluation-container {
  width: 100%;
  min-height: 100%;
}

/* 评估头部样式 */
.evaluation-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 20px;
}

.header-left {
  flex: 1;
  min-width: 300px;
}

.header-right {
  display: flex;
  align-items: flex-start;
}

.filter-controls {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
  margin-top: 10px;
}

.filter-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-select {
  width: 200px;
  margin-top: 0;
}

.filter-input {
  width: 250px;
  margin-top: 0;
}

.filter-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-top: 2px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .evaluation-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-left,
  .header-right {
    width: 100%;
  }
  
  .filter-controls {
    width: 100%;
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .filter-container {
    flex-direction: column;
    align-items: flex-start;
    width: 100%;
  }
  
  .filter-select {
    width: 100%;
  }
  
  .filter-input {
    width: 100%;
  }
  
  .filter-actions {
    width: 100%;
    justify-content: flex-start;
    margin-top: 10px;
  }
}

.evaluation-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
  transition: all 0.2s ease;
}

.evaluation-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.evaluation-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.evaluation-card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  flex: 1;
}

.evaluation-score {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #f5f5f5;
  padding: 6px 12px;
  border-radius: 16px;
}

.score-label {
  font-size: 14px;
  color: #666;
}

.score-value {
  font-size: 16px;
  font-weight: 600;
  color: #4CAF50;
}

.evaluation-card-body {
  margin-bottom: 16px;
}

.evaluation-item {
  margin-bottom: 16px;
}

.evaluation-item h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #666;
}

.evaluation-item p {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
  color: #333;
  word-break: break-word;
  max-height: 120px;
  overflow-y: auto;
  padding-right: 4px;
}

.evaluation-item p::-webkit-scrollbar {
  width: 4px;
}

.evaluation-item p::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 2px;
}

.evaluation-item p::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.evaluation-item p::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

.evaluation-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

.evaluation-time {
  font-size: 12px;
  color: #999;
}

.evaluation-actions {
  display: flex;
  gap: 8px;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 12px;
}

/* 空状态和加载状态 */
.empty-state,
.loading-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 60px 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.empty-state p {
  margin: 8px 0;
  color: #666;
}

.loading-state {
  gap: 16px;
}

.loading-state span {
  color: #666;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .evaluation-list {
    grid-template-columns: 1fr;
  }

  .evaluation-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .modal-content {
    padding: 20px;
    margin: 20px;
  }
}
</style>