<template>
  <div class="dictionary-management">
    <div class="management-header">
      <h3>字典管理</h3>
      <el-button type="primary" @click="openAddDialog">
        <el-icon><Plus /></el-icon>
        新增字典
      </el-button>
    </div>
    
    <div class="search-container">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="字典名称">
          <el-input v-model="searchForm.name" placeholder="请输入字典名称" clearable />
        </el-form-item>
        <el-form-item label="字典英文名">
          <el-input v-model="searchForm.type" placeholder="请输入字典英文名" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <div class="table-container">
      <el-table :data="filteredDictionaries" style="width: 100%">
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column prop="name" label="字典名称" />
        <el-table-column prop="type" label="字典英文名" />
        <el-table-column prop="description" label="字典描述" />
        <el-table-column prop="items" label="字典项数量" width="120" align="center">
          <template #default="scope">
            <div 
              v-if="scope.row.items && scope.row.items.length > 0"
              style="cursor: pointer; color: #409EFF;"
              @click="openItemsDialog(scope.row)"
            >
              {{ scope.row.items.length }}
            </div>
            <div v-else>
              数据为空
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column prop="updateTime" label="更新时间" width="180" />
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="openEditDialog(scope.row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row.id)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
<!--            <el-button type="info" size="small" @click="openItemsDialog(scope.row)">
              <el-icon><List /></el-icon>
              字典项
            </el-button>-->
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="pagination.currentPage"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="filteredDictionaries.length"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 新增/编辑字典对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form :model="dictionaryForm" :rules="dictionaryRules" ref="dictionaryFormRef">
        <el-form-item label="字典名称" prop="name">
          <el-input v-model="dictionaryForm.name" placeholder="请输入字典名称" />
        </el-form-item>
        <el-form-item label="字典英文名" prop="type">
          <el-input v-model="dictionaryForm.type" placeholder="请输入字典英文名" />
        </el-form-item>
        <el-form-item label="字典描述" prop="description">
          <el-input v-model="dictionaryForm.description" placeholder="请输入字典描述" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSave">保存</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 字典项管理对话框 -->
    <el-dialog
      v-model="itemsDialogVisible"
      title="字典项管理"
      width="800px"
    >
      <div class="dictionary-items-header">
        <h4>{{ currentDictionary?.name }} - 字典项</h4>
        <el-button type="primary" @click="openAddItemDialog">
          <el-icon><Plus /></el-icon>
          新增字典项
        </el-button>
      </div>
      
      <el-table :data="currentDictionary?.items" style="width: 100%">
        <el-table-column prop="key" label="字典键" />
        <el-table-column prop="value" label="字典值" />
        <el-table-column prop="label" label="显示文本" />
        <el-table-column prop="sort" label="排序" width="80" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="openEditItemDialog(scope.row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDeleteItem(scope.row.id)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="itemsDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 新增/编辑字典项对话框 -->
    <el-dialog
      v-model="itemDialogVisible"
      :title="itemDialogTitle"
      width="500px"
    >
      <el-form :model="itemForm" :rules="itemRules" ref="itemFormRef">
        <el-form-item label="字典键" prop="key">
          <el-input v-model="itemForm.key" placeholder="请输入字典键" />
        </el-form-item>
        <el-form-item label="字典值" prop="value">
          <el-input v-model="itemForm.value" placeholder="请输入字典值" />
        </el-form-item>
        <el-form-item label="显示文本" prop="label">
          <el-input v-model="itemForm.label" placeholder="请输入显示文本" />
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="itemForm.sort" :min="0" :max="999" placeholder="请输入排序" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="itemDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveItem">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, Search, Refresh, Edit, Delete, List } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { dictionaryApi } from '../../api/system'
import type { Dictionary, DictionaryItem } from '../../types/system'

// 字典数据
const dictionaries = ref<Dictionary[]>([])
const loading = ref(false)

// 搜索表单
const searchForm = ref({
  name: '',
  type: ''
})

// 分页配置
const pagination = ref({
  currentPage: 1,
  pageSize: 10
})

// 对话框状态
const dialogVisible = ref(false)
const itemsDialogVisible = ref(false)
const itemDialogVisible = ref(false)

