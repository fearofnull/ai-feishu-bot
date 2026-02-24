"""
目录验证属性测试
使用 Hypothesis 进行基于属性的测试

Feature: feishu-ai-bot
Property 7: 目录验证
Validates: Requirements 3.1
"""
import os
import tempfile
import shutil
import pytest
from hypothesis import given, strategies as st, settings
from feishu_bot.claude_cli_executor import ClaudeCodeCLIExecutor
from feishu_bot.gemini_cli_executor import GeminiCLIExecutor


# 定义策略：生成有效的目录路径
@st.composite
def valid_directory_path(draw):
    """生成有效的临时目录路径"""
    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="test_dir_")
    return temp_dir


# 定义策略：生成不存在的目录路径
@st.composite
def non_existent_directory_path(draw):
    """生成不存在的目录路径"""
    # 创建一个临时目录然后删除它
    temp_dir = tempfile.mkdtemp(prefix="test_nonexist_")
    shutil.rmtree(temp_dir)
    return temp_dir


# 定义策略：生成文件路径（而非目录）
@st.composite
def file_path_not_directory(draw):
    """生成文件路径（而非目录）"""
    # 创建临时文件
    fd, temp_file = tempfile.mkstemp(prefix="test_file_")
    os.close(fd)
    return temp_file


# Feature: feishu-ai-bot, Property 7: 目录验证
# **Validates: Requirements 3.1**
@settings(max_examples=100)
@given(directory_path=non_existent_directory_path())
def test_directory_verification_non_existent_claude(directory_path):
    """
    Property 7: 目录验证（Claude CLI - 不存在的目录）
    
    For any 不存在的目录路径，Claude_Executor 的 verify_directory 方法应该返回 false，
    并且不应该尝试执行 Claude 命令。
    
    **Validates: Requirements 3.1**
    """
    try:
        # 创建 Claude CLI 执行器
        executor = ClaudeCodeCLIExecutor(target_dir=directory_path, timeout=10)
        
        # 验证目录
        is_valid = executor.verify_directory()
        
        # 验证返回 False
        assert is_valid is False, \
            f"verify_directory should return False for non-existent directory: {directory_path}"
        
        # 尝试执行命令，应该返回错误
        result = executor.execute("test prompt")
        
        # 验证执行失败
        assert result.success is False, \
            "Execution should fail for non-existent directory"
        
        # 验证错误消息包含目录信息
        assert result.error_message is not None, \
            "Error message should not be None"
        assert "目标目录不存在" in result.error_message or "不存在" in result.error_message, \
            f"Error message should mention directory not found. Got: {result.error_message}"
        assert directory_path in result.error_message, \
            f"Error message should contain the directory path. Got: {result.error_message}"
    
    finally:
        # 清理：确保目录不存在
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)


# Feature: feishu-ai-bot, Property 7: 目录验证
# **Validates: Requirements 3.1**
@settings(max_examples=100)
@given(directory_path=non_existent_directory_path())
def test_directory_verification_non_existent_gemini(directory_path):
    """
    Property 7: 目录验证（Gemini CLI - 不存在的目录）
    
    For any 不存在的目录路径，Gemini_Executor 的 verify_directory 方法应该返回 false，
    并且不应该尝试执行 Gemini 命令。
    
    **Validates: Requirements 3.1**
    """
    try:
        # 创建 Gemini CLI 执行器
        executor = GeminiCLIExecutor(target_dir=directory_path, timeout=10)
        
        # 验证目录
        is_valid = executor.verify_directory()
        
        # 验证返回 False
        assert is_valid is False, \
            f"verify_directory should return False for non-existent directory: {directory_path}"
        
        # 尝试执行命令，应该返回错误
        result = executor.execute("test prompt")
        
        # 验证执行失败
        assert result.success is False, \
            "Execution should fail for non-existent directory"
        
        # 验证错误消息包含目录信息
        assert result.error_message is not None, \
            "Error message should not be None"
        assert "目标目录不存在" in result.error_message or "不存在" in result.error_message, \
            f"Error message should mention directory not found. Got: {result.error_message}"
        assert directory_path in result.error_message, \
            f"Error message should contain the directory path. Got: {result.error_message}"
    
    finally:
        # 清理：确保目录不存在
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)


# Feature: feishu-ai-bot, Property 7: 目录验证
# **Validates: Requirements 3.1**
@settings(max_examples=100)
@given(file_path=file_path_not_directory())
def test_directory_verification_file_not_directory_claude(file_path):
    """
    Property 7: 目录验证（Claude CLI - 文件而非目录）
    
    For any 文件路径（而非目录），Claude_Executor 的 verify_directory 方法应该返回 false。
    
    **Validates: Requirements 3.1**
    """
    try:
        # 创建 Claude CLI 执行器
        executor = ClaudeCodeCLIExecutor(target_dir=file_path, timeout=10)
        
        # 验证目录
        is_valid = executor.verify_directory()
        
        # 验证返回 False（文件不是目录）
        assert is_valid is False, \
            f"verify_directory should return False for file path: {file_path}"
        
        # 尝试执行命令，应该返回错误
        result = executor.execute("test prompt")
        
        # 验证执行失败
        assert result.success is False, \
            "Execution should fail for file path (not directory)"
    
    finally:
        # 清理：删除临时文件
        if os.path.exists(file_path):
            os.remove(file_path)


