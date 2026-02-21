<template>
  <div class="documents-container">
    <div class="documents-header">
      <h2>文档管理</h2>
      <div class="header-actions">
        <select v-model="selectedKnowledgeBase" class="kb-select">
          <option value="">选择知识库</option>
          <option
            v-for="kb in kbStore.knowledgeBases"
            :key="kb.id"
            :value="kb.id"
          >
            {{ kb.name }}
          </option>
        </select>
        <button
          class="btn btn-primary"
          @click="showUploadModal = true"
          :disabled="!selectedKnowledgeBase"
        >
          上传文档
        </button>
      </div>
    </div>

    <!-- 上传文档模态框 -->
    <div v-if="showUploadModal" class="modal-overlay" @click="showUploadModal = false">
      <div class="modal-content" @click.stop>
        <h3>上传文档</h3>
        <form @submit.prevent="uploadDocument">
          <div class="form-group">
            <label for="file-upload">选择文件</label>
            <input
              type="file"
              id="file-upload"
              ref="fileInput"
              @change="handleFileChange"
              required
              accept=".pdf,.docx,.txt"
            />
          </div>
          <div v-if="selectedFile" class="file-info">
            <p>已选择文件: {{ selectedFile.name }}</p>
            <p>文件大小: {{ formatFileSize(selectedFile.size) }}</p>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="showUploadModal = false">
              取消
            </button>
            <button type="submit" class="btn btn-primary" :disabled="kbStore.isLoading || !selectedFile">
              {{ kbStore.isLoading ? '上传中...' : '上传' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 查看文档内容模态框 -->
    <div v-if="showDocumentModal" class="modal-overlay" @click="showDocumentModal = false">
      <div class="modal-content document-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedDocument?.filename }}</h3>
          <button class="close-btn" @click="showDocumentModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="isLoadingDocument" class="loading-state">
            <div class="loading"></div>
            <span>加载文档内容中...</span>
          </div>
          <div v-else-if="documentChunks.length > 0" class="document-content">
            <div
              v-for="(chunk, index) in paginatedChunks"
              :key="chunk.id || index"
              class="document-chunk"
            >
              <div class="chunk-header">
                <span class="chunk-index">段落 {{ chunk.index }}</span>
                <span v-if="chunk.score" class="chunk-score">相关性: {{ (chunk.score * 100).toFixed(2) }}%</span>
              </div>
              <div class="chunk-content">{{ chunk.content }}</div>
            </div>
          </div>
          <div v-else class="empty-state">
            <p>文档内容为空</p>
          </div>
        </div>
        <div class="modal-footer">
          <!-- 文档块分页控件 -->
          <div class="chunk-pagination">
            <div class="pagination-info">
              共 {{ chunkPagination.total }} 个段落，
              第 {{ chunkPagination.currentPage }} / {{ chunkPagination.totalPages }} 页
            </div>
            <div class="pagination-controls">
              <button
                class="btn btn-outline"
                @click="changeChunkPage(1)"
                :disabled="chunkPagination.currentPage === 1"
              >
                首页
              </button>
              <button
                class="btn btn-outline"
                @click="changeChunkPage(chunkPagination.currentPage - 1)"
                :disabled="chunkPagination.currentPage === 1"
              >
                上一页
              </button>
              <button
                class="btn btn-outline"
                @click="changeChunkPage(chunkPagination.currentPage + 1)"
                :disabled="chunkPagination.currentPage >= chunkPagination.totalPages"
              >
                下一页
              </button>
              <button
                class="btn btn-outline"
                @click="changeChunkPage(chunkPagination.totalPages)"
                :disabled="chunkPagination.currentPage >= chunkPagination.totalPages"
              >
                末页
              </button>
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="showDocumentModal = false">
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 文档列表 -->
    <div class="documents-list">
      <div v-if="kbStore.currentKnowledgeBase" class="kb-info">
        <h3>{{ kbStore.currentKnowledgeBase.name }}</h3>
        <p>{{ kbStore.currentKnowledgeBase.description }}</p>
      </div>
      
      <!-- 查询表单 -->
      <div v-if="selectedKnowledgeBase" class="search-form">
        <div class="search-form-row">
          <div class="form-group">
            <label for="filename-search">文件名</label>
            <input
              type="text"
              id="filename-search"
              v-model="searchParams.filename"
              class="form-control"
              placeholder="请输入文件名"
            />
          </div>
          <div class="form-group">
            <label for="created-from">创建开始日期</label>
            <input
              type="date"
              id="created-from"
              v-model="searchParams.created_from"
              class="form-control"
            />
          </div>
          <div class="form-group">
            <label for="created-to">创建结束日期</label>
            <input
              type="date"
              id="created-to"
              v-model="searchParams.created_to"
              class="form-control"
            />
          </div>
          <div class="form-actions">
            <button
              class="btn btn-primary"
              @click="searchDocuments"
              :disabled="kbStore.isLoading"
            >
              查询
            </button>
            <button
              class="btn btn-secondary"
              @click="resetSearch"
            >
              重置
            </button>
          </div>
        </div>
      </div>
      
      <div class="document-table-container">
        <table class="document-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>文件名</th>
              <th>分块数量</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(doc, index) in kbStore.documents"
              :key="doc.id"
            >
              <td>{{ index + 1 }}</td>
              <td>{{ doc.filename }}</td>
              <td>
                <a href="#" class="document-link" @click.prevent="viewDocument(doc)">
                  {{ doc.chunk_count }}
                </a>
              </td>
              <td>{{ formatTime(doc.created_at) }}</td>
              <td>
                <button
                  class="btn btn-danger"
                  @click="confirmDeleteDocument(doc.id)"
                >
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 分页控件 -->
      <div v-if="selectedKnowledgeBase && kbStore.documentPagination.total > 0" class="pagination">
        <div class="pagination-info">
          共 {{ kbStore.documentPagination.total }} 条记录，
          第 {{ kbStore.documentPagination.page }} / {{ kbStore.documentPagination.totalPages }} 页
        </div>
        <div class="pagination-controls">
          <button
            class="btn btn-outline"
            @click="changePage(1)"
            :disabled="kbStore.documentPagination.page === 1 || kbStore.isLoading"
          >
            首页
          </button>
          <button
            class="btn btn-outline"
            @click="changePage(kbStore.documentPagination.page - 1)"
            :disabled="kbStore.documentPagination.page === 1 || kbStore.isLoading"
          >
            上一页
          </button>
          <button
            class="btn btn-outline"
            @click="changePage(kbStore.documentPagination.page + 1)"
            :disabled="kbStore.documentPagination.page >= kbStore.documentPagination.totalPages || kbStore.isLoading"
          >
            下一页
          </button>
          <button
            class="btn btn-outline"
            @click="changePage(kbStore.documentPagination.totalPages)"
            :disabled="kbStore.documentPagination.page >= kbStore.documentPagination.totalPages || kbStore.isLoading"
          >
            末页
          </button>
        </div>
      </div>
      
<!--      <div v-if="kbStore.documents.length === 0 && !kbStore.isLoading" class="empty-state">-->
      <div v-if="(kbStore.documents?.length ?? 0) === 0 && !kbStore.isLoading" class="empty-state">
        <p v-if="selectedKnowledgeBase">该知识库中还没有文档</p>
        <p v-else>请先选择一个知识库</p>
      </div>
      <div v-if="kbStore.isLoading" class="loading-state">
        <div class="loading"></div>
        <span>加载中...</span>
      </div>
      <div v-if="kbStore.isLoading" class="loading-state">
        <div class="loading"></div>
        <span>加载中...</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useKbStore } from '../stores/kb'
import { documentApi } from '../api/document'
import { ElMessageBox, ElMessage } from 'element-plus'

const route = useRoute()
const kbStore = useKbStore()

const selectedKnowledgeBase = ref<string | ''>('')
const showUploadModal = ref(false)
const showDocumentModal = ref(false)
const fileInput = ref<HTMLInputElement>()
const selectedFile = ref<File | null>(null)
const selectedDocument = ref<any>(null)
const documentChunks = ref<any[]>([])
const isLoadingDocument = ref(false)
const isInitializingModels = ref(false)
const searchParams = ref({
  filename: '',
  created_from: '',
  created_to: '',
  page: 1,
  page_size: 10
})

// 文档内容分页
const chunkPagination = ref({
  currentPage: 1,
  pageSize: 1,
  total: 0,
  totalPages: 0
})
const paginatedChunks = ref<any[]>([])

// 处理文件选择
const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
  }
}

