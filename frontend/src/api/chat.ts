import request from './request'
import type { ChatMessage, Conversation } from '../types'

export const chatApi = {
  // 发送消息
  sendMessage(data: {
    conversation_id?: string
    query: string
    kb_ids?: string[]
    model_id?: string
  }) {
    return request<ChatMessage>({
      url: `/chat`,
      method: 'post',
      data
    })
  },

  // 获取对话历史
  getConversations() {
    return request<Conversation[]>({
      url: '/chat/conversations',
      method: 'get'
    })
  },

  // 获取对话详情
  getConversation(conversationId: string) {
    return request<ChatMessage[]>({
      url: `/chat/conversations/${conversationId}/messages`,
      method: 'get'
    })
  },

  // 删除对话
  deleteConversation(conversationId: string) {
    return request({
      url: `/chat/conversations/${conversationId}`,
      method: 'delete'
    })
  },

  // 更新对话标题
  updateConversationTitle(conversationId: string, title: string) {
    return request({
      url: `/chat/conversations/${conversationId}/title`,
      method: 'put',
      data: { title }
    })
  },

  // 切换对话置顶状态
  toggleConversationPinned(conversationId: string, pinned: boolean) {
    return request({
      url: `/chat/conversations/${conversationId}/pinned`,
      method: 'put',
      data: { pinned }
    })
  }
}