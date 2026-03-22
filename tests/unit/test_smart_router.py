"""
SmartRouter 单元测试
"""
import pytest
from unittest.mock import Mock, MagicMock

from src.xagent.core.smart_router import SmartRouter
from src.xagent.core.executor_registry import ExecutorRegistry, ExecutorNotAvailableError
from src.xagent.models import ParsedCommand


class TestSmartRouter:
    """SmartRouter 测试类"""
    
    @pytest.fixture
    def mock_executor_registry(self):
        """创建模拟的执行器注册表"""
        registry = Mock(spec=ExecutorRegistry)
        return registry
    
    @pytest.fixture
    def mock_bot_config(self):
        """创建模拟的机器人配置"""
        config = Mock()
        config.agent_enabled = True
        return config
    
    @pytest.fixture
    def smart_router(self, mock_executor_registry, mock_bot_config):
        """创建 SmartRouter 实例"""
        return SmartRouter(
            executor_registry=mock_executor_registry,
            bot_config=mock_bot_config
        )
    
    def test_route_agent_explicit(self, smart_router, mock_executor_registry):
        """测试显式路由到 Agent"""
        # 准备
        mock_executor = Mock()
        mock_executor.get_provider_name.return_value = "agent"
        mock_executor_registry.get_executor.return_value = mock_executor
        
        parsed_command = ParsedCommand(
            provider="agent",
            execution_layer="agent",
            message="测试消息",
            explicit=True
        )
        
        # 执行
        result = smart_router.route(parsed_command)
        
        # 验证
        assert result == mock_executor
        mock_executor_registry.get_executor.assert_called_once_with("agent", "agent")
    
    def test_route_cli_explicit(self, smart_router, mock_executor_registry):
        """测试显式路由到 CLI"""
        # 准备
        mock_executor = Mock()
        mock_executor.get_provider_name.return_value = "claude-cli"
        mock_executor_registry.get_executor.return_value = mock_executor
        
        parsed_command = ParsedCommand(
            provider="claude",
            execution_layer="cli",
            message="测试消息",
            explicit=True
        )
        
        # 执行
        result = smart_router.route(parsed_command)
        
        # 验证
        assert result == mock_executor
        mock_executor_registry.get_executor.assert_called_once_with("claude", "cli")
    
    def test_route_agent_disabled(self, smart_router, mock_bot_config, mock_executor_registry):
        """测试 Agent 被禁用时路由失败"""
        # 准备
        mock_bot_config.agent_enabled = False
        
        parsed_command = ParsedCommand(
            provider="agent",
            execution_layer="agent",
            message="测试消息",
            explicit=True
        )
        
        # 执行和验证
        with pytest.raises(ExecutorNotAvailableError) as exc_info:
            smart_router.route(parsed_command)
        
        assert "Agent 功能已被管理员禁用" in str(exc_info.value)
    
    def test_route_executor_not_available(self, smart_router, mock_executor_registry):
        """测试执行器不可用时抛出异常"""
        # 准备
        mock_executor_registry.get_executor.side_effect = ExecutorNotAvailableError(
            "gemini", "cli", "Executor not found"
        )
        
        parsed_command = ParsedCommand(
            provider="gemini",
            execution_layer="cli",
            message="测试消息",
            explicit=True
        )
        
        # 执行和验证
        with pytest.raises(ExecutorNotAvailableError):
            smart_router.route(parsed_command)
    
    def test_route_default_to_agent(self, smart_router, mock_executor_registry):
        """测试默认路由到 Agent"""
        # 准备
        mock_executor = Mock()
        mock_executor.get_provider_name.return_value = "agent"
        mock_executor_registry.get_executor.return_value = mock_executor
        
        parsed_command = ParsedCommand(
            provider="agent",
            execution_layer="agent",
            message="测试消息",
            explicit=False
        )
        
        # 执行
        result = smart_router.route(parsed_command)
        
        # 验证
        assert result == mock_executor
        mock_executor_registry.get_executor.assert_called_once_with("agent", "agent")
    
    def test_get_executor_success(self, smart_router, mock_executor_registry):
        """测试成功获取执行器"""
        # 准备
        mock_executor = Mock()
        mock_executor_registry.get_executor.return_value = mock_executor
        
        # 执行
        result = smart_router.get_executor("claude", "cli")
        
        # 验证
        assert result == mock_executor
        mock_executor_registry.get_executor.assert_called_once_with("claude", "cli")
    
    def test_get_executor_not_available(self, smart_router, mock_executor_registry):
        """测试获取不存在的执行器"""
        # 准备
        mock_executor_registry.get_executor.side_effect = ExecutorNotAvailableError(
            "unknown", "cli", "Executor not found"
        )
        
        # 执行和验证
        with pytest.raises(ExecutorNotAvailableError):
            smart_router.get_executor("unknown", "cli")
