import request from './request'
import type { KnowledgeBase } from '../types'

export const kbApi = {
  // 获取知识库列表
  getKnowledgeBases() {
    return request<KnowledgeBase[]>({
      url: '/kb/knowledge-base',
      method: 'get'
    })
  },

  // 创建知识库
  createKnowledgeBase(data: {
    name: string
    description: string
    embedding_model_id?: string
    rerank_model_id?: string
    chunk_size?: number
    chunk_overlap?: number
  }) {
    return request<KnowledgeBase>({
      url: '/kb/knowledge-base',
      method: 'post',
      data
    })
  },

  // 获取知识库详情
  getKnowledgeBase(kbId: string) {
    return request<KnowledgeBase>({
      url: `/kb/knowledge-base/${kbId}`,
      method: 'get'
    })
  },

  // 更新知识库
  updateKnowledgeBase(kbId: string, data: {
    name?: string
    description?: string
    embedding_model_id?: string
    rerank_model_id?: string
    chunk_size?: number
    chunk_overlap?: number
  }) {
    return request<KnowledgeBase>({
      url: `/kb/knowledge-base/${kbId}`,
      method: 'put',
      data
    })
  },

  // 删除知识库
  deleteKnowledgeBase(kbId: string) {
    return request({
      url: `/kb/knowledge-base/${kbId}`,
      method: 'delete'
    })
  }
}