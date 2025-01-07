#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   check_balance.py
@Time    :   2025/01/07 23:32:52
@Author  :   lvguanjun
@Desc    :   check_balance.py
"""


import argparse
import locale
import os
import sys

# 设置控制台编码
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

from cursor_register import register_cursor
from tokenManager.oneapi_cursor import Cursor
from tokenManager.oneapi_manager import OneAPIManager


def check_and_register(
    oneapi_url: str,
    oneapi_token: str,
    oneapi_channel_url: str,
    channel_name: str,
    threshold: int = 20,
    register_number: int = 1,
):
    """检查 channel 余额并在需要时注册新账号

    Args:
        oneapi_url: OneAPI 服务器地址
        oneapi_token: OneAPI 访问令牌
        oneapi_channel_url: cursor-api 反向代理服务器地址
        threshold: 余额阈值，低于此值时触发注册
        register_number: 注册账号数量
    """
    oneapi = OneAPIManager(oneapi_url, oneapi_token)

    channel_key = oneapi.get_channel_key_by_name(channel_name)

    if channel_key:
        print(f"Channel {channel_name} found, checking balance...")
        tokens = channel_key.split(",")
        need_register = any(Cursor.get_remaining_quota(token) < threshold for token in tokens)

        if not need_register:
            print(
                f"[Info] Channel {channel_name} remaining quota is above threshold ({threshold}), no need to register"
            )
            return
    else:
        print(f"Channel {channel_name} not found, creating new...")

    # 注册新账号
    attempt, max_attempts = 0, 3
    registered_accounts = []
    while attempt < max_attempts:
        account_infos = register_cursor(register_number, max_workers=1)
        if account_infos:
            registered_accounts.extend(account_infos)
            if len(registered_accounts) >= register_number:
                registered_accounts = registered_accounts[:register_number]
                break
        attempt += 1
        print(f"[Info] Failed to register new accounts, attempt {attempt}")

    if not registered_accounts:
        print("[Error] Failed to register new accounts")
        return

    print(f"[Info] Successfully registered {len(registered_accounts)} new accounts")

    # 更新或创建新的 channel
    response = oneapi.update_or_create_channel(
        channel_name,
        oneapi_channel_url,
        [info["token"] for info in registered_accounts],
        OneAPIManager.cursor_models,
    )

    if response.status_code == 200:
        print(f"[Success] Updated or created channel {channel_name}")
        try:
            body = response.json()
            print("Response message:", body.get("message", ""))
            print("Response success:", body.get("success", ""))
        except Exception as e:
            print("Failed to print response:", str(e), "Response:", response.text)
    else:
        print(f"[Error] Failed to update or create channel {channel_name}: {response.status_code}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check Cursor channel balance and register new accounts if needed")
    parser.add_argument("--oneapi_url", type=str, required=False, help="OneAPI server URL")
    parser.add_argument("--oneapi_token", type=str, required=False, help="OneAPI access token")
    parser.add_argument("--oneapi_channel_url", type=str, required=False, help="Base URL for OneAPI channel")
    parser.add_argument("--threshold", type=int, default=10, help="Balance threshold to trigger registration")
    parser.add_argument("--register_number", type=int, default=2, help="Number of accounts to register")

    args = parser.parse_args()

    # 也支持从环境变量读取配置
    oneapi_url = args.oneapi_url or os.getenv("CURSOR_ONEAPI_URL")
    oneapi_token = args.oneapi_token or os.getenv("CURSOR_ONEAPI_TOKEN")
    oneapi_channel_url = args.oneapi_channel_url or os.getenv("CURSOR_CHANNEL_URL")

    if not all([oneapi_url, oneapi_token, oneapi_channel_url]):
        print("[Error] Missing required parameters. Please provide them via arguments or environment variables.")
        exit(1)

    check_and_register(
        oneapi_url,
        oneapi_token,
        oneapi_channel_url,
        "Cursor2API",
        args.threshold,
        args.register_number,
    )
