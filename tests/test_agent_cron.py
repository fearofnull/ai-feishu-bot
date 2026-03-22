#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试通过 Agent 创建定时任务
"""
import os
import sys
import json

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.agent_invoker import AgentInvoker

def test_agent_create_cron_job():
    """测试通过 Agent 创建定时任务"""
    print("\n=== 测试通过 Agent 创建定时任务 ===")
    
    # 创建 Agent 调用器
    invoker = AgentInvoker()
    
    # 检查默认提供商
    provider_info = invoker.get_default_provider()
    if not provider_info:
        print("❌ 未找到默认提供商配置")
        return False
    
    print(f"✅ 默认提供商: {provider_info.get('type')} - {provider_info.get('model')}")
    
    # 构建提示
    prompt = """请创建一个每分钟提醒我喝水的定时任务。

任务要求：
- 任务名称：每分钟喝水提醒
- 执行频率：每分钟执行一次
- 任务类型：文本任务
- 提醒内容：⏰ 喝水提醒：该喝水了！保持水分对健康很重要哦～
- 目标用户：当前用户

请使用 cron API 工具创建这个任务。"""
    
    # 调用 Agent
    result = invoker.invoke_agent_with_validation(
        prompt,
        validation_keywords=["创建", "成功", "任务", "cron", "job"]
    )
    
    print(f"\n执行结果: {result.get('success')}")
    print(f"Agent 输出: {result.get('output')}")
    
    if result.get("validated"):
        print("✅ 定时任务创建测试通过！")
        return True
    else:
        print("❌ 定时任务创建测试失败！")
        return False

def test_agent_list_cron_jobs():
    """测试通过 Agent 列出定时任务"""
    print("\n=== 测试通过 Agent 列出定时任务 ===")
    
    # 创建 Agent 调用器
    invoker = AgentInvoker()
    
    # 构建提示
    prompt = """请列出所有定时任务。

请使用 cron API 工具的 list 操作。"""
    
    # 调用 Agent
    result = invoker.invoke_agent_with_validation(
        prompt,
        validation_keywords=["cron job", "任务", "列表"]
    )
    
    print(f"\n执行结果: {result.get('success')}")
    print(f"Agent 输出: {result.get('output')}")
    
    if result.get("validated"):
        print("✅ 定时任务列出测试通过！")
        return True
    else:
        print("❌ 定时任务列出测试失败！")
        return False

def test_agent_delete_cron_job():
    """测试通过 Agent 删除定时任务"""
    print("\n=== 测试通过 Agent 删除定时任务 ===")
    
    # 创建 Agent 调用器
    invoker = AgentInvoker()
    
    # 构建提示
    prompt = """请删除名为"每分钟喝水提醒"的定时任务。

请使用 cron API 工具的 delete 操作。"""
    
    # 调用 Agent
    result = invoker.invoke_agent_with_validation(
        prompt,
        validation_keywords=["删除", "成功", "任务", "cron", "job"]
    )
    
    print(f"\n执行结果: {result.get('success')}")
    print(f"Agent 输出: {result.get('output')}")
    
    if result.get("validated"):
        print("✅ 定时任务删除测试通过！")
        return True
    else:
        print("❌ 定时任务删除测试失败！")
        return False

def main():
    """运行所有测试"""
    print("开始测试通过 Agent 操作定时任务...")
    
    # 运行测试
    create_success = test_agent_create_cron_job()
    list_success = test_agent_list_cron_jobs()
    delete_success = test_agent_delete_cron_job()
    
    # 汇总结果
    print("\n=== 测试结果汇总 ===")
    print(f"创建任务: {'✅ 通过' if create_success else '❌ 失败'}")
    print(f"列出任务: {'✅ 通过' if list_success else '❌ 失败'}")
    print(f"删除任务: {'✅ 通过' if delete_success else '❌ 失败'}")
    
    if create_success and list_success and delete_success:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n❌ 部分测试失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())
