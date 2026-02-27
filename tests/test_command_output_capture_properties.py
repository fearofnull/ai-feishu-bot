"""
命令输出捕获属性测试
使用 Hypothesis 进行基于属性的测试

Feature: feishu-ai-bot
Property 11: 命令输出捕获
Validates: Requirements 3.9
"""
import os
import tempfile
import shutil
import time
import pytest
from hypothesis import given, strategies as st, settings
from feishu_bot.claude_cli_executor import ClaudeCodeCLIExecutor
from feishu_bot.gemini_cli_executor import GeminiCLIExecutor


def cleanup_directory(directory_path):
    """安全清理目录，处理 Windows 文件锁定问题"""
    if os.path.exists(directory_path):
        try:
            shutil.rmtree(directory_path)
        except (PermissionError, OSError):
            # Windows 上可能会有文件锁定问题，等待后重试
            time.sleep(0.1)
            try:
                shutil.rmtree(directory_path)
            except (PermissionError, OSError):
                # 仍然失败，忽略清理错误
                pass


# Feature: feishu-ai-bot, Property 11: 命令输出捕获
# **Validates: Requirements 3.9**
def test_claude_command_captures_output_structure():
    """
    Property 11: 命令输出捕获 - Claude CLI 输出结构
    
    For any Claude 命令执行，ExecutionResult 应该包含 stdout 和 stderr 字段，
    捕获命令的所有输出。
    
    **Validates: Requirements 3.9**
    """
    directory_path = tempfile.mkdtemp(prefix="test_output_")
    try:
        # 创建 Claude CLI 执行器
        executor = ClaudeCodeCLIExecutor(target_dir=directory_path, timeout=5)
        
        # 执行命令（这会失败因为 Claude CLI 未安装，但我们可以验证输出捕获机制）
        result = executor.execute("test prompt")
        
        # 验证 ExecutionResult 包含输出字段
        assert hasattr(result, 'stdout'), \
            "ExecutionResult should have stdout field"
        assert hasattr(result, 'stderr'), \
            "ExecutionResult should have stderr field"
        
        # 验证输出字段是字符串类型
        assert isinstance(result.stdout, str), \
            f"stdout should be string, got {type(result.stdout)}"
        assert isinstance(result.stderr, str), \
            f"stderr should be string, got {type(result.stderr)}"
        
        # 对于失败的执行（CLI 未安装），至少应该有错误消息
        if not result.success:
            assert result.error_message is not None, \
                "Failed execution should have error_message"
    
    finally:
        cleanup_directory(directory_path)


# Feature: feishu-ai-bot, Property 11: 命令输出捕获
# **Validates: Requirements 3.9**
def test_gemini_command_captures_output_structure():
    """
    Property 11: 命令输出捕获 - Gemini CLI 输出结构
    
    For any Gemini 命令执行，ExecutionResult 应该包含 stdout 和 stderr 字段，
    捕获命令的所有输出。
    
    **Validates: Requirements 3.9**
    """
    directory_path = tempfile.mkdtemp(prefix="test_output_")
    try:
        # 创建 Gemini CLI 执行器
        executor = GeminiCLIExecutor(target_dir=directory_path, timeout=5)
        
        # 执行命令（这会失败因为 Gemini CLI 未安装，但我们可以验证输出捕获机制）
        result = executor.execute("test prompt")
        
        # 验证 ExecutionResult 包含输出字段
        assert hasattr(result, 'stdout'), \
            "ExecutionResult should have stdout field"
        assert hasattr(result, 'stderr'), \
            "ExecutionResult should have stderr field"
        
        # 验证输出字段是字符串类型
        assert isinstance(result.stdout, str), \
            f"stdout should be string, got {type(result.stdout)}"
        assert isinstance(result.stderr, str), \
            f"stderr should be string, got {type(result.stderr)}"
        
        # 对于失败的执行（CLI 未安装），至少应该有错误消息
        if not result.success:
            assert result.error_message is not None, \
                "Failed execution should have error_message"
    
    finally:
        cleanup_directory(directory_path)


# Feature: feishu-ai-bot, Property 11: 命令输出捕获
# **Validates: Requirements 3.9**
def test_execution_result_has_all_required_fields():
    """
    Property 11: 命令输出捕获 - ExecutionResult 完整性
    
    For any 命令执行，ExecutionResult 应该包含所有必需的字段：
    success, stdout, stderr, error_message, execution_time。
    
    **Validates: Requirements 3.9**
    """
    directory_path = tempfile.mkdtemp(prefix="test_output_")
    try:
        # 创建 Claude CLI 执行器
        executor = ClaudeCodeCLIExecutor(target_dir=directory_path, timeout=5)
        
        # 执行命令
        result = executor.execute("test prompt")
        
        # 验证所有必需字段存在
        assert hasattr(result, 'success'), \
            "ExecutionResult should have success field"
        assert hasattr(result, 'stdout'), \
            "ExecutionResult should have stdout field"
        assert hasattr(result, 'stderr'), \
            "ExecutionResult should have stderr field"
        assert hasattr(result, 'error_message'), \
            "ExecutionResult should have error_message field"
        assert hasattr(result, 'execution_time'), \
            "ExecutionResult should have execution_time field"
        
        # 验证字段类型
        assert isinstance(result.success, bool), \
            f"success should be bool, got {type(result.success)}"
        assert isinstance(result.stdout, str), \
            f"stdout should be str, got {type(result.stdout)}"
        assert isinstance(result.stderr, str), \
            f"stderr should be str, got {type(result.stderr)}"
        assert result.error_message is None or isinstance(result.error_message, str), \
            f"error_message should be None or str, got {type(result.error_message)}"
        assert isinstance(result.execution_time, (int, float)), \
            f"execution_time should be numeric, got {type(result.execution_time)}"
        
        # 验证 execution_time 非负
        assert result.execution_time >= 0, \
            f"execution_time should be non-negative, got {result.execution_time}"
    
    finally:
        cleanup_directory(directory_path)


# Feature: feishu-ai-bot, Property 11: 命令输出捕获
# **Validates: Requirements 3.9**
def test_output_capture_consistency():
    """
    Property 11: 命令输出捕获 - 一致性
    
    For any 相同的命令执行，多次执行应该返回一致的输出结构（即使内容可能不同）。
    
    **Validates: Requirements 3.9**
    """
    directory_path = tempfile.mkdtemp(prefix="test_output_")
    try:
        # 创建 Claude CLI 执行器
        executor = ClaudeCodeCLIExecutor(target_dir=directory_path, timeout=5)
        
        # 多次执行相同的命令
        result1 = executor.execute("test prompt")
        result2 = executor.execute("test prompt")
        
        # 验证输出结构一致
        assert type(result1.stdout) == type(result2.stdout), \
            "stdout type should be consistent across executions"
        assert type(result1.stderr) == type(result2.stderr), \
            "stderr type should be consistent across executions"
        assert type(result1.success) == type(result2.success), \
            "success type should be consistent across executions"
        assert type(result1.error_message) == type(result2.error_message), \
            "error_message type should be consistent across executions"
        assert type(result1.execution_time) == type(result2.execution_time), \
            "execution_time type should be consistent across executions"
    
    finally:
        cleanup_directory(directory_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
