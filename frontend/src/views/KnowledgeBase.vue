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
          <div class="form-group">
            <label for="kb-embedding-model">Embedding模型</label>
            <select
              id="kb-embedding-model"
              v-model="newKbEmbeddingModelId"
              class="form-control"
            >
              <option
                v-for="model in modelStore.embeddingModels"
                :key="model.id"
                :value="model.id"
              >
                {{ model.name }} ({{ model.vendorName }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <label for="kb-rerank-model">Rerank模型</label>
            <select
              id="kb-rerank-model"
              v-model="newKbRerankModelId"
              class="form-control"
            >
              <option
                v-for="model in modelStore.rerankModels"
                :key="model.id"
                :value="model.id"
              >
                {{ model.name }} ({{ model.vendorName }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <label for="kb-chunk-method">分块方式 (chunk_method)</label>
            <select
              id="kb-chunk-method"
              v-model="newKbChunkMethod"
              class="form-control"
            >
              <option value="smart">智能分块</option>
              <option value="line">按行分块</option>
              <option value="paragraph">按段落分块</option>
              <option value="hierarchical">父子分块</option>
            </select>
          </div>
          <div class="form-group">
            <label for="kb-chunk-size">分块大小 (chunk_size)</label>
            <input
              type="number"
              id="kb-chunk-size"
              v-model.number="newKbChunkSize"
              class="form-control"
              min="100"
              max="2048"
              placeholder="请输入分块大小"
            />
          </div>
          <div class="form-group">
            <label for="kb-chunk-overlap">分块重叠 (chunk_overlap)</label>
            <input
              type="number"
              id="kb-chunk-overlap"
              v-model.number="newKbChunkOverlap"
              class="form-control"
              min="0"
              max="512"
              placeholder="请输入分块重叠"
            />
          </div>
          <div class="form-group">
            <label>标签</label>
            <div class="tag-selector">
              <el-checkbox-group v-model="newKbTagIds">
                <el-checkbox
                  v-for="tag in tagStore.tags"
                  :key="tag.id"
                  :label="tag.id"
                  :disabled="!tag.is_active"
                >
                  <span :style="{ color: tag.color }"> {{ tag.name }}</span>
                </el-checkbox>
              </el-checkbox-group>
            </div>
          </div>
          <div class="form-group">
            <label>领域</label>
            <div class="domain-selector">
              <el-checkbox-group v-model="newKbDomainIds">
                <el-checkbox
                  v-for="domain in domainStore.domains"
                  :key="domain.id"
                  :label="domain.id"
                  :disabled="!domain.is_active"
                >
                  {{ domain.name }}
                </el-checkbox>
              </el-checkbox-group>
            </div>
          </div>
        </form>
        <div class="modal-actions">
          <button type="button" class="btn btn-secondary" @click="showCreateModal = false">
            取消
          </button>
          <button type="button" class="btn btn-primary" @click="createKnowledgeBase" :disabled="kbStore.isLoading">
            {{ kbStore.isLoading ? '创建中...' : '创建' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑知识库模态框 -->
    <div v-if="showEditModal" class="modal-overlay" @click="showEditModal = false">
      <div class="modal-content" @click.stop>
        <h3>编辑知识库</h3>
        <form @submit.prevent="updateKnowledgeBase">
          <div class="form-group">
            <label for="edit-kb-name">知识库名称</label>
            <input
              type="text"
              id="edit-kb-name"
              v-model="editKbName"
              required
              placeholder="请输入知识库名称"
            />
          </div>
          <div class="form-group">
            <label for="edit-kb-description">知识库描述</label>
            <textarea
              id="edit-kb-description"
              v-model="editKbDescription"
              rows="3"
              placeholder="请输入知识库描述"
            ></textarea>
          </div>
          <div class="form-group">
            <label for="edit-kb-embedding-model">Embedding模型</label>
            <select
              id="edit-kb-embedding-model"
              v-model="editKbEmbeddingModelId"
              class="form-control"
            >
              <option
                v-for="model in modelStore.embeddingModels"
                :key="model.id"
                :value="model.id"
              >
                {{ model.name }} ({{ model.vendorName }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <label for="edit-kb-rerank-model">Rerank模型</label>
            <select
              id="edit-kb-rerank-model"
              v-model="editKbRerankModelId"
              class="form-control"
            >
              <option
                v-for="model in modelStore.rerankModels"
                :key="model.id"
                :value="model.id"
              >
                {{ model.name }} ({{ model.vendorName }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <label for="edit-kb-chunk-method">分块方式 (chunk_method)</label>
            <select
              id="edit-kb-chunk-method"
              v-model="editKbChunkMethod"
              class="form-control"
            >
              <option value="smart">智能分块</option>
              <option value="line">按行分块</option>
              <option value="paragraph">按段落分块</option>
              <option value="hierarchical">父子分块</option>
            </select>
          </div>
          <div class="form-group">
            <label for="edit-kb-chunk-size">分块大小 (chunk_size)</label>
            <input
              type="number"
              id="edit-kb-chunk-size"
              v-model.number="editKbChunkSize"
              class="form-control"
              min="100"
              max="2048"
              placeholder="请输入分块大小"
            />
          </div>
          <div class="form-group">
            <label for="edit-kb-chunk-overlap">分块重叠 (chunk_overlap)</label>
            <input
              type="number"
              id="edit-kb-chunk-overlap"
              v-model.number="editKbChunkOverlap"
              class="form-control"
              min="0"
              max="512"
              placeholder="请输入分块重叠"
            />
          </div>
          <div class="form-group">
            <label>标签</label>
            <div class="tag-selector">
              <el-checkbox-group v-model="editKbTagIds">
                <el-checkbox
                  v-for="tag in tagStore.tags"
                  :key="tag.id"
                  :label="tag.id"
                  :disabled="!tag.is_active"
                >
                  <span :style="{ color: tag.color }"> {{ tag.name }}</span>
                </el-checkbox>
              </el-checkbox-group>
            </div>
          </div>
          <div class="form-group">
            <label>领域</label>
            <div class="domain-selector">
              <el-checkbox-group v-model="editKbDomainIds">
                <el-checkbox
                  v-for="domain in domainStore.domains"
                  :key="domain.id"
                  :label="domain.id"
                  :disabled="!domain.is_active"
                >
                  {{ domain.name }}
                </el-checkbox>
              </el-checkbox-group>
            </div>
          </div>
        </form>
        <div class="modal-actions">
          <button type="button" class="btn btn-secondary" @click="showEditModal = false">
            取消
          </button>
          <button type="button" class="btn btn-primary" @click="updateKnowledgeBase" :disabled="kbStore.isLoading">
            {{ kbStore.isLoading ? '更新中...' : '更新' }}
          </button>
        </div>
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
          <div class="kb-tags" v-if="kb.tags && kb.tags.length > 0">
            <span class="kb-label">标签：</span>
            <span
              v-for="tag in kb.tags"
              :key="tag.id"
              class="kb-tag"
              :style="{ backgroundColor: tag.color + '20', color: tag.color }"
            >
              {{ tag.name }}
            </span>
          </div>
          <div class="kb-domains" v-if="kb.domains && kb.domains.length > 0">
            <span class="kb-label">所属领域：</span>
            <span
              v-for="domain in kb.domains"
              :key="domain.id"
              class="kb-domain"
            >
              {{ domain.name }}
            </span>
          </div>
          <div class="kb-stats">
            <span class="kb-stat-item">
              📄 {{ kb.doc_count }} 个文档
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
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useKbStore } from '../stores/kb'
import { useModelStore } from '../stores/model'
import { useTagStore } from '../stores/tag'
import { useDomainStore } from '../stores/domain'
import { ElMessageBox, ElMessage } from 'element-plus'
import type { KnowledgeBase } from '../types'

const route = useRoute()

const kbStore = useKbStore()
const modelStore = useModelStore()
const tagStore = useTagStore()
const domainStore = useDomainStore()

// 创建知识库表单
const showCreateModal = ref(false)
const newKbName = ref('')
const newKbDescription = ref('')
const newKbEmbeddingModelId = ref('')
const newKbRerankModelId = ref('')
const newKbChunkSize = ref(512)
const newKbChunkOverlap = ref(64)
const newKbChunkMethod = ref('smart')
const newKbTagIds = ref<string[]>([])
const newKbDomainIds = ref<string[]>([])

// 编辑知识库表单
const showEditModal = ref(false)
const editKbId = ref('')
const editKbName = ref('')
const editKbDescription = ref('')
const editKbEmbeddingModelId = ref('')
const editKbRerankModelId = ref('')
const editKbChunkSize = ref(512)
const editKbChunkOverlap = ref(64)
const editKbChunkMethod = ref('smart')
const editKbTagIds = ref<string[]>([])
const editKbDomainIds = ref<string[]>([])

// 编辑知识库
const editKnowledgeBase = (kb: KnowledgeBase) => {
  editKbId.value = kb.id
  editKbName.value = kb.name
  editKbDescription.value = kb.description || ''
  editKbEmbeddingModelId.value = kb.embedding_model_id || ''
  editKbRerankModelId.value = kb.rerank_model_id || ''
  editKbChunkSize.value = kb.chunk_size || 512
  editKbChunkOverlap.value = kb.chunk_overlap || 64
  editKbChunkMethod.value = kb.chunk_method || 'smart'
  editKbTagIds.value = kb.tags?.map(tag => tag.id) || []
  editKbDomainIds.value = kb.domains?.map(domain => domain.id) || []
  showEditModal.value = true
}

// 确认删除知识库
const confirmDeleteKnowledgeBase = async (kbId: string) => {
  ElMessageBox.confirm(
    '确定要删除这个知识库吗？删除后将无法恢复。',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      await kbStore.deleteKnowledgeBase(kbId)
      // 刷新知识库列表
      await kbStore.getKnowledgeBases()
      ElMessage.success('知识库删除成功')
    })
    .catch(() => {
      // 用户取消删除
    })
}

// 创建知识库
const createKnowledgeBase = async () => {
  if (!newKbName.value.trim()) return

  try {
    await kbStore.createKnowledgeBase({
      name: newKbName.value.trim(),
      description: newKbDescription.value.trim(),
      embedding_model_id: newKbEmbeddingModelId.value,
      rerank_model_id: newKbRerankModelId.value,
      chunk_size: newKbChunkSize.value,
      chunk_overlap: newKbChunkOverlap.value,
      chunk_method: newKbChunkMethod.value,
      tag_ids: newKbTagIds.value,
      domain_ids: newKbDomainIds.value
    })
    showCreateModal.value = false
    newKbName.value = ''
    newKbDescription.value = ''
    newKbEmbeddingModelId.value = ''
    newKbRerankModelId.value = ''
    newKbChunkSize.value = 512
    newKbChunkOverlap.value = 64
    newKbChunkMethod.value = 'smart'
    newKbTagIds.value = []
    newKbDomainIds.value = []
    ElMessage.success('创建知识库成功')
  } catch (error: any) {
    // 提取详细错误信息
    const errorMessage = error.response?.data?.detail || '创建知识库失败'
    ElMessage.error(errorMessage)
  }
}

// 更新知识库
const updateKnowledgeBase = async () => {
  if (!editKbName.value.trim()) return

  try {
    await kbStore.updateKnowledgeBase(editKbId.value, {
      name: editKbName.value.trim(),
      description: editKbDescription.value.trim(),
      embedding_model_id: editKbEmbeddingModelId.value,
      rerank_model_id: editKbRerankModelId.value,
      chunk_size: editKbChunkSize.value,
      chunk_overlap: editKbChunkOverlap.value,
      chunk_method: editKbChunkMethod.value,
      tag_ids: editKbTagIds.value,
      domain_ids: editKbDomainIds.value
    })
    showEditModal.value = false
    ElMessage.success('知识库更新成功')
  } catch (error: any) {
    // 提取详细错误信息
    const errorMessage = error.response?.data?.detail || '更新知识库失败'
    ElMessage.error(errorMessage)
  }
}

// 格式化时间
const formatTime = (timeString: string): string => {
  const date = new Date(timeString)
  return date.toLocaleString('zh-CN')
}

// 加载数据
const loadData = async () => {
  try {
    await Promise.all([
      kbStore.getKnowledgeBases(),
      modelStore.getEmbeddingModels(),
      modelStore.getRerankModels(),
      tagStore.getTags(),
      domainStore.getDomains()
    ])
  } catch (error: any) {
    // 提取详细错误信息
    const errorMessage = error.response?.data?.detail || '加载数据失败'
    ElMessage.error(errorMessage)
  }
}

// 加载知识库列表
onMounted(async () => {
  await loadData()
})

// 监听路由变化，当检测到_refresh参数时重新加载数据
watch(
  () => route.query, 
  async (newQuery) => {
    if (newQuery._refresh) {
      await loadData()
    }
  },
  { deep: true }
)
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
  width: 100%;
  max-width: 500px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-content h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  padding: 30px 30px 0 30px;
}

.modal-content form {
  flex: 1;
  overflow-y: auto;
  padding: 0 30px;
  margin-bottom: 20px;
}

.modal-actions {
  padding: 20px 30px 30px 30px;
  border-top: 1px solid #e0e0e0;
  background-color: white;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 0;
}

/* 标签和领域选择器样式 */
.tag-selector,
.domain-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 8px;
  max-height: 120px;
  overflow-y: auto;
  padding: 8px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
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

/* 标签和领域显示样式 */
.kb-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.kb-label {
  font-size: 12px;
  font-weight: 600;
  color: #666;
  margin-right: 8px;
}

.kb-tag {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  margin-right: 8px;
  margin-bottom: 8px;
}

.kb-domains {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.kb-domain {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  background-color: #f0f0f0;
  color: #333;
  margin-right: 8px;
  margin-bottom: 8px;
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

  .tag-selector,
  .domain-selector {
    max-height: 100px;
  }
}
</style>