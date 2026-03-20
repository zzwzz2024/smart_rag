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

    async sendMessage(message: string, knowledgeBaseId?: string, modelId?: string, contextRound?: number) {
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
          model_id: modelId,
          context_round: contextRound
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
    },

    async agentSendMessage(message: string, knowledgeBaseId?: string, modelId?: string, contextRound?: number) {
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
        const chatResponse = await chatApi.agentChat({
          conversation_id: this.currentConversation?.id,
          query: message,
          kb_ids: knowledgeBaseId ? [knowledgeBaseId] : [],
          model_id: modelId,
          context_round: contextRound
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

    async agentSendMessageStream(message: string, knowledgeBaseId?: string, modelId?: string, contextRound?: number) {
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
        const response = await chatApi.agentChatStream({
          conversation_id: this.currentConversation?.id,
          query: message,
          kb_ids: knowledgeBaseId ? [knowledgeBaseId] : [],
          model_id: modelId,
          context_round: contextRound
        })

        if (!response.ok) {
          throw new Error('流式请求失败')
        }

        // 获取响应流
        const reader = response.body?.getReader()
        if (!reader) {
          throw new Error('无法获取响应流')
        }

        // 构建临时助手消息
        const tempAssistantMessageId = Date.now() + 1
        const tempAssistantMessage = {
          id: tempAssistantMessageId,
          conversation_id: userMessage.conversation_id,
          role: 'assistant' as const,
          content: '',
          citations: [],
          confidence: 0,
          created_at: new Date().toISOString()
        }

        // 添加临时助手消息
        this.messages.push(tempAssistantMessage)

        // 读取流数据
        let fullContent = ''
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          
          // 解码数据
          const chunk = new TextDecoder().decode(value)
          
          // 解析Server-Sent Events
          const lines = chunk.split('\n')
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.substring(6)
              if (data === '[DONE]') {
                break
              }
              try {
                const parsed = JSON.parse(data)
                if (parsed.token) {
                  fullContent += parsed.token
                  // 更新临时助手消息
                  const msgIndex = this.messages.findIndex(m => m.id === tempAssistantMessageId)
                  if (msgIndex > -1) {
                    this.messages[msgIndex].content = fullContent
                  }
                }
              } catch (e) {
                console.error('解析流数据失败:', e)
              }
            }
          }
        }

        // 模拟获取真实的消息ID和对话ID（实际应该从服务器返回）
        const realMessageId = Date.now() + 2
        const realConversationId = this.currentConversation?.id || `conv_${Date.now()}`

        // 构建真实助手消息
        const assistantMessage = {
          id: realMessageId,
          conversation_id: realConversationId,
          role: 'assistant' as const,
          content: fullContent,
          citations: [],
          confidence: 0.9,
          created_at: new Date().toISOString()
        }

        // 替换临时助手消息
        const tempMsgIndex = this.messages.findIndex(m => m.id === tempAssistantMessageId)
        if (tempMsgIndex > -1) {
          this.messages.splice(tempMsgIndex, 1, assistantMessage)
        }

        // 更新消息列表和对话
        if (this.currentConversation) {
          // 检查是否是临时对话
          if (this.currentConversation.id.startsWith('temp_')) {
            // 替换临时对话为真实对话
            const tempIndex = this.conversations.findIndex(c => c.id === this.currentConversation?.id)
            
            const realConversation: Conversation = {
              id: realConversationId,
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
              this.messages[userMsgIndex].conversation_id = realConversationId
            }
          } else {
            // 现有对话，不需要更新对话信息
          }
        } else {
          // 创建新对话
          const newConversation: Conversation = {
            id: realConversationId,
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
            this.messages[userMsgIndex].conversation_id = realConversationId
          }
        }

        return assistantMessage
      } catch (error: any) {
        this.error = error.response?.data?.message || '发送消息失败'
        ElMessage.error(this.error)
        throw error
      } finally {
        this.isSending = false
      }
    }
  }
})