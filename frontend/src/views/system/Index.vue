<template>
  <div class="system-container">
    <div class="system-content">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// 初始化
onMounted(() => {
  // 如果当前路径是/system但没有子路径，重定向到/system/users
  if (route.path === '/system') {
    router.push('/system/users')
  }
})

</script>

<style scoped>
.system-container {
  padding: 20px 0;
}

.system-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 24px;
  min-height: 600px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .system-content {
    padding: 16px;
  }
}
</style>