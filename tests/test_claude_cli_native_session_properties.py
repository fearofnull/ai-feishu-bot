"""
Claude Code CLI 原生会话属性测试
使用 Hypothesis 进行基于属性的测试

Feature: feishu-ai-bot
Property 31: Claude Code CLI 原生会话使用
Property 33: Claude Code CLI 会话映射
Validates: Requirements 10.11, 10.12
"""
import os
import tempfile
import shutil
import time
import pytest
from hypothesis import given, strategies as st, settings
from feishu_bot.claude_cli_executor import ClaudeCodeCLIExecutor


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


# Feature: feishu-ai-bot, Property 31: Claude Code CLI 原生会话使用
# **Validates: Requirements 10.11, 10.12**
@settings(max_examples=100)
@given(user_id=user_id_strategy())
def test_claude_cli_uses_native_session_when_enabled(user_id):
    """
    Property 31: Claude Code CLI 原生会话使用
    
    For any 使用 Claude Code CLI 的执行，当启用原生会话管理时，
    构造的命令应该包含 --session 参数和对应用户的 Claude 会话 ID。
    
    **Validates: Requirements 10.11, 10.12**
    """
    directory_path = tempfile.mkdtemp(prefix="test_claude_session_")
    session_storage_path = os.path.join(directory_path, "executor_sessions.json")
    try:
        # 创建 Claude CLI 执行器，启用原生会话
        executor = ClaudeCodeCLIExecutor(
            target_dir=directory_path,
            timeout=5,
            use_native_session=True,
            session_storage_path=session_storage_path
        )
        
        # 首次执行，会话 ID 为 None
        command_args_1 = executor.build_command_args(
            "test prompt",
            additional_params={"user_id": user_id}
        )
        
        # 验证首次执行不包含 --session（因为会话 ID 为 None）
        assert "--session" not in command_args_1, \
            f"First execution should not include --session when session_id is None. Got: {command_args_1}"
        
        # 模拟设置会话 ID
        test_session_id = f"claude_session_{user_id}"
        executor.update_session_id(user_id, test_session_id)
        
        # 第二次执行，应该包含 --session
        command_args_2 = executor.build_command_args(
            "test prompt",
            additional_params={"user_id": user_id}
        )
        
        # 验证包含 --session 参数
        assert "--session" in command_args_2, \
            f"Command should include --session when session_id is set. Got: {command_args_2}"
        
        # 验证 --session 后面跟着会话 ID
        session_index = command_args_2.index("--session")
        assert session_index + 1 < len(command_args_2), \
            "Command should have session ID after --session"
        
        assert command_args_2[session_index + 1] == test_session_id, \
            f"Session ID should be {test_session_id}, got {command_args_2[session_index + 1]}"
    
    finally:
        cleanup_directory(directory_path)


# Feature: feishu-ai-bot, Property 31: Claude Code CLI 原生会话使用
# **Validates: Requirements 10.11, 10.12**
@settings(max_examples=100)
@given(user_id=user_id_strategy())
def test_claude_cli_no_session_when_disabled(user_id):
    """
    Property 31: Claude Code CLI 原生会话使用 - 禁用时不使用会话
    
    For any 使用 Claude Code CLI 的执行，当禁用原生会话管理时，
    构造的命令不应该包含 --session 参数。
    
    **Validates: Requirements 10.11**
    """
    directory_path = tempfile.mkdtemp(prefix="test_claude_no_session_")
    session_storage_path = os.path.join(directory_path, "executor_sessions.json")
    try:
        # 创建 Claude CLI 执行器，禁用原生会话
        executor = ClaudeCodeCLIExecutor(
            target_dir=directory_path,
            timeout=5,
            use_native_session=False,
            session_storage_path=session_storage_path
        )
        
        # 构建命令参数
        command_args = executor.build_command_args(
            "test prompt",
            additional_params={"user_id": user_id}
        )
        
        # 验证不包含 --session 参数
        assert "--session" not in command_args, \
            f"Command should not include --session when native session is disabled. Got: {command_args}"
    
    finally:
        cleanup_directory(directory_path)


