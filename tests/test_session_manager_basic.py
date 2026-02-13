"""
基本单元测试 - SessionManager
"""
import os
import tempfile
import shutil
import pytest
from feishu_bot.session_manager import SessionManager


@pytest.fixture
def temp_storage():
    """创建临时存储目录"""
    temp_dir = tempfile.mkdtemp()
    storage_path = os.path.join(temp_dir, "sessions.json")
    yield storage_path
    # 清理
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_session_manager_initialization(temp_storage):
    """测试 SessionManager 初始化"""
    manager = SessionManager(
        storage_path=temp_storage,
        max_messages=10,
        session_timeout=3600
    )
    
    assert manager.storage_path == temp_storage
    assert manager.max_messages == 10
    assert manager.session_timeout == 3600
    assert len(manager.sessions) == 0


def test_create_and_get_session(temp_storage):
    """测试创建和获取会话"""
    manager = SessionManager(storage_path=temp_storage)
    
    # 创建会话
    session1 = manager.get_or_create_session("user_1")
    assert session1.user_id == "user_1"
    assert len(session1.messages) == 0
    
    # 再次获取应该返回相同会话
    session2 = manager.get_or_create_session("user_1")
    assert session2.session_id == session1.session_id


def test_add_message(temp_storage):
    """测试添加消息"""
    manager = SessionManager(storage_path=temp_storage)
    
    # 添加消息
    manager.add_message("user_1", "user", "Hello")
    manager.add_message("user_1", "assistant", "Hi there!")
    
    # 获取历史
    history = manager.get_conversation_history("user_1")
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[0].content == "Hello"
    assert history[1].role == "assistant"
    assert history[1].content == "Hi there!"


def test_session_info(temp_storage):
    """测试获取会话信息"""
    manager = SessionManager(storage_path=temp_storage)
    
    # 不存在的会话
    info = manager.get_session_info("user_1")
    assert info["exists"] is False
    
    # 创建会话并添加消息
    manager.add_message("user_1", "user", "Test")
    info = manager.get_session_info("user_1")
    
    assert info["exists"] is True
    assert "session_id" in info
    assert info["message_count"] == 1


def test_new_session_command(temp_storage):
    """测试新会话命令"""
    manager = SessionManager(storage_path=temp_storage)
    
    # 创建初始会话
    session1 = manager.get_or_create_session("user_1")
    manager.add_message("user_1", "user", "Message 1")
    
    # 处理新会话命令
    response = manager.handle_session_command("user_1", "/new")
    assert response is not None
    assert "新会话" in response or "New session" in response
    
    # 验证创建了新会话
    session2 = manager.get_or_create_session("user_1")
    assert session2.session_id != session1.session_id
    assert len(session2.messages) == 0


def test_session_persistence(temp_storage):
    """测试会话持久化"""
    # 创建会话并保存
    manager1 = SessionManager(storage_path=temp_storage)
    manager1.add_message("user_1", "user", "Hello")
    manager1.add_message("user_1", "assistant", "Hi")
    manager1.save_sessions()
    
    # 创建新的 manager 实例并加载
    manager2 = SessionManager(storage_path=temp_storage)
    history = manager2.get_conversation_history("user_1")
    
    assert len(history) == 2
    assert history[0].content == "Hello"
    assert history[1].content == "Hi"


def test_format_history_for_ai(temp_storage):
    """测试格式化对话历史"""
    manager = SessionManager(storage_path=temp_storage)
    
    # 空历史
    formatted = manager.format_history_for_ai("user_1")
    assert formatted == ""
    
    # 添加消息
    manager.add_message("user_1", "user", "What is Python?")
    manager.add_message("user_1", "assistant", "Python is a programming language.")
    
    formatted = manager.format_history_for_ai("user_1")
    assert "Previous conversation:" in formatted
    assert "User: What is Python?" in formatted
    assert "Assistant: Python is a programming language." in formatted


