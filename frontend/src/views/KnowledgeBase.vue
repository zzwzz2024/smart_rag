<template>
  <div class="kb-container">
    <div class="kb-header">
      <h2>知识库管理</h2>
      <button class="btn btn-primary" @click="showCreateModal = true">
        创建知识库
      </button>
    </div>

    <!-- 创建知识库模态框 -->
    <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
      <div class="modal-content" @click.stop>
        <h3>创建知识库</h3>
        <form @submit.prevent="createKnowledgeBase">
          <div class="form-group">
            <label for="kb-name">知识库名称</label>
            <input
              type="text"
              id="kb-name"
              v-model="newKbName"
              required
              placeholder="请输入知识库名称"
            />
          </div>
          <div class="form-group">
            <label for="kb-description">知识库描述</label>
            <textarea
              id="kb-description"
              v-model="newKbDescription"
              rows="3"
              placeholder="请输入知识库描述"
            ></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="showCreateModal = false">
              取消
            </button>
            <button type="submit" class="btn btn-primary" :disabled="kbStore.isLoading">
              {{ kbStore.isLoading ? '创建中...' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 知识库列表 -->
    <div class="kb-list">
      <div
        v-for="kb in kbStore.knowledgeBases"
        :key="kb.id"
        class="kb-card"
      >
        <div class="kb-card-header">
          <h3>{{ kb.name }}</h3>
          <div class="kb-card-actions">
            <button
              class="btn btn-secondary"
              @click="editKnowledgeBase(kb)"
            >
              编辑
            </button>
            <button
              class="btn btn-danger"
              @click="confirmDeleteKnowledgeBase(kb.id)"
            >
              删除
            </button>
          </div>
        </div>
        <div class="kb-card-body">
          <p class="kb-description">{{ kb.description }}</p>
          <div class="kb-stats">
            <span class="kb-stat-item">
              📄 {{ kb.document_count }} 个文档
            </span>
            <span class="kb-stat-item">
              📅 {{ formatTime(kb.created_at) }}
            </span>
          </div>
        </div>
        <div class="kb-card-footer">
          <router-link :to="`/documents?kbId=${kb.id}`" class="btn btn-primary">
            管理文档
          </router-link>
        </div>
      </div>
      <div v-if="kbStore.knowledgeBases.length === 0" class="empty-state">
        <p>还没有创建知识库</p>
        <p>点击上方"创建知识库"按钮开始创建</p>
      </div>
      <div v-if="kbStore.isLoading" class="loading-state">
        <div class="loading"></div>
        <span>加载中...</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useKbStore } from '../stores/kb'
import { ElMessageBox, ElMessage } from 'element-plus'
import type { KnowledgeBase } from '../types'

const kbStore = useKbStore()

// 创建知识库表单
const showCreateModal = ref(false)
const newKbName = ref('')
const newKbDescription = ref('')

// 编辑知识库
const editKnowledgeBase = (kb: KnowledgeBase) => {
  // 这里可以实现编辑功能，例如打开编辑模态框
  console.log('编辑知识库:', kb)
}

// 确认删除知识库
const confirmDeleteKnowledgeBase = (kbId: number) => {
  ElMessageBox.confirm(
    '确定要删除这个知识库吗？删除后将无法恢复。',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(() => {
      kbStore.deleteKnowledgeBase(kbId)
    })
    .catch(() => {
      // 用户取消删除
    })
}

// 创建知识库
const createKnowledgeBase = async () => {
  if (!newKbName.value.trim()) return

  try {
    await kbStore.createKnowledgeBase(newKbName.value.trim(), newKbDescription.value.trim())
    showCreateModal.value = false
    newKbName.value = ''
    newKbDescription.value = ''
    ElMessage.success('创建知识库成功')
  } catch (error: any) {
    ElMessage.error('创建知识库失败: ' + (error.message || '未知错误'))
  }
}

// 格式化时间
const formatTime = (timeString: string): string => {
  const date = new Date(timeString)
  return date.toLocaleString('zh-CN')
}

// 加载知识库列表
onMounted(async () => {
  try {
    await kbStore.getKnowledgeBases()
  } catch (error) {
    console.error('加载知识库列表失败:', error)
  }
})
</script>

<style scoped>
.kb-container {
  padding: 20px 0;
}

.kb-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.kb-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

/* 模态框样式 */
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
  max-width: 500px;
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

/* 知识库列表样式 */
.kb-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.kb-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
  transition: all 0.2s ease;
}

.kb-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.kb-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.kb-card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  flex: 1;
}

.kb-card-actions {
  display: flex;
  gap: 8px;
}

.kb-card-body {
  margin-bottom: 20px;
}

.kb-description {
  font-size: 14px;
  line-height: 1.5;
  color: #666;
  margin-bottom: 16px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.kb-stats {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #999;
}

.kb-stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.kb-card-footer {
  display: flex;
  justify-content: flex-end;
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
  .kb-list {
    grid-template-columns: 1fr;
  }

  .kb-header {
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