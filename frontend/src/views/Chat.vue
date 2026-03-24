<template>
  <div class="chat-container">
<!--    <div class="chat-header-top">-->
<!--      <h1>ZZZWZ RAG</h1>-->
<!--      <div class="top-actions">-->
<!--        <button class="btn btn-secondary" @click="toggleDarkMode">-->
<!--          切换暗色模式-->
<!--        </button>-->
<!--      </div>-->
<!--    </div>-->
    <div class="chat-wrapper">
      <!-- 左侧对话历史 -->
      <div class="chat-history">
        <h3>对话历史</h3>
        <div class="conversation-list">
          <div
            v-for="conversation in chatStore.conversations"
            :key="conversation.id"
            class="conversation-item"
            :class="{ active: chatStore.currentConversation?.id === conversation.id }"
            @click="selectConversation(conversation)"
          >
            <div class="conversation-info">
              <div class="conversation-title" @dblclick="startRenameConversation(conversation)">
                <span v-if="editingConversationId !== conversation.id">{{ getConversationTitle(conversation) }}</span>
                <input
                  v-else
                  v-model="editTitle"
                  class="conversation-title-input"
                  @blur="finishRenameConversation"
                  @keyup.enter="finishRenameConversation"
                  @keyup.esc="cancelRenameConversation"
                  ref="titleInputRef"
                />
              </div>
              <div class="conversation-time">
                {{ formatTime(conversation.created_at) }}
              </div>
            </div>
            <div class="conversation-actions">
              <button
                class="pin-conversation-btn"
                @click.stop="togglePinConversation(conversation)"
                :title="conversation.pinned ? '取消置顶' : '置顶对话'"
              >
                {{ conversation.pinned ? '📌' : '📌' }}
              </button>
              <button
                class="delete-conversation-btn"
                @click.stop="deleteConversation(conversation.id as string)"
                title="删除对话"
              >
                🗑️
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧聊天区域 -->
      <div class="chat-main">
        <!-- 聊天头部 -->
        <div class="chat-header">
