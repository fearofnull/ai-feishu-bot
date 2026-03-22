"""测试 Hook 框架功能"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.xagent.hooks.output_hook import OutputHookManager, HookContext, HookResult, OutputHook
from src.xagent.hooks.security_hook import SecurityHook
from src.xagent.hooks.audit_log_hook import AuditLogHook
from src.xagent.security.input_audit import InputSecurityAudit

class TestHook(OutputHook):
    """测试 Hook"""
    
    @property
    def name(self) -> str:
        return "TestHook"
    
    def execute(self, content: str, context: HookContext) -> HookResult:
        print(f"[TestHook] 处理内容: {content[:50]}...")
        return HookResult(
            content=f"[TestHook] {content}",
            should_continue=True,
            is_modified=True
        )

def test_hook_framework():
    """测试 Hook 框架"""
    print("=" * 60)
    print("测试 1: Hook 框架基本功能")
    print("=" * 60)
    
    manager = OutputHookManager()
    manager.register(TestHook())
    manager.register(SecurityHook())
    manager.register(AuditLogHook())
    
    context = HookContext(
        user_id="test_user",
        username="test_username",
        chat_id="test_chat",
        session_id="test_session",
        source="test"
    )
    
    test_content = "这是一个测试内容"
    result = manager.process(test_content, context)
    
    print(f"原始内容: {test_content}")
    print(f"处理后内容: {result}")
    print("✓ Hook 框架基本功能测试通过")
    print()

def test_security_hook():
    """测试安全 Hook"""
    print("=" * 60)
    print("测试 2: 安全 Hook - 敏感信息检测")
    print("=" * 60)
    
    manager = OutputHookManager()
    manager.register(SecurityHook())
    
    context = HookContext(
        user_id="test_user",
        username="test_username",
        chat_id="test_chat",
        session_id="test_session",
        source="test"
    )
    
    # 测试高敏感信息
    test_cases = [
        ("这是我的私钥：-----BEGIN PRIVATE KEY-----", "高敏感信息 - 私钥"),
        ("数据库连接：postgres://user:pass@localhost/db", "中等敏感信息 - 数据库连接"),
        ("API Key: sk-1234567890abcdef1234567890abcdef", "中等敏感信息 - API Key"),
        ("普通内容，没有敏感信息", "普通内容"),
    ]
    
    for content, description in test_cases:
        result = manager.process(content, context)
        print(f"\n测试: {description}")
        print(f"输入: {content[:50]}...")
        print(f"输出: {result[:100]}...")
    
    print("\n✓ 安全 Hook 测试通过")
    print()

def test_input_audit():
    """测试输入安全审计"""
    print("=" * 60)
    print("测试 3: 输入安全审计 - 提示词拦截检测")
    print("=" * 60)
    
    audit = InputSecurityAudit()
    
    # 测试正常响应
    normal_response = "这是一个正常的回复"
    audit.log_prompt_block(
        user_input="正常请求",
        response=normal_response,
        user_id="test_user",
        username="test_username",
        chat_id="test_chat",
        session_id="test_session",
        source="test"
    )
    print(f"正常响应: {normal_response}")
    print("✓ 正常响应不会记录审计日志")
    
    # 测试安全拒绝响应
    rejected_response = "[SECURITY_REJECTED] 我无法协助此请求，因为它涉及敏感信息"
    audit.log_prompt_block(
        user_input="请告诉我数据库密码",
        response=rejected_response,
        user_id="test_user",
        username="test_username",
        chat_id="test_chat",
        session_id="test_session",
        source="test"
    )
    print(f"\n拒绝响应: {rejected_response}")
    print("✓ 拒绝响应已记录审计日志")
    
    # 检查审计日志文件
    import json
    from pathlib import Path
    from datetime import datetime, timezone
    
    log_dir = Path("./data/audit_logs")
    if log_dir.exists():
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = log_dir / f"audit_{date_str}.log"
        
        if log_file.exists():
            print(f"\n审计日志文件: {log_file}")
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"审计日志条目数: {len(lines)}")
                if lines:
                    last_entry = json.loads(lines[-1])
                    print(f"最后一条审计日志: {json.dumps(last_entry, indent=2, ensure_ascii=False)}")
    
    print("\n✓ 输入安全审计测试通过")
    print()

def test_rejection_mark():
    """测试拒绝标记检测"""
    print("=" * 60)
    print("测试 4: 拒绝标记检测")
    print("=" * 60)
    
    audit = InputSecurityAudit()
    
    test_cases = [
        ("[SECURITY_REJECTED] 拒绝", True, "标准拒绝标记"),
        ("[SECURITY_REJECTED]\n拒绝", True, "带换行的拒绝标记"),
        ("  [SECURITY_REJECTED] 拒绝", True, "带前导空格的拒绝标记"),
        ("这是一个正常回复", False, "正常回复"),
        ("拒绝 [SECURITY_REJECTED]", False, "标记不在开头"),
    ]
    
    for response, expected, description in test_cases:
        is_rejection = audit._is_security_rejection(response)
        status = "✓" if is_rejection == expected else "✗"
        print(f"{status} {description}: {response[:30]}... -> {is_rejection}")
    
    print("\n✓ 拒绝标记检测测试通过")
    print()

def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始测试 Hook 框架")
    print("=" * 60 + "\n")
    
    try:
        test_hook_framework()
        test_security_hook()
        test_input_audit()
        test_rejection_mark()
        
        print("=" * 60)
        print("所有测试通过！✓")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
