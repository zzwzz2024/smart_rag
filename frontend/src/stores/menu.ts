import { defineStore } from 'pinia'
import { menuApi } from '../api/system'
import type { Menu } from '../types/system'

export const useMenuStore = defineStore('menu', {
  state: () => ({
    menus: [] as Menu[],
    isLoading: false,
    error: null as string | null
  }),

  getters: {
    menuTree: (state) => {
      return state.menus
    }
  },

  actions: {
    async loadUserMenus() {
      this.isLoading = true
      this.error = null
      try {
        const menus = await menuApi.getUserMenus()
        this.menus = menus
        return menus
      } catch (error: any) {
        this.error = error.message || '获取菜单权限失败'
        this.menus = []
        throw error
      } finally {
        this.isLoading = false
      }
    },

    clearMenus() {
      this.menus = []
    }
  }
})