<!--          <h3>{{ chatStore.currentConversation ? '正在聊天' : '新对话' }}</h3>-->
          <h3>{{ chatStore.currentConversation ? `正在与${getConversationTitle(chatStore.currentConversation)}聊天` : '新对话' }}</h3>
          <div class="chat-actions">
            <div class="select-with-label">
              <label>会话轮次</label>
              <select
                v-model="contextRound"
                class="context-select"
              >
                <option value="2">2 轮</option>
                <option value="4">4 轮</option>
                <option value="6">6 轮</option>
                <option value="8">8 轮</option>
                <option value="10">10 轮</option>
              </select>
            </div>
            <button
              class="btn btn-primary"
              @click="startNewConversation"
            >
              新对话
            </button>
          </div>
        </div>

        <!-- 聊天消息列表 -->
        <div class="chat-messages" ref="chatMessagesRef">
          <div
            v-for="message in chatStore.messages"
            :key="message.id"
            class="chat-message"
            :class="message.role === 'user' ? 'chat-message-user' : 'chat-message-bot'"
          >
            <div class="chat-message-content">
              <!-- 用户消息 -->
              <div v-if="message.role === 'user'" class="user-message-bubble">
                <div class="user-message-content">{{ message.content }}</div>
                <div class="user-message-actions">
                  <button class="user-copy-button" @click="copyMessage(message.content)">
                    复制
                  </button>
                </div>
              </div>
              
              <!-- AI 消息 -->
              <div v-else class="bot-message-container">
                <!-- 步骤列表 -->
                <div v-if="showWorkflowSteps(message)" class="workflow-steps-list">
                  <ul>
                    <li v-for="(step, index) in getWorkflowSteps(message)" :key="index" class="workflow-step-item">
                      <div class="step-indicator" :class="{ 'completed': step.status === 'completed', 'current': step.status === 'running' }"></div>
                      <span class="step-text">{{ translateStepName(step.step) }}</span>
                    </li>
                    <!-- 添加完成标记 -->
                    <li v-if="isWorkflowCompleted(message)" class="workflow-step-item">
                      <div class="step-indicator completed"></div>
                      <span class="step-text">完成</span>
                    </li>
                  </ul>
                </div>
                
                <!-- 消息内容 -->
                <div v-if="message.content" class="message-text">
                  {{ formatMessageContent(message.content) }}
                </div>
                
                <!-- 置信度 -->
                <div v-if="message.confidence" class="confidence-badge" :class="{
                  'confidence-low': message.confidence < 0.5,
                  'confidence-medium': message.confidence >= 0.5 && message.confidence < 0.75,
                  'confidence-high': message.confidence >= 0.75
                }">
                  置信度：{{ Math.round(message.confidence * 100) }}%
                </div>
                
                <!-- 表格输出 -->
                <div v-if="message.table_data" class="table-container">
                  <table class="data-table">
                    <thead>
                      <tr>
                        <th v-for="(header, index) in message.table_data.headers" :key="index">{{ header }}</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, rowIndex) in message.table_data.rows" :key="rowIndex">
                        <td v-for="(cell, cellIndex) in row" :key="cellIndex">{{ cell }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                
                <!-- 操作按钮 -->
                <div class="message-actions">
                  <button class="copy-button" @click="copyMessage(message.content)">
                    复制
                  </button>
                  <div class="feedback-buttons">
                    <button 
                      class="feedback-btn feedback-positive"
                      @click="submitFeedback(message.id, 1)"
                      :class="{ 'feedback-given': message.feedback === 1 }"
                    >
                      👍
                    </button>
                    <button 
                      class="feedback-btn feedback-negative"
                      @click="submitFeedback(message.id, 0)"
                      :class="{ 'feedback-given': message.feedback === 0 }"
                    >
                      👎
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="message.role === 'assistant' && message.citations && message.citations.length > 0" class="citations">
              <h4>引用来源:</h4>
              <ul>
                <li v-for="(citation, index) in message.citations" :key="index">
                  <span class="citation-source">{{ citation.filename }}</span>
                  <span class="citation-content">{{ citation.content.substring(0, 100) }}...</span>
                </li>
              </ul>
            </div>
            <div class="chat-message-time">
              {{ formatTime(message.created_at) }}
            </div>
          </div>
          <div v-if="chatStore.isSending" class="loading-message">
            <div class="loading"></div>
            <div class="loading-content">
              <div class="loading-title">AI 正在处理...</div>
              <div v-if="chatStore.totalWorkflowSteps > 0" class="loading-progress">
                <div class="progress-dots">
                  <div 
                    v-for="(step, index) in chatStore.totalWorkflowSteps" 
                    :key="index"
                    class="progress-dot"
                    :class="{ 'active': index <= chatStore.currentWorkflowStepIndex }"
                  ></div>
                </div>
                <div class="loading-step" v-if="chatStore.currentWorkflowStep">
                  {{ chatStore.currentWorkflowStep }}
                </div>
              </div>
              <div v-else class="loading-progress">
                <div class="progress-dots">
                  <div class="progress-dot"></div>
                  <div class="progress-dot"></div>
                  <div class="progress-dot"></div>
                </div>
                <div class="loading-step">准备中...</div>
              </div>
            </div>
          </div>
          <div v-if="chatStore.messages.length === 0 && !chatStore.isSending" class="empty-chat">
            <p>开始与 AI 聊天吧！</p>
            <p>你可以选择一个知识库来获取基于特定文档的回答</p>
          </div>
        </div>

        <!-- 消息输入区域 -->
        <div class="chat-input-area">
          <textarea
            v-model="inputMessage"
            class="message-input"
            placeholder="输入消息..."
            rows="3"
            :disabled="chatStore.isSending"
            @keyup.enter.ctrl="agentChat"
          ></textarea>
          <div class="input-actions">
            <div class="input-info">
              <span>按 Ctrl+Enter 发送消息</span>
            </div>
            <button
              class="btn btn-primary send-btn"
              @click="agentChat"
              :disabled="!inputMessage.trim() || chatStore.isSending"
            >
              发送
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useChatStore } from '../stores/chat'
import { useKbStore } from '../stores/kb'
import { useModelStore } from '../stores/model'
import { ElMessage } from 'element-plus'
import { chatApi } from '../api/chat'
import { agentApi } from '../api/agent'
import type { Conversation } from '../types'

