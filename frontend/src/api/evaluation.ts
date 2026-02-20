import request from './request'
import type { Evaluation } from '../types'

export const evaluationApi = {
  // 获取评估列表
  getEvaluations(params?: { kb_id?: string, query?: string }) {
    return request<Evaluation[]>({
      url: '/eval',
      method: 'get',
      params
    })
  },

  // 创建评估
  createEvaluation(data: {
    query: string
    reference_answer: string
    kb_ids: string[]
    model_id: string
  }) {
    return request<Evaluation>({
      url: '/eval',
      method: 'post',
      data
    })
  },

  // 删除评估
  deleteEvaluation(evalId: number) {
    return request({
      url: `/eval/${evalId}`,
      method: 'delete'
    })
  },

  // 更新评估（重新评估）
  updateEvaluation(evalId: number, data: {
    query: string
    reference_answer: string
    kb_ids: string[]
    model_id: string
  }) {
    return request({
      url: `/eval/${evalId}`,
      method: 'put',
      data
    })
  }
}