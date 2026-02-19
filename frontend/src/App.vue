<template>
  <router-view />
</template>

<script setup lang="ts">
// App组件
</script>

<style scoped>
#app,
.layout-container,
.el-container,
.el-main {
  height: 100vh;
  overflow: hidden;
}

/* 额外保险：全局禁止 body 滚动 */
html,
body {
  margin: 0;
  padding: 0;
  height: 100%;
  overflow: hidden;
}
</style>