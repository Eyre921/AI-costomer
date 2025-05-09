import time
import uuid
import os
import httpx
import json # 确保导入 json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Dict, Union, Optional, Any
from dotenv import load_dotenv # <--- 1. 导入 load_dotenv

# --- 加载 .env 文件中的环境变量 ---
load_dotenv() # <--- 2. 在所有配置读取之前调用

# --- 从环境变量读取配置 ---
# 如果环境变量中没有设置，则使用提供的默认值（对于API密钥，强烈建议必须在.env中设置）
EXTERNAL_API_URL = os.getenv("EXTERNAL_API_URL", "https://api.siliconflow.cn/v1/chat/completions")
EXTERNAL_API_KEY = os.getenv("EXTERNAL_API_KEY") # <--- 3. 直接从环境变量获取，不再硬编码默认密钥
DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "deepseek-ai/DeepSeek-V3")

# --- 检查关键配置是否已设置 ---
if not EXTERNAL_API_KEY:
    print("错误：EXTERNAL_API_KEY 未在 .env 文件或环境变量中设置。程序将无法调用外部LLM API。")
    # 可以选择在这里退出程序，或者让 call_llm 中的模拟数据逻辑接管（如果已配置为那样）
    # raise ValueError("EXTERNAL_API_KEY is not set. Please configure it in your .env file or environment variables.")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Pydantic 模型定义 ---
# (ProductInfoRequest, GeneratedQuestion, CustomerProfile, AiCustomerDataResponse 模型保持不变)
class ProductInfoRequest(BaseModel):
    product_document: str
    num_customer_profiles: int = Field(default=5, ge=1, le=10)
    num_questions_per_profile: int = Field(default=5, ge=3, le=10)

class GeneratedQuestion(BaseModel):
    id: str = Field(default_factory=lambda: f"q-{uuid.uuid4().hex[:8]}")
    text: str

class CustomerProfile(BaseModel):
    id: str = Field(default_factory=lambda: f"profile-{uuid.uuid4().hex[:8]}")
    name: str
    description: str
    country_region: Optional[str] = None
    occupation: Optional[str] = None
    cognitive_level: Optional[str] = None
    main_concerns: Optional[List[str]] = None
    potential_needs: Optional[str] = None
    cultural_background_summary: Optional[str] = None
    questions: List[GeneratedQuestion] = []

class AiCustomerDataResponse(BaseModel):
    product_summary: Optional[str] = None
    customer_profiles: List[CustomerProfile]


