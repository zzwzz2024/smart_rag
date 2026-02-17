<template>
  <div class="chat-container">
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
            <select
              v-model="selectedKnowledgeBase"
              class="kb-select"
            >
              <option value="">选择知识库</option>
              <option
                v-for="kb in kbStore.knowledgeBases"
                :key="kb.id"
                :value="kb.id"
              >
                {{ kb.name }}
              </option>
            </select>
            <select
              v-model="selectedModel"
              class="model-select"
            >
              <option value="">选择模型</option>
              <option
                v-for="model in modelStore.chatModels"
                :key="model.id"
                :value="model.id"
              >
                {{ model.name }}
              </option>
            </select>
            <button
              class="btn btn-secondary"
              @click="startNewConversation"
            >
              新对话
            </button>
          </div>
        </div>

        <!-- 聊天消息列表 -->
        <div class="chat-messages">
          <div
            v-for="message in chatStore.messages"
            :key="message.id"
            class="chat-message"
            :class="message.role === 'user' ? 'chat-message-user' : 'chat-message-bot'"
          >
            <div class="chat-message-content">
              {{ message.content }}
              <div v-if="message.role === 'assistant' && message.confidence" class="confidence-badge">
                置信度: {{ Math.round(message.confidence * 100) }}%
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
            <span>AI 正在思考...</span>
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
            @keyup.enter.ctrl="sendMessage"
          ></textarea>
          <div class="input-actions">
            <div class="input-info">
              <span>按 Ctrl+Enter 发送消息</span>
            </div>
            <button
              class="btn btn-primary send-btn"
              @click="sendMessage"
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
import { useChatStore } from '../stores/chat'
import { useKbStore } from '../stores/kb'
import { useModelStore } from '../stores/model'
import { ElMessage } from 'element-plus'
import { chatApi } from '../api/chat'
import type { Conversation } from '../types'

const chatStore = useChatStore()
const kbStore = useKbStore()
const modelStore = useModelStore()

const inputMessage = ref('')
const selectedKnowledgeBase = ref<string | ''>('')
const selectedModel = ref<string | ''>('')

// 对话重命名相关
const editingConversationId = ref<string | null>(null)
const editTitle = ref('')
const titleInputRef = ref<HTMLInputElement | null>(null)

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
const sendMessage = async () => {
  if (!inputMessage.value.trim()) return

  const message = inputMessage.value.trim()
  inputMessage.value = ''

  try {
    const kbId = selectedKnowledgeBase.value !== '' ? selectedKnowledgeBase.value : undefined
    const modelId = selectedModel.value !== '' ? selectedModel.value : undefined

    if (!kbId || typeof kbId !== 'string' || kbId.trim() === '') {
      ElMessage.error('请先选择一个知识库')
    } else if (!modelId || typeof modelId !== 'string' || modelId.trim() === '') {
      ElMessage.error('请先选择一个模型，如果没有可用模型，请前往模型设置页面配置')
    } else {
      await chatStore.sendMessage(message, kbId, modelId)
    }
  } catch (error: any) {
    // 提取详细错误信息
    const errorMessage = error.response?.data?.detail || '发送消息失败'
    ElMessage.error(errorMessage)
  }
}

// 监听模型选择变化
watch(selectedModel, async (newModelId) => {
  if (newModelId) {
    try {
      // 从modelStore中获取模型详情
      const model = modelStore.chatModels.find(m => m.id === newModelId)
      if (model) {
        console.log('初始化模型:', model.name)
        // 调用后端API来初始化模型
        await chatApi.initializeModel(newModelId)
        console.log('模型初始化成功')
      }
    } catch (error) {
      console.error('初始化模型失败:', error)
    }
  }
})

// 加载对话历史和知识库列表
onMounted(async () => {
  try {
    await Promise.all([
      chatStore.getConversations(),
      kbStore.getKnowledgeBases(),
      modelStore.getChatModels()
    ])
  } catch (error: any) {
    // 提取详细错误信息
    const errorMessage = error.response?.data?.detail || '加载数据失败'
    ElMessage.error(errorMessage)
  }
})
</script>

<style scoped>
.chat-container {
  height: 100%;
  display: flex;
  flex-direction: column;
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

.kb-select,
.model-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

/* 聊天消息列表 */
.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chat-message {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 18px;
  word-wrap: break-word;
}

.chat-message-user {
  align-self: flex-end;
  background-color: #e3f2fd;
  border-radius: 18px 18px 4px 18px;
}

.chat-message-bot {
  align-self: flex-start;
  background-color: #f5f5f5;
  border-radius: 18px 18px 18px 4px;
}

.chat-message-content {
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 8px;
}

.confidence-badge {
  font-size: 12px;
  color: #666;
  margin-top: 8px;
  padding: 4px 8px;
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: 12px;
  display: inline-block;
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
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background-color: #f5f5f5;
  border-radius: 18px 18px 18px 4px;
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

.send-btn {
  padding: 8px 20px;
  font-size: 14px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
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