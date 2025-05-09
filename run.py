# run.py (在项目根目录)
import uvicorn
from app.config import settings # <--- 修改: 直接从 app.config 导入

if __name__ == "__main__":
    print(f"Starting {settings.PROJECT_NAME} server...")
    print(f"  External API URL configured: {settings.EXTERNAL_API_URL}")
    print(f"  Default LLM Model: {settings.DEFAULT_LLM_MODEL}")
    if settings.EXTERNAL_API_KEY:
        print(f"  External API Key: {'********' + settings.EXTERNAL_API_KEY[-4:] if len(settings.EXTERNAL_API_KEY) > 4 else 'Key is very short'}")
    else:
        print("  External API Key: NOT SET (CRITICAL - LLM calls will use mock data or fail)")

    # Uvicorn会查找名为 app 的模块中名为 app 的FastAPI实例
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

    # 生产环境配置
    # reload=False, workers 可以根据CPU核心数设置，例如 2 * CPU核心数 + 1
    # 例如，如果有2核CPU，可以设置 workers=5
    # 如果不确定，可以先不设置 workers，Uvicorn 默认是1个 worker
    # uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False, workers=4) # 示例 workers=4