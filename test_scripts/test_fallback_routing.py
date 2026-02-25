#!/usr/bin/env python3
"""
测试降级路由逻辑

验证当默认provider不可用时，系统能否正确降级到其他可用的provider
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from feishu_bot.executor_registry import ExecutorRegistry, ExecutorMetadata
from feishu_bot.smart_router import SmartRouter
from feishu_bot.command_parser import CommandParser
from feishu_bot.models import ParsedCommand
from feishu_bot.openai_api_executor import OpenAIAPIExecutor
from feishu_bot.config import BotConfig


def test_fallback_routing():
    """测试降级路由"""
    print("=" * 60)
    print("测试降级路由逻辑")
    print("=" * 60)
    
    # 加载配置
    config = BotConfig.from_env()
    
    print(f"\n当前配置:")
    print(f"  DEFAULT_PROVIDER: {config.default_provider}")
    print(f"  DEFAULT_LAYER: {config.default_layer}")
    print(f"  CLAUDE_API_KEY: {'已配置' if config.claude_api_key else '未配置'}")
    print(f"  GEMINI_API_KEY: {'已配置' if config.gemini_api_key else '未配置'}")
    print(f"  OPENAI_API_KEY: {'已配置' if config.openai_api_key else '未配置'}")
    
    # 创建执行器注册表
    registry = ExecutorRegistry()
    
    # 只注册OpenAI（模拟用户只配置了OpenAI的情况）
    if config.openai_api_key:
        openai_api = OpenAIAPIExecutor(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url,
            model=config.openai_model,
            timeout=config.ai_timeout
        )
        openai_api_metadata = ExecutorMetadata(
            name="OpenAI API",
            provider="openai",
            layer="api",
            version="1.0.0",
            description="OpenAI API for general Q&A",
            capabilities=["general_qa", "text_generation", "analysis"],
            command_prefixes=["@openai", "@gpt"],
            priority=3,
            config_required=["api_key"]
        )
        registry.register_api_executor("openai", openai_api, openai_api_metadata)
        print(f"\n✅ 已注册: OpenAI API")
    
    # 创建智能路由器
    router = SmartRouter(
        executor_registry=registry,
        default_provider=config.default_provider,  # 可能是claude
        default_layer=config.default_layer
    )
    
    # 创建命令解析器
    parser = CommandParser()
    
    print("\n" + "=" * 60)
    print("测试场景")
    print("=" * 60)
    
    test_cases = [
        ("你是谁", "简单问答，无前缀"),
        ("什么是Python装饰器？", "概念解释，无前缀"),
        ("@claude 你好", "显式指定Claude（不可用）"),
        ("@openai 你好", "显式指定OpenAI（可用）"),
    ]
    
    all_passed = True
    for message, description in test_cases:
        print(f"\n测试: {description}")
        print(f"消息: '{message}'")
        
        try:
            # 解析命令
            parsed = parser.parse_command(message)
            print(f"  解析结果: provider={parsed.provider}, layer={parsed.execution_layer}, explicit={parsed.explicit}")
            
            # 路由
            executor = router.route(parsed)
            print(f"  ✅ 路由成功: {executor.get_provider_name()}")
            
        except Exception as e:
            print(f"  ❌ 路由失败: {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    if all_passed:
        print("🎉 所有测试通过！降级路由工作正常")
        print("\n关键点:")
        print("  1. 当默认provider不可用时，系统会自动降级到其他可用provider")
        print("  2. 降级顺序: 同provider另一层 → 其他provider同一层 → 其他provider另一层")
        print("  3. 用户无需关心哪个provider可用，系统会自动选择")
        return 0
    else:
        print("⚠️  部分测试失败")
        print("\n建议:")
        print("  1. 检查 .env 文件中的 DEFAULT_PROVIDER 配置")
        print("  2. 确保至少配置了一个AI服务的API密钥")
        print("  3. 如果只配置了OpenAI，设置 DEFAULT_PROVIDER=openai")
        return 1


if __name__ == "__main__":
    sys.exit(test_fallback_routing())
