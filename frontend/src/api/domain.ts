import request from './request'

// interface Domain {
//   id: string
//   name: string
//   description: string
//   created_at: string
//   updated_at: string
// }

interface DomainCreate {
  name: string
  description?: string
}

interface DomainUpdate {
  name?: string
  description?: string
}

export const domainApi = {
  // 获取领域列表
  getDomains() {
    return request({
      url: '/domain',
      method: 'get'
    })
  },

  // 获取领域详情
  getDomain(domainId: string) {
    return request({
      url: `/domain/${domainId}`,
      method: 'get'
    })
  },

  // 创建领域
  createDomain(data: DomainCreate) {
    return request({
      url: '/domain',
      method: 'post',
      data
    })
  },

  // 更新领域
  updateDomain(domainId: string, data: DomainUpdate) {
    return request({
      url: `/domain/${domainId}`,
      method: 'put',
      data
    })
  },

  // 删除领域
  deleteDomain(domainId: string) {
    return request({
      url: `/domain/${domainId}`,
      method: 'delete'
    })
  }
}
