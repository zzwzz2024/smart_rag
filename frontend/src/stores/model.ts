import { defineStore } from 'pinia'
import modelApi from '../api/model'
import type { ModelResponse } from '../api/model'

export const useModelStore = defineStore('model', {
  state: () => ({
    models: [] as ModelResponse[],
    chatModels: [] as ModelResponse[],
    embeddingModels: [] as ModelResponse[],
    rerankModels: [] as ModelResponse[],
    isLoading: false,
    error: null as string | null
  }),

  actions: {
    async getModels(type?: 'embedding' | 'chat' | 'rerank') {
      this.isLoading = true
      this.error = null
      try {
        const response = await modelApi.getModels({ type })
        const models = response.items || []
        
        // Filter models by type
        if (!type) {
          // If no type specified, update all model arrays
          this.chatModels = models.filter(model => model.type === 'chat' && (model.isActive ?? true))
          this.embeddingModels = models.filter(model => model.type === 'embedding' && (model.isActive ?? true))
          this.rerankModels = models.filter(model => model.type === 'rerank' && (model.isActive ?? true))
          // Store all models
          this.models = models
        } else {
          // If type specified, update only the relevant model array
          switch (type) {
            case 'chat':
              this.chatModels = models.filter(model => model.type === 'chat' && (model.isActive ?? true))
              break
            case 'embedding':
              this.embeddingModels = models.filter(model => model.type === 'embedding' && (model.isActive ?? true))
              break
            case 'rerank':
              this.rerankModels = models.filter(model => model.type === 'rerank' && (model.isActive ?? true))
              break
          }
        }
        
        return models
      } catch (error: any) {
        this.error = error.response?.data?.detail || '获取模型列表失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async getChatModels() {
      return this.getModels('chat')
    },

    async getEmbeddingModels() {
      return this.getModels('embedding')
    },

    async getRerankModels() {
      return this.getModels('rerank')
    }
  }
})
