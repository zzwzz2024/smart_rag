<template>
  <el-pagination
    :current-page="currentPage"
    :page-size="pageSize"
    :page-sizes="pageSizes"
    layout="total, sizes, prev, pager, next, jumper"
    :total="total"
    @size-change="handleSizeChange"
    @current-change="handleCurrentChange"
    :locale="{
      total: '共 {total} 条',
      sizes: '条/页',
      prev: '上一页',
      next: '下一页',
      jumper: '前往第 {page} 页'
    }"
  />
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  currentPage: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 10
  },
  pageSizes: {
    type: Array,
    default: () => [10, 20, 50, 100]
  },
  total: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['size-change', 'current-change'])

const handleSizeChange = (size: number) => {
  emit('size-change', size)
}

const handleCurrentChange = (current: number) => {
  emit('current-change', current)
}
</script>

<style scoped>
.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>