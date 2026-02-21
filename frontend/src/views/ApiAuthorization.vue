<template>
  <div class="api-auth-container">
    <div class="api-auth-header">
      <h2>API授权管理</h2>
      <div class="header-buttons">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          <span>创建授权</span>
        </el-button>
        <el-button type="info" @click="openLogDialog">
          <el-icon><View /></el-icon>
          <span>查看日志</span>
        </el-button>
      </div>
    </div>

    <!-- 创建授权对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="dialogTitle"
      width="600px"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-form-item label="供应商名称" prop="vendor_name">
          <el-input v-model="formData.vendor_name" placeholder="请输入供应商名称" />
        </el-form-item>
        <el-form-item label="供应商负责人" prop="vendor_contact">
          <el-input v-model="formData.vendor_contact" placeholder="请输入供应商负责人" />
        </el-form-item>
        <el-form-item label="联系电话" prop="contact_phone">
          <el-input v-model="formData.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="授权IP地址">
          <el-input 
            v-model="formData.authorized_ips" 
            placeholder="请输入授权IP地址，多个IP以逗号分隔"
            type="textarea"
            :rows="2"
          />
        </el-form-item>
        <el-form-item label="授权知识库" prop="knowledge_base_ids">
          <el-select
            v-model="formData.knowledge_base_ids"
            multiple
            placeholder="请选择授权知识库"
            style="width: 100%"
          >
            <el-option
              v-for="kb in knowledgeBases"
              :key="kb.id"
              :label="kb.name"
              :value="kb.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="授权开始时间" prop="start_time">
          <el-date-picker
            v-model="formData.start_time"
            type="datetime"
            placeholder="选择开始时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="授权结束时间" prop="end_time">
          <el-date-picker
            v-model="formData.end_time"
            type="datetime"
            placeholder="选择结束时间"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="saveAuthorization">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 授权列表 -->
    <div class="api-auth-list">
      <el-table v-loading="loading" :data="authorizations" style="width: 100%">
        <el-table-column prop="vendor_name" label="供应商名称" width="180" />
        <el-table-column prop="vendor_contact" label="负责人" width="150" />
        <el-table-column prop="contact_phone" label="联系电话" width="150" />
        <el-table-column label="授权知识库" width="200">
          <template #default="scope">
            <el-tooltip :content="scope.row.knowledge_base_names.join(', ')">
              <div class="kb-tags">
                <el-tag v-for="name in scope.row.knowledge_base_names.slice(0, 2)" :key="name" size="small">
                  {{ name }}
                </el-tag>
                <el-tag v-if="scope.row.knowledge_base_names.length > 2" size="small" type="info">
                  +{{ scope.row.knowledge_base_names.length - 2 }}
                </el-tag>
              </div>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="授权码" width="300">
          <template #default="scope">
            <el-tooltip content="点击复制">
              <span class="auth-code" @click="copyAuthCode(scope.row.auth_code)">
                {{ scope.row.auth_code }}
              </span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="有效期" width="200">
          <template #default="scope">
            <div>
              <div>{{ formatDate(scope.row.start_time) }}</div>
              <div>{{ formatDate(scope.row.end_time) }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="isAuthorizationValid(scope.row) ? 'success' : 'danger'">
              {{ isAuthorizationValid(scope.row) ? '有效' : '无效' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="editAuthorization(scope.row)">
              <el-icon><Edit /></el-icon>
              <span>编辑</span>
            </el-button>
            <el-button size="small" type="primary" @click="downloadApiDoc(scope.row)">
              <el-icon><Download /></el-icon>
              <span>下载文档</span>
            </el-button>
            <el-button size="small" type="danger" @click="deleteAuthorization(scope.row.id)">
              <el-icon><Delete /></el-icon>
              <span>删除</span>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="api-auth-pagination">
      <el-pagination
        v-model:current-page="pagination.currentPage"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="pagination.total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 日志查看对话框 -->
    <el-dialog
      v-model="showLogDialog"
      title="API访问日志"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-tabs v-model="activeLogTab" @tab-click="handleTabChange">
        <el-tab-pane label="日志列表" name="list">
          <div class="log-list-container">
            <div class="log-search-form">
              <el-form :inline="true" :model="logSearchForm" class="mb-4">
                <el-form-item label="开始日期">
                  <el-date-picker
                    v-model="logSearchForm.startDate"
                    type="date"
                    placeholder="选择开始日期"
                    style="width: 180px"
                  />
                </el-form-item>
                <el-form-item label="结束日期">
                  <el-date-picker
                    v-model="logSearchForm.endDate"
                    type="date"
                    placeholder="选择结束日期"
                    style="width: 180px"
                  />
                </el-form-item>
                <el-form-item label="厂商">
                  <el-select
                    v-model="logSearchForm.vendor"
                    placeholder="选择厂商"
                    style="width: 180px"
                  >
                    <el-option
                      v-for="vendor in vendorOptions"
                      :key="vendor"
                      :label="vendor"
                      :value="vendor"
                    />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="searchLogs">
                    <el-icon><Search /></el-icon>
                    <span>查询</span>
                  </el-button>
                  <el-button @click="resetLogSearch">
                    <el-icon><Refresh /></el-icon>
                    <span>重置</span>
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
            <el-table :data="logsData" style="width: 100%" v-loading="logsLoading">
              <el-table-column label="访问时间" width="200">
                <template #default="scope">
                  {{ formatDate(scope.row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column prop="auth_code" label="授权码" width="300" />
              <el-table-column prop="endpoint" label="接口名" width="200" />
              <el-table-column label="响应时间" width="120">
                <template #default="scope">
                  {{ formatResponseTime(scope.row.response_time) }}
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100" />
              <el-table-column prop="ip" label="IP地址" width="150" />
            </el-table>
            <div class="log-pagination">
              <el-pagination
                v-model:current-page="logPagination.currentPage"
                v-model:page-size="logPagination.pageSize"
                :page-sizes="[10, 20, 50, 100]"
                layout="total, sizes, prev, pager, next, jumper"
                :total="logPagination.total"
                @size-change="handleLogSizeChange"
                @current-change="handleLogCurrentChange"
              />
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="访问统计" name="chart">
          <div class="log-chart-container">
            <!-- 接口访问趋势 -->
            <el-card class="mb-4">
              <template #header>
                <div class="card-header">
                  <span>接口访问趋势</span>
                  <el-form :inline="true" :model="chartDateForm" class="chart-date-form">
                    <el-form-item label="统计天数">
                      <el-select
                        v-model="chartDateForm.days"
                        placeholder="选择统计天数"
                        style="width: 120px"
                        @change="loadAllStats"
                      >
                        <el-option label="7天" value="7" />
                        <el-option label="30天" value="30" />
                        <el-option label="90天" value="90" />
                      </el-select>
                    </el-form-item>
                  </el-form>
                </div>
              </template>
              <div id="accessChart" style="height: 400px;"></div>
            </el-card>
            
            <!-- 按厂商统计 -->
            <el-card class="mb-4">
              <template #header>
                <div class="card-header">
                  <span>按厂商统计</span>
                </div>
              </template>
              <div id="vendorChart" style="height: 400px;"></div>
            </el-card>
            
            <!-- 按接口名统计 -->
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>按接口名统计</span>
                </div>
              </template>
              <div id="endpointChart" style="height: 400px;"></div>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Search, Refresh, View } from '@element-plus/icons-vue'
import { useKbStore } from '../stores/kb'
import request from '../api/request'
import type { KnowledgeBase } from '../types'
// 引入ECharts
import * as echarts from 'echarts'

// API 接口
const apiAuthApi = {
  // 获取授权列表
  getAuthorizations(params?: any) {
    return request({
      url: '/api-auth',
      method: 'get',
      params
    })
  },
  
  // 创建授权
  createAuthorization(data: any) {
    return request({
      url: '/api-auth',
      method: 'post',
      data
    })
  },
  
  // 更新授权
  updateAuthorization(id: string, data: any) {
    return request({
      url: `/api-auth/${id}`,
      method: 'put',
      data
    })
  },
  
  // 删除授权
  deleteAuthorization(id: string) {
    return request({
      url: `/api-auth/${id}`,
      method: 'delete'
    })
  }
}

// 数据
const authorizations = ref<any[]>([])
const knowledgeBases = ref<KnowledgeBase[]>([])
const loading = ref(false)
const showCreateDialog = ref(false)
const dialogTitle = ref('创建授权')
const currentAuthorizationId = ref<string>('')

// 表单数据
const formData = ref({
  vendor_name: '',
  vendor_contact: '',
  contact_phone: '',
  authorized_ips: '',
  knowledge_base_ids: [] as string[],
  start_time: new Date(),
  end_time: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) // 默认30天后
})

// 表单验证规则
const formRules = ref({
  vendor_name: [{ required: true, message: '请输入供应商名称', trigger: 'blur' }],
  vendor_contact: [{ required: true, message: '请输入供应商负责人', trigger: 'blur' }],
  contact_phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
  knowledge_base_ids: [{ required: true, message: '请选择授权知识库', trigger: 'change' }],
  start_time: [{ required: true, message: '请选择授权开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择授权结束时间', trigger: 'change' }]
})

// 分页
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 表单引用
const formRef = ref()

// 加载授权列表
const loadAuthorizations = async () => {
  loading.value = true
  try {
    const response = await apiAuthApi.getAuthorizations({
      skip: (pagination.value.currentPage - 1) * pagination.value.pageSize,
      limit: pagination.value.pageSize
    })
    authorizations.value = response.data || response
    pagination.value.total = authorizations.value.length
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || '获取授权列表失败'
    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
  }
}

// 加载知识库列表
const loadKnowledgeBases = async () => {
  try {
    await useKbStore().getKnowledgeBases()
    knowledgeBases.value = useKbStore().knowledgeBases
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || '获取知识库列表失败'
    ElMessage.error(errorMessage)
  }
}

// 保存授权
const saveAuthorization = async () => {
  if (!formRef.value) return
  
  formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      loading.value = true
      try {
        if (currentAuthorizationId.value) {
          // 更新授权
          await apiAuthApi.updateAuthorization(currentAuthorizationId.value, formData.value)
          ElMessage.success('更新授权成功')
        } else {
          // 创建授权
          await apiAuthApi.createAuthorization(formData.value)
          ElMessage.success('创建授权成功')
        }
        showCreateDialog.value = false
        await loadAuthorizations()
        resetForm()
      } catch (error: any) {
        const errorMessage = error.response?.data?.detail || '保存授权失败'
        ElMessage.error(errorMessage)
      } finally {
        loading.value = false
      }
    }
  })
}

// 编辑授权
const editAuthorization = (authorization: any) => {
  currentAuthorizationId.value = authorization.id
  dialogTitle.value = '编辑授权'
  formData.value = {
    vendor_name: authorization.vendor_name,
    vendor_contact: authorization.vendor_contact,
    contact_phone: authorization.contact_phone,
    authorized_ips: authorization.authorized_ips,
    knowledge_base_ids: authorization.knowledge_base_ids,
    start_time: new Date(authorization.start_time),
    end_time: new Date(authorization.end_time)
  }
  showCreateDialog.value = true
}

// 删除授权
const deleteAuthorization = (id: string) => {
  ElMessageBox.confirm(
    '确定要删除这个授权吗？删除后将无法恢复。',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      loading.value = true
      try {
        await apiAuthApi.deleteAuthorization(id)
        ElMessage.success('删除授权成功')
        await loadAuthorizations()
      } catch (error: any) {
        const errorMessage = error.response?.data?.detail || '删除授权失败'
        ElMessage.error(errorMessage)
      } finally {
        loading.value = false
      }
    })
    .catch(() => {
      // 用户取消删除
    })
}

