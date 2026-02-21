import axios from 'axios'

const request = axios.create({
  baseURL: '/api',
  timeout: 100000
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    // 如果是blob类型的响应，直接返回，用于文件下载
    if (response.config.responseType === 'blob') {
      return response.data
    }
    
    // 处理统一的响应格式
    const data = response.data
    if (data.code === 200) {
      return data.data // 直接返回data字段，保持向后兼容
    } else {
      return Promise.reject(new Error(data.msg || '请求失败'))
    }
  },
  (error) => {
    if (error.response.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default request