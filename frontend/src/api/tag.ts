import request from './request'

// interface Tag {
//   id: string
//   name: string
//   color: string
//   created_at: string
//   updated_at: string
// }

interface TagCreate {
  name: string
  color?: string
}

interface TagUpdate {
  name?: string
  color?: string
}

export const tagApi = {
  // 获取标签列表
  getTags(skip = 0, limit = 10) {
    return request({
      url: '/tag',
      method: 'get',
      params: { skip, limit }
    })
  },

  // 获取标签详情
  getTag(tagId: string) {
    return request({
      url: `/tag/${tagId}`,
      method: 'get'
    })
  },

  // 创建标签
  createTag(data: TagCreate) {
    return request({
      url: '/tag',
      method: 'post',
      data
    })
  },

  // 更新标签
  updateTag(tagId: string, data: TagUpdate) {
    return request({
      url: `/tag/${tagId}`,
      method: 'put',
      data
    })
  },

  // 删除标签
  deleteTag(tagId: string) {
    return request({
      url: `/tag/${tagId}`,
      method: 'delete'
    })
  }
}