// 计算分页后的文档块
const calculatePaginatedChunks = () => {
  const total = documentChunks.value.length
  const currentPage = chunkPagination.value.currentPage
  const pageSize = chunkPagination.value.pageSize
  const startIndex = (currentPage - 1) * pageSize
  const endIndex = startIndex + pageSize
  
  paginatedChunks.value = documentChunks.value.slice(startIndex, endIndex)
  chunkPagination.value.total = total
  chunkPagination.value.totalPages = Math.ceil(total / pageSize)
}

// 切换文档块页码
const changeChunkPage = (page: number) => {
  if (page < 1 || page > chunkPagination.value.totalPages) return
  chunkPagination.value.currentPage = page
  calculatePaginatedChunks()
}

// 上传文档
const uploadDocument = async () => {
  if (!selectedFile.value || !selectedKnowledgeBase.value) return

  try {
    console.log('开始上传文档:', selectedFile.value.name)
    await kbStore.uploadDocument(selectedKnowledgeBase.value, selectedFile.value)
    console.log('上传文档成功，准备关闭模态框')
    showUploadModal.value = false
    selectedFile.value = null
    if (fileInput.value) {
      fileInput.value.value = ''
    }
    ElMessage.success('上传文档成功')
    console.log('模态框已关闭')
    // 刷新文档列表
    await searchDocuments()
    console.log('文档列表已刷新')
  } catch (error: any) {
    console.error('上传文档失败:', error)
    // 提取详细错误信息
    const errorMessage = error.response?.data?.detail || '上传文档失败'
    ElMessage.error(errorMessage)
  }
}