// 表单引用
const dictionaryFormRef = ref<FormInstance>()
const itemFormRef = ref<FormInstance>()

// 当前操作的字典
const currentDictionary = ref<Dictionary | null>(null)

// 字典表单
const dictionaryForm = ref<Partial<Dictionary>>({
  name: '',
  type: '',
  description: ''
})

// 字典项表单
const itemForm = ref<Partial<DictionaryItem>>({
  key: '',
  value: '',
  label: '',
  sort: 0,
  dictionaryId: ''
})

// 表单规则
const dictionaryRules = ref<FormRules>({
  name: [
    { required: true, message: '请输入字典名称', trigger: 'blur' },
    { min: 1, max: 50, message: '字典名称长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请输入字典英文名', trigger: 'blur' },
    { min: 1, max: 50, message: '字典英文名长度在 1 到 50 个字符', trigger: 'blur' }
  ]
})

const itemRules = ref<FormRules>({
  key: [
    { required: true, message: '请输入字典键', trigger: 'blur' },
    { min: 1, max: 50, message: '字典键长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  value: [
    { required: true, message: '请输入字典值', trigger: 'blur' },
    { min: 1, max: 100, message: '字典值长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  label: [
    { required: true, message: '请输入显示文本', trigger: 'blur' },
    { min: 1, max: 50, message: '显示文本长度在 1 到 50 个字符', trigger: 'blur' }
  ]
})

// 过滤后的字典数据
const filteredDictionaries = computed(() => {
  let result = [...dictionaries.value]
  
  // 按照搜索条件过滤
  if (searchForm.value.name) {
    result = result.filter(item => item.name.includes(searchForm.value.name))
  }
  if (searchForm.value.type) {
    result = result.filter(item => item.type.includes(searchForm.value.type))
  }
  
  return result
})

// 对话框标题
const dialogTitle = computed(() => {
  return dictionaryForm.value.id ? '编辑字典' : '新增字典'
})

const itemDialogTitle = computed(() => {
  return itemForm.value.key ? '编辑字典项' : '新增字典项'
})

// 活跃的子菜单
const activeSubMenu = computed(() => {
  return 'dictionaries'
})

// 加载字典列表
const loadDictionaries = async () => {
  loading.value = true
  try {
    const dictionariesList = await dictionaryApi.getDictionaries({
      skip: (pagination.value.currentPage - 1) * pagination.value.pageSize,
      limit: pagination.value.pageSize
    })
    
    // 为每个字典加载字典项
    const dictionariesWithItems = await Promise.all(
      dictionariesList.map(async (dictionary) => {
        try {
          const fullDictionary = await dictionaryApi.getDictionaryById(dictionary.id)
          return fullDictionary
        } catch (error) {
          console.error(`加载字典 ${dictionary.id} 的字典项失败:`, error)
          return dictionary
        }
      })
    )
    
    dictionaries.value = dictionariesWithItems
  } catch (error) {
    console.error('加载字典列表失败:', error)
    ElMessage.error('加载字典列表失败')
  } finally {
    loading.value = false
  }
}

// 打开新增对话框
const openAddDialog = () => {
  dictionaryForm.value = {
    name: '',
    type: '',
    description: ''
  }
  dialogVisible.value = true
}

// 打开编辑对话框
const openEditDialog = (dictionary: Dictionary) => {
  dictionaryForm.value = { ...dictionary }
  dialogVisible.value = true
}

// 打开字典项管理对话框
const openAddItemDialog = () => {
  if (!currentDictionary.value) return
  
  itemForm.value = {
    key: '',
    value: '',
    label: '',
    sort: 0,
    dictionaryId: currentDictionary.value.id
  }
  itemDialogVisible.value = true
}

// 打开编辑字典项对话框
const openEditItemDialog = (item: DictionaryItem) => {
  itemForm.value = { ...item }
  itemDialogVisible.value = true
}

// 打开字典项管理对话框
const openItemsDialog = async (dictionary: Dictionary) => {
  currentDictionary.value = { ...dictionary }
  // 加载字典项
  try {
    const items = await dictionaryApi.getDictionaryItems(dictionary.id)
    if (currentDictionary.value) {
      currentDictionary.value.items = items
    }
  } catch (error) {
    console.error('加载字典项失败:', error)
    ElMessage.error('加载字典项失败')
  }
  itemsDialogVisible.value = true
}

// 处理搜索
const handleSearch = () => {
  pagination.value.currentPage = 1
  loadDictionaries()
}

// 重置搜索
const resetSearch = () => {
  searchForm.value = {
    name: '',
    type: ''
  }
  pagination.value.currentPage = 1
  loadDictionaries()
}

// 处理保存字典
const handleSave = async () => {
  if (!dictionaryFormRef.value) return
  
  try {
    await dictionaryFormRef.value.validate()
    
    if (dictionaryForm.value.id) {
      // 编辑现有字典
      await dictionaryApi.updateDictionary(dictionaryForm.value.id, {
        name: dictionaryForm.value.name || '',
        type: dictionaryForm.value.type || '',
        description: dictionaryForm.value.description || ''
      })
    } else {
      // 新增字典
      await dictionaryApi.createDictionary({
        name: dictionaryForm.value.name || '',
        type: dictionaryForm.value.type || '',
        description: dictionaryForm.value.description || ''
      })
    }
    
    dialogVisible.value = false
    ElMessage.success('保存成功')
    await loadDictionaries()
  } catch (error) {
    console.error('保存字典失败:', error)
    ElMessage.error('保存字典失败')
  }
}

// 处理保存字典项
const handleSaveItem = async () => {
  if (!itemFormRef.value || !currentDictionary.value) return
  
  try {
    await itemFormRef.value.validate()
    
    if (itemForm.value.id) {
      // 编辑现有字典项
      await dictionaryApi.updateDictionaryItem(itemForm.value.id, {
        key: itemForm.value.key || '',
        value: itemForm.value.value || '',
        label: itemForm.value.label || '',
        sort: itemForm.value.sort || 0
      })
    } else {
      // 新增字典项
      await dictionaryApi.createDictionaryItem({
        key: itemForm.value.key || '',
        value: itemForm.value.value || '',
        label: itemForm.value.label || '',
        sort: itemForm.value.sort || 0,
        dictionaryId: currentDictionary.value.id
      })
    }
    
    // 重新加载字典项
    const items = await dictionaryApi.getDictionaryItems(currentDictionary.value.id)
    if (currentDictionary.value) {
      currentDictionary.value.items = items
    }
    
    itemDialogVisible.value = false
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存字典项失败:', error)
    ElMessage.error('保存字典项失败')
  }
}

// 处理删除字典
const handleDelete = (id: string) => {
  ElMessageBox.confirm('确定要删除这个字典吗？', '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await dictionaryApi.deleteDictionary(id)
      ElMessage.success('删除成功')
      await loadDictionaries()
    } catch (error) {
      console.error('删除字典失败:', error)
      ElMessage.error('删除字典失败')
    }
  }).catch(() => {
    // 取消删除
  })
}

