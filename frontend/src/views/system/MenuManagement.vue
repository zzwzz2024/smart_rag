<template>
  <div class="menu-management-container">
    <div class="menu-management-header">
      <h3>菜单管理</h3>
      <el-button type="primary" @click="showAddMenuDialog = true">
        <el-icon><Plus /></el-icon>
        <span>添加菜单</span>
      </el-button>
    </div>
    
    <!-- 菜单树 -->
    <div class="menu-tree">
      <el-tree
        :data="menuTree"
        node-key="id"
        :default-expanded-keys="['1']"
        :props="menuProps"
        @node-click="handleNodeClick"
      >
        <template #default="{ node, data }">
          <div class="menu-node">
            <span>{{ data.name }}</span>
            <div class="menu-node-actions">
              <el-button size="small" @click.stop="editMenu(data)">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button size="small" @click.stop="addSubMenu(data)">
                <el-icon><Plus /></el-icon>
              </el-button>
              <el-button size="small" type="danger" @click.stop="deleteMenu(data.id)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </template>
      </el-tree>
    </div>
    
    <!-- 添加/编辑菜单对话框 -->
    <el-dialog
      v-model="showAddMenuDialog"
      :title="dialogTitle"
      width="500px"
    >
      <el-form :model="menuForm" :rules="menuRules" ref="menuFormRef" label-width="100px">
        <el-form-item label="菜单名称" prop="name">
          <el-input v-model="menuForm.name" placeholder="请输入菜单名称" />
        </el-form-item>
        <el-form-item label="菜单路径" prop="path">
          <el-input v-model="menuForm.path" placeholder="请输入菜单路径" />
        </el-form-item>
        <el-form-item label="组件路径" prop="component">
          <el-input v-model="menuForm.component" placeholder="请输入组件路径" />
        </el-form-item>
        <el-form-item label="菜单图标" prop="icon">
          <el-input v-model="menuForm.icon" placeholder="请输入菜单图标" />
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="menuForm.sort" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="父菜单" prop="parentId">
          <el-select v-model="menuForm.parentId" placeholder="请选择父菜单">
            <el-option label="顶级菜单" value="0" />
            <el-option
              v-for="menu in topLevelMenus"
              :key="menu.id"
              :label="menu.name"
              :value="menu.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddMenuDialog = false">取消</el-button>
          <el-button type="primary" @click="saveMenu">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { menuApi } from '../../api/system'
import type { Menu } from '../../types/system'

// 菜单数据
const menuTree = ref<any[]>([])
const loading = ref(false)

// 菜单属性
const menuProps = {
  children: 'children',
  label: 'name'
}

// 顶级菜单
const topLevelMenus = computed(() => {
  return menuTree.value.filter(menu => menu.parentId === '0')
})

// 对话框
const showAddMenuDialog = ref(false)
const dialogTitle = ref('添加菜单')
const menuForm = ref({
  id: '',
  name: '',
  path: '',
  component: '',
  icon: '',
  sort: 0,
  parentId: '0'
})
const menuFormRef = ref()

// 表单验证规则
const menuRules = {
  name: [
    { required: true, message: '请输入菜单名称', trigger: 'blur' }
  ],
  path: [
    { required: true, message: '请输入菜单路径', trigger: 'blur' }
  ],
  component: [
    { required: true, message: '请输入组件路径', trigger: 'blur' }
  ],
  icon: [
    { required: true, message: '请输入菜单图标', trigger: 'blur' }
  ],
  sort: [
    { required: true, message: '请输入排序', trigger: 'blur' }
  ]
}

// 加载菜单树
const loadMenus = async () => {
  loading.value = true
  try {
    const response = await menuApi.getMenuTree()
    menuTree.value = response
  } catch (error) {
    console.error('加载菜单失败:', error)
    ElMessage.error('加载菜单失败')
  } finally {
    loading.value = false
  }
}

// 处理节点点击
const handleNodeClick = (data: any) => {
  console.log('点击菜单:', data)
}

// 编辑菜单
const editMenu = (menu: any) => {
  menuForm.value = { ...menu }
  dialogTitle.value = '编辑菜单'
  showAddMenuDialog.value = true
}

// 添加子菜单
const addSubMenu = (parentMenu: any) => {
  menuForm.value = {
    id: '',
    name: '',
    path: '',
    component: '',
    icon: '',
    sort: 0,
    parentId: parentMenu.id
  }
  dialogTitle.value = `添加子菜单 - ${parentMenu.name}`
  showAddMenuDialog.value = true
}

// 删除菜单
const deleteMenu = (menuId: string) => {
  ElMessageBox.confirm(
    '确定要删除这个菜单吗？',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'danger'
    }
  ).then(async () => {
    try {
      await menuApi.deleteMenu(menuId)
      ElMessage.success('菜单删除成功')
      await loadMenus()
    } catch (error) {
      console.error('删除菜单失败:', error)
      ElMessage.error('删除菜单失败')
    }
  }).catch(() => {
    // 取消删除
  })
}

// 保存菜单
const saveMenu = async () => {
  if (!menuFormRef.value) return
  
  menuFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        if (menuForm.value.id) {
          // 编辑菜单
          await menuApi.updateMenu(menuForm.value.id, {
            name: menuForm.value.name,
            path: menuForm.value.path,
            component: menuForm.value.component,
            icon: menuForm.value.icon,
            sort: menuForm.value.sort,
            parentId: menuForm.value.parentId
          })
          ElMessage.success('菜单更新成功')
        } else {
          // 添加菜单
          await menuApi.createMenu({
            name: menuForm.value.name,
            path: menuForm.value.path,
            component: menuForm.value.component,
            icon: menuForm.value.icon,
            sort: menuForm.value.sort,
            parentId: menuForm.value.parentId
          })
          ElMessage.success('菜单添加成功')
        }
        showAddMenuDialog.value = false
        await loadMenus()
      } catch (error) {
        console.error('保存菜单失败:', error)
        ElMessage.error('保存菜单失败')
      }
    }
  })
}

// 初始化
onMounted(async () => {
  await loadMenus()
})
</script>

<style scoped>
.menu-management-container {
  padding: 20px 0;
}

.menu-management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.menu-management-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.menu-tree {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.menu-node {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.menu-node-actions {
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.menu-node:hover .menu-node-actions {
  opacity: 1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .menu-management-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .menu-tree {
    padding: 16px;
  }
  
  .menu-node {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .menu-node-actions {
    opacity: 1;
  }
}
</style>