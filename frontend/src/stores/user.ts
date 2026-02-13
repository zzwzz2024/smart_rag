import { defineStore } from 'pinia'
import { authApi } from '../api/auth'
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
        const response = await authApi.login({ username, password })
        // const loginData = response.data
        const loginData =  response.data
        localStorage.setItem('token', loginData.access_token)
        this.user = loginData.user
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
         const response = await authApi.register({ username, password, email });
         // const registerData = response?.data; // 可选链操作符
         const registerData =  response.data

         // console.log('完整响应:', response);
         //  console.log('response.data:', response?.data);
         //  console.log('response.data 类型:', typeof response?.data);
         if (!registerData || !registerData.access_token) {
           throw new Error('注册响应数据无效');
         }
         console.log(registerData.access_token);
         localStorage.setItem('token', registerData.access_token);
         this.user = registerData.user;
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
        const response = await authApi.getCurrentUser()
        const user = response.data
        this.user = user
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
    }
  }
})