// 确认删除文档
const confirmDeleteDocument = async (docId: number) => {
  ElMessageBox.confirm(
    '确定要删除这个文档吗？删除后将无法恢复。',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      await kbStore.deleteDocument(docId)
      // 刷新文档列表
      await searchDocuments()
      ElMessage.success('文档删除成功')
    })
    .catch(() => {
      // 用户取消删除
    })
}

// 查看文档内容
const viewDocument = async (doc: any) => {
  selectedDocument.value = doc
  isLoadingDocument.value = true
  try {
    const response = await documentApi.getDocumentChunks(doc.id)
    const chunks = response.data || response
    // 为每个分块添加索引属性
    documentChunks.value = chunks.map((chunk: any, index: number) => ({
      ...chunk,
      index: index + 1
    }))
    // 重置分页
    chunkPagination.value.currentPage = 1
    calculatePaginatedChunks()
    showDocumentModal.value = true
  } catch (error: any) {
    // 提取详细错误信息
    const errorMessage = error.response?.data?.detail || '获取文档内容失败'
    ElMessage.error(errorMessage)
  } finally {
    isLoadingDocument.value = false
  }
}

// 查询文档
const searchDocuments = async () => {
  if (!selectedKnowledgeBase.value) return
  
  try {
    const res = await kbStore.getDocuments(selectedKnowledgeBase.value, searchParams.value);
  } catch (error: any) {
    // 提取详细错误信息
    const errorMessage = error.response?.data?.detail || '查询文档失败'
    ElMessage.error(errorMessage)
  }
}

// 重置查询
const resetSearch = () => {
  searchParams.value = {
    filename: '',
    created_from: '',
    created_to: '',
    page: 1,
    page_size: 10
  }
  searchDocuments()
}

// 切换页码
const changePage = (page: number) => {
  if (page < 1 || page > kbStore.documentPagination.totalPages) return
  searchParams.value.page = page
  searchDocuments()
}

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化时间
const formatTime = (timeString: string): string => {
  const date = new Date(timeString)
  return date.toLocaleString('zh-CN')
}

// 初始化知识库模型
const initializeKbModels = async (kbId: string) => {
  try {
    isInitializingModels.value = true
    await documentApi.initializeKbModels(kbId)
    console.log('知识库模型初始化成功')
  } catch (error: any) {
    console.error('初始化知识库模型失败:', error)
    // 提取详细错误信息
    const errorMessage = error.response?.data?.detail || '初始化知识库模型失败'
    ElMessage.warning(errorMessage)
  } finally {
    isInitializingModels.value = false
  }
}

// 监听知识库选择变化
watch(selectedKnowledgeBase, async (newKbId) => {
  if (newKbId) {
    try {
      // 重置查询参数
      searchParams.value.page = 1
      await Promise.all([
        kbStore.getKnowledgeBase(newKbId),
        kbStore.getDocuments(newKbId, searchParams.value),
        initializeKbModels(newKbId)
      ])
    } catch (error) {
      console.error('加载知识库文档失败:', error)
    }
  } else {
    kbStore.setCurrentKnowledgeBase(null)
  }
})

