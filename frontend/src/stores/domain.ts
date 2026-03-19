import { defineStore } from 'pinia'
import { domainApi } from '../api/domain'
import type { Domain } from '../types'

export const useDomainStore = defineStore('domain', {
  state: () => ({
    domains: [] as Domain[],
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
    async getDomains(page = 1, pageSize = 10) {
      this.isLoading = true
      this.error = null
      try {
        const skip = (page - 1) * pageSize
        const response = await domainApi.getDomains(skip, pageSize)
        // 检查响应格式
        if (response && response.items) {
          // 后端返回了分页格式
          this.domains = response.items
          this.pagination = {
            total: response.total || 0,
            page,
            pageSize,
            totalPages: Math.ceil((response.total || 0) / pageSize)
          }
        } else {
          // 后端返回了直接的领域列表
          this.domains = response || response
          this.pagination = {
            total: this.domains.length,
            page: 1,
            pageSize: this.domains.length,
            totalPages: 1
          }
        }
      } catch (error: any) {
        this.error = error.response?.data?.detail || '获取领域列表失败'
        console.error('获取领域列表失败:', error)
      } finally {
        this.isLoading = false
      }
    },

    async createDomain(data: { name: string; description?: string }) {
      this.isLoading = true
      this.error = null
      try {
        const response = await domainApi.createDomain(data)
        await this.getDomains() // 重新获取领域列表
        return response
      } catch (error: any) {
        this.error = error.response?.data?.detail || '创建领域失败'
        console.error('创建领域失败:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async updateDomain(domainId: string, data: { name?: string; description?: string }) {
      this.isLoading = true
      this.error = null
      try {
        const response = await domainApi.updateDomain(domainId, data)
        await this.getDomains() // 重新获取领域列表
        return response
      } catch (error: any) {
        this.error = error.response?.data?.detail || '更新领域失败'
        console.error('更新领域失败:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async deleteDomain(domainId: string) {
      this.isLoading = true
      this.error = null
      try {
        await domainApi.deleteDomain(domainId)
        await this.getDomains() // 重新获取领域列表
      } catch (error: any) {
        this.error = error.response?.data?.detail || '删除领域失败'
        console.error('删除领域失败:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    }
  }
})