// 复制授权码
const copyAuthCode = (authCode: string) => {
  navigator.clipboard.writeText(authCode).then(() => {
    ElMessage.success('授权码已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败，请手动复制')
  })
}

// 重置表单
const resetForm = () => {
  currentAuthorizationId.value = ''
  formData.value = {
    vendor_name: '',
    vendor_contact: '',
    contact_phone: '',
    authorized_ips: '',
    knowledge_base_ids: [],
    start_time: new Date(),
    end_time: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
  }
  dialogTitle.value = '创建授权'
}

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 格式化响应时间
const formatResponseTime = (ms: number): string => {
  if (ms < 1000) {
    return `${ms}ms`
  }
  
  const totalSeconds = ms / 1000
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60
  
  let result = ''
  
  if (hours > 0) {
    result += `${hours}h `
  }
  
  if (minutes > 0 || hours > 0) {
    result += `${minutes}m `
  }
  
  // 格式化秒数，保留小数点后三位，去除末尾的零
  const secondsStr = seconds.toFixed(3).replace(/\.?0+$/, '')
  result += `${secondsStr}s`
  
  return result
}

// 判断授权是否有效
const isAuthorizationValid = (authorization: any) => {
  // 首先检查is_active状态
  if (!authorization.is_active) {
    return false
  }
  
  // 然后检查有效期
  const now = new Date()
  const startTime = new Date(authorization.start_time)
  const endTime = new Date(authorization.end_time)
  
  return now >= startTime && now <= endTime
}

