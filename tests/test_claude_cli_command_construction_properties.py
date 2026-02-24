"""
Claude CLI 命令构造属性测试
使用 Hypothesis 进行基于属性的测试

Feature: feishu-ai-bot
Property 8: Claude 命令构造完整性
Validates: Requirements 3.3, 3.4, 3.5, 3.6, 3.10
"""
import os
import tempfile
import shutil
import platform
import pytest
from hypothesis import given, strategies as st, settings
from feishu_bot.claude_cli_executor import ClaudeCodeCLIExecutor


# 定义策略：生成有效的用户提示
@st.composite
def user_prompt_strategy(draw):
    """生成有效的用户提示"""
    # 生成包含各种字符的提示
    prompt = draw(st.text(min_size=1, max_size=500))
    return prompt


# 定义策略：生成有效的目录路径
@st.composite
def valid_directory_path(draw):
    """生成有效的临时目录路径"""
    temp_dir = tempfile.mkdtemp(prefix="test_claude_")
    return temp_dir


# 定义策略：生成额外参数
@st.composite
def additional_params_strategy(draw):
    """生成额外参数字典"""
    params = {}
    
    # 可选的 user_id
    if draw(st.booleans()):
        params["user_id"] = draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
    
    # 可选的 model
    if draw(st.booleans()):
        params["model"] = draw(st.sampled_from(["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"]))
    
    # 可选的 max_tokens
    if draw(st.booleans()):
        params["max_tokens"] = draw(st.integers(min_value=100, max_value=4096))
    
    # 可选的布尔参数
    if draw(st.booleans()):
        params["json"] = True
    
    return params if params else None


# Feature: feishu-ai-bot, Property 8: Claude 命令构造完整性
# **Validates: Requirements 3.3, 3.4, 3.5, 3.6, 3.10**
@settings(max_examples=100)
@given(
    directory_path=valid_directory_path(),
    user_prompt=user_prompt_strategy()
)
def test_claude_command_includes_add_dir_flag(directory_path, user_prompt):
    """
    Property 8: Claude 命令构造完整性 - --add-dir 标志
    
    For any 用户提示和目标目录，Claude Executor 构造的命令应该包含 --add-dir 标志和目标目录路径。
    
    **Validates: Requirements 3.3**
    """
    try:
        # 创建 Claude CLI 执行器
        executor = ClaudeCodeCLIExecutor(target_dir=directory_path, timeout=10)
        
        # 构建命令参数
        command_args = executor.build_command_args(user_prompt)
        
        # 验证包含 --add-dir 标志
        assert "--add-dir" in command_args, \
            f"Command should include --add-dir flag. Got: {command_args}"
        
        # 验证 --add-dir 后面跟着目录路径
        add_dir_index = command_args.index("--add-dir")
        assert add_dir_index + 1 < len(command_args), \
            "Command should have directory path after --add-dir"
        
        assert command_args[add_dir_index + 1] == directory_path, \
            f"Directory path should be {directory_path}, got {command_args[add_dir_index + 1]}"
    
    finally:
        # 清理：删除临时目录
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)


# Feature: feishu-ai-bot, Property 8: Claude 命令构造完整性
# **Validates: Requirements 3.3, 3.4, 3.5, 3.6, 3.10**
@settings(max_examples=100)
@given(
    directory_path=valid_directory_path(),
    user_prompt=user_prompt_strategy()
)
def test_claude_command_includes_prompt_flag(directory_path, user_prompt):
    """
    Property 8: Claude 命令构造完整性 - -p/--prompt 标志
    
    For any 用户提示和目标目录，Claude Executor 构造的命令应该包含 -p 或 --prompt 标志和用户提示。
    
    **Validates: Requirements 3.4**
    """
    try:
        # 创建 Claude CLI 执行器
        executor = ClaudeCodeCLIExecutor(target_dir=directory_path, timeout=10)
        
        # 构建命令参数
        command_args = executor.build_command_args(user_prompt)
        
        # 验证包含 -p 标志
        assert "-p" in command_args, \
            f"Command should include -p flag. Got: {command_args}"
        
        # 验证 -p 后面跟着用户提示
        prompt_index = command_args.index("-p")
        assert prompt_index + 1 < len(command_args), \
            "Command should have user prompt after -p"
        
        assert command_args[prompt_index + 1] == user_prompt, \
            f"User prompt should be {user_prompt}, got {command_args[prompt_index + 1]}"
    
    finally:
        # 清理：删除临时目录
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)


