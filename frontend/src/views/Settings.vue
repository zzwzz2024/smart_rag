<template>
  <div class="settings-container">
    <h2>系统设置</h2>
    <div class="settings-card">
      <h3>用户设置</h3>
      <div class="settings-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            type="text"
            id="username"
            :value="userStore.user?.username || ''"
            disabled
          />
        </div>
        <div class="form-group">
          <label for="email">邮箱</label>
          <input
            type="email"
            id="email"
            :value="userStore.user?.email || ''"
            disabled
          />
        </div>
        <div class="form-group">
          <label for="password">修改密码</label>
          <input
            type="password"
            id="password"
            v-model="newPassword"
            placeholder="请输入新密码"
          />
        </div>
        <button
          class="btn btn-primary"
          @click="changePassword"
          :disabled="!newPassword.trim()"
        >
          修改密码
        </button>
      </div>
    </div>

    <div class="settings-card">
      <h3>系统设置</h3>
      <div class="settings-form">
        <div class="form-group">
          <label for="api-url">API 地址</label>
          <input
            type="text"
            id="api-url"
            v-model="apiUrl"
            placeholder="请输入 API 地址"
          />
        </div>
        <div class="form-group">
          <label for="model-select">AI 模型</label>
          <select id="model-select" v-model="selectedModel">
            <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
            <option value="gpt-4">GPT-4</option>
            <option value="gpt-4o">GPT-4o</option>
          </select>
        </div>
        <button class="btn btn-primary" @click="saveSettings">
          保存设置
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()

const newPassword = ref('')
const apiUrl = ref('http://localhost:8000')
const selectedModel = ref('gpt-3.5-turbo')

// 修改密码
const changePassword = async () => {
  if (!newPassword.value.trim()) return
  try {
    // 这里需要实现修改密码的API调用
    console.log('修改密码:', newPassword.value)
    alert('密码修改成功')
    newPassword.value = ''
  } catch (error) {
    console.error('修改密码失败:', error)
    alert('密码修改失败')
  }
}

// 保存设置
const saveSettings = () => {
  try {
    // 这里需要实现保存设置的API调用
    console.log('保存设置:', {
      apiUrl: apiUrl.value,
      model: selectedModel.value
    })
    alert('设置保存成功')
  } catch (error) {
    console.error('保存设置失败:', error)
    alert('设置保存失败')
  }
}

// 加载用户信息
onMounted(async () => {
  try {
    await userStore.getCurrentUser()
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
})
</script>

<style scoped>
.settings-container {
  padding: 20px 0;
}

.settings-container h2 {
  margin-bottom: 24px;
  font-size: 20px;
  font-weight: 600;
}

.settings-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.settings-card h3 {
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #666;
}

.form-group input,
.form-group select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.form-group input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.btn-primary {
  align-self: flex-start;
  padding: 10px 20px;
  font-size: 14px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  opacity: 0.9;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-container {
    padding: 10px 0;
  }

  .settings-card {
    padding: 16px;
  }

  .btn-primary {
    align-self: stretch;
  }
}
</style>