# Feature: feishu-ai-bot, Property 7: 目录验证
# **Validates: Requirements 3.1**
@settings(max_examples=100)
@given(file_path=file_path_not_directory())
def test_directory_verification_file_not_directory_gemini(file_path):
    """
    Property 7: 目录验证（Gemini CLI - 文件而非目录）
    
    For any 文件路径（而非目录），Gemini_Executor 的 verify_directory 方法应该返回 false。
    
    **Validates: Requirements 3.1**
    """
    try:
        # 创建 Gemini CLI 执行器
        executor = GeminiCLIExecutor(target_dir=file_path, timeout=10)
        
        # 验证目录
        is_valid = executor.verify_directory()
        
        # 验证返回 False（文件不是目录）
        assert is_valid is False, \
            f"verify_directory should return False for file path: {file_path}"
        
        # 尝试执行命令，应该返回错误
        result = executor.execute("test prompt")
        
        # 验证执行失败
        assert result.success is False, \
            "Execution should fail for file path (not directory)"
    
    finally:
        # 清理：删除临时文件
        if os.path.exists(file_path):
            os.remove(file_path)


# Feature: feishu-ai-bot, Property 7: 目录验证
# **Validates: Requirements 3.1**
@settings(max_examples=100)
@given(directory_path=valid_directory_path())
def test_directory_verification_valid_directory_claude(directory_path):
    """
    Property 7: 目录验证（Claude CLI - 有效目录）
    
    For any 存在的有效目录路径，Claude_Executor 的 verify_directory 方法应该返回 true。
    
    **Validates: Requirements 3.1**
    """
    try:
        # 创建 Claude CLI 执行器
        executor = ClaudeCodeCLIExecutor(target_dir=directory_path, timeout=10)
        
        # 验证目录
        is_valid = executor.verify_directory()
        
        # 验证返回 True
        assert is_valid is True, \
            f"verify_directory should return True for valid directory: {directory_path}"
        
        # 验证目录确实存在
        assert os.path.exists(directory_path), \
            f"Directory should exist: {directory_path}"
        assert os.path.isdir(directory_path), \
            f"Path should be a directory: {directory_path}"
    
    finally:
        # 清理：删除临时目录
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)


# Feature: feishu-ai-bot, Property 7: 目录验证
# **Validates: Requirements 3.1**
@settings(max_examples=100)
@given(directory_path=valid_directory_path())
def test_directory_verification_valid_directory_gemini(directory_path):
    """
    Property 7: 目录验证（Gemini CLI - 有效目录）
    
    For any 存在的有效目录路径，Gemini_Executor 的 verify_directory 方法应该返回 true。
    
    **Validates: Requirements 3.1**
    """
    try:
        # 创建 Gemini CLI 执行器
        executor = GeminiCLIExecutor(target_dir=directory_path, timeout=10)
        
        # 验证目录
        is_valid = executor.verify_directory()
        
        # 验证返回 True
        assert is_valid is True, \
            f"verify_directory should return True for valid directory: {directory_path}"
        
        # 验证目录确实存在
        assert os.path.exists(directory_path), \
            f"Directory should exist: {directory_path}"
        assert os.path.isdir(directory_path), \
            f"Path should be a directory: {directory_path}"
    
    finally:
        # 清理：删除临时目录
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)


# Feature: feishu-ai-bot, Property 7: 目录验证
# **Validates: Requirements 3.1**
@settings(max_examples=100)
@given(
    directory_path=valid_directory_path(),
    verify_count=st.integers(min_value=1, max_value=10)
)
def test_directory_verification_idempotent_claude(directory_path, verify_count):
    """
    Property 7: 目录验证（Claude CLI - 幂等性）
    
    For any 有效目录，多次调用 verify_directory 应该返回相同的结果（幂等性）。
    
    **Validates: Requirements 3.1**
    """
    try:
        # 创建 Claude CLI 执行器
        executor = ClaudeCodeCLIExecutor(target_dir=directory_path, timeout=10)
        
        # 多次验证目录
        results = []
        for _ in range(verify_count):
            is_valid = executor.verify_directory()
            results.append(is_valid)
        
        # 验证所有结果相同
        assert len(set(results)) == 1, \
            f"Multiple verifications should return the same result. Got: {results}"
        
        # 验证结果为 True
        assert results[0] is True, \
            f"All verifications should return True for valid directory"
    
    finally:
        # 清理：删除临时目录
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)


