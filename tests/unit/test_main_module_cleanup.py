"""
Task 2.3 单元测试 - 验证主模块清理

验证主模块（feishu_bot/feishu_bot.py）已移除传统API执行器：
1. 代码中不包含 ClaudeAPIExecutor 和 GeminiAPIExecutor 的导入
2. _register_executors 方法不注册传统API执行器
3. 保留 OpenAIAPIExecutor 导入（用于 UnifiedAPIInterface）
4. 保留所有 CLI 执行器的导入和注册

需求: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6
"""
import sys
import os
import importlib.util
from pathlib import Path
import ast
import inspect


def test_main_module_file_exists():
    """验证主模块文件存在"""
    file_path = Path("feishu_bot/feishu_bot.py")
    assert file_path.exists(), f"主模块文件不存在: {file_path}"
    print("✓ 主模块文件存在: feishu_bot/feishu_bot.py")


def test_no_legacy_executor_imports():
    """验证代码中不包含 ClaudeAPIExecutor 和 GeminiAPIExecutor 的导入
    
    需求: 2.1, 2.2
    """
    file_path = Path("feishu_bot/feishu_bot.py")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 检查不应该存在的导入
    assert "ClaudeAPIExecutor" not in content, \
        "主模块不应包含 ClaudeAPIExecutor 的导入"
    assert "GeminiAPIExecutor" not in content, \
        "主模块不应包含 GeminiAPIExecutor 的导入"
    
    # 检查不应该存在的导入语句
    assert "from .executors.claude_api_executor import" not in content, \
        "主模块不应包含 claude_api_executor 的导入语句"
    assert "from .executors.gemini_api_executor import" not in content, \
        "主模块不应包含 gemini_api_executor 的导入语句"
    
    print("✓ 主模块不包含 ClaudeAPIExecutor 和 GeminiAPIExecutor 的导入")


def test_openai_executor_import_preserved():
    """验证 OpenAIAPIExecutor 导入被保留（用于 UnifiedAPIInterface）
    
    需求: 2.3
    """
    file_path = Path("feishu_bot/feishu_bot.py")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # OpenAIAPIExecutor 应该被保留
    assert "OpenAIAPIExecutor" in content, \
        "主模块应该保留 OpenAIAPIExecutor 的导入（用于 UnifiedAPIInterface）"
    assert "from .executors.openai_api_executor import OpenAIAPIExecutor" in content, \
        "主模块应该包含 openai_api_executor 的导入语句"
    
    print("✓ OpenAIAPIExecutor 导入被保留（用于 UnifiedAPIInterface）")


def test_cli_executor_imports_preserved():
    """验证所有 CLI 执行器的导入被保留
    
    需求: 2.7
    """
    file_path = Path("feishu_bot/feishu_bot.py")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 检查 CLI 执行器导入
    assert "ClaudeCodeCLIExecutor" in content, \
        "主模块应该保留 ClaudeCodeCLIExecutor 的导入"
    assert "GeminiCLIExecutor" in content, \
        "主模块应该保留 GeminiCLIExecutor 的导入"
    assert "QwenCLIExecutor" in content, \
        "主模块应该保留 QwenCLIExecutor 的导入"
    
    print("✓ 所有 CLI 执行器的导入被保留")


def test_no_legacy_executor_registration():
    """验证 _register_executors 方法不注册传统API执行器
    
    需求: 2.4, 2.5, 2.6
    """
    file_path = Path("feishu_bot/feishu_bot.py")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 解析 AST
    tree = ast.parse(content)
    
    # 查找 _register_executors 方法
    register_method = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_register_executors":
            register_method = node
            break
    
    assert register_method is not None, "_register_executors 方法不存在"
    
    # 获取方法的源代码
    method_source = ast.get_source_segment(content, register_method)
    
    # 检查不应该存在的注册代码
    assert "ClaudeAPIExecutor" not in method_source, \
        "_register_executors 不应该注册 ClaudeAPIExecutor"
    assert "GeminiAPIExecutor" not in method_source, \
        "_register_executors 不应该注册 GeminiAPIExecutor"
    
    # 检查不应该存在的注册调用
    assert "register_api_executor" not in method_source or \
           ("claude" not in method_source.lower() and "gemini" not in method_source.lower()), \
        "_register_executors 不应该包含传统API执行器的注册调用"
    
    print("✓ _register_executors 方法不注册传统API执行器")


def test_cli_executor_registration_preserved():
    """验证 _register_executors 方法保留 CLI 执行器的注册
    
    需求: 2.7
    """
    file_path = Path("feishu_bot/feishu_bot.py")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 解析 AST
    tree = ast.parse(content)
    
    # 查找 _register_executors 方法
    register_method = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_register_executors":
            register_method = node
            break
    
    assert register_method is not None, "_register_executors 方法不存在"
    
    # 获取方法的源代码
    method_source = ast.get_source_segment(content, register_method)
    
    # 检查 CLI 执行器的注册
    assert "ClaudeCodeCLIExecutor" in method_source, \
        "_register_executors 应该注册 ClaudeCodeCLIExecutor"
    assert "GeminiCLIExecutor" in method_source, \
        "_register_executors 应该注册 GeminiCLIExecutor"
    assert "QwenCLIExecutor" in method_source, \
        "_register_executors 应该注册 QwenCLIExecutor"
    
    # 检查 CLI 注册调用
    assert "register_cli_executor" in method_source, \
        "_register_executors 应该包含 register_cli_executor 调用"
    
    print("✓ _register_executors 方法保留 CLI 执行器的注册")


def test_no_legacy_api_key_references():
    """验证主模块不包含传统API密钥的引用
    
    需求: 10.1, 10.2
    """
    file_path = Path("feishu_bot/feishu_bot.py")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 检查不应该存在的 API 密钥引用
    assert "claude_api_key" not in content, \
        "主模块不应包含 claude_api_key 的引用"
    assert "gemini_api_key" not in content, \
        "主模块不应包含 gemini_api_key 的引用"
    
    # 注意：openai_api_key 可能在注释或文档中出现，所以不做严格检查
    # 但不应该在代码逻辑中使用
    
    print("✓ 主模块不包含传统API密钥的引用")


def test_unified_api_interface_initialization():
    """验证 UnifiedAPIInterface 正确初始化
    
    需求: 9.1, 9.2
    """
    file_path = Path("feishu_bot/feishu_bot.py")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 检查 UnifiedAPIInterface 的导入和初始化
    assert "from feishu_bot.core.unified_api import UnifiedAPIInterface" in content or \
           "from .core.unified_api import UnifiedAPIInterface" in content, \
        "主模块应该导入 UnifiedAPIInterface"
    
    assert "UnifiedAPIInterface" in content, \
        "主模块应该使用 UnifiedAPIInterface"
    
    assert "self.unified_api_interface" in content, \
        "主模块应该初始化 unified_api_interface 属性"
    
    print("✓ UnifiedAPIInterface 正确初始化")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("Task 2.3 单元测试 - 验证主模块清理")
    print("=" * 60)
    print()
    
    try:
        test_main_module_file_exists()
        test_no_legacy_executor_imports()
        test_openai_executor_import_preserved()
        test_cli_executor_imports_preserved()
        test_no_legacy_executor_registration()
        test_cli_executor_registration_preserved()
        test_no_legacy_api_key_references()
        test_unified_api_interface_initialization()
        
        print()
        print("=" * 60)
        print("✓ 所有测试通过！主模块清理验证成功")
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
