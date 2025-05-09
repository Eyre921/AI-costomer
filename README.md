好的，这是“AI Customer Generator”项目文档的中文翻译：

# AI 客户生成器

**版本：** 1.0.0
**最后更新：** 2025年5月9日

## 概述

AI 客户生成器是一款基于 FastAPI 的 Web 应用程序，它利用大型语言模型 (LLM) 分析产品信息，并生成专为外贸场景定制的多样化、AI驱动的客户画像。对于每个画像，它还会生成此类客户可能提出的潜在 B2B（企业对企业）和 B2C（企业对消费者）问题。此工具旨在帮助企业了解潜在的国际客户群体并预测他们的咨询。

生成的数据，包括产品摘要、客户画像和问题，都会保存在本地以供审查和进一步使用。

## 功能特性

* **产品分析**：从提供的产品信息中总结关键特性、优势和目标客户思路。
* **客户画像生成**：创建多个独特的国际客户画像，包括：
    * 姓名和描述
    * 国家/地区
    * 职业
    * 对产品的认知水平
    * 主要关切点
    * 潜在需求
    * 文化背景摘要
* **B2B 和 B2C 问题生成**：为每个生成的客户画像构建相关的 B2B 和 B2C 问题。
* **Web 界面**：简单的 HTML 界面，用于输入产品信息和查看结果。
* **API 接口**：提供 JSON API 以便程序化访问。
* **数据持久化**：将所有生成的输入和输出保存为 JSON 文件，按会话组织在 `data/` 目录中。
* **可配置的 LLM**：允许通过环境变量配置 LLM API 端点、API 密钥和模型名称。

## 先决条件

* Python 3.12+
* pip (Python 包安装器)
* 能够访问与 OpenAI API 格式兼容的 LLM API（例如，SiliconFlow，或对 `EXTERNAL_API_URL` 进行微调后的 OpenAI 本身）。

## 设置与安装

1.  **克隆仓库（如果适用）**：
    ```bash
    git clone https://github.com/Eyre921/AI-costomer.git
    cd ai-customer-generator
    ```

2.  **创建并激活虚拟环境**：
    ```bash
    python -m venv venv
    # Windows 系统
    venv\Scripts\activate
    # macOS/Linux 系统
    source venv/bin/activate
    ```

3.  **安装依赖**：
    创建一个包含以下内容的 `requirements.txt` 文件：
    ```txt
    fastapi
    uvicorn[standard]
    pydantic
    httpx
    python-dotenv
    jinja2
    ```
    然后安装它们：
    ```bash
    pip install -r requirements.txt
    ```

4.  **设置环境变量**：
    项目根目录中提供了一个名为 `.env.template` 的模板文件。复制并将其重命名为 `.env`：
    ```bash
    cp .env.template .env
    ```
    然后打开 `.env` 文件，并使用您的实际 API 配置更新它：
    ```env
    EXTERNAL_API_URL="https://api.siliconflow.cn/v1/chat/completions"
    EXTERNAL_API_KEY="sk-your_actual_api_key_here" # 请替换为您的真实 API 密钥
    DEFAULT_LLM_MODEL="Qwen/Qwen3-14B"
    ```
    * `EXTERNAL_API_URL`：您的 LLM 提供商的聊天补全端点。
    * `EXTERNAL_API_KEY`：您 LLM 提供商的 API 密钥。
    * `DEFAULT_LLM_MODEL`：您想使用的特定 LLM 模型。

    > ⚠️ 注意：如果未设置 `EXTERNAL_API_KEY`，应用程序将打印警告并改用模拟数据。

## 运行应用程序

1.  **启动 FastAPI 服务器**：
    推荐在项目根目录下：
    ```bash
    python run.py
    ```
    或者在项目根目录（`app/` 所在的目录）下：
    ```bash
    uvicorn app.main:app --reload
    ```
    `--reload` 标志启用了代码更改时的自动重新加载功能，这对于开发非常有用。

2.  **访问应用程序**：
    * **Web 界面**：打开您的网络浏览器并访问 `http://127.0.0.1:8000/`

## API 接口

* **接口**：`POST /v1/generate_ai_customer_data`
* **描述**：接受产品信息和生成参数，然后返回产品摘要、生成的客户画像以及相关的 B2B/B2C 问题。
* **请求体** (JSON)：
    ```json
    {
      "product_document": "关于产品的详细信息...",
      "num_customer_profiles": 3,
      "num_questions_per_profile": 6
    }
    ```
* **响应体** (JSON)：
    ```json
    {
      "product_summary": "AI生成的产品摘要...",
      "customer_profiles": [
        {
          "id": "profile-xxxxxxxx",
          "name": "陈丽拉 (台湾经销商)",
          "description": "台湾的一家中型经销商...",
          "country_region": "台湾",
          "occupation": "经销商",
          "cognitive_level": "中级",
          "main_concerns": ["合规性", "批量定价", "包装"],
          "potential_needs": "需要符合当地法规并可定制的产品。",
          "cultural_background_summary": "重视清晰沟通和建立信任。",
          "b2b_questions": [
            {"id": "q-xxxxxxxx", "text": "请您提供合规认证...吗？"}
          ],
          "b2c_questions": [
            {"id": "q-xxxxxxxx", "text": "这款产品对于最终用户来说安装设置有多容易？"}
          ]
        }
      ]
    }
    ```

## 数据存储

* 所有输入的产品信息和相应生成的 AI 数据都保存为 JSON 文件。
* 存储在项目根目录的 `data/` 文件夹中。
* 每个请求都会创建一个会话文件夹：`<YYYYMMDD>_<session_id>`
    * `input_product_info.json`：初始请求参数和产品文档。
    * `generated_customer_data.json`：生成的摘要和带问题的客户画像。

## 配置

设置在 `app/config.py` 中管理，并使用 `.env` 变量：
* `EXTERNAL_API_URL`
* `EXTERNAL_API_KEY`
* `DEFAULT_LLM_MODEL`
* `PROJECT_NAME`

请确保 `.env` 包含正确的值。您可以从 `.env.template` 开始，并根据需要进行编辑。

## 自定义

* **LLM 提示**：编辑 `app/prompt_templates.py`
* **数据结构**：编辑 `app/pydantic_models.py`
* **LLM 逻辑**：编辑 `app/llm_service.py`
* **前端**：编辑 `templates/ai_customer_generator.html` 和 `static/`

## 故障排除

* **`EXTERNAL_API_KEY 未设置` 警告**：
    * 检查根目录中的 `.env` 文件。
* **JSON 解析错误**：
    * 可能是由于 LLM 输出格式错误所致。
    * 可能原因：
        * LLM 错误或达到速率限制。
        * 输入过长，导致令牌限制溢出。
        * 模型未遵循严格的格式要求。
* **HTTP 错误 (401, 429 等)**：
    * 检查 API 密钥、账户限制和日志。