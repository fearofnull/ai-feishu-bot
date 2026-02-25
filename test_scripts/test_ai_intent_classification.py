#!/usr/bin/env python3
"""
测试AI意图分类功能

验证使用AI判断用户意图是否比关键词检测更准确
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from feishu_bot.executor_registry import ExecutorRegistry, ExecutorMetadata
from feishu_bot.smart_router import SmartRouter
from feishu_bot.command_parser import CommandParser
from feishu_bot.openai_api_executor import OpenAIAPIExecutor
from feishu_bot.config import BotConfig


def test_ai_intent_classification():
    """测试AI意图分类"""
    print("=" * 80)
    print("测试AI意图分类功能")
    print("=" * 80)
    
    # 加载配置
    config = BotConfig.from_env()
    
    print(f"\n当前配置:")
    print(f"  DEFAULT_PROVIDER: {config.default_provider}")
    print(f"  DEFAULT_LAYER: {config.default_layer}")
    print(f"  OPENAI_API_KEY: {'已配置' if config.openai_api_key else '未配置'}")
    
    if not config.openai_api_key:
        print("\n❌ 错误: 需要配置OPENAI_API_KEY才能测试AI意图分类")
        return 1
    
    # 创建执行器注册表
    registry = ExecutorRegistry()
    
    # 注册OpenAI API执行器
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
    
    # 创建两个路由器：一个使用AI分类，一个使用关键词
    router_ai = SmartRouter(
        executor_registry=registry,
        default_provider=config.default_provider,
        default_layer=config.default_layer,
        use_ai_intent_classification=True  # 使用AI分类
    )
    
    router_keyword = SmartRouter(
        executor_registry=registry,
        default_provider=config.default_provider,
        default_layer=config.default_layer,
        use_ai_intent_classification=False  # 使用关键词
    )
    
    # 创建命令解析器
    parser = CommandParser()
    
    print("\n" + "=" * 80)
    print("测试场景对比")
    print("=" * 80)
    
    # 测试用例：包含各种表达方式
    test_cases = [
        # 明显需要CLI的情况
        ("帮我看看这个项目的代码结构", "需要CLI", True),
        ("能否分析一下main.py文件的逻辑？", "需要CLI", True),
        ("我想重构一下现有的代码", "需要CLI", True),
        ("项目里有哪些配置文件？", "需要CLI", True),
        
        # 明显不需要CLI的情况
        ("你是谁？", "不需要CLI", False),
        ("什么是Python装饰器？", "不需要CLI", False),
        ("帮我写一个快速排序算法", "不需要CLI", False),
        ("解释一下什么是微服务架构", "不需要CLI", False),
        
        # 模糊情况（关键词检测可能误判）
        ("如何设计一个代码审查流程？", "不需要CLI（讨论流程）", False),
        ("给我讲讲代码重构的最佳实践", "不需要CLI（理论知识）", False),
        ("我想学习如何分析项目架构", "不需要CLI（学习方法）", False),
        ("帮我生成一个项目结构的示例", "不需要CLI（生成示例）", False),
    ]
    
    print(f"\n{'序号':<4} {'测试消息':<40} {'预期':<20} {'AI判断':<10} {'关键词判断':<10} {'结果':<10}")
    print("-" * 100)
    
    correct_ai = 0
    correct_keyword = 0
    total = len(test_cases)
    
    for idx, (message, description, expected_cli) in enumerate(test_cases, 1):
        # 解析命令
        parsed = parser.parse_command(message)
        
        # AI路由判断
        try:
            executor_ai = router_ai.route(parsed)
            ai_result = "CLI" if executor_ai.get_provider_name().endswith("-cli") else "API"
            ai_correct = (ai_result == "CLI") == expected_cli
            if ai_correct:
                correct_ai += 1
        except Exception as e:
            ai_result = f"错误: {str(e)[:20]}"
            ai_correct = False
        
        # 关键词路由判断
        try:
            executor_keyword = router_keyword.route(parsed)
            keyword_result = "CLI" if executor_keyword.get_provider_name().endswith("-cli") else "API"
            keyword_correct = (keyword_result == "CLI") == expected_cli
            if keyword_correct:
                correct_keyword += 1
        except Exception as e:
            keyword_result = f"错误: {str(e)[:20]}"
            keyword_correct = False
        
        # 显示结果
        expected_str = "CLI" if expected_cli else "API"
        result_str = "✅" if ai_correct and keyword_correct else ("🔶" if ai_correct != keyword_correct else "❌")
        
        print(f"{idx:<4} {message[:38]:<40} {description:<20} {ai_result:<10} {keyword_result:<10} {result_str:<10}")
    
    print("-" * 100)
    print(f"\n统计结果:")
    print(f"  AI分类准确率: {correct_ai}/{total} ({correct_ai/total*100:.1f}%)")
    print(f"  关键词准确率: {correct_keyword}/{total} ({correct_keyword/total*100:.1f}%)")
    
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    if correct_ai > correct_keyword:
        print(f"🎉 AI分类比关键词检测更准确！")
        print(f"   准确率提升: {(correct_ai - correct_keyword)/total*100:.1f}%")
        print(f"\n优势:")
        print(f"  ✅ 能理解用户真实意图，不被关键词误导")
        print(f"  ✅ 可以处理各种表达方式")
        print(f"  ✅ 能区分理论讨论和实际操作")
    elif correct_ai == correct_keyword:
        print(f"⚖️  AI分类和关键词检测准确率相同")
        print(f"\n建议:")
        print(f"  - 可以使用AI分类以获得更好的用户体验")
        print(f"  - 关键词检测可作为降级方案")
    else:
        print(f"⚠️  关键词检测在这些测试用例中表现更好")
        print(f"\n可能原因:")
        print(f"  - AI模型可能需要更好的提示词")
        print(f"  - 测试用例可能不够全面")
    
    print(f"\n配置建议:")
    if correct_ai >= correct_keyword:
        print(f"  建议在 .env 中设置: USE_AI_INTENT_CLASSIFICATION=true")
    else:
        print(f"  建议在 .env 中设置: USE_AI_INTENT_CLASSIFICATION=false")
    
    return 0


if __name__ == "__main__":
    sys.exit(test_ai_intent_classification())
