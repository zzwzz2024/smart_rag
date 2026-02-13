import request from './request'
import type { Evaluation } from '../types'

export const evaluationApi = {
  // 获取评估列表
  getEvaluations() {
    return request<Evaluation[]>({
      url: '/eval',
      method: 'get'
    })
  },

  // 创建评估
  createEvaluation(data: {
    query: string
    reference_answer: string
    kb_ids: string[]
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
  }
}