"""
统一配置管理器模块

整合 BotConfig、ConfigManager 和 ProviderConfigManager 的功能
提供统一的配置访问接口
"""
import logging
import os
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from enum import Enum

from .config_manager import ConfigManager
from .provider_config_manager import ProviderConfigManager
from ..config import BotConfig

logger = logging.getLogger(__name__)


class ConfigLayer(Enum):
    """配置层级"""
    DEFAULT = "default"           # 默认值
    GLOBAL = "global"             # 全局配置 (BotConfig)
    PROVIDER = "provider"         # 提供商配置
    SESSION = "session"           # 会话配置 (ConfigManager)
    TEMP = "temp"                 # 临时参数


@dataclass
class ConfigValue:
    """配置值包装器"""
    value: Any
    layer: ConfigLayer
    source: str  # 配置来源描述


class UnifiedConfigManager:
    """统一配置管理器
    
    整合所有配置管理功能，提供统一的配置访问接口：
    - 配置优先级：临时参数 > 会话配置 > 全局配置 > 默认值
    - 支持配置变更通知
    - 提供配置验证和类型转换
    """
    
    # 默认配置值
    DEFAULTS = {
        "ai_timeout": 600,
        "cache_size": 1000,
        "max_session_messages": 50,
        "session_timeout": 86400,
        "response_language": "zh-CN",
        "default_cli_provider": "claude",
        "agent_enabled": True,
    }
    
    # 配置项映射：统一名称 -> 各管理器中的名称
    CONFIG_MAPPINGS = {
        "target_project_dir": {
            "session": "target_project_dir",
            "global": "target_directory",
        },
        "response_language": {
            "session": "response_language",
            "global": "response_language",
        },
        "default_cli_provider": {
            "session": "default_cli_provider",
            "global": "default_cli_provider",
        },
        "ai_timeout": {
            "global": "ai_timeout",
        },
        "cache_size": {
            "global": "cache_size",
        },
    }
    
    def __init__(
        self,
        bot_config: BotConfig,
        session_config_path: str = "./data/session_configs.json",
        provider_config_path: str = "./data/provider_configs.json"
    ):
        """初始化统一配置管理器
        
        Args:
            bot_config: 全局机器人配置
            session_config_path: 会话配置存储路径
            provider_config_path: 提供商配置存储路径
        """
        self.bot_config = bot_config
        self.session_manager = ConfigManager(
            storage_path=session_config_path,
            global_config=bot_config
        )
        self.provider_manager = ProviderConfigManager(
            storage_path=provider_config_path
        )
        
        logger.info("UnifiedConfigManager initialized")
    
    def get(
        self,
        key: str,
        session_id: Optional[str] = None,
        session_type: Optional[str] = None,
        temp_params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """获取配置值（按优先级）
        
        优先级：临时参数 > 会话配置 > 全局配置 > 默认值
        
        Args:
            key: 配置键名
            session_id: 会话 ID
            session_type: 会话类型
            temp_params: 临时参数
            
        Returns:
            配置值，如果未找到则返回 None
        """
        # 1. 检查临时参数
        if temp_params and key in temp_params:
            return temp_params[key]
        
        # 2. 检查会话配置
        if session_id and session_type:
            session_value = self._get_from_session(key, session_id, session_type)
            if session_value is not None:
                return session_value
        
        # 3. 检查全局配置
        global_value = self._get_from_global(key)
        if global_value is not None:
            return global_value
        
        # 4. 返回默认值
        return self.DEFAULTS.get(key)
    
    def get_with_layer(
        self,
        key: str,
        session_id: Optional[str] = None,
        session_type: Optional[str] = None,
        temp_params: Optional[Dict[str, Any]] = None
    ) -> ConfigValue:
        """获取配置值及其来源层级
        
        Args:
            key: 配置键名
            session_id: 会话 ID
            session_type: 会话类型
            temp_params: 临时参数
            
        Returns:
            ConfigValue 对象，包含值和来源信息
        """
        # 1. 检查临时参数
        if temp_params and key in temp_params:
            return ConfigValue(
                value=temp_params[key],
                layer=ConfigLayer.TEMP,
                source="temp_params"
            )
        
        # 2. 检查会话配置
        if session_id and session_type:
            session_value = self._get_from_session(key, session_id, session_type)
            if session_value is not None:
                return ConfigValue(
                    value=session_value,
                    layer=ConfigLayer.SESSION,
                    source=f"session:{session_id}"
                )
        
        # 3. 检查全局配置
        global_value = self._get_from_global(key)
        if global_value is not None:
            return ConfigValue(
                value=global_value,
                layer=ConfigLayer.GLOBAL,
                source="bot_config"
            )
        
        # 4. 返回默认值
        default_value = self.DEFAULTS.get(key)
        return ConfigValue(
            value=default_value,
            layer=ConfigLayer.DEFAULT,
            source="defaults"
        )
    
    def set_session_config(
        self,
        session_id: str,
        session_type: str,
        key: str,
        value: Any
    ) -> bool:
        """设置会话配置
        
        Args:
            session_id: 会话 ID
            session_type: 会话类型
            key: 配置键名
            value: 配置值
            
        Returns:
            是否设置成功
        """
        try:
            # 获取或创建会话配置
            session_config = self.session_manager.get_or_create_config(
                session_id, session_type
            )
            
            # 映射键名
            mapped_key = self._map_key_to_session(key)
            if mapped_key:
                setattr(session_config, mapped_key, value)
                self.session_manager.save_configs()
                logger.info(f"Set session config: {session_id}.{key} = {value}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to set session config: {e}")
            return False
    
    def get_effective_config(
        self,
        session_id: str,
        session_type: str,
        temp_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """获取有效配置（完整配置字典）
        
        Args:
            session_id: 会话 ID
            session_type: 会话类型
            temp_params: 临时参数
            
        Returns:
            完整的有效配置字典
        """
        # 复用 ConfigManager 的有效配置逻辑
        return self.session_manager.get_effective_config(
            session_id, session_type, temp_params
        )
    
    def _get_from_session(
        self,
        key: str,
        session_id: str,
        session_type: str
    ) -> Any:
        """从会话配置获取值"""
        try:
            session_config = self.session_manager.get_config(session_id)
            if session_config:
                mapped_key = self._map_key_to_session(key)
                if mapped_key and hasattr(session_config, mapped_key):
                    value = getattr(session_config, mapped_key)
                    # 过滤空值
                    if value is not None and value != "":
                        return value
            return None
        except Exception as e:
            logger.debug(f"Failed to get session config: {e}")
            return None
    
    def _get_from_global(self, key: str) -> Any:
        """从全局配置获取值"""
        mapped_key = self._map_key_to_global(key)
        if mapped_key and hasattr(self.bot_config, mapped_key):
            value = getattr(self.bot_config, mapped_key)
            # 过滤空值
            if value is not None and value != "":
                return value
        return None
    
    def _map_key_to_session(self, key: str) -> Optional[str]:
        """映射统一键名到会话配置键名"""
        mapping = self.CONFIG_MAPPINGS.get(key, {})
        return mapping.get("session")
    
    def _map_key_to_global(self, key: str) -> Optional[str]:
        """映射统一键名到全局配置键名"""
        mapping = self.CONFIG_MAPPINGS.get(key, {})
        return mapping.get("global")
    
    def is_config_command(self, message: str) -> bool:
        """检查是否为配置命令"""
        return self.session_manager.is_config_command(message)
    
    def handle_config_command(
        self,
        session_id: str,
        session_type: str,
        user_id: Optional[str],
        message: str
    ) -> Optional[str]:
        """处理配置命令"""
        return self.session_manager.handle_config_command(
            session_id, session_type, user_id, message
        )
    
    def get_provider_config(self, name: str) -> Optional[Any]:
        """获取提供商配置"""
        return self.provider_manager.get_config(name)
    
    def get_default_provider_config(self) -> Optional[Any]:
        """获取默认提供商配置"""
        return self.provider_manager.get_default_config()
    
    def list_provider_configs(self) -> List[str]:
        """列出所有提供商配置名称"""
        return self.provider_manager.list_configs()
