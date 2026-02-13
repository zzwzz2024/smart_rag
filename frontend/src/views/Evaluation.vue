<template>
  <div class="evaluation-container">
    <div class="evaluation-header">
      <h2>系统评估</h2>
      <button class="btn btn-primary" @click="showCreateModal = true">
        创建评估
      </button>
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
            <label for="eval-kb">选择知识库</label>
            <select
              id="eval-kb"
              v-model="selectedKnowledgeBase"
              class="form-control"
            >
              <option value="">选择知识库（可选）</option>
              <option
                v-for="kb in kbStore.knowledgeBases"
                :key="kb.id"
                :value="kb.id"
              >
                {{ kb.name }}
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

    <!-- 评估列表 -->
    <div class="evaluation-list">
      <div
        v-for="evaluation in evaluations"
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
        </div>
        <div class="evaluation-card-footer">
          <span class="evaluation-time">{{ formatTime(evaluation.created_at) }}</span>
          <button class="btn btn-danger" @click="deleteEvaluation(evaluation.id)">
            删除
          </button>
        </div>
      </div>
      <div v-if="evaluations.length === 0 && !isLoading" class="empty-state">
        <p>还没有创建评估</p>
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
import { ref, onMounted } from 'vue'
import { evaluationApi } from '../api/evaluation'
import { useKbStore } from '../stores/kb'
import { ElMessageBox, ElMessage } from 'element-plus'
import type { Evaluation } from '../types'

const kbStore = useKbStore()

const evaluations = ref<Evaluation[]>([])
const isLoading = ref(false)
const showCreateModal = ref(false)
const newEvalQuery = ref('')
const newEvalReference = ref('')
const selectedKnowledgeBase = ref<string>('')

// 获取评估列表
const getEvaluations = async () => {
  isLoading.value = true
  try {
    const response = await evaluationApi.getEvaluations()
    evaluations.value = response.data || response
  } catch (error: any) {
    ElMessage.error('获取评估列表失败: ' + (error.message || '未知错误'))
  } finally {
    isLoading.value = false
  }
}

// 创建评估
const createEvaluation = async () => {
  if (!newEvalQuery.value.trim() || !newEvalReference.value.trim()) return

  isLoading.value = true
  try {
    const response = await evaluationApi.createEvaluation({
      query: newEvalQuery.value.trim(),
      reference_answer: newEvalReference.value.trim(),
      kb_ids: selectedKnowledgeBase.value ? [selectedKnowledgeBase.value] : []
    })
    const evaluation = response.data || response
    evaluations.value.push(evaluation)
    showCreateModal.value = false
    newEvalQuery.value = ''
    newEvalReference.value = ''
    selectedKnowledgeBase.value = ''
    ElMessage.success('创建评估成功')
  } catch (error: any) {
    ElMessage.error('创建评估失败: ' + (error.message || '未知错误'))
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
        ElMessage.success('删除评估成功')
      } catch (error: any) {
        ElMessage.error('删除评估失败: ' + (error.message || '未知错误'))
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

// 加载评估列表
onMounted(async () => {
  try {
    // 加载评估列表
    await getEvaluations()
    // 加载知识库列表
    await kbStore.getKnowledgeBases()
  } catch (error: any) {
    ElMessage.error('加载数据失败: ' + (error.message || '未知错误'))
  }
})
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