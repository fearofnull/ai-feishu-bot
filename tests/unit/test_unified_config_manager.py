"""
UnifiedConfigManager 单元测试
"""
import pytest
from unittest.mock import Mock, MagicMock, patch

from src.xagent.core.unified_config_manager import (
    UnifiedConfigManager,
    ConfigLayer,
    ConfigValue
)


class TestUnifiedConfigManager:
    """UnifiedConfigManager 测试类"""
    
    @pytest.fixture
    def mock_bot_config(self):
        """创建模拟的 BotConfig"""
        config = Mock()
        config.ai_timeout = 600
        config.cache_size = 1000
        config.target_directory = "/global/dir"
        config.response_language = "en-US"
        config.default_cli_provider = "claude"
        return config
    
    @pytest.fixture
    def mock_session_manager(self):
        """创建模拟的 SessionManager"""
        with patch("src.xagent.core.unified_config_manager.ConfigManager") as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def mock_provider_manager(self):
        """创建模拟的 ProviderConfigManager"""
        with patch("src.xagent.core.unified_config_manager.ProviderConfigManager") as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def unified_config(self, mock_bot_config, mock_session_manager, mock_provider_manager):
        """创建 UnifiedConfigManager 实例"""
        return UnifiedConfigManager(
            bot_config=mock_bot_config,
            session_config_path="./data/session_configs.json",
            provider_config_path="./data/provider_configs.json"
        )
    
    def test_get_from_temp_params(self, unified_config):
        """测试从临时参数获取配置"""
        # 执行
        result = unified_config.get(
            "target_project_dir",
            session_id="user_123",
            session_type="user",
            temp_params={"target_project_dir": "/temp/dir"}
        )
        
        # 验证
        assert result == "/temp/dir"
    
    def test_get_from_session_config(self, unified_config, mock_session_manager):
        """测试从会话配置获取配置"""
        # 准备
        mock_session_config = Mock()
        mock_session_config.target_project_dir = "/session/dir"
        mock_session_manager.get_config.return_value = mock_session_config
        
        # 执行
        result = unified_config.get(
            "target_project_dir",
            session_id="user_123",
            session_type="user"
        )
        
        # 验证
        assert result == "/session/dir"
    
    def test_get_from_global_config(self, unified_config, mock_session_manager):
        """测试从全局配置获取配置"""
        # 准备
        mock_session_manager.get_config.return_value = None
        
        # 执行
        result = unified_config.get(
            "target_project_dir",
            session_id="user_123",
            session_type="user"
        )
        
        # 验证
        assert result == "/global/dir"
    
    def test_get_default_value(self, unified_config, mock_bot_config, mock_session_manager):
        """测试获取默认值"""
        # 准备
        mock_session_manager.get_config.return_value = None
        mock_bot_config.ai_timeout = None  # 全局配置为空
        
        # 执行
        result = unified_config.get(
            "ai_timeout",
            session_id="user_123",
            session_type="user"
        )
        
        # 验证
        assert result == 600  # 默认值
    
    def test_get_with_layer_temp(self, unified_config):
        """测试获取配置及来源（临时参数）"""
        # 执行
        result = unified_config.get_with_layer(
            "target_project_dir",
            session_id="user_123",
            session_type="user",
            temp_params={"target_project_dir": "/temp/dir"}
        )
        
        # 验证
        assert isinstance(result, ConfigValue)
        assert result.value == "/temp/dir"
        assert result.layer == ConfigLayer.TEMP
        assert result.source == "temp_params"
    
    def test_get_with_layer_session(self, unified_config, mock_session_manager):
        """测试获取配置及来源（会话配置）"""
        # 准备
        mock_session_config = Mock()
        mock_session_config.response_language = "zh-CN"
        mock_session_manager.get_config.return_value = mock_session_config
        
        # 执行
        result = unified_config.get_with_layer(
            "response_language",
            session_id="user_123",
            session_type="user"
        )
        
        # 验证
        assert isinstance(result, ConfigValue)
        assert result.value == "zh-CN"
        assert result.layer == ConfigLayer.SESSION
    
    def test_get_with_layer_global(self, unified_config, mock_session_manager):
        """测试获取配置及来源（全局配置）"""
        # 准备
        mock_session_manager.get_config.return_value = None
        
        # 执行
        result = unified_config.get_with_layer(
            "response_language",
            session_id="user_123",
            session_type="user"
        )
        
        # 验证
        assert isinstance(result, ConfigValue)
        assert result.value == "en-US"
        assert result.layer == ConfigLayer.GLOBAL
    
    def test_get_with_layer_default(self, unified_config, mock_bot_config, mock_session_manager):
        """测试获取配置及来源（默认值）"""
        # 准备
        mock_session_manager.get_config.return_value = None
        mock_bot_config.agent_enabled = None
        
        # 执行
        result = unified_config.get_with_layer(
            "agent_enabled",
            session_id="user_123",
            session_type="user"
        )
        
        # 验证
        assert isinstance(result, ConfigValue)
        assert result.value == True  # 默认值
        assert result.layer == ConfigLayer.DEFAULT
    
    def test_set_session_config_success(self, unified_config, mock_session_manager):
        """测试成功设置会话配置"""
        # 准备
        mock_session_config = Mock()
        mock_session_manager.get_or_create_config.return_value = mock_session_config
        
        # 执行
        result = unified_config.set_session_config(
            session_id="user_123",
            session_type="user",
            key="target_project_dir",
            value="/new/dir"
        )
        
        # 验证
        assert result is True
        assert mock_session_config.target_project_dir == "/new/dir"
        mock_session_manager.save_configs.assert_called_once()
    
    def test_set_session_config_failure(self, unified_config, mock_session_manager):
        """测试设置会话配置失败"""
        # 准备
        mock_session_manager.get_or_create_config.side_effect = Exception("Save failed")
        
        # 执行
        result = unified_config.set_session_config(
            session_id="user_123",
            session_type="user",
            key="target_project_dir",
            value="/new/dir"
        )
        
        # 验证
        assert result is False
    
    def test_is_config_command(self, unified_config, mock_session_manager):
        """测试检查是否为配置命令"""
        # 准备
        mock_session_manager.is_config_command.return_value = True
        
        # 执行
        result = unified_config.is_config_command("/setdir /path")
        
        # 验证
        assert result is True
        mock_session_manager.is_config_command.assert_called_once_with("/setdir /path")
    
    def test_handle_config_command(self, unified_config, mock_session_manager):
        """测试处理配置命令"""
        # 准备
        mock_session_manager.handle_config_command.return_value = "配置已更新"
        
        # 执行
        result = unified_config.handle_config_command(
            session_id="user_123",
            session_type="user",
            user_id="user_123",
            message="/setdir /path"
        )
        
        # 验证
        assert result == "配置已更新"
    
    def test_get_provider_config(self, unified_config, mock_provider_manager):
        """测试获取提供商配置"""
        # 准备
        mock_config = Mock()
        mock_provider_manager.get_config.return_value = mock_config
        
        # 执行
        result = unified_config.get_provider_config("openai")
        
        # 验证
        assert result == mock_config
        mock_provider_manager.get_config.assert_called_once_with("openai")
    
    def test_get_default_provider_config(self, unified_config, mock_provider_manager):
        """测试获取默认提供商配置"""
        # 准备
        mock_config = Mock()
        mock_provider_manager.get_default_config.return_value = mock_config
        
        # 执行
        result = unified_config.get_default_provider_config()
        
        # 验证
        assert result == mock_config
        mock_provider_manager.get_default_config.assert_called_once()
    
    def test_list_provider_configs(self, unified_config, mock_provider_manager):
        """测试列出所有提供商配置"""
        # 准备
        mock_provider_manager.list_configs.return_value = ["openai", "gemini", "claude"]
        
        # 执行
        result = unified_config.list_provider_configs()
        
        # 验证
        assert result == ["openai", "gemini", "claude"]
