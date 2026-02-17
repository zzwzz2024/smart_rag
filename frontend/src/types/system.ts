// 系统设置相关类型定义

// 用户类型
export interface User {
  id: string
  username: string
  email: string
  password?: string
  hashed_password?: string
  is_active: boolean
  role: string
  role_id?: string
  createdAt: string
  updatedAt: string
}

// 角色类型
export interface Role {
  id: string
  name: string
  code: string
  description?: string
  permissions?: Permission[]
  createdAt: string
  updatedAt: string
}

// 菜单类型
export interface Menu {
  id: string
  name: string
  code: string
  path: string
  icon?: string
  parent_id?: string
  sort: number
  is_active: boolean
  children?: Menu[]
  createdAt: string
  updatedAt: string
}

// 权限类型
export interface Permission {
  id: string
  name: string
  code: string
  description?: string
  menu_id?: string
  createdAt: string
  updatedAt: string
}

// 字典类型
export interface Dictionary {
  id: string
  name: string
  type: string
  description?: string
  items?: DictionaryItem[]
  createdAt: string
  updatedAt: string
}

// 字典项类型
export interface DictionaryItem {
  id: string
  dictionary_id: string
  key: string
  value: string
  label: string
  sort: number
  is_active: boolean
  createdAt: string
  updatedAt: string
}
