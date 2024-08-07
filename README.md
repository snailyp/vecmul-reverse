# 已失效

# vecmul_service

这个项目是一个反向代理服务,用于将Vecmul WebSocket转换为REST API。它允许用户通过HTTP请求与多种AI模型进行交互,包括GPT-4、Claude 3和Gemini等。

## 项目结构

- `vecmul.py`: 包含与Vecmul WebSocket API交互的核心逻辑。
- `vecmul_service.py`: 实现FastAPI服务,处理HTTP请求并与Vecmul WebSocket通信。
- `build.py`: 用于构建可执行文件的PyInstaller脚本。
- `Dockerfile`: 用于创建Docker容器的配置文件。
- `requirements.txt`: 列出项目的Python依赖。

## 功能

- 支持多种AI模型,包括GPT-4、Claude 3系列、Gemini等。
- 提供流式和非流式响应选项。
- 支持上下文。
- 使用FastAPI实现RESTful API。
- 支持Docker部署。

## 安装

1. 克隆仓库:

    ```bash
    git clone https://github.com/snailyp/vecmul-reverse.git
    cd vecmul-reverse
    ```

2. 安装依赖:

    ```bash
    pip install -r requirements.txt
    ```

3. 创建`.env`文件并设置`APP_SECRET`。

## 使用方法

### 本地运行

1. 启动服务:

    ```bash
    python vecmul_service.py
    ```

2. 服务将在 `http://localhost:8002` 上运行。

### Docker部署

1. 构建Docker镜像:

    ```bash
    docker build -t vecmul-reverse .
    ```

2. 运行Docker容器:

    ```bash
    docker run -d --name vecmul-reverse -p 8002:8002 -e APP_SECRET=your_secret vecmul-reverse
    ```

### 模型映射关系

```json
{
    "claude-3-opus": "Claude3-Opus",
    "claude-3-haiku": "Claude3-Haiku",
    "claude-3-sonnet-20240229": "Claude3-Sonnet",
    "claude-3-opus-20240229": "Claude3-Opus",
    "claude-3-haiku-20240307": "Claude3-Haiku",
    "gpt-4o": "GPT-4o",
    "gpt-4o-2024-05-13": "GPT-4o",
    "gemini-1.5-flash-latest": "gemini-1.5-flash",
    "gemini-1.5-pro-latest": "gemini-1.5-pro",
    "claude-3-5-sonnet-20240620": "Claude3.5-Sonnet",
    "gpt-3.5-turbo": "GPT-3.5",
    "gpt-4": "GPT-4",
    "Claude3-Sonnet": "Claude3-Sonnet",
    "Claude3-Opus": "Claude3-Opus",
    "Claude3-Haiku": "Claude3-Haiku",
    "GPT-4o": "GPT-4o",
    "gemini-1.5-flash": "gemini-1.5-flash",
    "gemini-1.5-pro": "gemini-1.5-pro",
    "Claude3.5-Sonnet": "Claude3.5-Sonnet",
    "GPT-3.5": "GPT-3.5",
    "GPT-4": "GPT-4"
}
```

### API使用

发送POST请求到 `/v1/chat/completions` 端点,格式如下:

```json
{
  "model": "gpt-4",
  "messages": [
    {"role": "user", "content": "Hello, how are you?"}
  ],
  "stream": false
}
```

请在请求头中包含 `Authorization: Bearer your_app_secret`。

## 构建可执行文件

运行 `python build.py` 来为当前平台构建可执行文件。

## 注意事项

- 确保在使用前设置正确的 APP_SECRET。
- 本项目仅用于教育和研究目的,请遵守Vecmul的服务条款。
