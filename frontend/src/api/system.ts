import axios from 'axios'
import type { User, Role, Menu, Permission, Dictionary, DictionaryItem } from '../types/system'

// 创建axios实例
const api = axios.create({
  baseURL: '/api/system',
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 添加认证token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API请求错误:', error)
    return Promise.reject(error)
  }
)

// 1. 用户管理API
export const userApi = {
  // 获取用户列表
  getUsers: (params?: { skip?: number; limit?: number }) => {
    return api.get('/users', { params })
  },
  
  // 根据ID获取用户
  getUserById: (userId: string) => {
    return api.get(`/users/${userId}`)
  },
  
  // 创建用户
  createUser: (userData: Omit<User, 'id' | 'createdAt' | 'updatedAt'>) => {
    return api.post('/users', userData)
  },
  
  // 更新用户
  updateUser: (userId: string, userData: Partial<User>) => {
    return api.put(`/users/${userId}`, userData)
  },
  
  // 更新用户角色
  updateUserRole: (userId: string, roleId: string) => {
    return api.put(`/users/${userId}/role`, { role_id: roleId })
  },
  
  // 删除用户
  deleteUser: (userId: string) => {
    return api.delete(`/users/${userId}`)
  }
}

// 2. 角色管理API
export const roleApi = {
  // 获取角色列表
  getRoles: (params?: { skip?: number; limit?: number }) => {
    return api.get('/roles', { params })
  },
  
  // 根据ID获取角色
  getRoleById: (roleId: string) => {
    return api.get(`/roles/${roleId}`)
  },
  
  // 创建角色
  createRole: (roleData: Omit<Role, 'id' | 'createdAt' | 'updatedAt'>) => {
    return api.post('/roles', roleData)
  },
  
  // 更新角色
  updateRole: (roleId: string, roleData: Partial<Role>) => {
    return api.put(`/roles/${roleId}`, roleData)
  },
  
  // 删除角色
  deleteRole: (roleId: string) => {
    return api.delete(`/roles/${roleId}`)
  },
  
  // 为角色分配权限
  assignPermissions: (roleId: string, permissionIds: string[]) => {
    return api.post(`/roles/${roleId}/permissions`, { role_id: roleId, permission_ids: permissionIds })
  }
}

// 3. 菜单管理API
export const menuApi = {
  // 获取菜单列表
  getMenus: (params?: { skip?: number; limit?: number }) => {
    return api.get('/menus', { params })
  },
  
  // 获取菜单树结构
  getMenuTree: () => {
    return api.get('/menus/tree')
  },
  
  // 根据ID获取菜单
  getMenuById: (menuId: string) => {
    return api.get(`/menus/${menuId}`)
  },
  
  // 创建菜单
  createMenu: (menuData: Omit<Menu, 'id' | 'createdAt' | 'updatedAt'>) => {
    return api.post('/menus', menuData)
  },
  
  // 更新菜单
  updateMenu: (menuId: string, menuData: Partial<Menu>) => {
    return api.put(`/menus/${menuId}`, menuData)
  },
  
  // 删除菜单
  deleteMenu: (menuId: string) => {
    return api.delete(`/menus/${menuId}`)
  }
}

// 4. 权限管理API
export const permissionApi = {
  // 获取权限列表
  getPermissions: (params?: { skip?: number; limit?: number }) => {
    return api.get('/permissions', { params })
  },
  
  // 根据ID获取权限
  getPermissionById: (permissionId: string) => {
    return api.get(`/permissions/${permissionId}`)
  },
  
  // 创建权限
  createPermission: (permissionData: Omit<Permission, 'id' | 'createdAt' | 'updatedAt'>) => {
    return api.post('/permissions', permissionData)
  },
  
  // 更新权限
  updatePermission: (permissionId: string, permissionData: Partial<Permission>) => {
    return api.put(`/permissions/${permissionId}`, permissionData)
  },
  
  // 删除权限
  deletePermission: (permissionId: string) => {
    return api.delete(`/permissions/${permissionId}`)
  }
}

// 5. 字典管理API
export const dictionaryApi = {
  // 获取字典列表
  getDictionaries: (params?: { skip?: number; limit?: number }) => {
    return api.get('/dictionaries', { params })
  },
  
  // 根据ID获取字典
  getDictionaryById: (dictionaryId: string) => {
    return api.get(`/dictionaries/${dictionaryId}`)
  },
  
  // 根据类型获取字典
  getDictionaryByType: (dictionaryType: string) => {
    return api.get(`/dictionaries/type/${dictionaryType}`)
  },
  
  // 创建字典
  createDictionary: (dictionaryData: Omit<Dictionary, 'id' | 'createdAt' | 'updatedAt' | 'items'>) => {
    return api.post('/dictionaries', dictionaryData)
  },
  
  // 更新字典
  updateDictionary: (dictionaryId: string, dictionaryData: Partial<Dictionary>) => {
    return api.put(`/dictionaries/${dictionaryId}`, dictionaryData)
  },
  
  // 删除字典
  deleteDictionary: (dictionaryId: string) => {
    return api.delete(`/dictionaries/${dictionaryId}`)
  },
  
  // 获取字典项列表
  getDictionaryItems: (dictionaryId: string) => {
    return api.get(`/dictionaries/${dictionaryId}/items`)
  },
  
  // 创建字典项
  createDictionaryItem: (itemData: Omit<DictionaryItem, 'id' | 'createdAt' | 'updatedAt'>) => {
    return api.post('/dictionary-items', itemData)
  },
  
  // 更新字典项
  updateDictionaryItem: (itemId: string, itemData: Partial<DictionaryItem>) => {
    return api.put(`/dictionary-items/${itemId}`, itemData)
  },
  
  // 删除字典项
  deleteDictionaryItem: (itemId: string) => {
    return api.delete(`/dictionary-items/${itemId}`)
  }
}

export default {
  user: userApi,
  role: roleApi,
  menu: menuApi,
  permission: permissionApi,
  dictionary: dictionaryApi
}
