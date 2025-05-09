# app/llm_service.py
import httpx
import json
from typing import List, Dict, Optional, Any
from fastapi import HTTPException

from .config import settings             # <--- 修改: 使用相对导入
from . import prompt_templates           # <--- 修改: 使用相对导入
from .pydantic_models import CustomerProfile, GeneratedQuestion # <--- 修改: 使用相对导入


async def call_llm_api(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048
) -> str:
    llm_model_to_use = model if model else settings.DEFAULT_LLM_MODEL

    if not settings.EXTERNAL_API_URL or not settings.EXTERNAL_API_KEY:
        print("警告: 外部API URL或密钥未正确配置。将返回模拟数据。")
        if "customer profiles" in messages[-1]["content"].lower():
            return """[{"name": "Mock Profile (LLM Config Missing)","description": "Mock data due to missing API key.","country_region": "N/A","occupation": "N/A","cognitive_level": "N/A","main_concerns": [],"potential_needs": "N/A","cultural_background_summary": "N/A"}]"""
        elif "questions for the customer profile" in messages[-1]["content"].lower():
            return """[{"text": "Mock question: How to configure LLM API key?"}]"""
        return json.dumps({"error": "LLM API Key not configured."})

    headers = {
        "Authorization": f"Bearer {settings.EXTERNAL_API_KEY}",
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
            print(f"Calling LLM: {settings.EXTERNAL_API_URL} with model {llm_model_to_use}")
            response = await client.post(settings.EXTERNAL_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            response_json = response.json()
            if "choices" not in response_json or not response_json["choices"]:
                raise HTTPException(status_code=500, detail="LLM response missing 'choices' field.")
            if "message" not in response_json["choices"][0] or "content" not in response_json["choices"][0]["message"]:
                raise HTTPException(status_code=500, detail="LLM response missing 'content' in message.")
            content_str = response_json["choices"][0]["message"]["content"]
            return content_str
        except httpx.HTTPStatusError as e:
            error_detail = {"error": f"LLM API HTTP Status Error: {e.response.status_code}"}
            try:
                error_detail_msg = e.response.json()
                if isinstance(error_detail_msg, dict): error_detail.update(error_detail_msg)
                else: error_detail["raw_response_text"] = str(error_detail_msg)
            except json.JSONDecodeError:
                error_detail["raw_response_text"] = e.response.text
            print(f"LLM API HTTPStatusError: {error_detail}")
            raise HTTPException(status_code=e.response.status_code, detail=error_detail)
        except httpx.RequestError as e:
            print(f"LLM API RequestError: {str(e)}")
            raise HTTPException(status_code=503, detail=f"Service Unavailable: {str(e)}")
        except Exception as e:
            print(f"Unexpected error calling LLM: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Internal Server Error while calling LLM: {str(e)}")

async def generate_product_summary(product_document: str) -> str:
    messages = [
        {"role": "system", "content": prompt_templates.PRODUCT_ANALYST_SYSTEM_PROMPT},
        {"role": "user", "content": prompt_templates.get_product_summary_user_prompt(product_document)}
    ]
    summary_json_str = await call_llm_api(messages, max_tokens=500)
    try:
        summary_data = json.loads(summary_json_str)
        raw_summary = summary_data.get("product_summary")
        if raw_summary is None: return "Product summary was not provided by the AI."
        elif isinstance(raw_summary, str): return raw_summary
        elif isinstance(raw_summary, dict): return json.dumps(raw_summary, ensure_ascii=False, indent=2)
        else: return f"Product summary has an unexpected format: {type(raw_summary).__name__}."
    except json.JSONDecodeError:
        return f"Summary JSON from AI was malformed. Received: {summary_json_str[:200]}..."
    except Exception as e:
        return f"Error processing product summary: {str(e)}"

async def generate_customer_profiles_from_llm(
    product_info_or_summary: str, num_profiles: int
) -> List[Dict[str, Any]]:
    user_prompt = prompt_templates.get_profile_generation_user_prompt(product_info_or_summary, num_profiles)
    messages = [
        {"role": "system", "content": prompt_templates.MARKET_ANALYSIS_EXPERT_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    profiles_json_str = await call_llm_api(messages, temperature=0.8, max_tokens=num_profiles * 400)
    try:
        profiles_data = json.loads(profiles_json_str)
        if not isinstance(profiles_data, list):
            print(f"LLM did not return a list of profiles: {profiles_data}")
            raise HTTPException(status_code=500, detail="AI failed to generate profiles in list format.")
        return profiles_data
    except json.JSONDecodeError as e:
        print(f"Failed to parse profiles JSON: {profiles_json_str}. Error: {e}")
        raise HTTPException(status_code=500, detail="AI returned invalid JSON for customer profiles.")

async def generate_questions_for_profile_from_llm(
    profile: CustomerProfile, product_info_or_summary: str, num_questions: int
) -> List[Dict[str, str]]:
    user_prompt = prompt_templates.get_question_generation_user_prompt(
        profile_name=profile.name, profile_description=profile.description,
        profile_main_concerns=profile.main_concerns, product_info_or_summary=product_info_or_summary,
        num_questions=num_questions
    )
    messages = [
        {"role": "system", "content": prompt_templates.CUSTOMER_ROLEPLAYER_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    questions_json_str = await call_llm_api(messages, temperature=0.7, max_tokens=num_questions * 100)
    try:
        questions_data = json.loads(questions_json_str)
        if not isinstance(questions_data, list):
            print(f"LLM did not return a list of questions for profile {profile.name}: {questions_data}")
            return []
        valid_questions = []
        for q_data in questions_data:
            if isinstance(q_data, dict) and "text" in q_data and isinstance(q_data["text"], str):
                valid_questions.append({"text": q_data["text"]})
            else:
                print(f"Skipping invalid question data for profile {profile.name}: {q_data}")
        return valid_questions
    except json.JSONDecodeError as e:
        print(f"Failed to parse questions JSON for profile {profile.name}: {questions_json_str}. Error: {e}")
        return []