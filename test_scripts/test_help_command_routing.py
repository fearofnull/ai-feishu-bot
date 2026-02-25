#!/usr/bin/env python3
"""
测试 /help 命令路由问题修复

验证 /help 命令是否被正确识别为会话命令，而不是路由到 AI
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from feishu_bot.session_manager import SessionManager
from feishu_bot.command_parser import CommandParser


def test_session_command_detection():
    """测试会话命令检测"""
    print("=" * 60)
    print("测试 1: 会话命令检测")
    print("=" * 60)
    
    session_manager = SessionManager()
    
    test_cases = [
        ("/help", True, "英文 help 命令"),
        ("帮助", True, "中文帮助命令"),
        ("help", True, "小写 help"),
        ("/HELP", True, "大写 HELP"),
        ("/new", True, "新会话命令"),
        ("/session", True, "会话信息命令"),
        ("/history", True, "历史记录命令"),
        ("hello world", False, "普通消息"),
        ("@claude help me", False, "带前缀的消息"),
    ]
    
    all_passed = True
    for message, expected, description in test_cases:
        result = session_manager.is_session_command(message)
        status = "✅" if result == expected else "❌"
        if result != expected:
            all_passed = False
        print(f"{status} {description}: '{message}' -> {result} (期望: {expected})")
    
    print()
    return all_passed


def test_command_parsing_with_help():
    """测试命令解析不会影响 help 命令"""
    print("=" * 60)
    print("测试 2: 命令解析与 help 命令")
    print("=" * 60)
    
    parser = CommandParser()
    session_manager = SessionManager()
    
    test_cases = [
        "/help",
        "帮助",
        "help",
        "@claude /help",  # 带前缀的 help
    ]
    
    all_passed = True
    for message in test_cases:
        parsed = parser.parse_command(message)
        is_session_cmd = session_manager.is_session_command(parsed.message)
        
        # 对于不带前缀的 help，应该被识别为会话命令
        # 对于带前缀的，parsed.message 会去掉前缀，也应该被识别
        if is_session_cmd:
            print(f"✅ '{message}' -> parsed.message='{parsed.message}' -> 会话命令")
        else:
            print(f"❌ '{message}' -> parsed.message='{parsed.message}' -> 未识别为会话命令")
            all_passed = False
    
    print()
    return all_passed


def test_help_command_response():
    """测试 help 命令响应"""
    print("=" * 60)
    print("测试 3: help 命令响应内容")
    print("=" * 60)
    
    session_manager = SessionManager()
    
    test_user_id = "test_user_123"
    
    # 测试不同的 help 命令变体
    help_commands = ["/help", "帮助", "help"]
    
    all_passed = True
    for cmd in help_commands:
        response = session_manager.handle_session_command(test_user_id, cmd)
        
        # 检查响应是否包含关键内容（不带空格）
        if response and "AI提供商命令" in response and "会话管理命令" in response:
            print(f"✅ '{cmd}' 返回了完整的帮助信息")
            print(f"   响应长度: {len(response)} 字符")
        else:
            print(f"❌ '{cmd}' 未返回正确的帮助信息")
            if response:
                print(f"   实际响应: {response[:100]}...")
            all_passed = False
    
    print()
    return all_passed


def test_message_flow_simulation():
    """模拟消息处理流程"""
    print("=" * 60)
    print("测试 4: 消息处理流程模拟")
    print("=" * 60)
    
    parser = CommandParser()
    session_manager = SessionManager()
    
    # 模拟用户发送 /help
    user_message = "/help"
    print(f"用户消息: '{user_message}'")
    
    # 步骤 1: 命令解析
    parsed = parser.parse_command(user_message)
    print(f"1. 命令解析: provider={parsed.provider}, layer={parsed.execution_layer}")
    print(f"   parsed.message='{parsed.message}'")
    
    # 步骤 2: 会话命令检查
    is_session_cmd = session_manager.is_session_command(parsed.message)
    print(f"2. 会话命令检查: {is_session_cmd}")
    
    if is_session_cmd:
        # 步骤 3: 处理会话命令
        response = session_manager.handle_session_command("test_user", parsed.message)
        print(f"3. 会话命令处理: 返回响应 ({len(response)} 字符)")
        print(f"   ✅ 命令被正确拦截，不会路由到 AI")
        return True
    else:
        print(f"   ❌ 命令未被识别为会话命令，会路由到 AI")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("测试 /help 命令路由修复")
    print("=" * 60 + "\n")
    
    results = []
    
    results.append(("会话命令检测", test_session_command_detection()))
    results.append(("命令解析与 help", test_command_parsing_with_help()))
    results.append(("help 命令响应", test_help_command_response()))
    results.append(("消息流程模拟", test_message_flow_simulation()))
    
    # 总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 所有测试通过！/help 命令路由问题已修复")
        return 0
    else:
        print("⚠️  部分测试失败，请检查")
        return 1


if __name__ == "__main__":
    sys.exit(main())
