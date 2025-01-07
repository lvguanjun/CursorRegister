import requests


class OneAPIManager:

    cursor_models = [
        "gpt-4o-mini",
        "claude-3.5-sonnet",
        "cursor-small",
        "claude-3-opus",
        "cursor-fast",
        "gpt-3.5-turbo",
        "gpt-4-turbo-2024-04-09",
        "gpt-4",
        "gpt-4o-128k",
        "gemini-1.5-flash-500k",
        "claude-3-haiku-200k",
        "claude-3-5-sonnet-200k",
        "claude-3-5-sonnet-20240620",
        "claude-3-5-sonnet-20241022",
        "o1-mini",
        "o1-preview",
        "o1",
        "claude-3.5-haiku",
        "gemini-exp-1206",
        "gemini-2.0-flash-thinking-exp",
        "gemini-2.0-flash-exp",
    ]

    def __init__(self, url, access_token):
        self.base_url = url
        self.access_token = access_token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": self.access_token,
        }

    def get_channel(self, id):
        url = self.base_url + f"/api/channel/{id}"

        response = requests.get(url, headers=self.headers)
        return response

    def get_channels(self, page, pagesize):
        url = self.base_url + f"/api/channel/?p={page}&page_size={pagesize}"

        response = requests.get(url, headers=self.headers)
        return response

    def add_channel(self, name, base_url, keys, models, rate_limit_count=0):
        url = self.base_url + "/api/channel"

        data = {
            "name": name,
            "type": 1,
            "key": "\n".join(keys),
            "openai_organization": "",
            "base_url": base_url,
            "other": "",
            "model_mapping": "",
            "status_code_mapping": "",
            "headers": "",
            "models": ",".join(models),
            "auto_ban": 0,
            "is_image_url_enabled": 0,
            "model_test": models[0],
            "tested_time": 0,
            "priority": 0,
            "weight": 0,
            "groups": ["default"],
            "proxy_url": "",
            "region": "",
            "sk": "",
            "ak": "",
            "project_id": "",
            "client_id": "",
            "client_secret": "",
            "refresh_token": "",
            "gcp_account": "",
            "rate_limit_count": rate_limit_count,
            "gemini_model": "",
            "tags": "Cursor",
            "rate_limited": rate_limit_count > 0,
            "is_tools": False,
            "claude_original_request": False,
            "group": "default",
        }

        response = requests.post(url, json=data, headers=self.headers)
        return response

    def delete_channel(self, id):
        url = self.base_url + f"/api/channel/{id}"

        response = requests.delete(url, headers=self.headers)
        return response

    def search_channel(self, keyword: str) -> dict:
        url = self.base_url + f"/api/channel/search?keyword={keyword}"
        return requests.get(url, headers=self.headers)

    def update_channel_key(self, channel_info: dict, keys: list):
        url = self.base_url + f"/api/channel/"

        channel_info["key"] = ",".join(keys)

        response = requests.put(url, json=channel_info, headers=self.headers)
        return response

    def update_or_create_channel(self, name, base_url, keys, models, rate_limit_count=0):
        # 先搜索是否存在
        search_response = self.search_channel(keyword=name)

        if search_response.status_code == 200:
            channels = [channel for channel in search_response.json().get("data", []) if channel["name"] == name]
            if channels:
                print(f"[OneAPI] Channel {name} already exists, updating...")
                # 找到现有channel，更新它
                channel: dict = channels[0]
                return self.update_channel_key(channel, keys)

        # 没找到，创建新的
        print(f"[OneAPI] Channel {name} not found, creating new...")
        return self.add_channel(name, base_url, keys, models, rate_limit_count)

    def get_channel_key_by_name(self, name: str) -> str:
        search_response = self.search_channel(keyword=name)
        if search_response.status_code == 200:
            for channel in search_response.json().get("data", []):
                if channel["name"] == name:
                    channel_info = channel
                    break
            else:
                return None
        update_response = self.update_channel_key(channel_info, [])
        if update_response.status_code == 200:
            return update_response.json()["data"]["key"]
        return None
