import { defineStore } from 'pinia'
import { authApi } from '../api/auth'
import { useMenuStore } from './menu'
import type { User } from '../types'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null as User | null,
    isLoading: false,
    error: null as string | null
  }),

  getters: {
    isLoggedIn: (state) => !!state.user
  },

  actions: {
    async login(username: string, password: string) {
      this.isLoading = true
      this.error = null
      try {
        const loginData = await authApi.login({ username, password })
        localStorage.setItem('token', loginData.access_token)
        this.user = loginData.user
        
        // 登录成功后加载菜单权限
        const menuStore = useMenuStore()
        await menuStore.loadUserMenus()
        
        return loginData
      } catch (error: any) {
        this.error = error.response?.data?.message || '登录失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async register(username: string, password: string, email: string) {
       this.isLoading = true;
       this.error = null;
       try {
         const registerData = await authApi.register({ username, password, email });

         if (!registerData || !registerData.access_token) {
           throw new Error('注册响应数据无效');
         }
         console.log(registerData.access_token);
         localStorage.setItem('token', registerData.access_token);
         this.user = registerData.user;
         
         // 注册成功后加载菜单权限
         const menuStore = useMenuStore();
         await menuStore.loadUserMenus();
         
         return registerData;
     } catch (error: any) {
         this.error = error.response?.data?.message || '注册失败';
         throw error;
     } finally {
        this.isLoading = false;
     }
   },


    async getCurrentUser() {
      this.isLoading = true
      this.error = null
      try {
        const user = await authApi.getCurrentUser()
        this.user = user
        
        // 获取用户信息后加载菜单权限
        const menuStore = useMenuStore()
        await menuStore.loadUserMenus()
        
        return user
      } catch (error: any) {
        this.error = error.response?.data?.message || '获取用户信息失败'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    logout() {
      localStorage.removeItem('token')
      this.user = null
      
      // 退出登录时清除菜单
      const menuStore = useMenuStore()
      menuStore.clearMenus()
    }
  }
})