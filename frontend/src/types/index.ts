// 用户类型
export interface User {
  id: number
  username: string
  email: string
  created_at: string
}

// 登录请求类型
export interface LoginRequest {
  username: string
  password: string
}

// 登录响应类型
export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

// 知识库类型
export interface KnowledgeBase {
  id: string
  name: string
  description: string
  document_count: number
  created_at: string
}

// 文档类型
export interface Document {
  id: string
  kb_id: string
  filename: string
  file_type: string
  file_size: number
  status: string
  chunk_count: number
  error_msg?: string
  created_at: string
}

// 聊天消息类型
export interface ChatMessage {
  id: number
  conversation_id: number
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  confidence?: number
  created_at: string
}

// 引用类型
export interface Citation {
  document_id: number
  filename: string
  chunk_id: string
  content: string
  score: number
}

// 对话类型
export interface Conversation {
  id: string
  user_id?: string
  title: string
  kb_id?: string
  created_at: string
  updated_at: string
  messages?: ChatMessage[]
}

// 评估类型
export interface Evaluation {
  id: number
  query: string
  reference_answer: string
  rag_answer: string
  score: number
  created_at: string
}

// API响应类型
export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
}