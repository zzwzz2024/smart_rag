import request from './request'
import type { LoginRequest, LoginResponse, User } from '../types'

export const authApi = {
  // 登录
  login(data: LoginRequest) {
    return request<LoginResponse>({
      url: '/auth/login',
      method: 'post',
      data
    })
  },

  // 注册
  async register(data: {
    username: string
    password: string
    email: string
  }) {
    return request<LoginResponse>({
      url: '/auth/register',
      method: 'post',
      data
    })
  },

  // 获取当前用户信息
  getCurrentUser() {
    return request<User>({
      url: '/auth/me',
      method: 'get'
    })
  },

  // 退出登录
  logout() {
    return request({
      url: '/auth/logout',
      method: 'post'
    })
  }
}