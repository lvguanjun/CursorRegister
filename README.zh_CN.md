<p align="center">
  <span>
   <a href="https://github.com/JiuZ-Chn/CursorRegister/blob/main/README.md">English</a>  | 
   <a href="https://github.com/JiuZ-Chn/CursorRegister/blob/main/README.zh_CN.md">简体中文</a>
  </span>
<p>

# Cursor 注册机

自动注册Cursor账号并保存邮箱、密码和令牌(token)

大陆的网络环境可能对本项目性能有较大影响，如果注册成功率较低，请考虑使用代理或者使用其他网络。此外本项目提供Github Action以供网络条件不便的用户试用。

## 功能

- 注册Cursor账号并保存账号、密码、令牌(token)到本地
- 注册Cursor账号并上传令牌(token)到One-API
- 清理One-API中额度不足的Cursor账号
- 上述功能均支持在Github Action中运行

## 本地运行

### 安装依赖 **(务必使用 `Python >= 3.10`)**

本项目可能无法在浏览器无头(headless)模式下运行，请尽可能使用Windows桌面环境。不保证在无UI界面的系统中的运行状况。

```
pip install -r requirements.txt
```

### 注册账号，并将账号信息保存到csv文件

```
python cursor_register.py --number 3
```
- `number`: 希望注册的账号数量

### 注册账号，并将账号的令牌(Cookie token)导入到[One-API](https://github.com/songquanpeng/one-api)

```
python cursor_register.py --oneapi_url {oneapi_url} --oneapi_token {oneapi_token} --oneapi_channel_url {oneapi_channel_url} --oneapi --number 5
```
- `oneapi_url`: One-API 地址
- `oneapi_token`: One-API 访问令牌(token)，详见 [OneAPI API](https://github.com/songquanpeng/one-api/blob/main/docs/API.md)
- `oneapi_channel_url`: Cursor-API 反代服务地址，需自行搭建Cursor-API反代服务 [cursor-api](https://github.com/lvguanjun/cursor-api)

### 清除[One-API](https://github.com/songquanpeng/one-api)的低额度渠道 

```
python tokenManager/oneapi_cursor_cleaner.py --oneapi_url {oneapi_url} --oneapi_token {oneapi_token}
```
- `oneapi_url`: One-API 地址
- `oneapi_token`: One-API 访问令牌(token)，详见 [OneAPI API](https://github.com/songquanpeng/one-api/blob/main/docs/API.md)

## 在Github Action中运行

GitHub Action适用于不便在本地搭建环境或本地环境不佳的用户以供试用。

### 注册账号，随后从[工作流程构件(GitHub Artifacts)](https://docs.github.com/zh/actions/managing-workflow-runs-and-deployments/managing-workflow-runs/downloading-workflow-artifacts)中下载账号信息

适用于手动导入账户令牌(token)或One-API没有公网ip的用户。账号注册完成后需手动从工作流程构件(GitHub Artifacts)中下载账号信息。

**务必在下载完成后删除网页中的工作流程构件(GitHub Artifacts)以避免数据泄漏**

请运行 **`Cursor Register`** 并使用下列参数
- `number`: 希望注册的账号数量
- `max_workers`: 线程池的并行度. 推荐在Github Action中使用 `max_workers=1`
- `Ingest account tokens to OneAPI`: 不选此项，因为在此不必使用One-API服务
- `Upload account infos to artifact`: 选中此项，以保证数据被上传到工作流程构件(GitHub Artifacts)
 
### 注册账号，并将账号令牌(Cookie Token)直接导入到[One-API](https://github.com/songquanpeng/one-api)

为了在GitHub Action中使用One-API服务，你需要在你的仓库中添加如下机密(secrets)，请参考 [Github 安全指南 - 为存储库创建机密](https://docs.github.com/zh/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository)

- `CURSOR_ONEAPI_URL`: 对应参数 `oneapi_url`
- `CURSOR_ONEAPI_TOKEN`: 对应参数 `oneapi_token`
- `CURSOR_CHANNEL_URL`: 对应参数 `oneapi_channel_url`

请运行 **`Cursor Register`** 并使用下列参数
- `number`: 希望注册的账号数量
- `max_workers`: 线程池的并行度. 推荐在Github Action中使用 `max_workers=1`
- `Ingest account tokens to OneAPI`: 选中此项，以开启One-API服务
- `Upload account infos to artifact`: 如果选中，那么数据也将被上传到工作流程构件(GitHub Artifacts)，如果不选则跳过该步骤。
 
### 清理[One-API](https://github.com/songquanpeng/one-api)中额度不足的Cursor账号 

请运行 **`OneAPI Cursor Cleaner`**。需要保证已添加了下列机密(secrets)。

- `CURSOR_ONEAPI_URL`: 对应参数 `oneapi_url`
- `CURSOR_ONEAPI_TOKEN`: 对应参数 `oneapi_token`

## 计划
- 修复多线程模式下可能存在的某些bugs。（众所周知多线程很容易出问题）
- 一个自动维护One-API中额度的Github Action pipeline

## 致谢
- 感谢[cursor-api](https://github.com/Old-Camel/cursor-api/)中的注册机代码思路