# Feature: feishu-ai-bot, Property 8: Claude 命令构造完整性
# **Validates: Requirements 3.3, 3.4, 3.5, 3.6, 3.10**
@settings(max_examples=100)
@given(directory_path=valid_directory_path())
def test_claude_command_uses_correct_executable(directory_path):
    """
    Property 8: Claude 命令构造完整性 - 正确的可执行文件
    
    For any 目标目录，在 Windows 上应该使用 claude.cmd，在 Unix-like 系统上应该使用 claude。
    
    **Validates: Requirements 3.10**
    """
    try:
        # 创建 Claude CLI 执行器
        executor = ClaudeCodeCLIExecutor(target_dir=directory_path, timeout=10)
        
        # 获取命令名称
        command_name = executor.get_command_name()
        
        # 验证命令名称
        if platform.system() == "Windows":
            assert command_name == "claude.cmd", \
                f"On Windows, command should be 'claude.cmd', got '{command_name}'"
        else:
            assert command_name == "claude", \
                f"On Unix-like systems, command should be 'claude', got '{command_name}'"
        
        # 构建命令参数
        command_args = executor.build_command_args("test prompt")
        
        # 验证命令的第一个参数是正确的可执行文件
        assert command_args[0] == command_name, \
            f"First argument should be {command_name}, got {command_args[0]}"
    
    finally:
        # 清理：删除临时目录
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)


# Feature: feishu-ai-bot, Property 8: Claude 命令构造完整性
# **Validates: Requirements 3.3, 3.4, 3.5, 3.6, 3.10**
@settings(max_examples=100)
@given(
    directory_path=valid_directory_path(),
    user_prompt=user_prompt_strategy(),
    additional_params=additional_params_strategy()
)
def test_claude_command_includes_additional_params(directory_path, user_prompt, additional_params):
    """
    Property 8: Claude 命令构造完整性 - 额外参数
    
    For any 额外参数，Claude Executor 构造的命令应该正确包含这些参数。
    
    **Validates: Requirements 3.6**
    """
    try:
        # 创建 Claude CLI 执行器
        executor = ClaudeCodeCLIExecutor(target_dir=directory_path, timeout=10)
        
        # 构建命令参数
        command_args = executor.build_command_args(user_prompt, additional_params)
        
        # 验证额外参数
        if additional_params:
            for key, value in additional_params.items():
                # 跳过内部参数
                if key == "user_id":
                    continue
                
                # 布尔参数
                if value is True:
                    assert f"--{key}" in command_args, \
                        f"Command should include --{key} flag. Got: {command_args}"
                # 其他参数
                elif value is not None:
                    assert f"--{key}" in command_args, \
                        f"Command should include --{key} flag. Got: {command_args}"
                    
                    # 验证参数值
                    key_index = command_args.index(f"--{key}")
                    assert key_index + 1 < len(command_args), \
                        f"Command should have value after --{key}"
                    
                    assert command_args[key_index + 1] == str(value), \
                        f"Value for --{key} should be {value}, got {command_args[key_index + 1]}"
    
    finally:
        # 清理：删除临时目录
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)