const route = useRoute()
const chatStore = useChatStore()
const kbStore = useKbStore()
const modelStore = useModelStore()

const inputMessage = ref('')

const contextRound = ref<number>(4)
const useAgent = ref<boolean>(false)

// 对话重命名相关
const editingConversationId = ref<string | null>(null)
const editTitle = ref('')
const titleInputRef = ref<HTMLInputElement | null>(null)

// 聊天消息容器引用
const chatMessagesRef = ref<HTMLElement | null>(null)

// 获取对话标题
const getConversationTitle = (conversation: Conversation): string => {
  return conversation.title || '新对话'
}

// 格式化时间
const formatTime = (timeString: string): string => {
  const date = new Date(timeString)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 选择对话
const selectConversation = async (conversation: Conversation) => {
  try {
    // 加载对话的历史消息
    await chatStore.getConversation(conversation.id)
    // 设置当前对话
    chatStore.setCurrentConversation(conversation)
    // 滚动到聊天消息底部
    scrollToBottom()
  } catch (error) {
    console.error('加载对话历史失败:', error)
  }
}

// 删除对话
const deleteConversation = async (conversationId: string) => {
  try {
    await chatStore.deleteConversation(conversationId)
  } catch (error: any) {
    // 提取详细错误信息
    const errorMessage = error.response?.data?.detail || '删除对话失败'
    ElMessage.error(errorMessage)
  }
}

// 开始重命名对话
const startRenameConversation = (conversation: Conversation) => {
  editingConversationId.value = conversation.id
  editTitle.value = conversation.title
  // 在下一个DOM更新周期聚焦输入框
  setTimeout(() => {
    titleInputRef.value?.focus()
    titleInputRef.value?.select()
  }, 100)
}

// 完成重命名对话
const finishRenameConversation = async () => {
  if (editingConversationId.value && editTitle.value.trim()) {
    try {
      await chatStore.updateConversationTitle(editingConversationId.value, editTitle.value.trim())
    } catch (error) {
      console.error('更新对话标题失败:', error)
    }
  }
  editingConversationId.value = null
}

// 取消重命名对话
const cancelRenameConversation = () => {
  editingConversationId.value = null
}

// 切换对话置顶状态
const togglePinConversation = async (conversation: Conversation) => {
  try {
    await chatStore.toggleConversationPinned(conversation.id, !conversation.pinned)
  } catch (error) {
    console.error('切换对话置顶状态失败:', error)
  }
}

// 发送消息
const agentChat = async () => {
  if (!inputMessage.value.trim()) return

  const message = inputMessage.value.trim()

  try {
    // 发送前清空输入框
    inputMessage.value = ''
    if (useAgent.value) {
      await chatStore.agentagentChatStream(message, undefined, undefined, parseInt(contextRound.value.toString()))
    } else {
      await chatStore.agentChat(message, undefined, undefined, parseInt(contextRound.value.toString()))
    }
    // 滚动到聊天消息底部
    scrollToBottom()
  } catch (error: any) {
    // 提取详细错误信息
    const errorMessage = error.response?.data?.detail || '发送消息失败'
    ElMessage.error(errorMessage)
  }
}

// 开始新对话
const startNewConversation = () => {
  // 立即创建一个新对话对象
  const newConversation: Conversation = {
    id: `temp_${Date.now()}`, // 临时ID，后端会替换
    title: '新对话',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    pinned: false
  }
  
  // 添加到对话历史
  chatStore.conversations.unshift(newConversation)
  
  // 设置为当前对话
  chatStore.setCurrentConversation(newConversation)
  
  // 重置输入状态
  inputMessage.value = ''
}

// 滚动到聊天消息底部
const scrollToBottom = () => {
  setTimeout(() => {
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
    }
  }, 100)
}

// 切换暗色模式
const toggleDarkMode = () => {
  const body = document.body
  body.classList.toggle('dark-mode')
  // 这里可以添加保存暗色模式设置的逻辑
  localStorage.setItem('darkMode', body.classList.contains('dark-mode') ? 'true' : 'false')
}

