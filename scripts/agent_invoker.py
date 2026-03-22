#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用 Agent 调用模块
可被其他测试脚本和功能复用
"""
import os
import sys
import logging
from typing import Optional, List, Dict, Any

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
    logging.info("已加载 .env 文件")
except ImportError:
    logging.warning("dotenv module not installed, using environment variables directly")

from src.xagent.executors.agent_executor import AgentExecutor
from src.xagent.core.provider_config_manager import ProviderConfigManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentInvoker:
    """通用 Agent 调用器"""
    
    def __init__(self, timeout: int = 300):
        """初始化 Agent 调用器
        
        Args:
            timeout: 超时时间（秒）
        """
        self.timeout = timeout
        self.executor = None
        self.provider_config_manager = None
    
    def initialize_provider_config(self):
        """初始化提供商配置管理器
        
        每次调用都会重新创建管理器并加载配置，确保使用最新的配置。
        """
        try:
            # 重新创建提供商配置管理器，确保读取最新配置
            self.provider_config_manager = ProviderConfigManager()
            
            # 加载配置（ProviderConfigManager 会自动检查文件修改时间）
            self.provider_config_manager.load()
            
            # 获取默认提供商
            default_config = self.provider_config_manager.get_default()
            if default_config:
                logger.info(f"默认提供商: {default_config.type} - {default_config.default_model}")
                return True
            else:
                logger.warning("未找到默认提供商配置")
                return False
        except Exception as e:
            logger.error(f"初始化提供商配置失败: {e}")
            return False
    
    def initialize_executor(self):
        """初始化 Agent 执行器
        
        每次调用都会重新初始化，确保使用最新的配置。
        """
        try:
            # 重新初始化提供商配置管理器，确保读取最新配置
            if not self.initialize_provider_config():
                logger.warning("使用默认配置初始化 Agent 执行器")
            
            # 重新初始化执行器
            self.executor = AgentExecutor(
                timeout=self.timeout,
                provider_config_manager=self.provider_config_manager
            )
            
            # 检查执行器是否可用
            if hasattr(self.executor, 'is_available') and not self.executor.is_available():
                logger.warning("Agent 执行器初始化成功，但可能不可用（缺少 API 密钥）")
            
            logger.info("Agent 执行器初始化成功")
            return True
        except Exception as e:
            logger.error(f"Agent 执行器初始化失败: {e}")
            return False
    
    def invoke_agent(self, prompt: str, conversation_history: Optional[List] = None) -> Dict:
        """调用 Agent 执行任务
        
        每次调用前都会重新加载配置，确保使用最新的提供商设置。
        
        Args:
            prompt: 提示文本
            conversation_history: 对话历史
            
        Returns:
            Dict: 执行结果，包含 success, output, error_message
        """
        # 重新初始化配置和执行器，确保使用最新的配置
        if not self.initialize_executor():
            return {
                "success": False,
                "output": "",
                "error_message": "Agent 执行器初始化失败"
            }
        
        try:
            logger.info(f"正在调用 Agent，提示长度: {len(prompt)}")
            
            # 执行 Agent（AgentExecutor.execute 是同步方法）
            result = self.executor.execute(prompt, conversation_history)
            
            # 处理结果
            response = {
                "success": result.success,
                "output": result.stdout,
                "error_message": result.error_message
            }
            
            logger.info(f"Agent 执行结果: {result.success}")
            logger.debug(f"Agent 输出: {result.stdout}")
            
            if not result.success:
                logger.error(f"Agent 执行失败: {result.error_message}")
            
            return response
            
        except Exception as e:
            logger.error(f"调用 Agent 时发生异常: {e}", exc_info=True)
            return {
                "success": False,
                "output": "",
                "error_message": f"调用 Agent 时发生异常: {str(e)}"
            }
    
    def invoke_agent_with_validation(self, prompt: str, validation_keywords: List[str]) -> Dict:
        """调用 Agent 并验证结果
        
        Args:
            prompt: 提示文本
            validation_keywords: 验证关键词列表
            
        Returns:
            Dict: 执行结果，包含 success, output, error_message, validated
        """
        result = self.invoke_agent(prompt)
        
        # 验证结果
        validated = False
        if result.get("success") and result.get("output"):
            output = result.get("output", "")
            for keyword in validation_keywords:
                if keyword in output:
                    validated = True
                    break
        
        result["validated"] = validated
        return result
    
    def get_default_provider(self) -> Optional[Dict]:
        """获取默认提供商信息
        
        Returns:
            Dict: 提供商信息，包含 type, model, api_key 等
        """
        if not self.provider_config_manager:
            if not self.initialize_provider_config():
                return None
        
        try:
            default_config = self.provider_config_manager.get_default()
            if default_config:
                return {
                    "type": default_config.type,
                    "model": default_config.default_model,
                    "api_key": "****" if default_config.api_key else None,  # 隐藏 API 密钥
                    "base_url": default_config.base_url
                }
            return None
        except Exception as e:
            logger.error(f"获取默认提供商信息失败: {e}")
            return None
    
    def reset(self):
        """重置 Agent 状态"""
        if self.executor:
            self.executor.reset()
            logger.info("Agent 状态已重置")

def test_agent_invoker():
    """测试 Agent 调用器"""
    invoker = AgentInvoker(timeout=300)
    
    # 测试获取默认提供商
    provider_info = invoker.get_default_provider()
    print(f"默认提供商信息: {provider_info}")
    
    # 测试简单任务
    prompt = "请告诉我今天的日期"
    result = invoker.invoke_agent(prompt)
    
    print(f"测试结果: {result}")
    
    if result.get("success"):
        print(f"Agent 输出: {result.get('output')}")
    else:
        print(f"Agent 执行失败: {result.get('error_message')}")

if __name__ == "__main__":
    test_agent_invoker()
