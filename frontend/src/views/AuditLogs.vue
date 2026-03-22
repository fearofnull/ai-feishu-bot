<template>
  <div class="audit-logs-container">
    <div class="audit-logs-header">
      <h1>审计日志</h1>
      <p>查看系统审计日志记录，包括用户操作、安全事件和系统活动。</p>
    </div>
    
    <div class="filter-container">
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
        @change="loadAuditLogs"
        class="filter-item"
      />
      <el-select v-model="sourceFilter" placeholder="来源" @change="loadAuditLogs" class="filter-item">
        <el-option label="全部" value="" />
        <el-option label="React Agent" value="react_agent" />
        <el-option label="Qwen CLI" value="qwen-cli" />
        <el-option label="Claude CLI" value="claude-cli" />
        <el-option label="Gemini CLI" value="gemini-cli" />
      </el-select>
      <el-input
        v-model="searchKeyword"
        placeholder="搜索关键词"
        clearable
        @keyup.enter="loadAuditLogs"
        class="filter-item search-input"
      >
        <template #append>
          <el-button @click="loadAuditLogs"><el-icon><Search /></el-icon></el-button>
        </template>
      </el-input>
    </div>

    <el-table
      :data="auditLogs"
      style="width: 100%"
      :loading="loading"
      stripe
    >
      <el-table-column prop="timestamp" label="时间" width="200">
        <template #default="scope">
          {{ formatDate(scope.row.timestamp) }}
        </template>
      </el-table-column>
      <el-table-column prop="user_id" label="用户ID" width="150" />
      <el-table-column prop="username" label="用户名" width="150" />
      <el-table-column prop="source" label="来源" width="120" />
      <el-table-column prop="action" label="操作" width="100" />
      <el-table-column prop="layer" label="层级" width="80" />
      <el-table-column prop="user_input_length" label="输入长度" width="100" />
      <el-table-column prop="response_length" label="响应长度" width="100" />
      <el-table-column prop="metadata" label="详情" min-width="300">
        <template #default="scope">
          <div class="metadata-content">
            <div v-if="scope.row.metadata.user_input_preview" class="metadata-item">
              <span class="metadata-label">输入:</span>
              <span class="metadata-value">{{ scope.row.metadata.user_input_preview }}</span>
            </div>
            <div v-if="scope.row.metadata.response_preview" class="metadata-item">
              <span class="metadata-label">响应:</span>
              <span class="metadata-value">{{ scope.row.metadata.response_preview }}</span>
            </div>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import apiClient from '../api/client'

export default {
  name: 'AuditLogs',
  components: {
    Search
  },
  setup() {
    const auditLogs = ref([])
    const loading = ref(false)
    const currentPage = ref(1)
    const pageSize = ref(20)
    const total = ref(0)
    const dateRange = ref([])
    const sourceFilter = ref('')
    const searchKeyword = ref('')

    const loadAuditLogs = async () => {
      loading.value = true
      try {
        console.log('开始加载审计日志...')
        console.log('当前页码:', currentPage.value)
        console.log('每页大小:', pageSize.value)
        console.log('日期范围:', dateRange.value)
        console.log('来源筛选:', sourceFilter.value)
        console.log('搜索关键词:', searchKeyword.value)
        
        const response = await apiClient.get('/audit-logs', {
          params: {
            page: currentPage.value,
            page_size: pageSize.value,
            start_date: dateRange.value[0] || undefined,
            end_date: dateRange.value[1] || undefined,
            source: sourceFilter.value || undefined,
            keyword: searchKeyword.value || undefined
          }
        })
        
        console.log('API响应:', response)
        console.log('响应数据:', response.data)
        console.log('审计日志数据:', response.data.data.items)
        console.log('总记录数:', response.data.data.total)
        
        auditLogs.value = response.data.data.items
        total.value = response.data.data.total
        
        console.log('设置后的auditLogs:', auditLogs.value)
        console.log('设置后的total:', total.value)
      } catch (error) {
        console.error('加载审计日志失败:', error)
        console.error('错误详情:', error.response)
      } finally {
        loading.value = false
        console.log('加载审计日志完成')
      }
    }

    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      loadAuditLogs()
    }

    const handleCurrentChange = (current) => {
      currentPage.value = current
      loadAuditLogs()
    }

    const formatDate = (timestamp) => {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }

    onMounted(() => {
      loadAuditLogs()
    })

    return {
      auditLogs,
      loading,
      currentPage,
      pageSize,
      total,
      dateRange,
      sourceFilter,
      searchKeyword,
      loadAuditLogs,
      handleSizeChange,
      handleCurrentChange,
      formatDate
    }
  }
}
</script>

<style scoped>
.audit-logs-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.audit-logs-header {
  margin-bottom: 32px;
}

.audit-logs-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
}

.audit-logs-header p {
  font-size: 14px;
  color: #666;
  margin-bottom: 16px;
}

.filter-container {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-item {
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  min-width: 200px;
}

.metadata-content {
  font-size: 14px;
  line-height: 1.5;
}

.metadata-item {
  margin-bottom: 5px;
}

.metadata-label {
  font-weight: bold;
  margin-right: 5px;
  color: #606266;
}

.metadata-value {
  color: #303133;
  word-break: break-word;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.audit-logs-container :deep(.el-table__body tr:hover > td) {
  background-color: #e6f7ff !important;
}

.audit-logs-container :deep(.el-table) {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
}

@media (max-width: 768px) {
  .filter-container {
    flex-direction: column;
  }
  
  .filter-container > * {
    width: 100%;
  }
}
</style>