// 复制消息内容
const copyMessage = async (content: string) => {
  try {
    // 尝试使用现代的 Clipboard API
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(content)
      ElMessage.success('复制成功')
    } else {
      // 降级到传统的复制方法
      const textArea = document.createElement('textarea')
      textArea.value = content
      textArea.style.position = 'fixed'
      textArea.style.left = '-999999px'
      textArea.style.top = '-999999px'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      try {
        document.execCommand('copy')
        ElMessage.success('复制成功')
      } catch (err) {
        ElMessage.error('复制失败，请手动复制')
      } finally {
        document.body.removeChild(textArea)
      }
    }
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败，请手动复制')
  }
}

// 提交反馈
const submitFeedback = async (messageId: string, rating: number) => {
  try {
    await agentApi.submitFeedback({
      message_id: messageId,
      rating: rating
    })
    
    // 更新消息的反馈状态
    const message = chatStore.messages.find(m => m.id === messageId)
    if (message) {
      message.feedback = rating
    }
    
    ElMessage.success('反馈提交成功')
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || '反馈提交失败'
    ElMessage.error(errorMessage)
  }
}

// 格式化消息内容，确保序号正确换行
// 格式化消息内容，确保序号正确换行
const formatMessageContent = (content: string): string => {
  if (!content) return content
  let formatted = content

  // 只在编号前不是换行符时才添加换行（排除已经在行首的编号）
  // 匹配"非换行符 + 可选空白 + 数字。" 的模式
  formatted = formatted.replace(/([^\r\n\d])\s*(\d+\.\s+)/g, '$1\n$2')

  // 处理可能出现的多个连续换行
  formatted = formatted.replace(/\n{3,}/g, '\n\n')

  return formatted
}

// 检查消息是否有工作流步骤
const hasWorkflowSteps = (message: any): boolean => {
  const steps = getWorkflowSteps(message)
  return steps && steps.length > 0
}

// 检查是否显示工作流步骤（有 retrieval_info 就显示）
const showWorkflowSteps = (message: any): boolean => {
  return message.retrieval_info !== undefined && message.retrieval_info !== null
}

// 检查工作流是否完成
const isWorkflowCompleted = (message: any): boolean => {
  return message.retrieval_info?.current_state === 'completed'
}

// 获取工作流步骤
const getWorkflowSteps = (message: any): any[] => {
  // 优先从 retrieval_info 获取
  if (message.retrieval_info?.workflow_steps) {
    return message.retrieval_info.workflow_steps
  }
  // 尝试从 content 解析（兼容旧数据）
  if (message.content) {
    try {
      // 检查是否是 JSON 字符串
      if (message.content.startsWith('data:')) {
        const jsonStr = message.content.substring(5)
        const parsed = JSON.parse(jsonStr)
        if (parsed.workflow_steps) {
          return parsed.workflow_steps
        }
      }
    } catch (e) {
      // 不是 JSON 格式，忽略
    }
  }
  return []
}

// 翻译步骤名称
const translateStepName = (stepName: string): string => {
  const stepTranslations: Record<string, string> = {
    'process_query': '处理查询',
    'detect_intent': '意图识别',
    'retrieve': '检索文档',
    'rerank': '重排序',
    'generate': '生成回答',
    'validate_sql': '验证 SQL',
    'execute_sql': '执行 SQL',
    'filter_data': '过滤数据',
    'format_output': '格式化输出'
  }
  return stepTranslations[stepName] || stepName
}

// 监听消息列表变化，自动滚动到最底部
watch(() => chatStore.messages.length, () => {
  scrollToBottom()
})

// 加载数据
const loadData = async () => {
  try {
    await Promise.all([
      chatStore.getConversations(),
      modelStore.getChatModels()
    ])
    
    // 自动选择第一个对话并加载历史记录
    if (chatStore.conversations.length > 0) {
      await selectConversation(chatStore.conversations[0])
    }
  } catch (error: any) {
    // 提取详细错误信息
    const errorMessage = error.response?.data?.detail || '加载数据失败'
    ElMessage.error(errorMessage)
  }
}

// 加载对话历史和知识库列表
onMounted(async () => {
  await loadData()
})

