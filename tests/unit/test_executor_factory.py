"""
ExecutorFactory 单元测试
"""
import pytest
from unittest.mock import Mock, patch

from src.xagent.core.executor_factory import (
    CLIExecutorFactory,
    AgentExecutorFactory,
    CLIExecutorConfig,
    AgentExecutorConfig
)


class TestCLIExecutorFactory:
    """CLIExecutorFactory 测试类"""
    
    def test_cli_configs_defined(self):
        """测试 CLI 配置已定义"""
        assert len(CLIExecutorFactory.CLI_CONFIGS) == 3
        
        providers = [cfg.provider for cfg in CLIExecutorFactory.CLI_CONFIGS]
        assert "claude" in providers
        assert "gemini" in providers
        assert "qwen" in providers
    
    def test_get_target_dir_with_specific_config(self):
        """测试从特定配置获取目标目录"""
        # 准备
        mock_config = Mock()
        mock_config.claude_cli_target_dir = "/specific/claude"
        mock_config.target_directory = "/global/dir"
        
        cli_config = CLIExecutorConfig(
            provider="claude",
            name="Test",
            executor_class=Mock(),
            command_prefixes=["@claude"],
            priority=1,
            target_dir_config="claude_cli_target_dir"
        )
        
        # 执行
        result = CLIExecutorFactory.get_target_dir(cli_config, mock_config)
        
        # 验证
        assert result == "/specific/claude"
    
    def test_get_target_dir_with_global_config(self):
        """测试从全局配置获取目标目录"""
        # 准备
        mock_config = Mock()
        mock_config.claude_cli_target_dir = None
        mock_config.target_directory = "/global/dir"
        
        cli_config = CLIExecutorConfig(
            provider="claude",
            name="Test",
            executor_class=Mock(),
            command_prefixes=["@claude"],
            priority=1,
            target_dir_config="claude_cli_target_dir"
        )
        
        # 执行
        result = CLIExecutorFactory.get_target_dir(cli_config, mock_config)
        
        # 验证
        assert result == "/global/dir"
    
    def test_get_target_dir_not_configured(self):
        """测试未配置目标目录时返回 None"""
        # 准备
        mock_config = Mock()
        mock_config.claude_cli_target_dir = None
        mock_config.target_directory = None
        
        cli_config = CLIExecutorConfig(
            provider="claude",
            name="Test",
            executor_class=Mock(),
            command_prefixes=["@claude"],
            priority=1,
            target_dir_config="claude_cli_target_dir"
        )
        
        # 执行
        result = CLIExecutorFactory.get_target_dir(cli_config, mock_config)
        
        # 验证
        assert result is None
    
    def test_create_executor_success(self):
        """测试成功创建执行器"""
        # 准备
        mock_executor_class = Mock()
        mock_executor_instance = Mock()
        mock_executor_class.return_value = mock_executor_instance
        
        cli_config = CLIExecutorConfig(
            provider="claude",
            name="Claude Code CLI",
            executor_class=mock_executor_class,
            command_prefixes=["@claude", "@code"],
            priority=1,
            target_dir_config="claude_cli_target_dir"
        )
        
        # 执行
        result = CLIExecutorFactory.create_executor(
            config=cli_config,
            target_dir="/test/dir",
            timeout=600,
            session_storage_path="./data/sessions"
        )
        
        # 验证
        assert result == mock_executor_instance
        mock_executor_class.assert_called_once_with(
            target_dir="/test/dir",
            timeout=600,
            use_native_session=True,
            session_storage_path="./data/sessions"
        )
    
    def test_create_executor_failure(self):
        """测试创建执行器失败时返回 None"""
        # 准备
        mock_executor_class = Mock()
        mock_executor_class.side_effect = Exception("Creation failed")
        
        cli_config = CLIExecutorConfig(
            provider="claude",
            name="Claude Code CLI",
            executor_class=mock_executor_class,
            command_prefixes=["@claude"],
            priority=1,
            target_dir_config="claude_cli_target_dir"
        )
        
        # 执行
        result = CLIExecutorFactory.create_executor(
            config=cli_config,
            target_dir="/test/dir",
            timeout=600,
            session_storage_path="./data/sessions"
        )
        
        # 验证
        assert result is None
    
    def test_create_metadata(self):
        """测试创建执行器元数据"""
        # 准备
        cli_config = CLIExecutorConfig(
            provider="claude",
            name="Claude Code CLI",
            executor_class=Mock(),
            command_prefixes=["@claude", "@code"],
            priority=1,
            target_dir_config="claude_cli_target_dir"
        )
        
        # 执行
        metadata = CLIExecutorFactory.create_metadata(cli_config)
        
        # 验证
        assert metadata.name == "Claude Code CLI"
        assert metadata.provider == "claude"
        assert metadata.layer == "cli"
        assert "@claude" in metadata.command_prefixes
        assert "@code" in metadata.command_prefixes
        assert metadata.priority == 1


class TestAgentExecutorFactory:
    """AgentExecutorFactory 测试类"""
    
    def test_create_executor_success(self):
        """测试成功创建 Agent 执行器"""
        # 准备
        mock_agent_executor_class = Mock()
        mock_executor_instance = Mock()
        mock_agent_executor_class.return_value = mock_executor_instance
        
        mock_provider_manager = Mock()
        
        with patch("src.xagent.core.executor_factory.AgentExecutor", mock_agent_executor_class):
            # 执行
            result = AgentExecutorFactory.create_executor(
                timeout=600,
                search_api_key="test_key",
                provider_config_manager=mock_provider_manager
            )
        
        # 验证
        assert result == mock_executor_instance
        mock_agent_executor_class.assert_called_once_with(
            timeout=600,
            search_api_key="test_key",
            provider_config_manager=mock_provider_manager
        )
    
    def test_create_executor_failure(self):
        """测试创建 Agent 执行器失败时返回 None"""
        # 准备
        mock_agent_executor_class = Mock()
        mock_agent_executor_class.side_effect = Exception("Creation failed")
        
        with patch("src.xagent.core.executor_factory.AgentExecutor", mock_agent_executor_class):
            # 执行
            result = AgentExecutorFactory.create_executor(
                timeout=600,
                search_api_key="test_key",
                provider_config_manager=Mock()
            )
        
        # 验证
        assert result is None
    
    def test_create_metadata(self):
        """测试创建 Agent 执行器元数据"""
        # 执行
        metadata = AgentExecutorFactory.create_metadata()
        
        # 验证
        assert metadata.name == "Agent"
        assert metadata.provider == "agent"
        assert metadata.layer == "agent"
        assert "@agent" in metadata.command_prefixes
        assert metadata.priority == 0  # Agent 优先级最高
