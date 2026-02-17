import { defineStore } from 'pinia'
import type { RouteRecordNormalized } from 'vue-router'

interface Tab {
  path: string
  name: string
  title: string
  component?: RouteRecordNormalized['components']
}

export const useTabsStore = defineStore('tabs', {
  state: () => ({
    tabsList: [] as Tab[],
    activeTab: ''
  }),

  getters: {
    getTabsList: (state) => state.tabsList,
    getActiveTab: (state) => state.activeTab
  },

  actions: {
    addTab(tab: Tab) {
      const isExist = this.tabsList.some(item => item.path === tab.path)
      if (!isExist) {
        this.tabsList.push(tab)
      }
      this.activeTab = tab.path
    },

    removeTab(path: string) {
      const index = this.tabsList.findIndex(item => item.path === path)
      if (index > -1) {
        this.tabsList.splice(index, 1)
        // 如果删除的是当前激活的标签，切换到前一个标签
        if (this.activeTab === path) {
          this.activeTab = this.tabsList.length > 0 ? this.tabsList[this.tabsList.length - 1].path : ''
        }
      }
    },

    setActiveTab(path: string) {
      this.activeTab = path
    },

    closeAllTabs() {
      this.tabsList = []
      this.activeTab = ''
    },

    closeOtherTabs(path: string) {
      this.tabsList = this.tabsList.filter(item => item.path === path)
      this.activeTab = path
    }
  }
})
