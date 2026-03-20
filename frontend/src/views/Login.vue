<template>
  <div class="login-container">
    <!-- 左侧背景 -->
    <div class="login-bg">
      <div class="bg-content">
        <h1>知知检索</h1>
        <p>您的智能检索引擎，让知识搜索更简单</p>
      </div>
    </div>
    
    <!-- 右侧登录框 -->
    <div class="login-form">
      <div class="login-card" v-if="!showRegister">
<!--        <h2>知知检索登录</h2>-->
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
      <div class="login-card" v-if="showRegister">
        <h2>知知检索注册</h2>
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
  min-height: 100vh;
  padding: 0;
}

/* 左侧背景 */
.login-bg {
  flex: 1;
  background-image: url('../images/login_bg_3.jpg');
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  position: relative;
}

.login-bg::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  z-index: 1;
}

.bg-content {
  position: relative;
  z-index: 2;
  text-align: center;
}

.bg-content h1 {
  font-size: 80px;
  font-weight: bold;
  margin-bottom: 20px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.bg-content p {
  font-size: 24px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

/* 右侧登录框 */
.login-form {
  width: 550px;
  background-color: white;
  padding: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-card {
  width: 100%;
}

h2 {
  text-align: center;
  margin-bottom: 32px;
  color: #333;
  font-size: 24px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 10px;
  font-weight: 500;
  color: #555;
  font-size: 16px;
}

input {
  width: 100%;
  padding: 14px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
}

input:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
}

.btn {
  width: 100%;
  padding: 16px;
  font-size: 18px;
  border-radius: 6px;
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
  margin-top: 20px;
  text-align: center;
  font-size: 16px;
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
  margin-top: 20px;
  padding: 14px;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 6px;
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }
  
  .login-bg {
    width: 100%;
    height: 300px;
  }
  
  .login-form {
    width: 100%;
    padding: 40px;
  }
}
</style>