// 下载接口文档
const downloadApiDoc = async (authorization: any) => {
  try {
    // 使用axios发送请求，利用拦截器自动添加认证token
    const response = await request({
      url: `/api-auth/doc/${authorization.id}`,
      method: 'get',
      responseType: 'blob' // 重要：设置响应类型为blob
    })
    
    // 生成文件名
    const vendorName = authorization.vendor_name || 'unknown'
    const today = new Date().toISOString().split('T')[0]
    const filename = `之之接口说明文档-${vendorName}-${today}.md`
    
    // 创建Blob对象
    const blob = new Blob([response], { type: 'text/markdown; charset=utf-8' })
    
    // 创建下载链接
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    
    // 模拟点击下载
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    ElMessage.success('接口文档下载中，请选择保存路径')
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || '下载接口文档失败'
    ElMessage.error(errorMessage)
  }
}

// 分页处理
const handleSizeChange = (size: number) => {
  pagination.value.pageSize = size
  loadAuthorizations()
}

const handleCurrentChange = (current: number) => {
  pagination.value.currentPage = current
  loadAuthorizations()
}

// 日志相关变量
const showLogDialog = ref(false)
const activeLogTab = ref('list')
const logsData = ref<any[]>([])
const logsLoading = ref(false)
const logPagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 日志查询表单
const logSearchForm = ref({
  startDate: null as Date | null,
  endDate: null as Date | null,
  vendor: ''
})

