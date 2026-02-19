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
        // 构建用户消息
        const userMessage = {
          id: Date.now(),
          conversation_id: this.currentConversation?.id || `temp_${Date.now()}`,
          role: 'user' as const,
          content: message,
          created_at: new Date().toISOString()
        }

        // 立即添加用户消息到消息列表
        this.messages.push(userMessage)

        // 发送消息到API
        const chatResponse = await chatApi.sendMessage({
          conversation_id: this.currentConversation?.id,
          query: message,
          kb_ids: knowledgeBaseId ? [knowledgeBaseId] : [],
          model_id: modelId
        })
        if (chatResponse.detail) {
          this.error = chatResponse.detail; // 设置全局错误状态
          ElMessage.error(this.error)
          // 移除已添加的用户消息
          this.messages = this.messages.filter(m => m.id !== userMessage.id)
          throw new Error(chatResponse.detail); // 抛出异常供上层捕获
        }

        // 构建助手消息
        const assistantMessage = {
          id: chatResponse.message_id,
          conversation_id: chatResponse.conversation_id,
          role: 'assistant' as const,
          content: chatResponse.answer || chatResponse.content,
          citations: chatResponse.citations,
          confidence: chatResponse.confidence,
          created_at: new Date().toISOString()
        }

        // 更新消息列表和对话
        if (this.currentConversation) {
          // 检查是否是临时对话
          if (this.currentConversation.id.startsWith('temp_')) {
            // 替换临时对话为真实对话
            const tempIndex = this.conversations.findIndex(c => c.id === this.currentConversation?.id)
            
            const realConversation: Conversation = {
              id: chatResponse.conversation_id,
              title: message.substring(0, 30) + '...',
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
              pinned: this.currentConversation.pinned || false,
              messages: [userMessage, assistantMessage]
            }
            
            // 更新或替换对话
            if (tempIndex > -1) {
              this.conversations.splice(tempIndex, 1, realConversation)
            } else {
              this.conversations.unshift(realConversation)
            }
            
            this.currentConversation = realConversation
            
            // 更新用户消息的conversation_id为真实ID
            const userMsgIndex = this.messages.findIndex(m => m.id === userMessage.id)
            if (userMsgIndex > -1) {
              this.messages[userMsgIndex].conversation_id = chatResponse.conversation_id
            }
            
            // 添加助手消息
            this.messages.push(assistantMessage)
          } else {
            // 现有对话，添加助手消息
            this.messages.push(assistantMessage)
          }
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
          
          // 更新用户消息的conversation_id为真实ID
          const userMsgIndex = this.messages.findIndex(m => m.id === userMessage.id)
          if (userMsgIndex > -1) {
            this.messages[userMsgIndex].conversation_id = chatResponse.conversation_id
          }
          
          // 添加助手消息
          this.messages.push(assistantMessage)
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
      // 对于新对话，清空消息列表
      if (conversation && conversation.id.startsWith('temp_')) {
        this.messages = []
      } else if (conversation?.messages) {
        // 只在conversation有messages属性时使用
        this.messages = conversation.messages
      }
    }
  }
})