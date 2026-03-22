"""
AI CLI 执行器抽象基类

定义所有 AI CLI 执行器的通用接口和共享逻辑。
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import os
from ..models import ExecutionResult
from ..security.input_audit import InputSecurityAudit
from ..hooks.output_hook import HookContext, OutputHookManager


class AICLIExecutor(ABC):
    """AI CLI 执行器抽象基类
    
    所有 AI CLI 执行器（Claude Code CLI、Gemini CLI）的基类。
    定义了通用接口和共享的初始化逻辑。
    
    Requirements: 3.1, 3.2
    """
    
    def __init__(self, target_dir: str, timeout: int = 600):
        """初始化 AI CLI 执行器
        
        Args:
            target_dir: 目标代码仓库目录
            timeout: 命令执行超时时间（秒），默认 600 秒
        """
        self.target_dir = target_dir
        self.timeout = timeout
        
        # 初始化输入安全审计和 Hook 管理器
        self._input_audit = InputSecurityAudit()
        self._hook_manager = OutputHookManager()
    
    @abstractmethod
    def execute(
        self,
        user_prompt: str,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """执行 AI CLI 命令，返回执行结果
        
        Args:
            user_prompt: 用户提示
            additional_params: 额外参数（如 user_id, model, max_tokens 等）
            
        Returns:
            ExecutionResult: 执行结果
        """
        pass
    
    @abstractmethod
    def verify_directory(self) -> bool:
        """验证目标目录是否存在
        
        Returns:
            True 如果目录存在且可访问
        """
        pass
    
    @abstractmethod
    def get_command_name(self) -> str:
        """返回 AI CLI 命令名称
        
        Returns:
            命令名称（如 "claude", "claude.cmd", "gemini"）
        """
        pass
    
    def _wrap_prompt_with_security_rules(self, user_prompt: str) -> str:
        """用安全规则包装用户提示

        在用户提示前添加安全规则，防止危险操作。

        Args:
            user_prompt: 原始用户提示

        Returns:
            包装后的提示词
        """
        from ..constants.security import SECURITY_RULES
        security_rules = f"""
你是一个安全的 AI 助手，必须遵守以下安全规则：

{SECURITY_RULES}

现在处理用户的请求：

"""
        return security_rules + user_prompt

    def build_command_args(
        self,
        user_prompt: str,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """构建 AI CLI 命令参数列表

        Args:
            user_prompt: 用户提示
            additional_params: 额外参数

        Returns:
            命令参数列表
        """
        pass
    
    def _verify_directory_exists(self) -> bool:
        """通用的目录验证实现
        
        Returns:
            True 如果目录存在且可访问
        """
        return os.path.exists(self.target_dir) and os.path.isdir(self.target_dir)
    
    def is_available(self) -> bool:
        """检查执行器是否可用
        
        Returns:
            True 如果目标目录存在
        """
        return self._verify_directory_exists()
    
    def _apply_hooks(self, result: ExecutionResult, additional_params: Optional[Dict[str, Any]] = None, original_user_prompt: Optional[str] = None) -> ExecutionResult:
        """应用 Hook 处理到执行结果
        
        Args:
            result: 原始执行结果
            additional_params: 额外参数
            original_user_prompt: 原始用户提示（不包含语言提示词）
            
        Returns:
            处理后的执行结果
        """
        # 记录输入安全检查审计（提示词拦截）
        self._input_audit.log_prompt_block(
            user_input=original_user_prompt if original_user_prompt else (result.stdout if result.success else ""),
            response=result.stdout if result.success else "",
            user_id=additional_params.get('user_id') if additional_params else None,
            username=additional_params.get('username') if additional_params else None,
            chat_id=additional_params.get('chat_id') if additional_params else None,
            session_id=additional_params.get('session_id') if additional_params else None,
            source=self.get_provider_name()
        )
        
        # 应用输出 Hook 处理
        context = HookContext(
            user_id=additional_params.get('user_id') if additional_params else None,
            username=additional_params.get('username') if additional_params else None,
            chat_id=additional_params.get('chat_id') if additional_params else None,
            session_id=additional_params.get('session_id') if additional_params else None,
            source=self.get_provider_name()
        )
        processed_stdout = self._hook_manager.process(result.stdout, context)
        
        return ExecutionResult(
            success=result.success,
            stdout=processed_stdout,
            stderr=result.stderr,
            error_message=result.error_message,
            execution_time=result.execution_time
        )
