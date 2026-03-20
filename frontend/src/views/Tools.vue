<template>
  <div class="tools-container">
    <div class="tools-header">
      <h1>工具管理</h1>
      <p>管理内置工具及其启用状态。禁用的工具将对代理不可用。</p>
      <div class="tools-actions">
        <el-button 
          type="primary" 
          @click="enableAll" 
          :disabled="loading || batchLoading || !hasDisabledTools"
        >
          全部启用
        </el-button>
        <el-button 
          type="danger" 
          @click="disableAll" 
          :disabled="loading || batchLoading || !hasEnabledTools"
        >
          全部禁用
        </el-button>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <el-icon class="loading-icon"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <div v-else-if="tools.length === 0" class="empty-container">
      <el-empty description="暂无工具" />
    </div>

    <div v-else class="tools-grid">
      <el-card 
        v-for="tool in tools" 
        :key="tool.name"
        class="tool-card"
        :class="{ 'enabled-card': tool.enabled }"
      >
        <template #header>
          <div class="card-header">
            <h3 class="tool-name">{{ tool.name }}</h3>
            <div class="status-badge" :class="{ 'enabled': tool.enabled, 'disabled': !tool.enabled }">
              {{ tool.enabled ? '已启用' : '已禁用' }}
            </div>
          </div>
        </template>
        <div class="tool-description">{{ tool.description }}</div>
        <div class="card-footer">
          <el-switch 
            v-model="tool.enabled" 
            @change="handleToggle(tool)"
            :loading="toggleLoading[tool.name]"
          />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElEmpty, ElSwitch, ElCard, ElButton, ElIcon } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import client from '@/api/client'

const authStore = useAuthStore()
const tools = ref([])
const loading = ref(false)
const batchLoading = ref(false)
const toggleLoading = ref({})

const hasDisabledTools = computed(() => {
  return tools.value.some(tool => !tool.enabled)
})

const hasEnabledTools = computed(() => {
  return tools.value.some(tool => tool.enabled)
})

const loadTools = async () => {
  loading.value = true
  try {
    const response = await client.get('/tools')
    tools.value = response.data.data
  } catch (error) {
    console.error('加载工具失败:', error)
    ElMessage.error('加载工具失败')
  } finally {
    loading.value = false
  }
}

const handleToggle = async (tool) => {
  toggleLoading.value[tool.name] = true
  try {
    const response = await client.post(`/tools/${tool.name}/toggle`)
    // 更新工具状态
    const updatedTool = response.data.data
    const index = tools.value.findIndex(t => t.name === tool.name)
    if (index !== -1) {
      tools.value[index] = updatedTool
    }
    ElMessage.success(updatedTool.enabled ? '工具已启用' : '工具已禁用')
  } catch (error) {
    console.error('切换工具状态失败:', error)
    // 恢复原始状态
    tool.enabled = !tool.enabled
    ElMessage.error('切换工具状态失败')
  } finally {
    toggleLoading.value[tool.name] = false
  }
}

const enableAll = async () => {
  batchLoading.value = true
  try {
    await client.post('/tools/enable-all')
    // 更新所有工具状态
    tools.value.forEach(tool => {
      tool.enabled = true
    })
    ElMessage.success('所有工具已启用')
  } catch (error) {
    console.error('启用所有工具失败:', error)
    ElMessage.error('启用所有工具失败')
  } finally {
    batchLoading.value = false
  }
}

const disableAll = async () => {
  batchLoading.value = true
  try {
    await client.post('/tools/disable-all')
    // 更新所有工具状态
    tools.value.forEach(tool => {
      tool.enabled = false
    })
    ElMessage.success('所有工具已禁用')
  } catch (error) {
    console.error('禁用所有工具失败:', error)
    ElMessage.error('禁用所有工具失败')
  } finally {
    batchLoading.value = false
  }
}

onMounted(() => {
  loadTools()
})
</script>

<style scoped>
.tools-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.tools-header {
  margin-bottom: 32px;
}

.tools-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
}

.tools-header p {
  font-size: 14px;
  color: #666;
  margin-bottom: 16px;
}

.tools-actions {
  display: flex;
  gap: 12px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 0;
}

.loading-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 16px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.empty-container {
  padding: 64px 0;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.tool-card {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.tool-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.enabled-card {
  border-left: 4px solid #67c23a;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tool-name {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #333;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.enabled {
  background-color: #f0f9eb;
  color: #67c23a;
}

.status-badge.disabled {
  background-color: #fef0f0;
  color: #f56c6c;
}

.tool-description {
  font-size: 14px;
  color: #666;
  margin: 16px 0;
  line-height: 1.5;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

@media (max-width: 768px) {
  .tools-container {
    padding: 16px;
  }

  .tools-grid {
    grid-template-columns: 1fr;
  }

  .tools-actions {
    flex-direction: column;
  }
}
</style>