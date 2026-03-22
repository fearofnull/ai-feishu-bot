<template>
  <nav class="sidebar">
    <!-- Logo and Title -->
    <div class="sidebar-brand">
      <div class="logo-icon">
        <el-icon :size="28"><Setting /></el-icon>
      </div>
      <h1 class="app-title">飞书 AI Bot 管理</h1>
    </div>

    <!-- Navigation Links -->
    <div class="sidebar-nav">
      <router-link 
        to="/providers" 
        class="nav-link"
        active-class="nav-link-active"
      >
        <el-icon><Connection /></el-icon>
        <span>提供商配置</span>
      </router-link>
      
      <router-link 
        to="/global-config" 
        class="nav-link"
        active-class="nav-link-active"
      >
        <el-icon><Tools /></el-icon>
        <span>全局配置</span>
      </router-link>
      
      <router-link 
        to="/sessions" 
        class="nav-link"
        active-class="nav-link-active"
      >
        <el-icon><ChatDotRound /></el-icon>
        <span>会话记录</span>
      </router-link>
      
      <router-link 
        to="/configs" 
        class="nav-link"
        active-class="nav-link-active"
      >
        <el-icon><List /></el-icon>
        <span>会话配置列表</span>
      </router-link>
      
      <router-link 
        to="/cron-jobs" 
        class="nav-link"
        active-class="nav-link-active"
      >
        <el-icon><Clock /></el-icon>
        <span>定时任务</span>
      </router-link>
      
      <router-link 
        to="/tools" 
        class="nav-link"
        active-class="nav-link-active"
      >
        <el-icon><Setting /></el-icon>
        <span>工具管理</span>
      </router-link>
      
      <router-link 
        to="/audit-logs" 
        class="nav-link"
        active-class="nav-link-active"
      >
        <el-icon><DocumentCopy /></el-icon>
        <span>审计日志</span>
      </router-link>
    </div>

    <!-- Logout Button -->
    <div class="sidebar-actions">
      <el-button 
        type="danger" 
        :icon="SwitchButton"
        @click="handleLogout"
        :loading="isLoggingOut"
        class="logout-btn"
        full-width
      >
        登出
      </el-button>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { Setting, List, Tools, SwitchButton, ChatDotRound, Connection, Clock, DocumentCopy } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const isLoggingOut = ref(false)

/**
 * Handle logout action
 * Logs out user and redirects to login page
 */
const handleLogout = async () => {
  try {
    isLoggingOut.value = true
    
    // Call logout action from auth store
    await authStore.logout()
    
    // Show success message
    ElMessage.success('已成功登出')
    
    // Redirect to login page
    router.push('/login')
  } catch (error) {
    console.error('Logout failed:', error)
    ElMessage.error('登出失败，请重试')
  } finally {
    isLoggingOut.value = false
  }
}
</script>

<style scoped>
.sidebar {
  width: 240px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 4px 0 12px rgba(0, 0, 0, 0.15);
  height: 100vh;
  position: sticky;
  top: 0;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  padding: 24px 16px;
  backdrop-filter: blur(10px);
  overflow-y: auto;
}

/* Brand Section */
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 32px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: all 0.3s ease;
}

.logo-icon:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.app-title {
  font-size: 18px;
  font-weight: 600;
  color: white;
  margin: 0;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

/* Navigation Links */
.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.nav-link::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.1);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
  z-index: -1;
}

.nav-link:hover::before {
  transform: scaleX(1);
}

.nav-link:hover {
  color: white;
  background: rgba(255, 255, 255, 0.15);
}

.nav-link-active {
  color: white;
  background: rgba(255, 255, 255, 0.25);
  font-weight: 600;
}

.nav-link-active::after {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 60%;
  background: white;
  border-radius: 0 2px 2px 0;
}

/* Actions Section */
.sidebar-actions {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.logout-btn {
  font-weight: 500;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  margin-top: 16px;
}

.logout-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

/* Responsive Design */
@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    height: auto;
    flex-direction: row;
    padding: 16px;
    gap: 16px;
    overflow-x: auto;
  }

  .sidebar-brand {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
  }

  .app-title {
    font-size: 16px;
  }

  .sidebar-nav {
    flex-direction: row;
    flex: none;
  }

  .nav-link {
    padding: 10px 12px;
  }

  .nav-link span {
    display: none;
  }

  .sidebar-actions {
    margin-top: 0;
    padding-top: 0;
    border-top: none;
  }

  .logout-btn {
    margin-top: 0;
  }

  .logout-btn span {
    display: none;
  }
}

@media (max-width: 480px) {
  .sidebar {
    padding: 12px;
    gap: 8px;
  }

  .sidebar-brand {
    gap: 8px;
  }

  .app-title {
    font-size: 14px;
  }

  .sidebar-nav {
    gap: 4px;
  }
}
</style>