// 处理删除字典项
const handleDeleteItem = (id: string) => {
  if (!currentDictionary.value) return
  
  ElMessageBox.confirm('确定要删除这个字典项吗？', '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await dictionaryApi.deleteDictionaryItem(id)
      // 重新加载字典项
      const items = await dictionaryApi.getDictionaryItems(currentDictionary.value!.id)
      if (currentDictionary.value) {
        currentDictionary.value.items = items
      }
      ElMessage.success('删除成功')
    } catch (error) {
      console.error('删除字典项失败:', error)
      ElMessage.error('删除字典项失败')
    }
  }).catch(() => {
    // 取消删除
  })
}

// 分页处理
const handleSizeChange = (size: number) => {
  pagination.value.pageSize = size
  loadDictionaries()
}

const handleCurrentChange = (current: number) => {
  pagination.value.currentPage = current
  loadDictionaries()
}

// 初始化
onMounted(async () => {
  await loadDictionaries()
})
</script>

<style scoped>
.dictionary-management {
  padding: 20px 0;
}

.management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.management-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.search-container {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 24px;
}

.search-form {
  display: flex;
  align-items: center;
}

.table-container {
  margin-bottom: 24px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
}

.dictionary-items-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.dictionary-items-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-form {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-form .el-form-item {
    margin-bottom: 12px;
  }
  
  .management-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .management-header .el-button {
    margin-top: 12px;
  }
}
</style>