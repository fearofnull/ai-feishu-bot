"""
Task 3.3 单元测试 - 验证配置模块清理

验证配置模块（feishu_bot/config.py）已移除传统API密钥字段：
1. BotConfig 不包含传统API密钥字段
2. has_api_key 方法不存在
3. from_env 不加载传统API密钥
4. print_status 不打印传统API密钥状态

需求: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8
"""
import sys
import os
from pathlib import Path
import ast
import inspect
import importlib.util


def test_config_module_file_exists():
    """验证配置模块文件存在"""
    file_path = Path("feishu_bot/config.py")
    assert file_path.exists(), f"配置模块文件不存在: {file_path}"
    print("✓ 配置模块文件存在: feishu_bot/config.py")


def test_no_legacy_api_key_fields():
    """验证 BotConfig 不包含传统API密钥字段
    
    需求: 3.1, 3.2, 3.3, 3.4, 3.5
    """
    file_path = Path("feishu_bot/config.py")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 解析 AST
    tree = ast.parse(content)
    
    # 查找 BotConfig 类
    bot_config_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "BotConfig":
            bot_config_class = node
            break
    
    assert bot_config_class is not None, "BotConfig 类不存在"
    
    # 获取类的源代码
    class_source = ast.get_source_segment(content, bot_config_class)
    
    # 检查不应该存在的字段
    legacy_fields = [
        "claude_api_key",
        "gemini_api_key",
        "openai_api_key",
        "openai_base_url",
        "openai_model"
    ]
    
    for field in legacy_fields:
        assert field not in class_source, \
            f"BotConfig 不应包含字段: {field}"
    
    print("✓ BotConfig 不包含传统API密钥字段")


def test_has_api_key_method_removed():
    """验证 has_api_key 方法不存在
    
    需求: 3.6
    """
    file_path = Path("feishu_bot/config.py")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 解析 AST
    tree = ast.parse(content)
    
    # 查找 has_api_key 方法
    has_api_key_method = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "has_api_key":
            has_api_key_method = node
            break
    
    assert has_api_key_method is None, \
        "BotConfig 不应包含 has_api_key 方法"
    
    # 也检查字符串中是否存在
    assert "def has_api_key" not in content, \
        "配置模块不应包含 has_api_key 方法定义"
    
    print("✓ has_api_key 方法不存在")


def test_from_env_no_legacy_keys():
    """验证 from_env 方法不加载传统API密钥
    
    需求: 3.7
    """
    file_path = Path("feishu_bot/config.py")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 解析 AST
    tree = ast.parse(content)
    
    # 查找 from_env 方法
    from_env_method = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "from_env":
            from_env_method = node
            break
    
    assert from_env_method is not None, "from_env 方法不存在"
    
    # 获取方法的源代码
    method_source = ast.get_source_segment(content, from_env_method)
    
    # 检查不应该存在的环境变量加载
    legacy_env_vars = [
        "CLAUDE_API_KEY",
        "GEMINI_API_KEY",
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "OPENAI_MODEL"
    ]
    
    for env_var in legacy_env_vars:
        assert env_var not in method_source, \
            f"from_env 不应加载环境变量: {env_var}"
    
    # 检查不应该存在的字段赋值
    legacy_field_assignments = [
        "claude_api_key=",
        "gemini_api_key=",
        "openai_api_key=",
        "openai_base_url=",
        "openai_model="
    ]
    
    for assignment in legacy_field_assignments:
        assert assignment not in method_source, \
            f"from_env 不应包含字段赋值: {assignment}"
    
    print("✓ from_env 方法不加载传统API密钥")


def test_print_status_no_legacy_keys():
    """验证 print_status 方法不打印传统API密钥状态
    
    需求: 3.8
    """
    file_path = Path("feishu_bot/config.py")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 解析 AST
    tree = ast.parse(content)
    
    # 查找 print_status 方法
    print_status_method = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "print_status":
            print_status_method = node
            break
    
    assert print_status_method is not None, "print_status 方法不存在"
    
    # 获取方法的源代码
    method_source = ast.get_source_segment(content, print_status_method)
    
    # 检查不应该存在的打印语句
    legacy_print_patterns = [
        "CLAUDE_API_KEY",
        "GEMINI_API_KEY",
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "OPENAI_MODEL",
        "claude_api_key",
        "gemini_api_key",
        "openai_api_key",
        "openai_base_url",
        "openai_model"
    ]
    
    for pattern in legacy_print_patterns:
        assert pattern not in method_source, \
            f"print_status 不应打印: {pattern}"
    
    print("✓ print_status 方法不打印传统API密钥状态")