// 厂商选项
const vendorOptions = ref<string[]>([])

// 图表日期表单
const chartDateForm = ref({
  days: 7
})

// 加载日志数据
const loadLogs = async () => {
  logsLoading.value = true
  try {
    // 构建查询参数
    const queryData = {
      skip: (logPagination.value.currentPage - 1) * logPagination.value.pageSize,
      limit: logPagination.value.pageSize
    }
    
    // 添加日期和厂商查询条件
    if (logSearchForm.value.startDate) {
      queryData.start_date = logSearchForm.value.startDate.toISOString().split('T')[0]
    }
    if (logSearchForm.value.endDate) {
      queryData.end_date = logSearchForm.value.endDate.toISOString().split('T')[0]
    }
    if (logSearchForm.value.vendor) {
      queryData.vendor = logSearchForm.value.vendor
    }
    
    const response = await request({
      url: `/api-auth/logs/list`,
      method: 'post',
      data: queryData
    })
    logsData.value = response.logs || []
    logPagination.value.total = response.total || 0
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || '获取日志失败'
    ElMessage.error(errorMessage)
  } finally {
    logsLoading.value = false
  }
}

// 查询日志
const searchLogs = () => {
  logPagination.value.currentPage = 1
  loadLogs()
}

// 重置日志查询
const resetLogSearch = () => {
  logSearchForm.value = {
    startDate: null,
    endDate: null,
    vendor: ''
  }
  logPagination.value.currentPage = 1
  loadLogs()
}

// 日志分页处理
const handleLogSizeChange = (size: number) => {
  logPagination.value.pageSize = size
  loadLogs()
}

const handleLogCurrentChange = (current: number) => {
  logPagination.value.currentPage = current
  loadLogs()
}

// 初始化
onMounted(async () => {
  await Promise.all([
    loadKnowledgeBases(),
    loadAuthorizations()
  ])
})

// 加载统计数据
const loadStats = async () => {
  try {
    const response = await request({
      url: `/api-auth/logs/stats`,
      method: 'post',
      data: {
        days: chartDateForm.value.days
      }
    })
    
    const stats = response.stats || []
    initChart(stats)
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || '获取统计数据失败'
    ElMessage.error(errorMessage)
  }
}

// 加载厂商统计数据
const loadVendorStats = async () => {
  try {
    const response = await request({
      url: `/api-auth/logs/vendor-stats`,
      method: 'post',
      data: {
        days: chartDateForm.value.days
      }
    })
    
    const stats = response.stats || []
    initVendorChart(stats)
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || '获取厂商统计数据失败'
    ElMessage.error(errorMessage)
  }
}

// 加载接口名统计数据
const loadEndpointStats = async () => {
  try {
    const response = await request({
      url: `/api-auth/logs/endpoint-stats`,
      method: 'post',
      data: {
        days: chartDateForm.value.days
      }
    })
    
    const stats = response.stats || []
    initEndpointChart(stats)
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || '获取接口名统计数据失败'
    ElMessage.error(errorMessage)
  }
}

// 加载所有统计数据
const loadAllStats = async () => {
  await Promise.all([
    loadStats(),
    loadVendorStats(),
    loadEndpointStats()
  ])
}

// 初始化图表
let chartInstance: echarts.ECharts | null = null
let vendorChartInstance: echarts.ECharts | null = null
let endpointChartInstance: echarts.ECharts | null = null

