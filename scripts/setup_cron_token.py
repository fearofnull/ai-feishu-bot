#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置 Cron API Token 的便捷脚本

这个脚本会自动：
1. 检查 Web Admin 是否运行
2. 使用管理员密码登录获取 JWT Token
3. 将 Token 写入 .env 文件
4. 验证配置是否成功

使用方法：
    python3 scripts/setup_cron_token.py [options]

选项：
    --url URL          Web Admin 地址（默认：从 .env 读取或 http://localhost:8080）
    --password PWD     管理员密码（默认：从 .env 读取或 admin123）
    --expiry HOURS    Token 有效期，单位：小时（默认：2）
    --help             显示帮助信息
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='配置 Cron API Token',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 使用默认配置
  python3 scripts/setup_cron_token.py
  
  # 指定 Web Admin 地址
  python3 scripts/setup_cron_token.py --url http://localhost:9090
  
  # 指定 Token 有效期为 4 小时
  python3 scripts/setup_cron_token.py --expiry 4
  
  # 完整配置
  python3 scripts/setup_cron_token.py --url http://localhost:9090 --password mypassword --expiry 4
        """
    )
    
    parser.add_argument(
        '--url',
        type=str,
        default=None,
        help='Web Admin 地址（默认：从 .env 读取或 http://localhost:8080）'
    )
    
    parser.add_argument(
        '--password',
        type=str,
        default=None,
        help='管理员密码（默认：从 .env 读取或 admin123）'
    )
    
    parser.add_argument(
        '--expiry',
        type=int,
        default=None,
        help='Token 有效期，单位：小时（默认：2）'
    )
    
    return parser.parse_args()


def get_env_file_path():
    """获取 .env 文件路径"""
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    return env_file


def load_env_file(env_file):
    """加载现有的 .env 文件"""
    env_vars = {}
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars


def save_env_file(env_file, env_vars):
    """保存环境变量到 .env 文件（保留注释和格式）
    
    Args:
        env_file: .env 文件路径
        env_vars: 环境变量字典
    """
    # 读取现有文件内容（保留注释和格式）
    lines = []
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    
    # 查找 WEB_ADMIN_TOKEN 行
    token_line_found = False
    updated_lines = []
    
    for line in lines:
        # 检查是否是 WEB_ADMIN_TOKEN 行
        if line.strip().startswith('WEB_ADMIN_TOKEN='):
            # 更新 Token 行
            updated_lines.append(f"WEB_ADMIN_TOKEN={env_vars['WEB_ADMIN_TOKEN']}\n")
            token_line_found = True
        else:
            # 保留其他行（包括注释）
            updated_lines.append(line)
    
    # 如果没有找到 WEB_ADMIN_TOKEN 行，添加到文件末尾
    if not token_line_found:
        # 如果文件不为空且最后一行不是空行，添加一个空行
        if updated_lines and not updated_lines[-1].strip() == '':
            updated_lines.append('\n')
        # 添加 Token 行
        updated_lines.append(f"WEB_ADMIN_TOKEN={env_vars['WEB_ADMIN_TOKEN']}\n")
    
    # 写回文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)


def check_web_admin_status(base_url):
    """检查 Web Admin 是否运行"""
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def login_to_web_admin(base_url, password, expiry_hours):
    """登录 Web Admin 获取 Token
    
    Args:
        base_url: Web Admin 地址
        password: 管理员密码
        expiry_hours: Token 有效期（小时）
    
    Returns:
        Token 字符串或 None
    """
    login_url = f"{base_url}/api/auth/login"
    
    try:
        response = requests.post(
            login_url,
            json={"password": password},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                token = data['data']['token']
                # 从响应中获取有效期信息
                expires_in = data.get('data', {}).get('expires_in', expiry_hours * 3600)
                expires_at = data.get('data', {}).get('expires_at', '')
                
                print(f"✅ 登录成功！")
                print(f"📋 Token: {token[:20]}...{token[-10:]}")
                print(f"⏰ 有效期: {expires_in} 秒（约 {expires_in // 3600} 小时）")
                if expires_at:
                    print(f"📅 过期时间: {expires_at}")
                print()
                
                return token
        else:
            print(f"❌ 登录失败: 状态码 {response.status_code}")
            try:
                error_data = response.json()
                print(f"   错误信息: {error_data.get('message', '未知错误')}")
            except:
                print(f"   响应: {response.text}")
        
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ 登录失败: {e}")
        return None


def verify_token(base_url, token):
    """验证 Token 是否有效"""
    try:
        response = requests.get(
            f"{base_url}/api/cron/jobs",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=5
        )
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Token 验证失败: 状态码 {response.status_code}")
            try:
                error_data = response.json()
                print(f"   错误信息: {error_data.get('message', '未知错误')}")
            except:
                print(f"   响应: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Token 验证失败: {e}")
        return False


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    print("=" * 60)
    print("Cron API Token 配置工具")
    print("=" * 60)
    print()
    
    # 获取 .env 文件路径
    env_file = get_env_file_path()
    print(f"📁 配置文件: {env_file}")
    print()
    
    # 加载现有配置
    env_vars = load_env_file(env_file)
    
    # 获取 Web Admin URL（优先使用命令行参数）
    base_url = args.url or env_vars.get('WEB_ADMIN_URL', 'http://localhost:8080')
    print(f"🌐 Web Admin 地址: {base_url}")
    if args.url:
        print(f"   (使用命令行参数 --url)")
    else:
        print(f"   (从 .env 的 WEB_ADMIN_URL 读取)")
    print()
    
    # 检查 Web Admin 是否运行
    print("🔍 检查 Web Admin 服务状态...")
    if not check_web_admin_status(base_url):
        print("❌ Web Admin 服务未运行！")
        print(f"   请先启动 Web Admin 服务:")
        print(f"   python3 -m src.xagent.web_admin.server")
        print()
        print("💡 提示: 如果 Web Admin 运行在其他端口，请使用:")
        print("   --url http://localhost:YOUR_PORT")
        print()
        return 1
    print("✅ Web Admin 服务运行正常")
    print()
    
    # 获取管理员密码（优先使用命令行参数）
    admin_password = args.password or env_vars.get('WEB_ADMIN_PASSWORD', 'admin123')
    print(f"🔑 管理员密码: {'***' if admin_password else '未设置（使用默认 admin123）'}")
    if args.password:
        print(f"   (使用命令行参数 --password)")
    else:
        print(f"   (从 .env 的 WEB_ADMIN_PASSWORD 读取)")
    print()
    
    # 获取 Token 有效期（优先使用命令行参数）
    token_expiry_hours = args.expiry or 2
    print(f"⏰ Token 有效期: {token_expiry_hours} 小时")
    if args.expiry:
        print(f"   (使用命令行参数 --expiry)")
    else:
        print(f"   (使用默认值 2 小时)")
    print()
    
    # 如果没有设置密码，提示用户
    if not args.password and 'WEB_ADMIN_PASSWORD' not in env_vars:
        print("⚠️  警告: 未在 .env 中设置 WEB_ADMIN_PASSWORD")
        print("   将使用默认密码 'admin123'")
        print("   建议在 .env 中添加: WEB_ADMIN_PASSWORD=your_secure_password")
        print("   或使用命令行参数: --password your_password")
        print()
    
    # 登录获取 Token
    print("🔐 正在登录 Web Admin...")
    token = login_to_web_admin(base_url, admin_password, token_expiry_hours)
    
    if not token:
        print("❌ 登录失败！请检查:")
        print("   1. 管理员密码是否正确")
        print("   2. Web Admin 服务是否正常运行")
        print()
        return 1
    
    # 验证 Token
    print("🔍 验证 Token 有效性...")
    if not verify_token(base_url, token):
        print("❌ Token 验证失败！")
        print()
        return 1
    
    print("✅ Token 验证成功！")
    print()
    
    # 保存到 .env 文件
    env_vars['WEB_ADMIN_TOKEN'] = token
    save_env_file(env_file, env_vars)
    
    print("💾 已保存 Token 到 .env 文件")
    print()
    print("=" * 60)
    print("✅ 配置完成！")
    print("=" * 60)
    print()
    print("📝 重要提示:")
    print(f"   • Token 有效期为 {token_expiry_hours} 小时")
    print("   • 过期后需要重新运行此脚本")
    print("   • 建议定期更换管理员密码")
    print()
    print("🚀 现在可以重启应用使用 Cron API 功能了:")
    print("   python3 main.py")
    print()
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)