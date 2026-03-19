import { defineStore } from 'pinia'
import { tagApi } from '../api/tag'
import type { Tag } from '../types'

export const useTagStore = defineStore('tag', {
  state: () => ({
    tags: [] as Tag[],
    isLoading: false,
    error: null as string | null,
    pagination: {
      total: 0,
      page: 1,
      pageSize: 10,
      totalPages: 0
    }
  }),

  actions: {
    async getTags(page = 1, pageSize = 10) {
      this.isLoading = true
      this.error = null
      try {
        const skip = (page - 1) * pageSize
        const response = await tagApi.getTags(skip, pageSize)
        // 检查响应格式
        if (response && response.items) {
          // 后端返回了分页格式
          this.tags = response.items
          this.pagination = {
            total: response.total || 0,
            page,
            pageSize,
            totalPages: Math.ceil((response.total || 0) / pageSize)
          }
        } else {
          // 后端返回了直接的标签列表
          this.tags = response || response
          this.pagination = {
            total: this.tags.length,
            page: 1,
            pageSize: this.tags.length,
            totalPages: 1
          }
        }
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
        return response
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
        return response
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
