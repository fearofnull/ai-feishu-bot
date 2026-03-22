"""输出 Hook 框架"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class HookContext:
    """Hook 执行上下文"""
    user_id: Optional[str] = None
    username: Optional[str] = None
    chat_id: Optional[str] = None
    session_id: Optional[str] = None
    source: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class HookResult:
    """Hook 执行结果"""
    content: str
    should_continue: bool
    is_modified: bool
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class OutputHook(ABC):
    """输出 Hook 抽象基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Hook 名称"""
        pass
    
    @abstractmethod
    def execute(self, content: str, context: HookContext) -> HookResult:
        """
        执行 Hook 逻辑
        
        Args:
            content: 原始内容
            context: 上下文信息
        
        Returns:
            HookResult: 执行结果
        """
        pass
    
    def on_error(self, error: Exception, content: str, context: HookContext):
        """
        当 Hook 执行出错时的回调（可选实现）
        """
        pass

class OutputHookManager:
    """输出 Hook 管理器"""
    
    def __init__(self):
        self._hooks: list[OutputHook] = []
    
    def register(self, hook: OutputHook) -> 'OutputHookManager':
        """注册 Hook"""
        self._hooks.append(hook)
        return self
    
    def unregister(self, hook_name: str) -> 'OutputHookManager':
        """注销 Hook"""
        self._hooks = [h for h in self._hooks if h.name != hook_name]
        return self
    
    def process(self, content: str, context: HookContext) -> str:
        """
        依次执行所有 Hook
        
        如果某个 Hook 返回 should_continue=False，则停止执行
        """
        current_content = content
        
        for hook in self._hooks:
            try:
                result = hook.execute(current_content, context)
                
                if result.is_modified:
                    current_content = result.content
                
                if not result.should_continue:
                    break
                    
            except Exception as e:
                hook.on_error(e, current_content, context)
                # 出错时继续执行下一个 Hook
                continue
        
        return current_content
    
    def get_hooks(self) -> list[OutputHook]:
        """获取所有已注册的 Hook"""
        return self._hooks
