<template>
  <div class="kb-container">
    <div class="kb-header">
      <h2>知识库管理</h2>
      <button class="btn btn-primary" @click="openCreateModal">
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
            <div class="tag-pagination">
              <Pagination
                :current-page="tagPage"
                :page-size="tagPageSize"
                :total="tagStore.pagination.total"
                @size-change="handleTagSizeChange"
                @current-change="handleTagCurrentChange"
              />
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
            <div class="domain-pagination">
              <Pagination
                :current-page="domainPage"
                :page-size="domainPageSize"
                :total="domainStore.pagination.total"
                @size-change="handleDomainSizeChange"
                @current-change="handleDomainCurrentChange"
              />
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
            <div class="tag-pagination">
              <Pagination
                :current-page="tagPage"
                :page-size="tagPageSize"
                :total="tagStore.pagination.total"
                @size-change="handleTagSizeChange"
                @current-change="handleTagCurrentChange"
              />
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
            <div class="domain-pagination">
              <Pagination
                :current-page="domainPage"
                :page-size="domainPageSize"
                :total="domainStore.pagination.total"
                @size-change="handleDomainSizeChange"
                @current-change="handleDomainCurrentChange"
              />
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

    <!-- 知识库权限管理模态框 -->
    <div v-if="showPermissionModal" class="modal-overlay" @click="showPermissionModal = false">
      <div class="modal-content permission-modal" @click.stop>
        <div class="modal-header">
          <h3>知识库权限管理 - {{ selectedKnowledgeBaseForPermission?.name }}</h3>
        </div>
        <div class="modal-body">
          <div v-if="isLoadingPermissions" class="loading-state">
            <div class="loading"></div>
            <span>加载权限中...</span>
          </div>
          <div v-else>
            <!-- 已有权限列表 -->
            <div class="permission-section">
              <h4>已有权限</h4>
              <div v-if="knowledgeBasePermissions.length > 0" class="permission-list">
                <div
                  v-for="permission in knowledgeBasePermissions"
                  :key="permission.role_id"
                  class="permission-item"
                >
                  <span class="role-info">{{ permission.role_name }} ({{ permission.role_code }})</span>
                  <button
                    class="btn btn-danger btn-sm"
                    @click="removeKnowledgeBasePermission(permission.role_id)"
                  >
                    移除
                  </button>
                </div>
              </div>
              <div v-else class="empty-state no-permissions">
                <p>暂无权限设置</p>
              </div>
            </div>

            <!-- 添加权限 -->
            <div class="permission-section" style="margin-top: 20px;">
              <h4>添加权限</h4>
              <div class="add-permission-form">
                <select v-model="selectedRoleId" class="form-control">
                  <option value="">选择角色</option>
                  <option
                    v-for="role in availableRoles"
                    :key="role.id"
                    :value="role.id"
                  >
                    {{ role.name }} ({{ role.code }})
                  </option>
                </select>
                <button
                  class="btn btn-primary"
                  @click="addKnowledgeBasePermission"
                  :disabled="!selectedRoleId"
                >
                  添加权限
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="showPermissionModal = false">
              关闭
            </button>
          </div>
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
              class="btn btn-primary"
              @click="manageKnowledgeBasePermissions(kb)"
              style="margin-right: 8px;"
            >
              权限
            </button>
            <button
              class="btn btn-secondary"
              @click="editKnowledgeBase(kb)"
              style="margin-right: 8px;"
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
    
    <!-- 分页 -->
    <div class="pagination">
      <Pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :total="kbStore.kbPagination.total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
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
import Pagination from '../components/Pagination.vue'
import { roleApi } from '../api/system'

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

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)

// 标签和领域分页
const tagPage = ref(1)
const tagPageSize = ref(10)
const domainPage = ref(1)
const domainPageSize = ref(10)

// 知识库权限管理相关状态
const showPermissionModal = ref(false)
const selectedKnowledgeBaseForPermission = ref<any>(null)
const knowledgeBasePermissions = ref<any[]>([])
const availableRoles = ref<any[]>([])
const selectedRoleId = ref('')
const isLoadingPermissions = ref(false)

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
  
  // 重置标签和领域的分页参数
  tagPage.value = 1
  tagPageSize.value = 10
  domainPage.value = 1
  domainPageSize.value = 10
  
  // 重新加载标签和领域列表
  tagStore.getTags(tagPage.value, tagPageSize.value)
  domainStore.getDomains(domainPage.value, domainPageSize.value)
  
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

// 显示创建知识库模态框
const openCreateModal = () => {
  // 重置表单
  newKbName.value = ''
  newKbDescription.value = ''
  newKbEmbeddingModelId.value = ''
  newKbRerankModelId.value = ''
  newKbChunkSize.value = 512
  newKbChunkOverlap.value = 64
  newKbChunkMethod.value = 'smart'
  newKbTagIds.value = []
  newKbDomainIds.value = []
  
  // 重置标签和领域的分页参数
  tagPage.value = 1
  tagPageSize.value = 10
  domainPage.value = 1
  domainPageSize.value = 10
  
  // 重新加载标签和领域列表
  tagStore.getTags(tagPage.value, tagPageSize.value)
  domainStore.getDomains(domainPage.value, domainPageSize.value)
  
  showCreateModal.value = true
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
      kbStore.getKnowledgeBases({ page: currentPage.value, page_size: pageSize.value }),
      modelStore.getEmbeddingModels(),
      modelStore.getRerankModels(),
      tagStore.getTags(tagPage.value, tagPageSize.value),
      domainStore.getDomains(domainPage.value, domainPageSize.value)
    ])
  } catch (error: any) {
    // 提取详细错误信息
    const errorMessage = error.response?.data?.detail || '加载数据失败'
    ElMessage.error(errorMessage)
  }
}

