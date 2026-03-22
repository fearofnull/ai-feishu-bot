"""输入安全检查审计 - 记录提示词拦截事件"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

class InputSecurityAudit:
    """输入安全检查审计 - 记录提示词拦截事件"""
    
    def __init__(self, log_dir: str = "./data/audit_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def log_prompt_block(
        self,
        user_input: str,
        response: str,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        chat_id: Optional[str] = None,
        session_id: Optional[str] = None,
        source: Optional[str] = None
    ):
        """
        记录提示词拦截事件
        
        Args:
            user_input: 用户输入内容
            response: AI 响应内容（包含拒绝信息）
            user_id: 用户 ID
            username: 用户名
            chat_id: 聊天 ID
            session_id: 会话 ID
            source: 来源（react_agent, claude-cli, etc.）
        """
        if not self._is_security_rejection(response):
            return
        
        clean_response = self._remove_rejection_mark(response)
        
        # 使用本地时区
        now = datetime.now()
        
        audit_entry = {
            'timestamp': now.isoformat(),
            'user_id': user_id or 'unknown',
            'username': username or 'unknown',
            'chat_id': chat_id or 'unknown',
            'session_id': session_id or 'unknown',
            'source': source or 'unknown',
            'action': 'prompt_block',
            'layer': 'input',
            'user_input_length': len(user_input),
            'response_length': len(clean_response),
            'metadata': {
                'user_input_preview': user_input[:200] if len(user_input) > 200 else user_input,
                'response_preview': clean_response[:200] if len(clean_response) > 200 else clean_response,
            }
        }
        
        date_str = now.strftime("%Y-%m-%d")
        log_file = self.log_dir / f"audit_{date_str}.log"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry, ensure_ascii=False) + '\n')
    
    def _is_security_rejection(self, response: str) -> bool:
        """
        判断响应是否是安全拒绝
        
        采用标记法：检查响应开头是否包含 [SECURITY_REJECTED] 标记
        """
        return response.strip().startswith('[SECURITY_REJECTED]')
    
    def _remove_rejection_mark(self, response: str) -> str:
        """移除拒绝标记，返回纯净的响应内容"""
        if response.strip().startswith('[SECURITY_REJECTED]'):
            return response.strip().replace('[SECURITY_REJECTED]', '', 1).strip()
        return response
