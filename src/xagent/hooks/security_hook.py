"""安全过滤 Hook - 检测并处理敏感信息泄露"""

import re
import logging
from typing import Dict, Any
from .output_hook import OutputHook, HookContext, HookResult

logger = logging.getLogger(__name__)

class SecurityHook(OutputHook):
    """安全过滤 Hook - 检测并处理敏感信息泄露"""
    
    HIGH_RISK_PATTERNS = {
        'private_key': r'-----BEGIN (RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----',
        'env_file_content': r'^\s*[A-Z_]*(?:SECRET|KEY|TOKEN|PASSWORD)[A-Z_]*\s*=\s*[^\s]+',
        'aws_key': r'AKIA[0-9A-Z]{16}',
        'github_token': r'gh[pousr]_[A-Za-z0-9_]{36,}',
    }
    
    MEDIUM_RISK_PATTERNS = {
        'api_key': r'\b[a-zA-Z0-9_-]{32,}\b',
        'jwt_token': r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*',
        'db_connection': r'(postgres|mysql|mongodb|redis)://[^\s]+',
        'email': r'[\w\.-]+@[\w\.-]+\.\w+',
        'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
    }
    
    SENSITIVE_KEYWORDS = [
        '.env', 'id_rsa', 'id_ed25519', 'id_ecdsa', 'id_dsa',
        '.pem', '.key', '.p12', '.pfx', '.crt',
        'DATABASE_URL', 'API_SECRET', 'PRIVATE_KEY', 'SECRET_KEY',
        'AWS_ACCESS_KEY', 'AWS_SECRET_KEY', 'GITHUB_TOKEN',
    ]
    
    @property
    def name(self) -> str:
        return "SecurityHook"
    
    def execute(self, content: str, context: HookContext) -> HookResult:
        modified_content = content
        is_modified = False
        
        for pattern_name, pattern in self.HIGH_RISK_PATTERNS.items():
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                logger.warning(f"High risk pattern detected: {pattern_name}")
                return HookResult(
                    content="[安全系统已拦截此响应，因为包含敏感信息]",
                    should_continue=True,
                    is_modified=True,
                    metadata={"action": "block", "reason": pattern_name}
                )
        
        for keyword in self.SENSITIVE_KEYWORDS:
            if keyword.lower() in content.lower():
                if self._is_file_content_leak(content, keyword):
                    logger.warning(f"Sensitive file content detected: {keyword}")
                    return HookResult(
                        content="[安全系统已拦截此响应，因为包含敏感信息]",
                        should_continue=True,
                        is_modified=True,
                        metadata={"action": "block", "reason": f"sensitive_file_{keyword}"}
                    )
        
        warnings = []
        for pattern_name, pattern in self.MEDIUM_RISK_PATTERNS.items():
            matches = list(re.finditer(pattern, content))
            if matches:
                warnings.append(f"检测到敏感信息已脱敏: {pattern_name}")
                for match in reversed(matches):
                    start, end = match.span()
                    original = match.group()
                    masked = self._mask_sensitive_data(original, pattern_name)
                    modified_content = modified_content[:start] + masked + modified_content[end:]
                    is_modified = True
        
        if warnings:
            security_notice = self._build_security_notice(warnings)
            modified_content = security_notice + modified_content
            is_modified = True
        
        return HookResult(
            content=modified_content,
            should_continue=True,
            is_modified=is_modified,
            metadata={"action": "mask" if is_modified else "pass"}
        )
    
    def _is_file_content_leak(self, content: str, keyword: str) -> bool:
        keyword_lower = keyword.lower()
        content_lower = content.lower()
        idx = content_lower.find(keyword_lower)
        if idx == -1:
            return False
        
        surrounding = content[max(0, idx-50):min(len(content), idx+len(keyword)+200)]
        return ('=' in surrounding and len(surrounding) > 100) or surrounding.count('\n') > 3
    
    def _mask_sensitive_data(self, data: str, pattern_name: str) -> str:
        if pattern_name == 'email':
            parts = data.split('@')
            if len(parts) == 2:
                return f"{parts[0][:2]}***@{parts[1]}"
        elif pattern_name == 'ip_address':
            parts = data.split('.')
            return f"{parts[0]}.xxx.xxx.{parts[3]}" if len(parts) == 4 else "xxx.xxx.xxx.xxx"
        else:
            if len(data) > 12:
                return f"{data[:4]}****{data[-4:]}"
            else:
                return "****"
        return "[REDACTED]"
    
    def _build_security_notice(self, warnings: list[str]) -> str:
        notice = "⚠️ **安全提示**\n\n"
        notice += "系统检测到响应中包含敏感信息，已进行脱敏处理。\n"
        notice += "为了系统安全，请避免：\n"
        notice += "- 分享 API 密钥、密码或令牌\n"
        notice += "- 展示配置文件内容\n"
        notice += "- 泄露数据库连接信息\n\n"
        notice += "---\n\n"
        return notice
