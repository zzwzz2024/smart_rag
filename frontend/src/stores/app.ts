import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    sidebarCollapsed: false,
    currentView: 'chat',
    isDarkMode: false
  }),

  actions: {
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },

    setCurrentView(view: string) {
      this.currentView = view
    },

    toggleDarkMode() {
      this.isDarkMode = !this.isDarkMode
      // 保存到localStorage
      localStorage.setItem('darkMode', this.isDarkMode.toString())
      // 应用到DOM
      if (this.isDarkMode) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    },

    loadDarkMode() {
      const saved = localStorage.getItem('darkMode')
      if (saved) {
        this.isDarkMode = saved === 'true'
        if (this.isDarkMode) {
          document.documentElement.classList.add('dark')
        }
      }
    }
  }
})