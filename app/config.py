# app/config.py
import os
from dotenv import load_dotenv

# load_dotenv() 会从当前工作目录或 .env 文件的指定路径加载变量。
# 当通过 run.py 启动时，当前工作目录通常是项目根目录。
load_dotenv()

class Settings:
    EXTERNAL_API_URL: str = os.getenv("EXTERNAL_API_URL", "https://api.siliconflow.cn/v1/chat/completions")
    EXTERNAL_API_KEY: str | None = os.getenv("EXTERNAL_API_KEY")
    DEFAULT_LLM_MODEL: str = os.getenv("DEFAULT_LLM_MODEL", "Qwen/Qwen3-14B")
    PROJECT_NAME: str = "AI Customer Generator"

settings = Settings()

if not settings.EXTERNAL_API_KEY:
    print(f"警告：EXTERNAL_API_KEY 未在 .env 文件或环境变量中设置。程序可能无法正常调用外部LLM API。")