def test_config_class_structure():
    """验证 BotConfig 类保留了必要的字段
    
    确保清理过程中没有误删重要字段
    """
    file_path = Path("feishu_bot/config.py")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 解析 AST
    tree = ast.parse(content)
    
    # 查找 BotConfig 类
    bot_config_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "BotConfig":
            bot_config_class = node
            break
    
    assert bot_config_class is not None, "BotConfig 类不存在"
    
    # 获取类的源代码
    class_source = ast.get_source_segment(content, bot_config_class)
    
    # 检查应该保留的重要字段
    required_fields = [
        "app_id",
        "app_secret",
        "target_directory",
        "ai_timeout",
    ]
    
    for field in required_fields:
        assert field in class_source, \
            f"BotConfig 应该保留字段: {field}"
    
    print("✓ BotConfig 类保留了必要的字段")


def test_cli_config_preserved():
    """验证 CLI 配置字段被保留
    
    确保 CLI 执行器相关的配置没有被误删
    """
    file_path = Path("feishu_bot/config.py")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 解析 AST
    tree = ast.parse(content)
    
    # 查找 BotConfig 类
    bot_config_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "BotConfig":
            bot_config_class = node
            break
    
    assert bot_config_class is not None, "BotConfig 类不存在"
    
    # 获取类的源代码
    class_source = ast.get_source_segment(content, bot_config_class)
    
    # 检查 CLI 配置字段
    cli_fields = [
        "target_directory",
        "claude_cli_target_dir",
        "gemini_cli_target_dir",
        "qwen_cli_target_dir"
    ]
    
    for field in cli_fields:
        assert field in class_source, \
            f"BotConfig 应该保留 CLI 配置字段: {field}"
    
    print("✓ CLI 配置字段被保留")


def test_no_legacy_api_key_in_comments():
    """验证注释和文档字符串中不包含传统API密钥的误导性说明
    
    需求: 10.3
    """
    file_path = Path("feishu_bot/config.py")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 检查不应该存在的注释模式
    # 注意：这里只检查明显的配置说明，不检查所有出现
    misleading_patterns = [
        "# Claude API 配置",
        "# Gemini API 配置",
        "# OpenAI API 配置",
        "# API 密钥配置"
    ]
    
    for pattern in misleading_patterns:
        assert pattern not in content, \
            f"配置模块不应包含误导性注释: {pattern}"
    
    print("✓ 注释和文档字符串中不包含传统API密钥的误导性说明")


def test_config_instantiation():
    """验证 BotConfig 可以正常实例化（不会因为缺少字段而失败）"""
    # 直接加载配置模块文件，避免导入整个包
    import importlib.util
    
    config_path = Path("feishu_bot/config.py")
    spec = importlib.util.spec_from_file_location("config", config_path)
    config_module = importlib.util.module_from_spec(spec)
    
    try:
        spec.loader.exec_module(config_module)
        BotConfig = config_module.BotConfig
        
        # 尝试创建实例（使用最小必需字段）
        config = BotConfig(
            app_id="test_app_id",
            app_secret="test_app_secret",
            target_directory="/test/dir"
        )
        
        # 验证实例创建成功
        assert config.app_id == "test_app_id"
        assert config.app_secret == "test_app_secret"
        assert config.target_directory == "/test/dir"
        
        # 验证不存在传统API密钥字段
        assert not hasattr(config, "claude_api_key"), \
            "BotConfig 实例不应有 claude_api_key 属性"
        assert not hasattr(config, "gemini_api_key"), \
            "BotConfig 实例不应有 gemini_api_key 属性"
        assert not hasattr(config, "openai_api_key"), \
            "BotConfig 实例不应有 openai_api_key 属性"
        assert not hasattr(config, "openai_base_url"), \
            "BotConfig 实例不应有 openai_base_url 属性"
        assert not hasattr(config, "openai_model"), \
            "BotConfig 实例不应有 openai_model 属性"
        
        # 验证不存在 has_api_key 方法
        assert not hasattr(config, "has_api_key"), \
            "BotConfig 实例不应有 has_api_key 方法"
        
        print("✓ BotConfig 可以正常实例化且不包含传统API密钥字段")
        
    except Exception as e:
        raise AssertionError(f"BotConfig 实例化失败: {e}")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("Task 3.3 单元测试 - 验证配置模块清理")
    print("=" * 60)
    print()
    
    try:
        test_config_module_file_exists()
        test_no_legacy_api_key_fields()
        test_has_api_key_method_removed()
        test_from_env_no_legacy_keys()
        test_print_status_no_legacy_keys()
        test_config_class_structure()
        test_cli_config_preserved()
        test_no_legacy_api_key_in_comments()
        test_config_instantiation()
        
        print()
        print("=" * 60)
        print("✓ 所有测试通过！配置模块清理验证成功")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"✗ 测试失败: {e}")
        print("=" * 60)
        return 1
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ 测试错误: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