// 加载知识库列表
const loadKnowledgeBases = async () => {
  try {
    await kbStore.getKnowledgeBases()
    // 从路由参数中获取知识库ID
    const kbId = route.query.kbId
    if (kbId) {
      selectedKnowledgeBase.value = kbId as string
    }
  } catch (error) {
    console.error('加载知识库列表失败:', error)
  }
}

// 加载知识库列表
onMounted(async () => {
  await loadKnowledgeBases()
})

// 监听路由变化，当检测到_refresh参数时重新加载数据
watch(
  () => route.query, 
  async (newQuery) => {
    if (newQuery._refresh) {
      await loadKnowledgeBases()
      // 如果当前有选中的知识库，重新加载其文档
      if (selectedKnowledgeBase.value) {
        try {
          await Promise.all([
            kbStore.getKnowledgeBase(selectedKnowledgeBase.value),
            kbStore.getDocuments(selectedKnowledgeBase.value, searchParams.value)
          ])
        } catch (error) {
          console.error('刷新知识库数据失败:', error)
        }
      }
    }
  },
  { deep: true }
)
</script>

<style scoped>
.documents-container {
  padding: 20px 0;
}

.documents-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 16px;
}

.documents-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.kb-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-width: 200px;
}

/* 上传文档模态框 */
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

.file-info {
  margin: 16px 0;
  padding: 12px;
  background-color: #f5f5f5;
  border-radius: 4px;
  font-size: 14px;
}

.file-info p {
  margin: 4px 0;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

/* 文档列表样式 */
.documents-list {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.kb-info {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.kb-info h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
}

.kb-info p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.document-table-container {
  overflow-x: auto;
}

.document-table {
  width: 100%;
  border-collapse: collapse;
}

.document-table th,
.document-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.document-table th {
  font-weight: 600;
  background-color: #f5f5f5;
  font-size: 14px;
}

.document-table td {
  font-size: 14px;
}

.document-table tr:hover {
  background-color: #f9f9f9;
}

.document-link {
  color: #4CAF50;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.document-link:hover {
  color: #45a049;
  text-decoration: underline;
}

/* 文档内容模态框 */
.document-modal {
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.document-modal .modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e0e0e0;
}

.document-modal .modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.document-modal .close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  transition: color 0.2s ease;
}

.document-modal .close-btn:hover {
  color: #333;
}

.document-modal .modal-body {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 20px;
}

.document-modal .modal-footer {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  background-color: #f9f9f9;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.document-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.document-chunk {
  padding: 16px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border-left: 4px solid #4CAF50;
}

.chunk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.chunk-index {
  font-size: 14px;
  font-weight: 600;
  color: #666;
}

.chunk-score {
  font-size: 12px;
  color: #999;
}

.document-modal .chunk-content {
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  white-space: pre-wrap;
  word-break: break-word;
}

/* 文档块分页控件样式 */
.chunk-pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.chunk-pagination .pagination-info {
  font-size: 14px;
  color: #666;
}

.chunk-pagination .pagination-controls {
  display: flex;
  gap: 8px;
}

.chunk-pagination .btn-outline {
  padding: 6px 12px;
  border: 1px solid #ddd;
  background-color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chunk-pagination .btn-outline:hover:not(:disabled) {
  border-color: #4CAF50;
  color: #4CAF50;
}

.chunk-pagination .btn-outline:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 查询表单样式 */
.search-form {
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.search-form-row {
  display: flex;
  gap: 16px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.search-form .form-group {
  flex: 1;
  min-width: 200px;
}

.search-form .form-group label {
  display: block;
  margin-bottom: 4px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.form-actions {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

/* 分页控件样式 */
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.pagination-info {
  font-size: 14px;
  color: #666;
}

.pagination-controls {
  display: flex;
  gap: 8px;
}

.btn-outline {
  padding: 6px 12px;
  border: 1px solid #ddd;
  background-color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-outline:hover:not(:disabled) {
  border-color: #4CAF50;
  color: #4CAF50;
}

.btn-outline:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-form-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .form-actions {
    margin-top: 16px;
    justify-content: flex-start;
  }
  
  .pagination {
    flex-direction: column;
    align-items: stretch;
  }
  
  .pagination-controls {
    justify-content: center;
  }
}

/* 空状态和加载状态 */
.empty-state,
.loading-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 60px 20px;
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
  .documents-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .kb-select {
    width: 100%;
  }

  .document-table {
    font-size: 12px;
  }

  .document-table th,
  .document-table td {
    padding: 8px 12px;
  }
}
</style>