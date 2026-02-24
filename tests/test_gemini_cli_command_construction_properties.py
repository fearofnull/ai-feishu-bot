"""
Gemini CLI 命令构造属性测试
使用 Hypothesis 进行基于属性的测试

Feature: feishu-ai-bot
Property 9: Gemini 命令构造完整性
Validates: Requirements 3.3, 3.4, 3.5, 3.6
"""
import os
import tempfile
import shutil
import pytest
from hypothesis import given, strategies as st, settings
from feishu_bot.gemini_cli_executor import GeminiCLIExecutor


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
    temp_dir = tempfile.mkdtemp(prefix="test_gemini_")
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
        params["model"] = draw(st.sampled_from(["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"]))
    
    # 可选的 temperature
    if draw(st.booleans()):
        params["temperature"] = draw(st.floats(min_value=0.0, max_value=2.0))
    
    # 可选的布尔参数
    if draw(st.booleans()):
        params["json"] = True
    
    return params if params else None


# Feature: feishu-ai-bot, Property 9: Gemini 命令构造完整性
# **Validates: Requirements 3.3, 3.4, 3.5, 3.6**
@settings(max_examples=100)
@given(
    directory_path=valid_directory_path(),
    user_prompt=user_prompt_strategy()
)
def test_gemini_command_includes_cwd_flag(directory_path, user_prompt):
    """
    Property 9: Gemini 命令构造完整性 - --cwd 标志
    
    For any 用户提示和目标目录，Gemini Executor 构造的命令应该包含 --cwd 标志和目标目录路径。
    
    **Validates: Requirements 3.3**
    """
    try:
        # 创建 Gemini CLI 执行器
        executor = GeminiCLIExecutor(target_dir=directory_path, timeout=10)
        
        # 构建命令参数
        command_args = executor.build_command_args(user_prompt)
        
        # 验证包含 --cwd 标志
        assert "--cwd" in command_args, \
            f"Command should include --cwd flag. Got: {command_args}"
        
        # 验证 --cwd 后面跟着目录路径
        cwd_index = command_args.index("--cwd")
        assert cwd_index + 1 < len(command_args), \
            "Command should have directory path after --cwd"
        
        assert command_args[cwd_index + 1] == directory_path, \
            f"Directory path should be {directory_path}, got {command_args[cwd_index + 1]}"
    
    finally:
        # 清理：删除临时目录
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)


# Feature: feishu-ai-bot, Property 9: Gemini 命令构造完整性
# **Validates: Requirements 3.3, 3.4, 3.5, 3.6**
@settings(max_examples=100)
@given(
    directory_path=valid_directory_path(),
    user_prompt=user_prompt_strategy()
)
def test_gemini_command_includes_prompt_flag(directory_path, user_prompt):
    """
    Property 9: Gemini 命令构造完整性 - --prompt 标志
    
    For any 用户提示和目标目录，Gemini Executor 构造的命令应该包含 --prompt 标志和用户提示。
    
    **Validates: Requirements 3.4**
    """
    try:
        # 创建 Gemini CLI 执行器
        executor = GeminiCLIExecutor(target_dir=directory_path, timeout=10)
        
        # 构建命令参数
        command_args = executor.build_command_args(user_prompt)
        
        # 验证包含 --prompt 标志
        assert "--prompt" in command_args, \
            f"Command should include --prompt flag. Got: {command_args}"
        
        # 验证 --prompt 后面跟着用户提示
        prompt_index = command_args.index("--prompt")
        assert prompt_index + 1 < len(command_args), \
            "Command should have user prompt after --prompt"
        
        assert command_args[prompt_index + 1] == user_prompt, \
            f"User prompt should be {user_prompt}, got {command_args[prompt_index + 1]}"
    
    finally:
        # 清理：删除临时目录
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)


# Feature: feishu-ai-bot, Property 9: Gemini 命令构造完整性
# **Validates: Requirements 3.3, 3.4, 3.5, 3.6**
@settings(max_examples=100)
@given(directory_path=valid_directory_path())
def test_gemini_command_uses_correct_executable(directory_path):
    """
    Property 9: Gemini 命令构造完整性 - 正确的可执行文件
    
    For any 目标目录，应该使用 gemini 命令。
    
    **Validates: Requirements 3.6**
    """
    try:
        # 创建 Gemini CLI 执行器
        executor = GeminiCLIExecutor(target_dir=directory_path, timeout=10)
        
        # 获取命令名称
        command_name = executor.get_command_name()
        
        # 验证命令名称
        assert command_name == "gemini", \
            f"Command should be 'gemini', got '{command_name}'"
        
        # 构建命令参数
        command_args = executor.build_command_args("test prompt")
        
        # 验证命令的第一个参数是正确的可执行文件
        assert command_args[0] == command_name, \
            f"First argument should be {command_name}, got {command_args[0]}"
    
    finally:
        # 清理：删除临时目录
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)


