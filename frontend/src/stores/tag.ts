import { defineStore } from 'pinia'
import { tagApi } from '../api/tag'
import type { Tag } from '../types'

export const useTagStore = defineStore('tag', {
  state: () => ({
    tags: [] as Tag[],
    isLoading: false,
    error: null as string | null
  }),

  actions: {
    async getTags() {
      this.isLoading = true
      this.error = null
      try {
        const response = await tagApi.getTags()
        this.tags = response
      } catch (error: any) {
        this.error = error.response?.data?.detail || '获取标签列表失败'
        console.error('获取标签列表失败:', error)
      } finally {
        this.isLoading = false
      }
    },

    async createTag(data: { name: string; color?: string }) {
      this.isLoading = true
      this.error = null
      try {
        const response = await tagApi.createTag(data)
        await this.getTags() // 重新获取标签列表
        return response.data
      } catch (error: any) {
        this.error = error.response?.data?.detail || '创建标签失败'
        console.error('创建标签失败:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async updateTag(tagId: string, data: { name?: string; color?: string }) {
      this.isLoading = true
      this.error = null
      try {
        const response = await tagApi.updateTag(tagId, data)
        await this.getTags() // 重新获取标签列表
        return response.data
      } catch (error: any) {
        this.error = error.response?.data?.detail || '更新标签失败'
        console.error('更新标签失败:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async deleteTag(tagId: string) {
      this.isLoading = true
      this.error = null
      try {
        await tagApi.deleteTag(tagId)
        await this.getTags() // 重新获取标签列表
      } catch (error: any) {
        this.error = error.response?.data?.detail || '删除标签失败'
        console.error('删除标签失败:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    }
  }
})