# Feature: feishu-ai-bot, Property 33: Claude Code CLI 会话映射
# **Validates: Requirements 10.12**
@settings(max_examples=100)
@given(
    user_id=user_id_strategy(),
    session_id=session_id_strategy()
)
def test_claude_cli_maintains_session_mapping(user_id, session_id):
    """
    Property 33: Claude Code CLI 会话映射
    
    For any 用户 ID，Claude Executor 应该维护一个从用户 ID 到 Claude 会话 ID 的映射，
    确保同一用户的多次请求使用相同的 Claude 会话。
    
    **Validates: Requirements 10.12**
    """
    directory_path = tempfile.mkdtemp(prefix="test_claude_mapping_")
    session_storage_path = os.path.join(directory_path, "executor_sessions.json")
    try:
        # 创建 Claude CLI 执行器
        executor = ClaudeCodeCLIExecutor(
            target_dir=directory_path,
            timeout=5,
            use_native_session=True,
            session_storage_path=session_storage_path
        )
        
        # 首次获取会话 ID（应该为 None）
        initial_session_id = executor.get_or_create_claude_session(user_id)
        assert initial_session_id is None, \
            f"Initial session ID should be None, got {initial_session_id}"
        
        # 更新会话 ID
        executor.update_session_id(user_id, session_id)
        
        # 再次获取会话 ID（应该是更新后的值）
        retrieved_session_id = executor.get_or_create_claude_session(user_id)
        assert retrieved_session_id == session_id, \
            f"Retrieved session ID should be {session_id}, got {retrieved_session_id}"
        
        # 多次获取应该返回相同的会话 ID
        for _ in range(5):
            current_session_id = executor.get_or_create_claude_session(user_id)
            assert current_session_id == session_id, \
                f"Session ID should remain {session_id}, got {current_session_id}"
    
    finally:
        cleanup_directory(directory_path)


# Feature: feishu-ai-bot, Property 33: Claude Code CLI 会话映射
# **Validates: Requirements 10.12**
@settings(max_examples=100)
@given(
    user_id_1=user_id_strategy(),
    user_id_2=user_id_strategy(),
    session_id_1=session_id_strategy(),
    session_id_2=session_id_strategy()
)
def test_claude_cli_isolates_user_sessions(user_id_1, user_id_2, session_id_1, session_id_2):
    """
    Property 33: Claude Code CLI 会话映射 - 用户会话隔离
    
    For any 两个不同的用户 ID，它们的 Claude 会话应该是独立的，
    一个用户的会话 ID 不应该影响另一个用户的会话 ID。
    
    **Validates: Requirements 10.12**
    """
    # 确保用户 ID 不同
    if user_id_1 == user_id_2:
        user_id_2 = user_id_2 + "_different"
    
    directory_path = tempfile.mkdtemp(prefix="test_claude_isolation_")
    session_storage_path = os.path.join(directory_path, "executor_sessions.json")
    try:
        # 创建 Claude CLI 执行器
        executor = ClaudeCodeCLIExecutor(
            target_dir=directory_path,
            timeout=5,
            use_native_session=True,
            session_storage_path=session_storage_path
        )
        
        # 为两个用户设置不同的会话 ID
        executor.update_session_id(user_id_1, session_id_1)
        executor.update_session_id(user_id_2, session_id_2)
        
        # 验证每个用户的会话 ID 独立
        retrieved_session_1 = executor.get_or_create_claude_session(user_id_1)
        retrieved_session_2 = executor.get_or_create_claude_session(user_id_2)
        
        assert retrieved_session_1 == session_id_1, \
            f"User 1 session ID should be {session_id_1}, got {retrieved_session_1}"
        assert retrieved_session_2 == session_id_2, \
            f"User 2 session ID should be {session_id_2}, got {retrieved_session_2}"
        
        # 验证会话 ID 不同（如果输入的会话 ID 不同）
        if session_id_1 != session_id_2:
            assert retrieved_session_1 != retrieved_session_2, \
                f"Different users should have different session IDs"
    
    finally:
        cleanup_directory(directory_path)


# Feature: feishu-ai-bot, Property 33: Claude Code CLI 会话映射
# **Validates: Requirements 10.12**
@settings(max_examples=100)
@given(
    user_id=user_id_strategy(),
    session_id=session_id_strategy()
)
def test_claude_cli_clear_session(user_id, session_id):
    """
    Property 33: Claude Code CLI 会话映射 - 清除会话
    
    For any 用户 ID，调用 clear_session 后，该用户的会话映射应该被删除。
    
    **Validates: Requirements 10.12**
    """
    directory_path = tempfile.mkdtemp(prefix="test_claude_clear_")
    session_storage_path = os.path.join(directory_path, "executor_sessions.json")
    try:
        # 创建 Claude CLI 执行器
        executor = ClaudeCodeCLIExecutor(
            target_dir=directory_path,
            timeout=5,
            use_native_session=True,
            session_storage_path=session_storage_path
        )
        
        # 设置会话 ID
        executor.update_session_id(user_id, session_id)
        
        # 验证会话 ID 已设置
        retrieved_session_id = executor.get_or_create_claude_session(user_id)
        assert retrieved_session_id == session_id, \
            f"Session ID should be {session_id}, got {retrieved_session_id}"
        
        # 清除会话
        executor.clear_session(user_id)
        
        # 验证会话已清除（get_or_create 应该返回 None）
        cleared_session_id = executor.get_or_create_claude_session(user_id)
        assert cleared_session_id is None, \
            f"Session ID should be None after clearing, got {cleared_session_id}"
    
    finally:
        cleanup_directory(directory_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