def test_session_command_detection(temp_storage):
    """测试会话命令检测"""
    manager = SessionManager(storage_path=temp_storage)
    
    # 会话命令
    assert manager.is_session_command("/new") is True
    assert manager.is_session_command("新会话") is True
    assert manager.is_session_command("/session") is True
    assert manager.is_session_command("会话信息") is True
    assert manager.is_session_command("/history") is True
    assert manager.is_session_command("历史记录") is True
    
    # 非会话命令
    assert manager.is_session_command("Hello") is False
    assert manager.is_session_command("What is AI?") is False


def test_session_storage_file_corruption_handling(temp_storage):
    """测试会话存储文件损坏处理
    
    Validates: Requirements 10.3
    """
    # 创建会话并保存
    manager1 = SessionManager(storage_path=temp_storage)
    manager1.add_message("user_1", "user", "Test message")
    manager1.save_sessions()
    
    # 损坏存储文件（写入无效的 JSON）
    with open(temp_storage, 'w', encoding='utf-8') as f:
        f.write("{ invalid json content }")
    
    # 创建新的 manager 实例并尝试加载
    # 应该优雅地处理错误，不抛出异常
    manager2 = SessionManager(storage_path=temp_storage)
    
    # 验证 manager 仍然可以工作（从空状态开始）
    assert len(manager2.sessions) == 0
    
    # 验证可以创建新会话
    session = manager2.get_or_create_session("user_2")
    assert session is not None
    assert session.user_id == "user_2"


def test_session_loading_failure_handling(temp_storage):
    """测试会话加载失败处理
    
    Validates: Requirements 10.3
    """
    # 创建会话并保存
    manager1 = SessionManager(storage_path=temp_storage)
    manager1.add_message("user_1", "user", "Test message")
    manager1.save_sessions()
    
    # 损坏存储文件（写入空内容）
    with open(temp_storage, 'w', encoding='utf-8') as f:
        f.write("")
    
    # 创建新的 manager 实例并尝试加载
    manager2 = SessionManager(storage_path=temp_storage)
    
    # 验证 manager 从空状态开始
    assert len(manager2.sessions) == 0
    
    # 验证可以正常使用
    manager2.add_message("user_2", "user", "New message")
    history = manager2.get_conversation_history("user_2")
    assert len(history) == 1


def test_session_loading_missing_fields(temp_storage):
    """测试加载缺少必需字段的会话数据
    
    Validates: Requirements 10.3
    """
    import json
    
    # 写入缺少字段的会话数据
    invalid_data = {
        "sessions": {
            "user_1": {
                "session_id": "test_session",
                "user_id": "user_1"
                # 缺少 created_at, last_active, messages
            }
        }
    }
    
    with open(temp_storage, 'w', encoding='utf-8') as f:
        json.dump(invalid_data, f)
    
    # 尝试加载应该失败但不崩溃
    manager = SessionManager(storage_path=temp_storage)
    
    # 验证 manager 从空状态开始（加载失败）
    assert len(manager.sessions) == 0


def test_session_saving_failure_handling(temp_storage):
    """测试会话保存失败处理
    
    Validates: Requirements 10.3
    """
    manager = SessionManager(storage_path=temp_storage)
    manager.add_message("user_1", "user", "Test message")
    
    # 使存储路径无效（设置为只读目录）
    import os
    storage_dir = os.path.dirname(temp_storage)
    
    # 保存原始权限
    original_mode = os.stat(storage_dir).st_mode
    
    try:
        # 将目录设置为只读（在 Windows 上可能不生效）
        os.chmod(storage_dir, 0o444)
        
        # 尝试保存（应该失败但不崩溃）
        manager.save_sessions()
        
        # 验证 manager 仍然可以工作
        manager.add_message("user_1", "assistant", "Response")
        history = manager.get_conversation_history("user_1")
        assert len(history) == 2
    finally:
        # 恢复原始权限
        try:
            os.chmod(storage_dir, original_mode)
        except:
            pass


