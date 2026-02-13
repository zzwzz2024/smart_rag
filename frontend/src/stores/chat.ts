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
        this.conversations = conversations
        return conversations
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

    async sendMessage(message: string, knowledgeBaseId?: string) {
      this.isSending = true
      this.error = null
      try {
        const response = await chatApi.sendMessage({
          conversation_id: this.currentConversation?.id,
          query: message,
          kb_ids: knowledgeBaseId ? [knowledgeBaseId] : []
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
          citations: chatResponse.citations?.map(c => ({
            document_id: c.doc_id,
            filename: c.filename,
            chunk_id: c.chunk_id,
            content: c.content,
            score: c.score
          })),
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

    setCurrentConversation(conversation: Conversation | null) {
      this.currentConversation = conversation
      this.messages = conversation?.messages || []
    }
  }
})