// 初始化访问趋势图表
const initChart = (stats: any[]) => {
  nextTick(() => {
    const chartDom = document.getElementById('accessChart')
    if (!chartDom) return
    
    // 销毁旧实例
    if (chartInstance) {
      chartInstance.dispose()
    }
    
    // 创建新实例
    chartInstance = echarts.init(chartDom)
    
    // 准备数据
    const dates = stats.map(item => item.date)
    const counts = stats.map(item => item.count)
    
    // 配置项
    const option = {
      tooltip: {
        trigger: 'axis',
        formatter: '{b}: {c} 次'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: dates
      },
      yAxis: {
        type: 'value',
        minInterval: 1
      },
      series: [
        {
          name: '访问次数',
          type: 'line',
          stack: 'Total',
          data: counts,
          smooth: true,
          itemStyle: {
            color: '#409EFF'
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              {
                offset: 0,
                color: 'rgba(64, 158, 255, 0.5)'
              },
              {
                offset: 1,
                color: 'rgba(64, 158, 255, 0.1)'
              }
            ])
          }
        }
      ]
    }
    
    // 设置配置项
    chartInstance.setOption(option)
    
    // 响应式处理
    window.addEventListener('resize', () => {
      chartInstance?.resize()
    })
  })
}

// 初始化厂商统计图表
const initVendorChart = (stats: any[]) => {
  nextTick(() => {
    const chartDom = document.getElementById('vendorChart')
    if (!chartDom) return
    
    // 销毁旧实例
    if (vendorChartInstance) {
      vendorChartInstance.dispose()
    }
    
    // 创建新实例
    vendorChartInstance = echarts.init(chartDom)
    
    // 准备数据
    const vendors = stats.map(item => item.vendor)
    const counts = stats.map(item => item.count)
    
    // 配置项
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} 次 ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        data: vendors
      },
      series: [
        {
          name: '访问次数',
          type: 'pie',
          radius: '50%',
          center: ['60%', '50%'],
          data: stats.map(item => ({name: item.vendor, value: item.count})),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
    
    // 设置配置项
    vendorChartInstance.setOption(option)
    
    // 响应式处理
    window.addEventListener('resize', () => {
      vendorChartInstance?.resize()
    })
  })
}

// 初始化接口名统计图表
const initEndpointChart = (stats: any[]) => {
  nextTick(() => {
    const chartDom = document.getElementById('endpointChart')
    if (!chartDom) return
    
    // 销毁旧实例
    if (endpointChartInstance) {
      endpointChartInstance.dispose()
    }
    
    // 创建新实例
    endpointChartInstance = echarts.init(chartDom)
    
    // 准备数据
    const endpoints = stats.map(item => item.endpoint)
    const counts = stats.map(item => item.count)
    
    // 配置项
    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        formatter: '{b}: {c} 次'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: endpoints,
        axisLabel: {
          rotate: 45
        }
      },
      yAxis: {
        type: 'value',
        minInterval: 1
      },
      series: [
        {
          name: '访问次数',
          type: 'bar',
          data: counts,
          itemStyle: {
            color: '#67C23A'
          }
        }
      ]
    }
    
    // 设置配置项
    endpointChartInstance.setOption(option)
    
    // 响应式处理
    window.addEventListener('resize', () => {
      endpointChartInstance?.resize()
    })
  })
}

// 打开日志对话框时加载数据
const openLogDialog = async () => {
  showLogDialog.value = true
  
  // 加载厂商选项
  loadVendorOptions()
  
  // 加载日志数据
  await loadLogs()
  
  // 切换到图表标签时再加载统计数据
  if (activeLogTab.value === 'chart') {
    await loadAllStats()
  }
}

// 加载厂商选项
const loadVendorOptions = () => {
  // 从授权列表中提取厂商名称
  const vendors = new Set<string>()
  authorizations.value.forEach(auth => {
    if (auth.vendor_name) {
      vendors.add(auth.vendor_name)
    }
  })
  vendorOptions.value = Array.from(vendors)
}

// 监听标签切换
const handleTabChange = async (tab: any) => {
  if (tab.props.name === 'chart') {
    await loadAllStats()
  }
}
</script>

<style scoped>
.api-auth-container {
  padding: 20px 0;
}

.api-auth-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header-buttons {
  display: flex;
  gap: 10px;
}

.api-auth-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.api-auth-list {
  margin-bottom: 20px;
}

.api-auth-pagination {
  display: flex;
  justify-content: flex-end;
}

.auth-code {
  cursor: pointer;
  color: #409EFF;
  text-decoration: underline;
}

.kb-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .api-auth-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}

/* 日志相关样式 */
.log-list-container {
  margin-bottom: 20px;
}

.log-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.log-chart-container {
  margin-top: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