def test_archived_session_functionality(temp_storage):
    """测试归档会话功能
    
    Validates: Requirements 10.3
    """
    manager = SessionManager(storage_path=temp_storage, max_messages=5)
    
    # 添加消息但不触发自动轮换
    manager.add_message("user_1", "user", "Message 1")
    manager.add_message("user_1", "assistant", "Response 1")
    manager.add_message("user_1", "user", "Message 2")
    
    # 获取旧会话 ID（不会触发轮换，因为只有3条消息，max_messages=5）
    old_session = manager.get_or_create_session("user_1")
    old_session_id = old_session.session_id
    
    # 验证会话有3条消息
    assert len(old_session.messages) == 3
    
    # 触发新会话（归档旧会话）
    manager.handle_session_command("user_1", "/new")
    
    # 验证归档目录存在
    assert os.path.exists(manager.archive_dir)
    
    # 验证归档文件已创建
    archive_files = os.listdir(manager.archive_dir)
    assert len(archive_files) == 1
    
    # 验证归档文件名格式
    archive_file = archive_files[0]
    assert archive_file.endswith('.json')
    assert old_session_id in archive_file
    
    # 验证归档文件内容
    import json
    archive_path = os.path.join(manager.archive_dir, archive_file)
    with open(archive_path, 'r', encoding='utf-8') as f:
        archived_data = json.load(f)
    
    assert archived_data['session_id'] == old_session_id
    assert archived_data['user_id'] == 'user_1'
    assert len(archived_data['messages']) == 3


def test_archived_session_with_special_characters_in_user_id(temp_storage):
    """测试包含特殊字符的用户 ID 的归档功能
    
    Validates: Requirements 10.3
    """
    manager = SessionManager(storage_path=temp_storage)
    
    # 使用包含特殊字符的用户 ID
    special_user_id = "user<>:\"/\\|?*\x00test"
    
    # 添加消息
    manager.add_message(special_user_id, "user", "Test message")
    
    # 触发归档
    manager.handle_session_command(special_user_id, "/new")
    
    # 验证归档文件已创建（特殊字符应该被清理）
    archive_files = os.listdir(manager.archive_dir)
    assert len(archive_files) == 1
    
    # 验证文件名不包含非法字符
    archive_file = archive_files[0]
    invalid_chars = '<>:"/\\|?*\x00'
    for char in invalid_chars:
        assert char not in archive_file


def test_multiple_archived_sessions(temp_storage):
    """测试多次归档会话
    
    Validates: Requirements 10.3
    """
    manager = SessionManager(storage_path=temp_storage)
    
    # 创建并归档多个会话
    num_sessions = 3
    for i in range(num_sessions):
        manager.add_message("user_1", "user", f"Message {i}")
        manager.handle_session_command("user_1", "/new")
    
    # 验证归档文件数量
    archive_files = os.listdir(manager.archive_dir)
    assert len(archive_files) == num_sessions
    
    # 验证所有归档文件都是有效的 JSON
    import json
    for archive_file in archive_files:
        archive_path = os.path.join(manager.archive_dir, archive_file)
        with open(archive_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert 'session_id' in data
            assert 'user_id' in data
            assert 'messages' in data


def test_archived_session_cleanup_on_rotation(temp_storage):
    """测试会话轮换时的归档
    
    Validates: Requirements 10.3
    """
    manager = SessionManager(storage_path=temp_storage, max_messages=2)
    
    # 添加第一条消息
    manager.add_message("user_1", "user", "Message 1")
    
    # 获取会话并记录 ID
    session1 = manager.get_or_create_session("user_1")
    old_session_id = session1.session_id
    assert len(session1.messages) == 1
    
    # 添加第二条消息，达到最大值
    manager.add_message("user_1", "assistant", "Response 1")
    
    # 此时会话已满（len(messages)=2 >= max_messages=2）
    # 下次调用 get_or_create_session 会触发轮换
    
    # 再次调用 get_or_create_session，应该触发轮换
    new_session = manager.get_or_create_session("user_1")
    
    # 验证会话已轮换
    assert new_session.session_id != old_session_id
    
    # 验证新会话是空的
    assert len(new_session.messages) == 0
    
    # 验证旧会话已归档
    archive_files = os.listdir(manager.archive_dir)
    assert len(archive_files) == 1
    
    # 验证归档文件包含旧会话 ID
    assert any(old_session_id in f for f in archive_files)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
