<p align="center">
  <span>
   <a href="https://github.com/JiuZ-Chn/CursorRegister/blob/main/README.md">English</a>  | 
   <a href="https://github.com/JiuZ-Chn/CursorRegister/blob/main/README.zh_CN.md">简体中文</a>
  </span>
<p>

# Cursor Register

Automatically register a Cursor account and save the account name, password, and token.


## Feature

- Register Cursor accounts and save account, password and token to .csv locally.
- Register Cursor accounts upload tokens to One API.
- Clean up Cursor channels with low balance in One API.
- The above features all support to run in Github Action environment.

## Run in local

### Install dependency **(It's required to use `Python >= 3.10`)**

The code does not support to run with headless mode now. Please run the python script in Windows platform with UI. 

```
pip install -r requirements.txt
```

### Register accounts. Save the account info and cookie token into csv.

```
python cursor_register.py --number 3
```

- `number`: The account number you want to register

### Register accounts. Upload the account cookie token into [One-API](https://github.com/songquanpeng/one-api)

```
python cursor_register.py --oneapi_url {oneapi_url} --oneapi_token {oneapi_token} --oneapi_channel_url {oneapi_channel_url} --oneapi --number 5
```

- `oneapi_url`: The web address for your oneapi server.
- `oneapi_token`: The access token for your oneapi website. See more details in [OneAPI API](https://github.com/songquanpeng/one-api/blob/main/docs/API.md)
- `oneapi_channel_url`: The cursor-api reverse proxy server like [cursor-api](https://github.com/lvguanjun/cursor-api)

### 余额检查和自动注册

检查通道的剩余配额，当余额低于阈值时自动注册新账号。

```
python check_balance.py --oneapi_url {oneapi_url} --oneapi_token {oneapi_token} --oneapi_channel_url {oneapi_channel_url} --threshold 20 --register_number 2
```

- `oneapi_url`: OneAPI 服务器地址
- `oneapi_token`: OneAPI 网站的访问令牌
- `oneapi_channel_url`: cursor-api 反向代理服务器地址
- `threshold`: 触发注册的余额阈值（默认：20）
- `register_number`: 要注册的账号数量（默认：2）

你也可以通过环境变量设置这些参数：

- `CURSOR_ONEAPI_URL`
- `CURSOR_ONEAPI_TOKEN`
- `CURSOR_CHANNEL_URL`
### Clean up low balance Cursor channels in [One-API](https://github.com/songquanpeng/one-api)

```
python tokenManager/oneapi_cursor_cleaner.py --oneapi_url {oneapi_url} --oneapi_token {oneapi_token}
```
- `oneapi_url`: The web address for your oneapi server. 
- `oneapi_token`: The access token for your oneapi website. See more details in [OneAPI API](https://github.com/songquanpeng/one-api/blob/main/docs/API.md)

## Run in Github Action

### Register accounts. Download account info and cookie token from Github Artifact.

If you want to use the token directly or your OneAPI does not have a public IP, you can manually download `token.csv` after running the GitHub Action pipeline. **Do not forget to delete the artifact after you download it to avoid data leakage.**

Please run the Github Action pipeline **`Cursor Register`** with the following parameter:
- `number`: The account number you want to register.
- `max_workers`: Parallelism for threading pool. Suggest to use `1` in Github Action environment.
- `Ingest account tokens to OneAPI`: Mark as `☐` to disable One-API service.
- `Upload account infos to artifact`: Mark as `☑` to make Github Action uploead the csv files to artifacts. Then you can download them after workflow succeeds.

### Register accounts. Upload the account cookie token into [One-API](https://github.com/songquanpeng/one-api)

Before ingest the account cookie into ONE API, you need to add the following secret in your repo. If you are new to use secret in Github Action. you can add the secret following [Security Guides](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository) 

- `CURSOR_ONEAPI_URL`: For parameter `oneapi_url`
- `CURSOR_ONEAPI_TOKEN`: For parameter `oneapi_token`
- `CURSOR_CHANNEL_URL`: For parameter `oneapi_channel_url`

Please run the Github Action pipeline **`Cursor Register`** with the following parameter:
- `number`: The account number you want to register.
- `max_workers`: Parallelism for threading pool. Suggest to use `1` in Github Action environment.
- `Ingest account tokens to OneAPI`: Mark as `☑` to enable One-API service.
- `Upload account infos to artifact`: `☑` for uploeading the artifact and `☑` will skip this step

## GitHub Actions 自动化

本项目支持通过 GitHub Actions 实现自动化注册和余额检查。

### 配置步骤

1. Fork 本仓库
2. 在仓库的 Settings -> Secrets and variables -> Actions 中添加以下 secrets:

   - `CURSOR_ONEAPI_URL`: OneAPI 服务器地址
   - `CURSOR_ONEAPI_TOKEN`: OneAPI 访问令牌
   - `CURSOR_CHANNEL_URL`: cursor-api 反向代理服务器地址

3. 在 Variables 中可选配置:
   - `CURSOR_ACCOUNTS_NUMBER`: 要注册的账号数量(默认为 2)
   - `CURSOR_BALANCE_THRESHOLD`: 余额检查阈值(默认为 20)

### 运行方式

- 自动运行：
  - 每 2 小时自动检查一次余额，低于阈值时自动注册新账号
- 手动运行：可以在 Actions 页面手动触发 workflow

### 注意事项

- 使用 Windows 环境运行以确保稳定性
- 默认使用单线程执行，以提高成功率
- 注册信息默认隐藏，确保安全性

## To do

1. 支持将注册得到的信息上传至数据库
2. 支持根据账号密码刷新 Token 值

## Thanks

1. 本项目基于[cursor-api](https://github.com/Old-Camel/cursor-api/)中的代码进行优化，感谢原作者的贡献。
### Clean up low balance Cursor channels in [One-API](https://github.com/songquanpeng/one-api)

Please run the Github Action pipeline **`OneAPI Cursor Cleaner`**. Before runnign the pipeline, you need to add the following secrets in your repo.

- `CURSOR_ONEAPI_URL`: For parameter `oneapi_url`
- `CURSOR_ONEAPI_TOKEN`: For parameter `oneapi_token`

## Todo
- Maybe some bugs when running in multiple threading mode (`max_workers` > 1), but not sure. :(
- A new Github Action pipeline to automatically maintain the minimum balance of Curosr accounts in OneAPI, and automatically register if the balance is too low.

## Thanks
- [cursor-api](https://github.com/Old-Camel/cursor-api/) for Python code in auto register