# --- 辅助函数：调用LLM ---
# (call_llm 函数保持不变)
async def call_llm(messages: List[Dict[str, str]], model: str = None, temperature: float = 0.7, max_tokens: int = 2048):
    # 如果未传入model，则使用环境变量中的默认模型
    llm_model_to_use = model if model else DEFAULT_LLM_MODEL

    if not EXTERNAL_API_URL or not EXTERNAL_API_KEY:
        print("警告: 外部API URL或密钥未正确配置。将返回模拟数据（如果实现）。")
        if "customer profiles" in messages[-1]["content"].lower():
            return """
[{"name": "Mock Profile (LLM Config Missing)","description": "This is mock data because LLM API key is missing.","country_region": "N/A","occupation": "N/A","cognitive_level": "N/A","main_concerns": [],"potential_needs": "N/A","cultural_background_summary": "N/A"}]"""
        elif "questions for the customer profile" in messages[-1]["content"].lower():
            return """[{"text": "Mock question: How to configure the LLM API key?"}]"""
        return json.dumps({"error": "LLM API Key not configured. Mock data cannot be fully generated."})

    headers = {
        "Authorization": f"Bearer {EXTERNAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": llm_model_to_use,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
        "response_format": {"type": "json_object"}
    }
    timeout_settings = httpx.Timeout(20.0, read=120.0)

    async with httpx.AsyncClient(timeout=timeout_settings) as client:
        try:
            response = await client.post(EXTERNAL_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            content_str = response.json()["choices"][0]["message"]["content"]
            return content_str
        except httpx.HTTPStatusError as e:
            error_detail = {"error": f"LLM API HTTP Status Error: {e.response.status_code}"}
            try:
                error_detail.update(e.response.json())
            except:
                error_detail["raw_response"] = e.response.text
            print(error_detail)
            raise HTTPException(status_code=e.response.status_code, detail=error_detail)
        except Exception as e:
            print(f"Error calling LLM: {e}")
            raise HTTPException(status_code=500, detail=f"Error calling LLM: {str(e)}")


@app.post("/v1/generate_ai_customer_data", response_model=AiCustomerDataResponse)
async def generate_ai_customer_data(request: ProductInfoRequest):
    product_document = request.product_document
    num_profiles = request.num_customer_profiles
    num_questions = request.num_questions_per_profile

    summary_messages = [
        {"role": "system",
         "content": "You are a senior product analyst. Your task is to understand the provided product information and extract its core features, main advantages, preliminary target customer profile ideas, and suitable foreign trade scenarios. Respond in JSON format with a single key 'product_summary'. The summary should be concise and informative, and the value of 'product_summary' should be a single string if possible, or a structured object if necessary."},
        {"role": "user", "content": f"Product Information:\n```\n{product_document}\n```"}
    ]
    product_summary_json_str = await call_llm(messages=summary_messages, max_tokens=500)
    product_summary_for_response: Optional[str] = None  # 明确类型

    try:
        product_summary_data = json.loads(product_summary_json_str)
        raw_summary_content = product_summary_data.get("product_summary")

        if raw_summary_content is None:
            product_summary_for_response = "Product summary was not provided by the AI."
        elif isinstance(raw_summary_content, str):
            product_summary_for_response = raw_summary_content
        elif isinstance(raw_summary_content, dict):
            # 如果LLM返回的是字典，将其转换为JSON字符串以便符合Pydantic模型的str类型
            product_summary_for_response = json.dumps(raw_summary_content, ensure_ascii=False, indent=2)
        else:
            product_summary_for_response = f"Product summary has an unexpected format: {type(raw_summary_content).__name__}."

    except json.JSONDecodeError:
        error_msg = f"Failed to parse product summary JSON from LLM. Received: {product_summary_json_str}"
        print(error_msg)
        product_summary_for_response = "Summary JSON from AI was malformed."
    except Exception as e:  # 捕获其他可能的错误
        error_msg = f"An unexpected error occurred while processing product summary: {str(e)}"
        print(error_msg)
        product_summary_for_response = error_msg

    # (后续的画像生成和问题生成逻辑保持不变)
    # ... (profile_generation_prompt, profile_messages, etc.)
    # ... (loop for question_generation_prompt, question_messages, etc.)
    # ...
    # Ensure the rest of the function (profile and question generation) is present here as in your previous version.
    # For brevity, I'm only showing the modified summary part and the final return.

    # ---- [PASTE THE REST OF YOUR profile and question generation logic here] ----
    # Example placeholder for the rest of the logic:
    profile_generation_prompt = f"""
You are an experienced foreign trade market analysis expert. Based on the following product information:
Product Summary: {product_summary_for_response if product_summary_for_response else product_document}

Please generate {num_profiles} distinct potential international customer profiles for this product.
Each profile MUST be a JSON object and include these keys:
- "name": A short, descriptive name (e.g., "Hans Müller (German Novice Importer)", "Sarah Jones (US Experienced Buyer)").
- "description": A more detailed description of the customer profile.
- "country_region": (e.g., "Germany", "USA", "Southeast Asia")
- "occupation": (e.g., "Junior Purchasing Agent", "Senior Procurement Manager", "Small Business Owner")
- "cognitive_level": (e.g., "Novice", "Intermediate", "Expert" regarding the product type)
- "main_concerns": A list of strings for their primary concerns (e.g., ["Price", "Quality", "Delivery Time", "Technical Support", "Compliance"]).
- "potential_needs": A string describing their potential needs or use case for the product.
- "cultural_background_summary": A brief summary of cultural communication style or business practice relevant to their region.

Ensure the profiles are significantly different from each other, covering various types of international buyers relevant to foreign trade.
Respond with a JSON array of these customer profile objects.
ONLY output the JSON array. Do not include any other text before or after the JSON.
"""
    profile_messages = [
        {"role": "system",
         "content": "You are an AI assistant that generates JSON data representing customer profiles for foreign trade scenarios based on product information. Output ONLY the JSON array of profiles."},
        {"role": "user", "content": profile_generation_prompt}
    ]
    generated_profiles_json_str = await call_llm(profile_messages, temperature=0.8, max_tokens=num_profiles * 400)

    try:
        profiles_data_list = json.loads(generated_profiles_json_str)
        if not isinstance(profiles_data_list, list):
            print(f"LLM did not return a list of profiles: {profiles_data_list}")
            raise HTTPException(status_code=500, detail="AI failed to generate profiles in the correct list format.")
    except json.JSONDecodeError as e:
        print(f"Failed to parse profiles JSON: {generated_profiles_json_str}. Error: {e}")
        raise HTTPException(status_code=500, detail="AI failed to generate valid JSON for customer profiles.")

    customer_profiles_list: List[CustomerProfile] = []

    for profile_data in profiles_data_list[:num_profiles]:
        if not isinstance(profile_data, dict):
            print(f"Skipping invalid profile data item: {profile_data}")
            continue

        current_profile = CustomerProfile(
            name=profile_data.get("name", "Unnamed Profile"),
            description=profile_data.get("description", "No description provided."),
            country_region=profile_data.get("country_region"),
            occupation=profile_data.get("occupation"),
            cognitive_level=profile_data.get("cognitive_level"),
            main_concerns=profile_data.get("main_concerns", []),
            potential_needs=profile_data.get("potential_needs"),
            cultural_background_summary=profile_data.get("cultural_background_summary")
        )

        question_generation_prompt = f"""
You are now role-playing as the customer: '{current_profile.name}'.
Your background is: {current_profile.description}
Your main concerns are: {', '.join(current_profile.main_concerns) if current_profile.main_concerns else 'not specified'}.
You are considering purchasing a product with the following summary: '{product_summary_for_response if product_summary_for_response else product_document}'.

Please generate {num_questions} distinct questions you would ask sequentially about this product.
The questions should be relevant to your customer profile (concerns, needs, background) and typical for foreign trade interactions.
The questions should exhibit a logical flow or continuity.
Respond with a JSON array of question objects, where each object has a "text" key containing the question string.
ONLY output the JSON array.
"""
        question_messages = [
            {"role": "system",
             "content": "You are an AI assistant that generates JSON data representing a list of questions a specific customer profile would ask. Output ONLY the JSON array of question objects."},
            {"role": "user", "content": question_generation_prompt}
        ]
        generated_questions_json_str = await call_llm(question_messages, temperature=0.7,
                                                      max_tokens=num_questions * 100)

        try:
            questions_data_list = json.loads(generated_questions_json_str)
            if not isinstance(questions_data_list, list):
                print(
                    f"LLM did not return a list of questions for profile {current_profile.name}: {questions_data_list}")
            else:
                for q_data in questions_data_list[:num_questions]:
                    if isinstance(q_data, dict) and "text" in q_data:
                        current_profile.questions.append(GeneratedQuestion(text=q_data["text"]))
                    else:
                        print(f"Skipping invalid question data for profile {current_profile.name}: {q_data}")
        except json.JSONDecodeError as e:
            print(
                f"Failed to parse questions JSON for profile {current_profile.name}: {generated_questions_json_str}. Error: {e}")

        customer_profiles_list.append(current_profile)
    # ---- [END OF PASTED LOGIC] ----

    return AiCustomerDataResponse(
        product_summary=product_summary_for_response,  # 使用处理过的变量
        customer_profiles=customer_profiles_list
    )

# --- 前端服务 ---
@app.get("/", response_class=HTMLResponse)
async def serve_homepage(request: Request):
    return templates.TemplateResponse("ai_customer_generator.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    print(f"Attempting to start server...")
    print(f"  External API URL configured: {EXTERNAL_API_URL}")
    print(f"  Default LLM Model: {DEFAULT_LLM_MODEL}")
    if EXTERNAL_API_KEY:
        print(f"  External API Key: {'********' + EXTERNAL_API_KEY[-4:] if len(EXTERNAL_API_KEY) > 4 else 'Key is very short'}") # 打印部分密钥以确认
    else:
        print("  External API Key: NOT SET (CRITICAL)")

    uvicorn.run(app, host="0.0.0.0", port=8000)