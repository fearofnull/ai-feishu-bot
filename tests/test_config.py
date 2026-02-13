"""
配置管理单元测试
测试从环境变量加载配置、配置验证和默认值设置
"""
import os
import pytest
from feishu_bot.config import BotConfig


class TestBotConfig:
    """BotConfig 测试类"""
    
    def test_from_env_with_required_fields(self, monkeypatch):
        """测试从环境变量加载必需字段"""
        # 设置环境变量
        monkeypatch.setenv("FEISHU_APP_ID", "test_app_id")
        monkeypatch.setenv("FEISHU_APP_SECRET", "test_app_secret")
        monkeypatch.setenv("TARGET_PROJECT_DIR", "/test/path")
        
        config = BotConfig.from_env()
        
        assert config.app_id == "test_app_id"
        assert config.app_secret == "test_app_secret"
        assert config.target_directory == "/test/path"
    
    def test_from_env_with_optional_fields(self, monkeypatch):
        """测试从环境变量加载可选字段"""
        monkeypatch.setenv("FEISHU_APP_ID", "test_app_id")
        monkeypatch.setenv("FEISHU_APP_SECRET", "test_app_secret")
        monkeypatch.setenv("CLAUDE_API_KEY", "test_claude_key")
        monkeypatch.setenv("GEMINI_API_KEY", "test_gemini_key")
        monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
        monkeypatch.setenv("DEFAULT_PROVIDER", "gemini")
        monkeypatch.setenv("DEFAULT_LAYER", "cli")
        
        config = BotConfig.from_env()
        
        assert config.claude_api_key == "test_claude_key"
        assert config.gemini_api_key == "test_gemini_key"
        assert config.openai_api_key == "test_openai_key"
        assert config.default_provider == "gemini"
        assert config.default_layer == "cli"
    
    def test_default_values(self, monkeypatch):
        """测试默认值设置"""
        monkeypatch.setenv("FEISHU_APP_ID", "test_app_id")
        monkeypatch.setenv("FEISHU_APP_SECRET", "test_app_secret")
        
        config = BotConfig.from_env()
        
        # 验证默认值
        assert config.ai_timeout == 600
        assert config.cache_size == 1000
        assert config.max_session_messages == 50
        assert config.session_timeout == 86400
        assert config.default_provider == "claude"
        assert config.default_layer == "api"
        assert config.log_level == "INFO"
    
    def test_validate_missing_required_fields(self):
        """测试验证缺少必需字段"""
        config = BotConfig(
            app_id="",  # 缺失
            app_secret="test_secret",
            target_directory="/test/path"
        )
        
        with pytest.raises(ValueError) as exc_info:
            config.validate()
        
        assert "FEISHU_APP_ID 未配置" in str(exc_info.value)
    
    def test_validate_invalid_provider(self):
        """测试验证无效的提供商"""
        config = BotConfig(
            app_id="test_id",
            app_secret="test_secret",
            target_directory="/test/path",
            default_provider="invalid_provider"
        )
        
        with pytest.raises(ValueError) as exc_info:
            config.validate()
        
        assert "DEFAULT_PROVIDER" in str(exc_info.value)
    
    def test_validate_invalid_layer(self):
        """测试验证无效的执行层"""
        config = BotConfig(
            app_id="test_id",
            app_secret="test_secret",
            target_directory="/test/path",
            default_layer="invalid_layer"
        )
        
        with pytest.raises(ValueError) as exc_info:
            config.validate()
        
        assert "DEFAULT_LAYER" in str(exc_info.value)
    
    def test_validate_invalid_timeout(self):
        """测试验证无效的超时时间"""
        config = BotConfig(
            app_id="test_id",
            app_secret="test_secret",
            target_directory="/test/path",
            ai_timeout=0  # 无效值
        )
        
        with pytest.raises(ValueError) as exc_info:
            config.validate()
        
        assert "AI_TIMEOUT" in str(exc_info.value)
    
    def test_validate_invalid_log_level(self):
        """测试验证无效的日志级别"""
        config = BotConfig(
            app_id="test_id",
            app_secret="test_secret",
            target_directory="/test/path",
            log_level="INVALID"
        )
        
        with pytest.raises(ValueError) as exc_info:
            config.validate()
        
        assert "LOG_LEVEL" in str(exc_info.value)
    
    def test_validate_success(self):
        """测试验证成功"""
        config = BotConfig(
            app_id="test_id",
            app_secret="test_secret",
            target_directory="/test/path"
        )
        
        # 不应该抛出异常
        config.validate()
    
    def test_has_api_key(self):
        """测试检查 API 密钥是否配置"""
        config = BotConfig(
            app_id="test_id",
            app_secret="test_secret",
            target_directory="/test/path",
            claude_api_key="test_claude_key",
            gemini_api_key=None,
            openai_api_key="test_openai_key"
        )
        
        assert config.has_api_key("claude") is True
        assert config.has_api_key("gemini") is False
        assert config.has_api_key("openai") is True
        assert config.has_api_key("unknown") is False
    
    def test_print_status(self, capsys):
        """测试打印配置状态"""
        config = BotConfig(
            app_id="test_id",
            app_secret="test_secret",
            target_directory="/test/path",
            claude_api_key="test_key"
        )
        
        config.print_status()
        
        captured = capsys.readouterr()
        assert "配置状态" in captured.out
        assert "✅ 已配置" in captured.out
        assert "DEFAULT_PROVIDER: claude" in captured.out