# Feature: feishu-ai-bot, Property 9: Gemini 命令构造完整性
# **Validates: Requirements 3.3, 3.4, 3.5, 3.6**
@settings(max_examples=100)
@given(
    directory_path=valid_directory_path(),
    user_prompt=user_prompt_strategy(),
    additional_params=additional_params_strategy()
)
def test_gemini_command_includes_additional_params(directory_path, user_prompt, additional_params):
    """
    Property 9: Gemini 命令构造完整性 - 额外参数
    
    For any 额外参数，Gemini Executor 构造的命令应该正确包含这些参数。
    
    **Validates: Requirements 3.6**
    """
    try:
        # 创建 Gemini CLI 执行器
        executor = GeminiCLIExecutor(target_dir=directory_path, timeout=10)
        
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


# Feature: feishu-ai-bot, Property 9: Gemini 命令构造完整性
# **Validates: Requirements 3.3, 3.4, 3.5, 3.6**
@settings(max_examples=100)
@given(
    directory_path=valid_directory_path(),
    user_prompt=user_prompt_strategy()
)
def test_gemini_command_sets_working_directory(directory_path, user_prompt):
    """
    Property 9: Gemini 命令构造完整性 - 工作目录
    
    For any 目标目录，Gemini Executor 应该将工作目录设置为目标目录（通过 --cwd 参数）。
    
    **Validates: Requirements 3.5**
    """
    try:
        # 创建 Gemini CLI 执行器
        executor = GeminiCLIExecutor(target_dir=directory_path, timeout=10)
        
        # 验证 target_dir 属性
        assert executor.target_dir == directory_path, \
            f"Executor target_dir should be {directory_path}, got {executor.target_dir}"
        
        # 构建命令参数
        command_args = executor.build_command_args(user_prompt)
        
        # 验证 --cwd 参数包含正确的目录
        assert "--cwd" in command_args, \
            "Command should include --cwd flag"
        
        cwd_index = command_args.index("--cwd")
        assert command_args[cwd_index + 1] == directory_path, \
            f"--cwd should specify {directory_path}, got {command_args[cwd_index + 1]}"
    
    finally:
        # 清理：删除临时目录
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)


# Feature: feishu-ai-bot, Property 9: Gemini 命令构造完整性
# **Validates: Requirements 3.3, 3.4, 3.5, 3.6**
@settings(max_examples=100)
@given(
    directory_path=valid_directory_path(),
    user_prompt=user_prompt_strategy()
)
def test_gemini_command_construction_order(directory_path, user_prompt):
    """
    Property 9: Gemini 命令构造完整性 - 参数顺序
    
    For any 用户提示和目标目录，Gemini Executor 构造的命令应该按照正确的顺序排列参数。
    
    **Validates: Requirements 3.3, 3.4, 3.5, 3.6**
    """
    try:
        # 创建 Gemini CLI 执行器
        executor = GeminiCLIExecutor(target_dir=directory_path, timeout=10)
        
        # 构建命令参数
        command_args = executor.build_command_args(user_prompt)
        
        # 验证命令结构
        # 1. 第一个参数应该是命令名称
        assert command_args[0] == "gemini", \
            f"First argument should be gemini command, got {command_args[0]}"
        
        # 2. --cwd 应该在 --prompt 之前
        cwd_index = command_args.index("--cwd")
        prompt_index = command_args.index("--prompt")
        assert cwd_index < prompt_index, \
            f"--cwd should come before --prompt. Got order: {command_args}"
        
        # 3. 验证完整的命令结构
        assert len(command_args) >= 5, \
            f"Command should have at least 5 arguments (command, --cwd, path, --prompt, prompt). Got: {command_args}"
    
    finally:
        # 清理：删除临时目录
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)


# Feature: feishu-ai-bot, Property 9: Gemini 命令构造完整性
# **Validates: Requirements 3.3, 3.4, 3.5, 3.6**
@settings(max_examples=100)
@given(
    directory_path=valid_directory_path(),
    user_prompt=user_prompt_strategy()
)
def test_gemini_command_construction_idempotent(directory_path, user_prompt):
    """
    Property 9: Gemini 命令构造完整性 - 幂等性
    
    For any 用户提示和目标目录，多次调用 build_command_args 应该返回相同的结果（幂等性）。
    
    **Validates: Requirements 3.3, 3.4, 3.5, 3.6**
    """
    try:
        # 创建 Gemini CLI 执行器
        executor = GeminiCLIExecutor(target_dir=directory_path, timeout=10)
        
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