// 监听路由变化，当检测到_refresh参数时重新加载数据
watch(
  () => route.fullPath, 
  async (newPath, oldPath) => {
    console.log('路由变化:', oldPath, '->', newPath)
    if (newPath.includes('_refresh=')) {
      console.log('检测到刷新参数，重新加载数据...')
      await loadData()
    }
  }
)
</script>

<style scoped>
.chat-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background-color: #f8f9fa;
  color: #333;
  border-bottom: 1px solid #e0e0e0;
}

.chat-header-top h1 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.top-actions {
  display: flex;
  gap: 10px;
}

.top-actions .btn {
  padding: 6px 12px;
  font-size: 14px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.top-actions .btn-secondary {
  background-color: #6c757d;
  color: white;
  border: 1px solid #6c757d;
}

.top-actions .btn-secondary:hover {
  background-color: #5a6268;
  border-color: #545b62;
}

body.dark-mode .top-actions .btn-secondary {
  background-color: #495057;
  border-color: #495057;
}

body.dark-mode .top-actions .btn-secondary:hover {
  background-color: #343a40;
  border-color: #23272b;
}

body.dark-mode .chat-header-top {
  background-color: #343a40;
  color: #e0e0e0;
  border-bottom: 1px solid #404040;
}

.chat-wrapper {
  display: flex;
  height: 100%;
  gap: 20px;
}

/* 对话历史 */
.chat-history {
  width: 300px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.chat-history h3 {
  padding: 20px;
  margin: 0;
  border-bottom: 1px solid #e0e0e0;
  font-size: 16px;
  font-weight: 600;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.conversation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 8px;
}

.conversation-item:hover {
  background-color: #f5f5f5;
}

.conversation-item.active {
  background-color: #e3f2fd;
  border-left: 3px solid #2196f3;
}

.conversation-info {
  flex: 1;
  min-width: 0;
}

.conversation-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
}

.conversation-title:hover {
  text-decoration: underline;
}

.conversation-title-input {
  font-size: 14px;
  font-weight: 500;
  padding: 2px 4px;
  border: 1px solid #2196f3;
  border-radius: 3px;
  width: 100%;
  box-sizing: border-box;
}

.conversation-time {
  font-size: 12px;
  color: #666;
}

.conversation-actions {
  display: flex;
  gap: 4px;
  align-items: center;
}

.pin-conversation-btn,
.delete-conversation-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
  opacity: 0.5;
  font-size: 14px;
}

.conversation-item:hover .pin-conversation-btn,
.conversation-item:hover .delete-conversation-btn {
  opacity: 1;
}

.pin-conversation-btn:hover {
  background-color: #fff3e0;
}

.delete-conversation-btn:hover {
  background-color: #ffebee;
}

/* 聊天主区域 */
.chat-main {
  flex: 1;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.chat-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.select-with-label {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.select-with-label label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

/* 开关样式 */
.switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #4CAF50;
}

input:checked + .slider:before {
  transform: translateX(24px);
}

body.dark-mode .slider {
  background-color: #555;
}

body.dark-mode input:checked + .slider {
  background-color: #3b82f6;
}

.kb-select,
.model-select,
.context-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-width: 120px;
}

body.dark-mode .context-select {
  background-color: #404040;
  border: 1px solid #505050;
  color: #e0e0e0;
}

/* 聊天消息列表 */
.chat-messages {
  flex: 1;
  padding: 30px 40px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background-color: #f9fafb;
}

.chat-message {
  display: flex;
  flex-direction: column;
  max-width: 100%;
}

.chat-message-user {
  align-self: flex-end;
  max-width: 70%;
}

.chat-message-bot {
  align-self: flex-start;
  max-width: 85%;
}

.chat-message-content {
  position: relative;
}

/* 用户消息气泡样式 */
.user-message-bubble {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  padding: 14px 18px;
  border-radius: 18px;
  font-size: 15px;
  line-height: 1.6;
  color: #1a1a1a;
  word-wrap: break-word;
  white-space: pre-wrap;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.user-message-content {
  word-wrap: break-word;
  white-space: pre-wrap;
}

.user-message-actions {
  display: flex;
  gap: 8px;
  align-self: flex-start;
}

.user-copy-button {
  background-color: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 6px;
  padding: 4px 12px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #555;
  opacity: 0.8;
}

.user-copy-button:hover {
  background-color: rgba(255, 255, 255, 0.9);
  opacity: 1;
  transform: scale(1.05);
}

/* AI 消息容器样式 */
.bot-message-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}


