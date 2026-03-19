import { defineStore } from 'pinia'
import { kbApi } from '../api/kb'
import { documentApi } from '../api/document'
import type { KnowledgeBase, Document } from '../types'

export const useKbStore = defineStore('kb', {
  state: () => ({
    knowledgeBases: [] as KnowledgeBase[],
    currentKnowledgeBase: null as KnowledgeBase | null,
    documents: [] as Document[],
    isLoading: false,
    error: null as string | null,
    documentPagination: {
      total: 0,
      page: 1,
      pageSize: 10,
      totalPages: 0
    },
    kbPagination: {
      total: 0,
      page: 1,
      pageSize: 10,
      totalPages: 0
    }
  }),

  actions: {
    async getKnowledgeBases(params?: {
      page?: number
      page_size?: number
    }) {
      this.isLoading = true
      this.error = null
      try {
        const data = await kbApi.getKnowledgeBases(params)
        // 检查响应格式
        if (data.items) {
          // 后端返回了分页格式
          this.knowledgeBases = data.items
          this.kbPagination = {
            total: data.total || 0,
            page: params?.page || 1,
            pageSize: params?.page_size || 10,
            totalPages: Math.ceil((data.total || 0) / (params?.page_size || 10))
          }
        }
        return data
      } catch (error: any) {
        this.error = error.response?.data?.message || '获取知识库列表失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async createKnowledgeBase(data: { name: string; description: string; embedding_model_id?: string; rerank_model_id?: string; chunk_size?: number; chunk_overlap?: number; chunk_method?: string; tag_ids?: string[]; domain_ids?: string[] }) {
      this.isLoading = true
      this.error = null
      try {
        const knowledgeBase = await kbApi.createKnowledgeBase(data)
        this.knowledgeBases.push(knowledgeBase)
        return knowledgeBase
      } catch (error: any) {
        this.error = error.response?.data?.message || '创建知识库失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async getKnowledgeBase(kbId: string) {
      this.isLoading = true
      this.error = null
      try {
        const knowledgeBase = await kbApi.getKnowledgeBase(kbId)
        this.currentKnowledgeBase = knowledgeBase
        return knowledgeBase
      } catch (error: any) {
        this.error = error.response?.data?.message || '获取知识库详情失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async updateKnowledgeBase(kbId: string, data: { name?: string; description?: string; embedding_model_id?: string; rerank_model_id?: string; chunk_size?: number; chunk_overlap?: number; chunk_method?: string; tag_ids?: string[]; domain_ids?: string[] }) {
      this.isLoading = true
      this.error = null
      try {
        const knowledgeBase = await kbApi.updateKnowledgeBase(kbId, data)
        const index = this.knowledgeBases.findIndex(kb => kb.id === kbId)
        if (index !== -1) {
          this.knowledgeBases[index] = knowledgeBase
        }
        if (this.currentKnowledgeBase?.id === kbId) {
          this.currentKnowledgeBase = knowledgeBase
        }
        return knowledgeBase
      } catch (error: any) {
        this.error = error.response?.data?.message || '更新知识库失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async deleteKnowledgeBase(kbId: string) {
      this.isLoading = true
      this.error = null
      try {
        await kbApi.deleteKnowledgeBase(kbId)
        this.knowledgeBases = this.knowledgeBases.filter(kb => kb.id !== kbId)
        if (this.currentKnowledgeBase?.id === kbId) {
          this.currentKnowledgeBase = null
          this.documents = []
        }
      } catch (error: any) {
        this.error = error.response?.data?.message || '删除知识库失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async getDocuments(kbId: string, params?: {
      filename?: string
      created_from?: string
      created_to?: string
      page?: number
      page_size?: number
    }) {
      this.isLoading = true
      this.error = null
      try {
        const result = await documentApi.getDocuments(kbId, params)
        console.log('获取文档列表成功', result)
        // 使用 $patch 方法更新状态，确保响应式
        this.$patch({
          documents: result.data || [],
          documentPagination: {
            total: result.total || 0,
            page: result.page || 1,
            pageSize: result.page_size || 10,
            totalPages: result.total_pages || 0
          }
        })
        return result
      } catch (error: any) {
        this.error = error.response?.data?.message || '获取文档列表失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async uploadDocument(kbId: string, file: File) {
      this.isLoading = true
      this.error = null
      try {
        const formData = new FormData()
        formData.append('file', file)
        const document = await documentApi.uploadDocument(kbId, formData)
        // this.documents.push(document)
        if (Array.isArray(this.documents)) {
          this.documents.push(document); // document 是你收到的这个对象
        } else {
          this.documents = [document]; // fallback
        }
        // 更新知识库的文档数量
        if (this.currentKnowledgeBase?.id === kbId) {
          this.currentKnowledgeBase.document_count++
        }
        const kbIndex = this.knowledgeBases.findIndex(kb => kb.id === kbId)
        if (kbIndex !== -1) {
          this.knowledgeBases[kbIndex].document_count++
        }
        return document
      } catch (error: any) {
        this.error = error.response?.data?.message || '上传文档失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async deleteDocument(docId: string) {
      this.isLoading = true
      this.error = null
      try {
        await documentApi.deleteDocument(docId)
        const document = this.documents.find(doc => doc.id === docId)
        if (document) {
          this.documents = this.documents.filter(doc => doc.id !== docId)
          // 更新知识库的文档数量
          if (this.currentKnowledgeBase?.id === document.kb_id) {
            this.currentKnowledgeBase.document_count--
          }
          const kbIndex = this.knowledgeBases.findIndex(kb => kb.id === document.kb_id)
          if (kbIndex !== -1) {
            this.knowledgeBases[kbIndex].document_count--
          }
        }
      } catch (error: any) {
        this.error = error.response?.data?.message || '删除文档失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    setCurrentKnowledgeBase(knowledgeBase: KnowledgeBase | null) {
      this.currentKnowledgeBase = knowledgeBase
      this.documents = []
    },

    // 知识库权限管理
    async getKnowledgeBasePermissions(kbId: string) {
      this.isLoading = true
      this.error = null
      try {
        const response = await kbApi.getKnowledgeBasePermissions(kbId)
        return response
      } catch (error: any) {
        this.error = error.response?.data?.message || '获取知识库权限失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async addKnowledgeBasePermission(kbId: string, roleId: string) {
      this.isLoading = true
      this.error = null
      try {
        const response = await kbApi.addKnowledgeBasePermission(kbId, roleId)
        return response
      } catch (error: any) {
        this.error = error.response?.data?.message || '添加知识库权限失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async removeKnowledgeBasePermission(kbId: string, roleId: string) {
      this.isLoading = true
      this.error = null
      try {
        const response = await kbApi.removeKnowledgeBasePermission(kbId, roleId)
        return response
      } catch (error: any) {
        this.error = error.response?.data?.message || '移除知识库权限失败'
        throw error
      } finally {
        this.isLoading = false
      }
    }
  }
})