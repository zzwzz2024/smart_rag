import { defineStore } from 'pinia'
import { chatApi } from '../api/chat'
import { ElMessage } from 'element-plus'
import type { ChatMessage, Conversation } from '../types'

export const useChatStore = defineStore('chat', {
  state: () => ({
    conversations: [] as Conversation[],
    currentConversation: null as Conversation | null,
    messages: [] as ChatMessage[],
    isLoading: false,
    error: null as string | null,
    isSending: false
  }),

  actions: {
    async getConversations() {
      this.isLoading = true
      this.error = null
      try {
        const response = await chatApi.getConversations()
        const conversations = response.data || response
        // 排序：置顶的对话排在前面，然后按更新时间倒序
        this.conversations = conversations.sort((a, b) => {
          if (a.pinned && !b.pinned) return -1
          if (!a.pinned && b.pinned) return 1
          return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
        })
        return this.conversations
      } catch (error: any) {
        this.error = error.response?.data?.message || '获取对话历史失败'
        ElMessage.error(this.error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async getConversation(conversationId: string) {
      this.isLoading = true
      this.error = null
      try {
        const response = await chatApi.getConversation(conversationId)
        const messages = response.data || response
        this.messages = messages
        return messages
      } catch (error: any) {
        this.error = error.response?.data?.message || '获取对话详情失败'
        ElMessage.error(this.error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async sendMessage(message: string, knowledgeBaseId?: string, modelId?: string) {
      this.isSending = true
      this.error = null
      try {
        const response = await chatApi.sendMessage({
          conversation_id: this.currentConversation?.id,
          query: message,
          kb_ids: knowledgeBaseId ? [knowledgeBaseId] : [],
          model_id: modelId
        })
        const chatResponse = response.data || response
        if (chatResponse.detail) {
          this.error = chatResponse.detail; // 设置全局错误状态
          ElMessage.error(this.error)
          throw new Error(chatResponse.detail); // 抛出异常供上层捕获
        }

        // 构建用户消息
        const userMessage = {
          id: Date.now(),
          conversation_id: chatResponse.conversation_id,
          role: 'user' as const,
          content: message,
          created_at: new Date().toISOString()
        }

        // 构建助手消息
        const assistantMessage = {
          id: chatResponse.message_id,
          conversation_id: chatResponse.conversation_id,
          role: 'assistant' as const,
          content: chatResponse.answer,
          citations: chatResponse.citations,
          confidence: chatResponse.confidence,
          created_at: new Date().toISOString()
        }

        // 更新消息列表
        if (this.currentConversation) {
          this.messages.push(userMessage)
          this.messages.push(assistantMessage)
        } else {
          // 创建新对话
          const newConversation: Conversation = {
            id: chatResponse.conversation_id,
            title: message.substring(0, 30) + '...',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            messages: [userMessage, assistantMessage]
          }
          this.currentConversation = newConversation
          this.conversations.push(newConversation)
        }

        return assistantMessage
      } catch (error: any) {
        this.error = error.response?.data?.message || '发送消息失败'
        ElMessage.error(this.error)
        throw error
      } finally {
        this.isSending = false
      }
    },

    async deleteConversation(conversationId: string) {
      this.isLoading = true
      this.error = null
      try {
        await chatApi.deleteConversation(conversationId)
        this.conversations = this.conversations.filter(c => c.id !== conversationId)
        if (this.currentConversation?.id === conversationId) {
          this.currentConversation = null
          this.messages = []
        }
      } catch (error: any) {
        this.error = error.response?.data?.message || '删除对话失败'
        ElMessage.error(this.error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async updateConversationTitle(conversationId: string, title: string) {
      this.isLoading = true
      this.error = null
      try {
        const response = await chatApi.updateConversationTitle(conversationId, title)
        const conversation = this.conversations.find(c => c.id === conversationId)
        if (conversation) {
          conversation.title = title
        }
        if (this.currentConversation?.id === conversationId) {
          this.currentConversation.title = title
        }
        ElMessage.success('标题已更新')
        return response
      } catch (error: any) {
        this.error = error.response?.data?.message || '更新标题失败'
        ElMessage.error(this.error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async toggleConversationPinned(conversationId: string, pinned: boolean) {
      this.isLoading = true
      this.error = null
      try {
        const response = await chatApi.toggleConversationPinned(conversationId, pinned)
        const conversation = this.conversations.find(c => c.id === conversationId)
        if (conversation) {
          conversation.pinned = pinned
        }
        // 重新排序对话列表，置顶的对话排在前面
        this.conversations.sort((a, b) => {
          if (a.pinned && !b.pinned) return -1
          if (!a.pinned && b.pinned) return 1
          return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
        })
        ElMessage.success(pinned ? '对话已置顶' : '对话已取消置顶')
        return response
      } catch (error: any) {
        this.error = error.response?.data?.message || '切换置顶状态失败'
        ElMessage.error(this.error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    setCurrentConversation(conversation: Conversation | null) {
      this.currentConversation = conversation
      // 不要覆盖已加载的消息，只在conversation有messages属性时使用
      // this.messages = conversation?.messages || []
    }
  }
})