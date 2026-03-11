import { defineStore } from 'pinia'
import { domainApi } from '../api/domain'
import type { Domain } from '../types'

export const useDomainStore = defineStore('domain', {
  state: () => ({
    domains: [] as Domain[],
    isLoading: false,
    error: null as string | null
  }),

  actions: {
    async getDomains() {
      this.isLoading = true
      this.error = null
      try {
        const response = await domainApi.getDomains()
        this.domains = response
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
        return response.data
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
        return response.data
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
