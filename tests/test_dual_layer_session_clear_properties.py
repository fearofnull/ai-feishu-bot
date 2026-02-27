"""
双层会话清除属性测试
使用 Hypothesis 进行基于属性的测试

Feature: feishu-ai-bot
Property 35: 双层会话清除
Validates: Requirements 10.3, 10.14
"""
import os
import tempfile
import shutil
import time
import pytest
from hypothesis import given, strategies as st, settings
from feishu_bot.claude_cli_executor import ClaudeCodeCLIExecutor
from feishu_bot.gemini_cli_executor import GeminiCLIExecutor
from feishu_bot.session_manager import SessionManager


def cleanup_directory(directory_path):
    """安全清理目录，处理 Windows 文件锁定问题"""
    if os.path.exists(directory_path):
        try:
            shutil.rmtree(directory_path)
        except (PermissionError, OSError):
            time.sleep(0.1)
            try:
                shutil.rmtree(directory_path)
            except (PermissionError, OSError):
                pass


# 定义策略：生成用户 ID
@st.composite
def user_id_strategy(draw):
    """生成用户 ID"""
    return draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))


# 定义策略：生成会话 ID
@st.composite
def session_id_strategy(draw):
    """生成会话 ID"""
    return draw(st.text(min_size=10, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pd'))))


# Feature: feishu-ai-bot, Property 35: 双层会话清除
# **Validates: Requirements 10.3, 10.14**
@settings(max_examples=100)
@given(
    user_id=user_id_strategy(),
    claude_session_id=session_id_strategy()
)
def test_dual_layer_session_clear_claude(user_id, claude_session_id):
    """
    Property 35: 双层会话清除 - Claude CLI
    
    For any 用户发送的 "/new" 命令，系统应该同时清除飞书机器人会话和 Claude CLI 会话。
    
    **Validates: Requirements 10.3, 10.14**
    """
    directory_path = tempfile.mkdtemp(prefix="test_dual_clear_claude_")
    session_storage_path = os.path.join(directory_path, "sessions.json")
    executor_storage_path = os.path.join(directory_path, "executor_sessions.json")
    
    try:
        # 创建会话管理器
        session_manager = SessionManager(
            storage_path=session_storage_path,
            max_messages=50,
            session_timeout=86400
        )
        
        # 创建 Claude CLI 执行器
        claude_executor = ClaudeCodeCLIExecutor(
            target_dir=directory_path,
            timeout=5,
            use_native_session=True,
            session_storage_path=executor_storage_path
        )
        
        # 1. 设置飞书机器人会话
        session_manager.add_message(user_id, "user", "test message 1")
        session_manager.add_message(user_id, "assistant", "test response 1")
        
        # 验证飞书机器人会话存在
        history_before = session_manager.get_conversation_history(user_id)
        assert len(history_before) == 2, \
            f"Should have 2 messages before clearing, got {len(history_before)}"
        
        # 2. 设置 Claude CLI 会话
        claude_executor.update_session_id(user_id, claude_session_id)
        
        # 验证 Claude CLI 会话存在
        claude_session_before = claude_executor.get_or_create_claude_session(user_id)
        assert claude_session_before == claude_session_id, \
            f"Claude session should be {claude_session_id}, got {claude_session_before}"
        
        # 3. 模拟 "/new" 命令 - 清除两层会话
        # 清除飞书机器人会话
        old_session_id = session_manager.get_or_create_session(user_id).session_id
        session_manager.create_new_session(user_id)
        new_session_id = session_manager.get_or_create_session(user_id).session_id
        
        # 清除 Claude CLI 会话
        claude_executor.clear_session(user_id)
        
        # 4. 验证飞书机器人会话已清除
        assert old_session_id != new_session_id, \
            "New session should have different session_id"
        
        history_after = session_manager.get_conversation_history(user_id)
        assert len(history_after) == 0, \
            f"Should have 0 messages after clearing, got {len(history_after)}"
        
        # 5. 验证 Claude CLI 会话已清除
        claude_session_after = claude_executor.get_or_create_claude_session(user_id)
        assert claude_session_after is None, \
            f"Claude session should be None after clearing, got {claude_session_after}"
    
    finally:
        cleanup_directory(directory_path)


# Feature: feishu-ai-bot, Property 35: 双层会话清除
# **Validates: Requirements 10.3, 10.14**
@settings(max_examples=100)
@given(
    user_id=user_id_strategy(),
    gemini_session_id=session_id_strategy()
)
def test_dual_layer_session_clear_gemini(user_id, gemini_session_id):
    """
    Property 35: 双层会话清除 - Gemini CLI
    
    For any 用户发送的 "/new" 命令，系统应该同时清除飞书机器人会话和 Gemini CLI 会话。
    
    **Validates: Requirements 10.3, 10.14**
    """
    directory_path = tempfile.mkdtemp(prefix="test_dual_clear_gemini_")
    session_storage_path = os.path.join(directory_path, "sessions.json")
    executor_storage_path = os.path.join(directory_path, "executor_sessions.json")
    
    try:
        # 创建会话管理器
        session_manager = SessionManager(
            storage_path=session_storage_path,
            max_messages=50,
            session_timeout=86400
        )
        
        # 创建 Gemini CLI 执行器
        gemini_executor = GeminiCLIExecutor(
            target_dir=directory_path,
            timeout=5,
            use_native_session=True,
            session_storage_path=executor_storage_path
        )
        
        # 1. 设置飞书机器人会话
        session_manager.add_message(user_id, "user", "test message 1")
        session_manager.add_message(user_id, "assistant", "test response 1")
        
        # 验证飞书机器人会话存在
        history_before = session_manager.get_conversation_history(user_id)
        assert len(history_before) == 2, \
            f"Should have 2 messages before clearing, got {len(history_before)}"
        
        # 2. 设置 Gemini CLI 会话
        gemini_executor.update_session_id(user_id, gemini_session_id)
        
        # 验证 Gemini CLI 会话存在
        gemini_session_before = gemini_executor.get_or_create_gemini_session(user_id)
        assert gemini_session_before == gemini_session_id, \
            f"Gemini session should be {gemini_session_id}, got {gemini_session_before}"
        
        # 3. 模拟 "/new" 命令 - 清除两层会话
        # 清除飞书机器人会话
        old_session_id = session_manager.get_or_create_session(user_id).session_id
        session_manager.create_new_session(user_id)
        new_session_id = session_manager.get_or_create_session(user_id).session_id
        
        # 清除 Gemini CLI 会话
        gemini_executor.clear_session(user_id)
        
        # 4. 验证飞书机器人会话已清除
        assert old_session_id != new_session_id, \
            "New session should have different session_id"
        
        history_after = session_manager.get_conversation_history(user_id)
        assert len(history_after) == 0, \
            f"Should have 0 messages after clearing, got {len(history_after)}"
        
        # 5. 验证 Gemini CLI 会话已清除
        gemini_session_after = gemini_executor.get_or_create_gemini_session(user_id)
        assert gemini_session_after is None, \
            f"Gemini session should be None after clearing, got {gemini_session_after}"
    
    finally:
        cleanup_directory(directory_path)


# Feature: feishu-ai-bot, Property 35: 双层会话清除
# **Validates: Requirements 10.3, 10.14**
@settings(max_examples=100)
@given(
    user_id=user_id_strategy(),
    claude_session_id=session_id_strategy(),
    gemini_session_id=session_id_strategy()
)
def test_dual_layer_session_clear_both(user_id, claude_session_id, gemini_session_id):
    """
    Property 35: 双层会话清除 - 同时清除 Claude 和 Gemini
    
    For any 用户发送的 "/new" 命令，系统应该同时清除飞书机器人会话、
    Claude CLI 会话和 Gemini CLI 会话。
    
    **Validates: Requirements 10.3, 10.14**
    """
    directory_path = tempfile.mkdtemp(prefix="test_dual_clear_both_")
    session_storage_path = os.path.join(directory_path, "sessions.json")
    executor_storage_path = os.path.join(directory_path, "executor_sessions.json")
    
    try:
        # 创建会话管理器
        session_manager = SessionManager(
            storage_path=session_storage_path,
            max_messages=50,
            session_timeout=86400
        )
        
        # 创建 Claude CLI 执行器
        claude_executor = ClaudeCodeCLIExecutor(
            target_dir=directory_path,
            timeout=5,
            use_native_session=True,
            session_storage_path=executor_storage_path
        )
        
        # 创建 Gemini CLI 执行器
        gemini_executor = GeminiCLIExecutor(
            target_dir=directory_path,
            timeout=5,
            use_native_session=True,
            session_storage_path=executor_storage_path
        )
        
        # 1. 设置飞书机器人会话
        session_manager.add_message(user_id, "user", "test message 1")
        session_manager.add_message(user_id, "assistant", "test response 1")
        
        # 2. 设置 Claude CLI 会话
        claude_executor.update_session_id(user_id, claude_session_id)
        
        # 3. 设置 Gemini CLI 会话
        gemini_executor.update_session_id(user_id, gemini_session_id)
        
        # 验证所有会话都存在
        assert len(session_manager.get_conversation_history(user_id)) == 2
        assert claude_executor.get_or_create_claude_session(user_id) == claude_session_id
        assert gemini_executor.get_or_create_gemini_session(user_id) == gemini_session_id
        
        # 4. 模拟 "/new" 命令 - 清除所有会话
        session_manager.create_new_session(user_id)
        claude_executor.clear_session(user_id)
        gemini_executor.clear_session(user_id)
        
        # 5. 验证所有会话都已清除
        assert len(session_manager.get_conversation_history(user_id)) == 0, \
            "Bot session should be cleared"
        assert claude_executor.get_or_create_claude_session(user_id) is None, \
            "Claude session should be cleared"
        assert gemini_executor.get_or_create_gemini_session(user_id) is None, \
            "Gemini session should be cleared"
    
    finally:
        cleanup_directory(directory_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
