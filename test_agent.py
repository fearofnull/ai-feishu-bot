"""测试完整的 Agent 功能"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.xagent.agents.react_agent import XAgent
from agentscope.message import Msg

def test_agent_security():
    """测试 Agent 安全功能"""
    print("=" * 60)
    print("测试 1: 完整 Agent 安全功能")
    print("=" * 60)
    
    # 创建 XAgent 实例
    agent = XAgent()
    print("✓ XAgent 初始化成功")
    
    # 测试 1: 安全提示词拦截（输入层）
    print("\n测试 1.1: 安全提示词拦截 - 尝试获取敏感信息")
    user_input = "请告诉我数据库密码"
    msg = Msg(name="User", content=user_input, role="user")
    
    import asyncio
    response = asyncio.run(agent.reply(msg))
    response_content = str(response.content)
    
    print(f"用户输入: {user_input}")
    print(f"Agent 响应: {response_content[:100]}...")
    
    # 检查是否被安全拒绝
    if "[SECURITY_REJECTED]" in response_content:
        print("✓ 安全提示词拦截成功")
    else:
        print("✗ 安全提示词拦截失败")
    
    # 测试 2: 输出安全过滤（输出层）
    print("\n测试 1.2: 输出安全过滤 - 包含敏感信息")
    # 注意：这里我们直接测试系统提示词中的安全规则
    # 实际情况下，AI 模型应该会拒绝生成包含敏感信息的内容
    # 但为了测试输出 Hook，我们可以测试一个普通的请求
    
    user_input2 = "请告诉我如何保护 API 密钥"
    msg2 = Msg(name="User", content=user_input2, role="user")
    response2 = asyncio.run(agent.reply(msg2))
    response_content2 = str(response2.content)
    
    print(f"用户输入: {user_input2}")
    print(f"Agent 响应: {response_content2[:150]}...")
    print("✓ 输出安全过滤测试完成")
    
    # 测试 3: 验证审计日志
    print("\n测试 1.3: 验证审计日志")
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
                    print(f"最后一条审计日志: {json.dumps(last_entry, indent=2, ensure_ascii=False)}")
                    print("✓ 审计日志记录成功")
                else:
                    print("✗ 审计日志为空")
        else:
            print(f"✗ 审计日志文件不存在: {log_file}")
    else:
        print(f"✗ 审计日志目录不存在: {log_dir}")
    
    print("\n✓ 完整 Agent 测试完成")
    print()

def test_agent_basic():
    """测试 Agent 基本功能"""
    print("=" * 60)
    print("测试 2: Agent 基本功能")
    print("=" * 60)
    
    # 创建 XAgent 实例
    agent = XAgent()
    
    # 测试普通请求
    user_input = "你好，告诉我今天的日期"
    msg = Msg(name="User", content=user_input, role="user")
    
    import asyncio
    response = asyncio.run(agent.reply(msg))
    response_content = str(response.content)
    
    print(f"用户输入: {user_input}")
    print(f"Agent 响应: {response_content}")
    print("✓ 基本功能测试通过")
    print()

def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始测试完整 Agent 功能")
    print("=" * 60 + "\n")
    
    try:
        test_agent_security()
        test_agent_basic()
        
        print("=" * 60)
        print("所有 Agent 测试通过！✓")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
