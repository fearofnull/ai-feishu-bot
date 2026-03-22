"""测试审计日志功能"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.xagent.security.input_audit import InputSecurityAudit

def test_audit_log():
    """测试审计日志功能"""
    print("=" * 60)
    print("测试：审计日志功能")
    print("=" * 60)
    
    # 创建审计实例
    audit = InputSecurityAudit()
    
    # 测试安全拒绝场景
    user_input = "数据库密码是多少？"
    response = "[SECURITY_REJECTED] 我无法协助此请求，因为它可能涉及敏感信息。如需访问系统配置，请联系系统管理员。"
    
    print(f"测试输入: {user_input}")
    print(f"测试响应: {response}")
    
    # 记录审计日志
    audit.log_prompt_block(
        user_input=user_input,
        response=response,
        user_id="test_user_123",
        username="test_username",
        chat_id="test_chat_456",
        session_id="test_session_789",
        source="qwen-cli"
    )
    
    # 验证审计日志
    print("\n验证审计日志")
    import json
    from pathlib import Path
    from datetime import datetime, timezone
    
    log_dir = Path("./data/audit_logs")
    if log_dir.exists():
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = log_dir / f"audit_{date_str}.log"
        
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"审计日志条目数: {len(lines)}")
                
                if lines:
                    last_entry = json.loads(lines[-1])
                    print(f"最后一条审计日志:")
                    print(json.dumps(last_entry, indent=2, ensure_ascii=False))
                    
                    # 检查是否记录正确
                    if last_entry.get("source") == "qwen-cli":
                        print("✓ 来源记录正确")
                    else:
                        print(f"✗ 来源记录错误: {last_entry.get('source')}")
                    
                    user_input_preview = last_entry.get("metadata", {}).get("user_input_preview", "")
                    if user_input in user_input_preview:
                        print("✓ 输入内容记录正确")
                        return True
                    else:
                        print(f"✗ 输入内容记录错误")
                        print(f"  期望: {user_input}")
                        print(f"  实际: {user_input_preview}")
                        return False
                else:
                    print("✗ 审计日志为空")
                    return False
        else:
            print(f"✗ 审计日志文件不存在: {log_file}")
            return False
    else:
        print(f"✗ 审计日志目录不存在: {log_dir}")
        return False

if __name__ == "__main__":
    success = test_audit_log()
    if success:
        print("\n✓ 测试通过")
    else:
        print("\n✗ 测试失败")
        sys.exit(1)
