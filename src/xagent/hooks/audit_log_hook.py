"""审计日志 Hook - 单独存储安全审计日志"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from .output_hook import OutputHook, HookContext, HookResult

class AuditLogHook(OutputHook):
    """审计日志 Hook - 单独存储安全审计日志"""
    
    def __init__(self, log_dir: str = "./data/audit_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def name(self) -> str:
        return "AuditLogHook"
    
    def execute(self, content: str, context: HookContext) -> HookResult:
        return HookResult(
            content=content,
            should_continue=True,
            is_modified=False,
            metadata={}
        )
    
    def on_error(self, error: Exception, content: str, context: HookContext):
        """记录错误"""
        self._log_audit_entry(
            action="error",
            content=content,
            context=context,
            metadata={"error": str(error)}
        )
    
    def _log_audit_entry(self, action: str, content: str, context: HookContext, metadata: Dict[str, Any] = None):
        """记录审计条目"""
        if metadata is None:
            metadata = {}
        
        # 使用本地时区
        now = datetime.now()
        
        audit_entry = {
            'timestamp': now.isoformat(),
            'user_id': context.user_id or 'unknown',
            'username': context.username or 'unknown',
            'chat_id': context.chat_id or 'unknown',
            'session_id': context.session_id or 'unknown',
            'source': context.source or 'unknown',
            'action': action,
            'layer': 'output',
            'content_length': len(content),
            'metadata': {**context.metadata, **metadata},
        }
        
        date_str = now.strftime("%Y-%m-%d")
        log_file = self.log_dir / f"audit_{date_str}.log"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry, ensure_ascii=False) + '\n')
