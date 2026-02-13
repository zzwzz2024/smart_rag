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
  }
}