// 打开知识库权限管理模态框
const manageKnowledgeBasePermissions = async (kb: any) => {
  selectedKnowledgeBaseForPermission.value = kb
  showPermissionModal.value = true
  await loadKnowledgeBasePermissions(kb.id)
  await loadAvailableRoles()
}

// 加载知识库权限
const loadKnowledgeBasePermissions = async (kbId: string) => {
  isLoadingPermissions.value = true
  try {
    const response = await kbStore.getKnowledgeBasePermissions(kbId)
    knowledgeBasePermissions.value = response || []
  } catch (error: any) {
    console.error('加载知识库权限失败:', error)
    const errorMessage = error.response?.data?.detail || '加载知识库权限失败'
    ElMessage.error(errorMessage)
  } finally {
    isLoadingPermissions.value = false
  }
}

// 加载可用角色
const loadAvailableRoles = async () => {
  try {
    const response = await roleApi.getRoles()
    availableRoles.value = response || []
  } catch (error: any) {
    console.error('加载角色列表失败:', error)
    const errorMessage = error.response?.data?.detail || '加载角色列表失败'
    ElMessage.error(errorMessage)
  }
}

// 添加知识库权限
const addKnowledgeBasePermission = async () => {
  if (!selectedKnowledgeBaseForPermission.value || !selectedRoleId.value) return
  
  try {
    await kbStore.addKnowledgeBasePermission(selectedKnowledgeBaseForPermission.value.id, selectedRoleId.value)
    ElMessage.success('权限添加成功')
    await loadKnowledgeBasePermissions(selectedKnowledgeBaseForPermission.value.id)
    selectedRoleId.value = ''
  } catch (error: any) {
    console.error('添加权限失败:', error)
    const errorMessage = error.response?.data?.detail || '添加权限失败'
    ElMessage.error(errorMessage)
  }
}

// 移除知识库权限
const removeKnowledgeBasePermission = async (roleId: string) => {
  if (!selectedKnowledgeBaseForPermission.value) return
  
  ElMessageBox.confirm(
    '确定要移除这个角色的访问权限吗？',
    '移除权限确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        await kbStore.removeKnowledgeBasePermission(selectedKnowledgeBaseForPermission.value.id, roleId)
        ElMessage.success('权限移除成功')
        await loadKnowledgeBasePermissions(selectedKnowledgeBaseForPermission.value.id)
      } catch (error: any) {
        console.error('移除权限失败:', error)
        const errorMessage = error.response?.data?.detail || '移除权限失败'
        ElMessage.error(errorMessage)
      }
    })
    .catch(() => {
      // 用户取消操作
    })
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  loadData()
}

const handleCurrentChange = (current: number) => {
  currentPage.value = current
  loadData()
}

// 标签分页处理
const handleTagSizeChange = (size: number) => {
  tagPageSize.value = size
  tagPage.value = 1
  tagStore.getTags(tagPage.value, tagPageSize.value)
}

const handleTagCurrentChange = (current: number) => {
  tagPage.value = current
  tagStore.getTags(tagPage.value, tagPageSize.value)
}

// 领域分页处理
const handleDomainSizeChange = (size: number) => {
  domainPageSize.value = size
  domainPage.value = 1
  domainStore.getDomains(domainPage.value, domainPageSize.value)
}

const handleDomainCurrentChange = (current: number) => {
  domainPage.value = current
  domainStore.getDomains(domainPage.value, domainPageSize.value)
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
  max-width: 900px;
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
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.kb-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 24px;
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

/* 分页样式 */
.pagination {
  margin-top: 30px;
  display: flex;
  justify-content: flex-end;
}

/* 标签和领域分页样式 */
.tag-pagination,
.domain-pagination {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
}

.tag-pagination .el-pagination,
.domain-pagination .el-pagination {
  font-size: 12px;
}

.tag-pagination .el-pagination__sizes,
.domain-pagination .el-pagination__sizes {
  margin-right: 10px;
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
  
  .pagination {
    justify-content: center;
  }
}

/* 权限管理模态框样式 */
.permission-modal {
  width: 90%;
  max-width: 700px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.permission-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.permission-list {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 20px;
}

.permission-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.permission-item:last-child {
  border-bottom: none;
}

.role-info {
  font-size: 14px;
  color: #333;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 12px;
}

.add-permission-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background-color: #f9f9f9;
}

.add-permission-form select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

/* 暂无权限提示样式 */
.no-permissions {
  background-color: #fff3cd;
  border: 1px solid #ffeeba;
  color: #856404;
  padding: 20px;
  border-radius: 4px;
  text-align: center;
  font-weight: 500;
  font-size: 16px;
}
</style>