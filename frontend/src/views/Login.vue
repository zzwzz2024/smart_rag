<template>
  <div class="login-container">
    <div class="login-card">
      <h2>ZZWZZ RAG 系统登录</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            type="text"
            id="username"
            v-model="username"
            required
            placeholder="请输入用户名"
          />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input
            type="password"
            id="password"
            v-model="password"
            required
            placeholder="请输入密码"
          />
        </div>
        <button
          type="submit"
          class="btn btn-primary w-full"
          :disabled="userStore.isLoading"
        >
          {{ userStore.isLoading ? '登录中...' : '登录' }}
        </button>
      </form>
      <div class="register-link">
        <p>还没有账号？<a href="#" @click.prevent="showRegister = true">立即注册</a></p>
      </div>
      <div v-if="userStore.error" class="error-message">
        {{ userStore.error }}
      </div>
    </div>

    <!-- 注册表单 -->
    <div v-if="showRegister" class="login-card register-card">
      <h2>ZZWZZ RAG 系统注册</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="reg-username">用户名</label>
          <input
            type="text"
            id="reg-username"
            v-model="regUsername"
            required
            placeholder="请输入用户名"
          />
        </div>
        <div class="form-group">
          <label for="reg-email">邮箱</label>
          <input
            type="email"
            id="reg-email"
            v-model="regEmail"
            required
            placeholder="请输入邮箱"
          />
        </div>
        <div class="form-group">
          <label for="reg-password">密码</label>
          <input
            type="password"
            id="reg-password"
            v-model="regPassword"
            required
            placeholder="请输入密码"
          />
        </div>
        <button
          type="submit"
          class="btn btn-primary w-full"
          :disabled="userStore.isLoading"
        >
          {{ userStore.isLoading ? '注册中...' : '注册' }}
        </button>
      </form>
      <div class="login-link">
        <p>已有账号？<a href="#" @click.prevent="showRegister = false">立即登录</a></p>
      </div>
      <div v-if="userStore.error" class="error-message">
        {{ userStore.error }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

// 登录表单
const username = ref('')
const password = ref('')

// 注册表单
const showRegister = ref(false)
const regUsername = ref('')
const regEmail = ref('')
const regPassword = ref('')

// 处理登录
const handleSubmit = async () => {
  try {
    await userStore.login(username.value, password.value)
    router.push('/chat')
  } catch (error) {
    console.error('登录失败:', error)
  }
}

// 处理注册
const handleRegister = async () => {
  try {
    await userStore.register(regUsername.value, regPassword.value, regEmail.value)
    router.push('/chat')
  } catch (error) {
    console.error('注册失败:', error)
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20px;
}

.login-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 30px;
  width: 100%;
  max-width: 400px;
}

.register-card {
  margin-top: 20px;
}

h2 {
  text-align: center;
  margin-bottom: 24px;
  color: #333;
}

.form-group {
  margin-bottom: 16px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

input:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.btn {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
  border: none;
}

.btn-primary:hover {
  background-color: #45a049;
}

.btn-primary:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.register-link,
.login-link {
  margin-top: 16px;
  text-align: center;
  font-size: 14px;
}

.register-link a,
.login-link a {
  color: #4CAF50;
  text-decoration: none;
  font-weight: 500;
}

.register-link a:hover,
.login-link a:hover {
  text-decoration: underline;
}

.error-message {
  margin-top: 16px;
  padding: 12px;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 4px;
  font-size: 14px;
}
</style>