.copy-button {
  position: static;
  background-color: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 6px 14px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #555;
  opacity: 1;
}

.chat-message:hover .copy-button {
  opacity: 1;
}

.copy-button:hover {
  background-color: #e8e8e8;
  border-color: #d0d0d0;
}

body.dark-mode .copy-button {
  background-color: rgba(255, 255, 255, 0.1);
}

body.dark-mode .copy-button:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

/* 反馈按钮样式 */
.feedback-buttons {
  display: flex;
  gap: 8px;
}

.feedback-btn {
  background: none;
  border: 1px solid #e0e0e0;
  border-radius: 50%;
  width: 34px;
  height: 34px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  transition: all 0.2s ease;
}

.feedback-btn:hover {
  transform: scale(1.15);
}

.feedback-positive:hover {
  background-color: #e8f5e9;
  border-color: #4CAF50;
}

.feedback-negative:hover {
  background-color: #ffebee;
  border-color: #f44336;
}

.feedback-given.feedback-positive {
  background-color: #e8f5e9;
  border-color: #4CAF50;
  color: #4CAF50;
}

.feedback-given.feedback-negative {
  background-color: #ffebee;
  border-color: #f44336;
  color: #f44336;
}

body.dark-mode .feedback-btn {
  border-color: #555;
}

body.dark-mode .feedback-positive:hover {
  background-color: rgba(76, 175, 80, 0.2);
  border-color: #4CAF50;
}

body.dark-mode .feedback-negative:hover {
  background-color: rgba(244, 67, 54, 0.2);
  border-color: #f44336;
}

body.dark-mode .feedback-given.feedback-positive {
  background-color: rgba(76, 175, 80, 0.2);
  border-color: #4CAF50;
  color: #4CAF50;
}

body.dark-mode .feedback-given.feedback-negative {
  background-color: rgba(244, 67, 54, 0.2);
  border-color: #f44336;
  color: #f44336;
}

body.dark-mode .copy-button {
  background-color: #404040;
  border-color: #555;
  color: #e0e0e0;
}

body.dark-mode .copy-button:hover {
  background-color: #4a4a4a;
  border-color: #666;
}

.confidence-badge {
  font-size: 12px;
  font-weight: 500;
  margin-top: 8px;
  padding: 4px 8px;
  border-radius: 12px;
  display: inline-block;
  border: 1px solid transparent;
}

.confidence-low {
  background-color: #ffebee;
  color: #c62828;
  border-color: #ffcdd2;
}

.confidence-medium {
  background-color: #fff3e0;
  color: #ef6c00;
  border-color: #ffcc80;
}

.confidence-high {
  background-color: #e8f5e8;
  color: #2e7d32;
  border-color: #c8e6c9;
}

.citations {
  margin-top: 12px;
  padding: 10px;
  background-color: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  font-size: 12px;
}

.citations h4 {
  margin: 0 0 8px 0;
  font-size: 12px;
  font-weight: 600;
  color: #666;
}

/* 步骤列表样式 */
.workflow-steps-list {
  background: linear-gradient(135deg, #f1f8f4 0%, #e8f5e9 100%);
  border-radius: 12px;
  padding: 16px 20px;
  border-left: 4px solid #4CAF50;
  box-shadow: 0 2px 4px rgba(76, 175, 80, 0.1);
}

.workflow-steps-list ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.workflow-step-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  font-size: 14px;
  color: #2c3e50;
  padding: 6px 0;
  transition: all 0.3s ease;
}

.workflow-step-item:last-child {
  margin-bottom: 0;
}

.step-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #c8e6c9;
  margin-right: 12px;
  flex-shrink: 0;
  position: relative;
  transition: all 0.3s ease;
}

.step-indicator::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background-color: transparent;
  transition: all 0.3s ease;
}

.step-indicator.completed {
  background-color: #4CAF50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.15);
}

.step-indicator.completed::before {
  background-color: white;
}