# Feature: feishu-ai-bot, Property 8: Claude 命令构造完整性
# **Validates: Requirements 3.3, 3.4, 3.5, 3.6, 3.10**
@settings(max_examples=100)
@given(
    directory_path=valid_directory_path(),
    user_prompt=user_prompt_strategy()
)
def test_claude_command_sets_working_directory(directory_path, user_prompt):
    """
    Property 8: Claude 命令构造完整性 - 工作目录
    
    For any 目标目录，Claude Executor 应该将工作目录设置为目标目录。
    
    **Validates: Requirements 3.5**
    """
    try:
        # 创建 Claude CLI 执行器
        executor = ClaudeCodeCLIExecutor(target_dir=directory_path, timeout=10)
        
        # 验证 target_dir 属性
        assert executor.target_dir == directory_path, \
            f"Executor target_dir should be {directory_path}, got {executor.target_dir}"
        
        # 注意：实际的工作目录设置在 execute 方法中通过 subprocess.run 的 cwd 参数完成
        # 这里我们验证 executor 保存了正确的目录路径
    
    finally:
        # 清理：删除临时目录
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)


# Feature: feishu-ai-bot, Property 8: Claude 命令构造完整性
# **Validates: Requirements 3.3, 3.4, 3.5, 3.6, 3.10**
@settings(max_examples=100)
@given(
    directory_path=valid_directory_path(),
    user_prompt=user_prompt_strategy()
)
def test_claude_command_construction_order(directory_path, user_prompt):
    """
    Property 8: Claude 命令构造完整性 - 参数顺序
    
    For any 用户提示和目标目录，Claude Executor 构造的命令应该按照正确的顺序排列参数。
    
    **Validates: Requirements 3.3, 3.4, 3.5, 3.6, 3.10**
    """
    try:
        # 创建 Claude CLI 执行器
        executor = ClaudeCodeCLIExecutor(target_dir=directory_path, timeout=10)
        
        # 构建命令参数
        command_args = executor.build_command_args(user_prompt)
        
        # 验证命令结构
        # 1. 第一个参数应该是命令名称
        assert command_args[0] in ["claude", "claude.cmd"], \
            f"First argument should be claude command, got {command_args[0]}"
        
        # 2. --add-dir 应该在 -p 之前
        add_dir_index = command_args.index("--add-dir")
        prompt_index = command_args.index("-p")
        assert add_dir_index < prompt_index, \
            f"--add-dir should come before -p. Got order: {command_args}"
        
        # 3. 验证完整的命令结构
        assert len(command_args) >= 5, \
            f"Command should have at least 5 arguments (command, --add-dir, path, -p, prompt). Got: {command_args}"
    
    finally:
        # 清理：删除临时目录
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)


# Feature: feishu-ai-bot, Property 8: Claude 命令构造完整性
# **Validates: Requirements 3.3, 3.4, 3.5, 3.6, 3.10**
@settings(max_examples=100)
@given(
    directory_path=valid_directory_path(),
    user_prompt=user_prompt_strategy()
)
def test_claude_command_construction_idempotent(directory_path, user_prompt):
    """
    Property 8: Claude 命令构造完整性 - 幂等性
    
    For any 用户提示和目标目录，多次调用 build_command_args 应该返回相同的结果（幂等性）。
    
    **Validates: Requirements 3.3, 3.4, 3.5, 3.6, 3.10**
    """
    try:
        # 创建 Claude CLI 执行器
        executor = ClaudeCodeCLIExecutor(target_dir=directory_path, timeout=10)
        
        # 多次构建命令参数
        command_args_1 = executor.build_command_args(user_prompt)
        command_args_2 = executor.build_command_args(user_prompt)
        command_args_3 = executor.build_command_args(user_prompt)
        
        # 验证所有结果相同
        assert command_args_1 == command_args_2, \
            f"Multiple calls should return same result. Got: {command_args_1} vs {command_args_2}"
        
        assert command_args_2 == command_args_3, \
            f"Multiple calls should return same result. Got: {command_args_2} vs {command_args_3}"
    
    finally:
        # 清理：删除临时目录
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