# Feature: feishu-ai-bot, Property 7: 目录验证
# **Validates: Requirements 3.1**
@settings(max_examples=100)
@given(
    directory_path=valid_directory_path(),
    verify_count=st.integers(min_value=1, max_value=10)
)
def test_directory_verification_idempotent_gemini(directory_path, verify_count):
    """
    Property 7: 目录验证（Gemini CLI - 幂等性）
    
    For any 有效目录，多次调用 verify_directory 应该返回相同的结果（幂等性）。
    
    **Validates: Requirements 3.1**
    """
    try:
        # 创建 Gemini CLI 执行器
        executor = GeminiCLIExecutor(target_dir=directory_path, timeout=10)
        
        # 多次验证目录
        results = []
        for _ in range(verify_count):
            is_valid = executor.verify_directory()
            results.append(is_valid)
        
        # 验证所有结果相同
        assert len(set(results)) == 1, \
            f"Multiple verifications should return the same result. Got: {results}"
        
        # 验证结果为 True
        assert results[0] is True, \
            f"All verifications should return True for valid directory"
    
    finally:
        # 清理：删除临时目录
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)


# Feature: feishu-ai-bot, Property 7: 目录验证
# **Validates: Requirements 3.1**
@settings(max_examples=100)
@given(directory_path=non_existent_directory_path())
def test_directory_verification_prevents_execution_claude(directory_path):
    """
    Property 7: 目录验证（Claude CLI - 阻止执行）
    
    For any 不存在的目录，执行命令时应该立即返回错误，不应该尝试调用 Claude CLI。
    
    **Validates: Requirements 3.1**
    """
    try:
        # 创建 Claude CLI 执行器
        executor = ClaudeCodeCLIExecutor(target_dir=directory_path, timeout=10)
        
        # 执行命令
        result = executor.execute("test prompt")
        
        # 验证执行失败
        assert result.success is False, \
            "Execution should fail immediately for non-existent directory"
        
        # 验证执行时间很短（没有实际调用 CLI）
        assert result.execution_time < 1.0, \
            f"Execution should fail quickly without calling CLI. Time: {result.execution_time}s"
        
        # 验证 stdout 和 stderr 为空（没有实际执行）
        assert result.stdout == "", \
            "stdout should be empty when directory verification fails"
        assert result.stderr == "", \
            "stderr should be empty when directory verification fails"
    
    finally:
        # 清理：确保目录不存在
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)


# Feature: feishu-ai-bot, Property 7: 目录验证
# **Validates: Requirements 3.1**
@settings(max_examples=100)
@given(directory_path=non_existent_directory_path())
def test_directory_verification_prevents_execution_gemini(directory_path):
    """
    Property 7: 目录验证（Gemini CLI - 阻止执行）
    
    For any 不存在的目录，执行命令时应该立即返回错误，不应该尝试调用 Gemini CLI。
    
    **Validates: Requirements 3.1**
    """
    try:
        # 创建 Gemini CLI 执行器
        executor = GeminiCLIExecutor(target_dir=directory_path, timeout=10)
        
        # 执行命令
        result = executor.execute("test prompt")
        
        # 验证执行失败
        assert result.success is False, \
            "Execution should fail immediately for non-existent directory"
        
        # 验证执行时间很短（没有实际调用 CLI）
        assert result.execution_time < 1.0, \
            f"Execution should fail quickly without calling CLI. Time: {result.execution_time}s"
        
        # 验证 stdout 和 stderr 为空（没有实际执行）
        assert result.stdout == "", \
            "stdout should be empty when directory verification fails"
        assert result.stderr == "", \
            "stderr should be empty when directory verification fails"
    
    finally:
        # 清理：确保目录不存在
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)


# Feature: feishu-ai-bot, Property 7: 目录验证
# **Validates: Requirements 3.1**
@settings(max_examples=100)
@given(directory_path=valid_directory_path())
def test_directory_verification_is_available_claude(directory_path):
    """
    Property 7: 目录验证（Claude CLI - is_available 方法）
    
    For any 有效目录，is_available 方法应该返回 True。
    
    **Validates: Requirements 3.1**
    """
    try:
        # 创建 Claude CLI 执行器
        executor = ClaudeCodeCLIExecutor(target_dir=directory_path, timeout=10)
        
        # 检查可用性
        is_available = executor.is_available()
        
        # 验证返回 True
        assert is_available is True, \
            f"is_available should return True for valid directory: {directory_path}"
        
        # 验证与 verify_directory 一致
        is_valid = executor.verify_directory()
        assert is_available == is_valid, \
            "is_available should be consistent with verify_directory"
    
    finally:
        # 清理：删除临时目录
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)


# Feature: feishu-ai-bot, Property 7: 目录验证
# **Validates: Requirements 3.1**
@settings(max_examples=100)
@given(directory_path=valid_directory_path())
def test_directory_verification_is_available_gemini(directory_path):
    """
    Property 7: 目录验证（Gemini CLI - is_available 方法）
    
    For any 有效目录，is_available 方法应该返回 True。
    
    **Validates: Requirements 3.1**
    """
    try:
        # 创建 Gemini CLI 执行器
        executor = GeminiCLIExecutor(target_dir=directory_path, timeout=10)
        
        # 检查可用性
        is_available = executor.is_available()
        
        # 验证返回 True
        assert is_available is True, \
            f"is_available should return True for valid directory: {directory_path}"
        
        # 验证与 verify_directory 一致
        is_valid = executor.verify_directory()
        assert is_available == is_valid, \
            "is_available should be consistent with verify_directory"
    
    finally:
        # 清理：删除临时目录
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
