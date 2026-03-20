import request from './request'

interface SubmitFeedbackRequest {
  message_id: string
  rating: number
  comment?: string
}

interface FeedbackResponse {
  id: string
  message_id: string
  rating: number
  comment?: string
  created_at: string
}

interface GetFeedbacksResponse {
  total: number
  items: FeedbackResponse[]
}

export const agentApi = {
  // 提交反馈
  submitFeedback: async (data: SubmitFeedbackRequest): Promise<FeedbackResponse> => {
    const response = await request.post('/agent/feedback', data)
    return response.data
  },

  // 获取反馈列表
  getFeedbacks: async (params?: { page?: number; limit?: number }): Promise<GetFeedbacksResponse> => {
    const response = await request.get('/agent/feedback', { params })
    return response.data
  }
}