.step-indicator.current {
  background-color: #66bb6a;
  animation: pulse 1.5s infinite;
}

.step-indicator.current::before {
  background-color: white;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(102, 187, 106, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(102, 187, 106, 0);
  }
}

.step-text {
  flex: 1;
  font-weight: 500;
}

.step-indicator.completed + .step-text {
  color: #2e7d32;
}

.step-indicator.current + .step-text {
  color: #1b5e20;
  font-weight: 600;
}

/* 消息文本样式 */
.message-text {
  line-height: 1.6;
  white-space: pre-wrap;
  font-size: 15px;
  color: #2c3e50;
  padding: 4px 0;
}

/* 表格容器样式 */
.table-container {
  margin: 12px 0;
  overflow-x: auto;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table th {
  background-color: #f5f5f5;
  padding: 8px 12px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
  font-weight: 600;
}

.data-table td {
  padding: 8px 12px;
  border-bottom: 1px solid #e0e0e0;
}

.data-table tr:last-child td {
  border-bottom: none;
}

/* 消息操作按钮样式 */
.message-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e0e0e0;
}

.copy-button {
  background-color: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 6px 14px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #555;
}

.copy-button:hover {
  background-color: #e8e8e8;
  border-color: #d0d0d0;
}

/* 暗色模式样式 */
body.dark-mode .workflow-steps-list {
  background: linear-gradient(135deg, #1e3a2f 0%, #1a2e2a 100%);
  border-left-color: #4CAF50;
}

body.dark-mode .workflow-step-item {
  color: #c8e6c9;
}

body.dark-mode .step-indicator {
  background-color: #2e7d32;
}

body.dark-mode .step-indicator.completed {
  background-color: #4CAF50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.3);
}

body.dark-mode .step-indicator.current {
  background-color: #66bb6a;
}

body.dark-mode .step-indicator.completed + .step-text {
  color: #81c784;
}

body.dark-mode .step-indicator.current + .step-text {
  color: #a5d6a7;
}

body.dark-mode .table-container {
  border-color: #555555;
}

body.dark-mode .data-table th {
  background-color: #333333;
  border-bottom-color: #555555;
  color: #e0e0e0;
}

body.dark-mode .data-table td {
  border-bottom-color: #555555;
  color: #e0e0e0;
}

.citations ul {
  margin: 0;
  padding-left: 16px;
}

.citations li {
  margin-bottom: 4px;
  line-height: 1.3;
}

.citation-source {
  font-weight: 600;
  color: #2196f3;
}

.citation-content {
  color: #666;
  margin-left: 4px;
}

.chat-message-time {
  font-size: 12px;
  color: #999;
  text-align: right;
}

.loading-message {
  align-self: flex-start;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px;
  background-color: #f5f5f5;
  border-radius: 18px 18px 18px 4px;
}

.loading-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.loading-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.loading-progress {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.progress-dots {
  display: flex;
  align-items: center;
  gap: 6px;
}

.progress-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #e0e0e0;
  transition: all 0.3s ease;
}

.progress-dot.active {
  background-color: #4CAF50;
  transform: scale(1.2);
}

.loading-step {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

body.dark-mode .loading-message {
  background-color: #333333;
}

body.dark-mode .loading-title {
  color: #e0e0e0;
}

body.dark-mode .loading-step {
  color: #a0a0a0;
}

body.dark-mode .progress-dot {
  background-color: #555555;
}

body.dark-mode .progress-dot.active {
  background-color: #4CAF50;
}

.empty-chat {
  align-self: center;
  text-align: center;
  color: #666;
  margin-top: 100px;
}

.empty-chat p {
  margin: 8px 0;
}

/* 消息输入区域 */
.chat-input-area {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
}

.message-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  resize: none;
  font-family: inherit;
  margin-bottom: 12px;
}

.message-input:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.input-info {
  font-size: 12px;
  color: #666;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 8px 20px;
  font-size: 14px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background-color: #45a049;
}

.btn-primary:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.send-btn {
  padding: 8px 20px;
  font-size: 14px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

/* 暗色模式 */
body.dark-mode {
  background-color: #dc3545;
  color: #e0e0e0;
}

body.dark-mode .chat-container {
  background-color: #dc3545;
}

body.dark-mode .chat-history,
body.dark-mode .chat-main {
  background-color: #2d2d2d;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

body.dark-mode .chat-history h3,
body.dark-mode .chat-header {
  border-bottom: 1px solid #404040;
}

body.dark-mode .conversation-item {
  background-color: #333333;
}

body.dark-mode .conversation-item:hover {
  background-color: #3d3d3d;
}

body.dark-mode .conversation-item.active {
  background-color: #1e3a5f;
  border-left: 3px solid #3b82f6;
}

body.dark-mode .conversation-title-input {
  background-color: #404040;
  border: 1px solid #3b82f6;
  color: #e0e0e0;
}

body.dark-mode .conversation-time {
  color: #a0a0a0;
}

body.dark-mode .kb-select,
body.dark-mode .model-select {
  background-color: #404040;
  border: 1px solid #505050;
  color: #e0e0e0;
}

body.dark-mode .chat-message-user {
  background-color: #1e3a5f;
}

body.dark-mode .chat-message-bot {
  background-color: #333333;
}

body.dark-mode .confidence-badge {
  background-color: rgba(255, 255, 255, 0.1);
  color: #a0a0a0;
}

body.dark-mode .confidence-low {
  background-color: rgba(198, 40, 40, 0.2);
  color: #ff8a80;
  border-color: rgba(198, 40, 40, 0.3);
}

body.dark-mode .confidence-medium {
  background-color: rgba(239, 108, 0, 0.2);
  color: #ffb74d;
  border-color: rgba(239, 108, 0, 0.3);
}

body.dark-mode .confidence-high {
  background-color: rgba(46, 125, 50, 0.2);
  color: #81c784;
  border-color: rgba(46, 125, 50, 0.3);
}

body.dark-mode .message-text {
  color: #e0e0e0;
}

body.dark-mode .user-message-bubble {
  background: linear-gradient(135deg, #1e3a5f 0%, #0d2137 100%);
  color: #e0e0e0;
}

body.dark-mode .workflow-steps-list {
  background: linear-gradient(135deg, #1e3a2f 0%, #1a2e2a 100%);
  border-left-color: #4CAF50;
}

body.dark-mode .workflow-step-item {
  color: #c8e6c9;
}

body.dark-mode .step-indicator {
  background-color: #2e7d32;
}

body.dark-mode .step-indicator.completed {
  background-color: #4CAF50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.3);
}

body.dark-mode .step-indicator.current {
  background-color: #66bb6a;
}

body.dark-mode .step-indicator.completed + .step-text {
  color: #81c784;
}

body.dark-mode .step-indicator.current + .step-text {
  color: #a5d6a7;
}

body.dark-mode .message-actions {
  border-top-color: #555;
}

body.dark-mode .copy-button {
  background-color: #404040;
  border-color: #555;
  color: #e0e0e0;
}

body.dark-mode .copy-button:hover {
  background-color: #4a4a4a;
  border-color: #666;
}

body.dark-mode .citations {
  background-color: rgba(255, 255, 255, 0.05);
}

body.dark-mode .citations h4 {
  color: #a0a0a0;
}

body.dark-mode .citation-source {
  color: #3b82f6;
}

body.dark-mode .citation-content {
  color: #a0a0a0;
}

body.dark-mode .chat-message-time {
  color: #808080;
}

body.dark-mode .loading-message {
  background-color: #333333;
}

body.dark-mode .empty-chat {
  color: #a0a0a0;
}

body.dark-mode .message-input {
  background-color: #404040;
  border: 1px solid #505050;
  color: #e0e0e0;
}

body.dark-mode .message-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

body.dark-mode .input-info {
  color: #a0a0a0;
}

body.dark-mode .btn {
  background-color: #3b82f6;
  color: white;
  border: none;
}

body.dark-mode .btn:hover {
  background-color: #2563eb;
}

body.dark-mode .btn-secondary {
  background-color: #4b5563;
}

body.dark-mode .btn-secondary:hover {
  background-color: #374151;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-wrapper {
    flex-direction: column;
  }

  .chat-history {
    width: 100%;
    max-height: 200px;
  }

  .chat-message {
    max-width: 90%;
  }
}
</style>