import request from './request'
import type { Document } from '../types'

export const documentApi = {
  // 获取文档列表
  getDocuments(kbId: string, params?: {
    filename?: string
    created_from?: string
    created_to?: string
    page?: number
    page_size?: number
  }) {
    return request({
      url: `/document/list/${kbId}`,
      method: 'get',
      params
    })
  },

  // 上传文档
  uploadDocument(kbId: string, formData: FormData) {
    return request<Document>({
      url: `/document/upload/${kbId}`,
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 初始化知识库模型
  initializeKbModels(kbId: string) {
    return request({
      url: `/document/initialize/${kbId}`,
      method: 'post'
    })
  },

  // 获取文档分块内容
  getDocumentChunks(docId: string) {
    return request({
      url: `/document/${docId}/chunks`,
      method: 'get'
    })
  },

  // 删除文档
  deleteDocument(docId: string) {
    return request({
      url: `/document/${docId}`,
      method: 'delete'
    })
  },

  // 获取文档权限
  getDocumentPermissions(docId: string) {
    return request({
      url: `/document/${docId}/permissions`,
      method: 'get'
    })
  },

  // 添加文档权限
  addDocumentPermission(docId: string, roleId: string) {
    return request({
      url: `/document/${docId}/permissions`,
      method: 'post',
      params: { role_id: roleId }
    })
  },

  // 移除文档权限
  removeDocumentPermission(docId: string, roleId: string) {
    return request({
      url: `/document/${docId}/permissions/${roleId}`,
      method: 'delete'
    })
  },

  // 更新文档分块
  updateDocumentChunk(chunkId: string, content: string) {
    return request({
      url: `/document/chunks/${chunkId}`,
      method: 'put',
      data: { content }
    })
  },

  // 删除文档分块
  deleteDocumentChunk(chunkId: string) {
    return request({
      url: `/document/chunks/${chunkId}`,
      method: 'delete'
    })
  },

  // 批量清洗文档分块
  batchCleanDocumentChunks(docId: string, params: {
    patterns?: string[]
    remove_empty?: boolean
    remove_duplicates?: boolean
  }) {
    return request({
      url: `/document/chunks/batch-clean`,
      method: 'post',
      data: { doc_id: docId, ...params }
    })
  }
}