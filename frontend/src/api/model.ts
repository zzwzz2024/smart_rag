import request from './request'

// 模型类型定义
export type ModelType = 'embedding' | 'chat' | 'rerank'

// 模型基础接口
export interface ModelBase {
  name: string
  model: string
  type: ModelType
  vendor?: string
  apiKey?: string
  baseUrl?: string
  description?: string
}

// 模型创建接口
export interface ModelCreate extends ModelBase {}

// 模型更新接口
export interface ModelUpdate {
  name?: string
  model?: string
  vendor?: string
  apiKey?: string
  baseUrl?: string
  description?: string
}

// 模型响应接口
export interface ModelResponse extends ModelBase {
  id: string
  vendorId?: string
  vendorName?: string
  isActive?: boolean
  isDefault?: boolean
  createdAt: string
  updatedAt: string
}

// 模型列表响应接口
export interface ModelListResponse {
  total: number
  items: ModelResponse[]
}

// 模型厂商响应接口
export interface ModelVendorResponse {
  id: string
  name: string
  description?: string
  createdAt: string
  updatedAt: string
}

// 模型厂商列表响应接口
export interface ModelVendorListResponse {
  total: number
  items: ModelVendorResponse[]
}

// 模型管理API
export default {
  // 创建模型
  createModel(data: any) {
    return request({
      url: '/model/',
      method: 'post',
      data
    })
  },

  // 获取模型列表
  getModels(params?: {
    type?: ModelType
    page?: number
    page_size?: number
  }) {
    return request({
      url: '/model/list',
      method: 'get',
      params
    })
  },

  // 获取模型详情
  getModel(modelId: string) {
    return request({
      url: `/model/${modelId}`,
      method: 'get'
    })
  },

  // 更新模型
  updateModel(modelId: string, data: any) {
    return request({
      url: `/model/${modelId}`,
      method: 'put',
      data
    })
  },

  // 删除模型
  deleteModel(modelId: string) {
    return request({
      url: `/model/${modelId}`,
      method: 'delete'
    })
  },

  // 设置模型为默认
  setDefaultModel(modelId: string) {
    return request({
      url: `/model/${modelId}/set-default`,
      method: 'put'
    })
  },

  // 获取模型厂商列表
  getVendors(params?: {
    page?: number
    page_size?: number
  }) {
    return request({
      url: '/model/vendor/list',
      method: 'get',
      params
    })
  }
}
