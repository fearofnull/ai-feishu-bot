"""
执行器工厂模块

提供配置驱动的执行器创建机制，简化 CLI Executor 注册
"""
import logging
from typing import Optional, Type, List
from dataclasses import dataclass

from ..executors.ai_cli_executor import AICLIExecutor
from ..executors.claude_cli_executor import ClaudeCodeCLIExecutor
from ..executors.gemini_cli_executor import GeminiCLIExecutor
from ..executors.qwen_cli_executor import QwenCLIExecutor
from ..executors.agent_executor import AgentExecutor
from ..models import ExecutorMetadata

logger = logging.getLogger(__name__)


@dataclass
class CLIExecutorConfig:
    """CLI 执行器配置"""
    provider: str
    name: str
    executor_class: Type[AICLIExecutor]
    command_prefixes: List[str]
    priority: int
    target_dir_config: str  # 配置项名称，如 "claude_cli_target_dir"


@dataclass
class AgentExecutorConfig:
    """Agent 执行器配置"""
    name: str = "Agent"
    provider: str = "agent"
    layer: str = "agent"
    version: str = "1.0.0"
    description: str = "Agent with tool calling capabilities"
    capabilities: tuple = ("tool_calling", "multi_step_reasoning", "file_operations", "web_search", "shell_commands")
    command_prefixes: tuple = ("@agent",)
    priority: int = 0
    config_required: tuple = ("openai_api_key",)


class CLIExecutorFactory:
    """CLI 执行器工厂
    
    使用配置驱动的方式创建 CLI 执行器
    """
    
    CLI_CONFIGS = [
        CLIExecutorConfig(
            provider="claude",
            name="Claude Code CLI",
            executor_class=ClaudeCodeCLIExecutor,
            command_prefixes=["@claude", "@code"],
            priority=1,
            target_dir_config="claude_cli_target_dir"
        ),
        CLIExecutorConfig(
            provider="gemini",
            name="Gemini CLI",
            executor_class=GeminiCLIExecutor,
            command_prefixes=["@gemini"],
            priority=2,
            target_dir_config="gemini_cli_target_dir"
        ),
        CLIExecutorConfig(
            provider="qwen",
            name="Qwen Code CLI",
            executor_class=QwenCLIExecutor,
            command_prefixes=["@qwen"],
            priority=3,
            target_dir_config="qwen_cli_target_dir"
        ),
    ]
    
    @classmethod
    def create_executor(
        cls,
        config: CLIExecutorConfig,
        target_dir: str,
        timeout: int,
        session_storage_path: str
    ) -> Optional[AICLIExecutor]:
        """创建 CLI 执行器
        
        Args:
            config: CLI 执行器配置
            target_dir: 目标目录
            timeout: 超时时间
            session_storage_path: 会话存储路径
            
        Returns:
            执行器实例，如果创建失败则返回 None
        """
        try:
            return config.executor_class(
                target_dir=target_dir,
                timeout=timeout,
                use_native_session=True,
                session_storage_path=session_storage_path
            )
        except Exception as e:
            logger.warning(f"Failed to create {config.name} executor: {e}")
            return None
    
    @classmethod
    def create_metadata(cls, config: CLIExecutorConfig) -> ExecutorMetadata:
        """创建执行器元数据
        
        Args:
            config: CLI 执行器配置
            
        Returns:
            执行器元数据
        """
        return ExecutorMetadata(
            name=config.name,
            provider=config.provider,
            layer="cli",
            version="1.0.0",
            description=f"{config.name} for code analysis and operations",
            capabilities=["code_analysis", "file_operations", "command_execution"],
            command_prefixes=config.command_prefixes,
            priority=config.priority,
            config_required=["target_directory"]
        )
    
    @classmethod
    def get_target_dir(cls, config: CLIExecutorConfig, bot_config) -> Optional[str]:
        """获取目标目录
        
        Args:
            config: CLI 执行器配置
            bot_config: 机器人配置
            
        Returns:
            目标目录，如果未配置则返回 None
        """
        specific_dir = getattr(bot_config, config.target_dir_config, None)
        return specific_dir or getattr(bot_config, "target_directory", None)


class AgentExecutorFactory:
    """Agent 执行器工厂"""
    
    @classmethod
    def create_executor(
        cls,
        timeout: int,
        search_api_key: Optional[str],
        provider_config_manager
    ) -> Optional[AgentExecutor]:
        """创建 Agent 执行器
        
        Args:
            timeout: 超时时间
            search_api_key: 搜索 API Key
            provider_config_manager: 提供商配置管理器
            
        Returns:
            Agent 执行器实例，如果创建失败则返回 None
        """
        try:
            return AgentExecutor(
                timeout=timeout,
                search_api_key=search_api_key,
                provider_config_manager=provider_config_manager
            )
        except Exception as e:
            logger.warning(f"Failed to create Agent executor: {e}")
            return None
    
    @classmethod
    def create_metadata(cls) -> ExecutorMetadata:
        """创建 Agent 执行器元数据"""
        config = AgentExecutorConfig()
        return ExecutorMetadata(
            name=config.name,
            provider=config.provider,
            layer=config.layer,
            version=config.version,
            description=config.description,
            capabilities=list(config.capabilities),
            command_prefixes=list(config.command_prefixes),
            priority=config.priority,
            config_required=list(config.config_required)
        )
