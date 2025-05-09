# app/main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import pathlib
import datetime  # For timestamped directory and filenames
import uuid  # For unique session ID
from typing import List, Any

# 使用相对导入
from .pydantic_models import (
    ProductInfoRequest,
    AiCustomerDataResponse,
    CustomerProfile,
    GeneratedQuestion
)
from . import llm_service
from .config import settings

app = FastAPI(title=settings.PROJECT_NAME)

PROJECT_ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
DATA_BASE_DIR = PROJECT_ROOT_DIR / "data"  # Base directory for all session data
DATA_BASE_DIR.mkdir(parents=True, exist_ok=True)  # 创建基础 data 目录

app.mount("/static", StaticFiles(directory=PROJECT_ROOT_DIR / "static"), name="static")
templates = Jinja2Templates(directory=PROJECT_ROOT_DIR / "templates")


def save_json_data(data_to_save: Any, filename: str, session_id: str, session_date_str: str):
    """
    Helper function to save data to a JSON file within a session-specific directory.
    The directory will be named <session_date_str>_<session_id>.
    The file will be named <filename> inside this directory.
    """
    session_dir_name = f"{session_date_str}_{session_id}"
    session_path = DATA_BASE_DIR / session_dir_name
    session_path.mkdir(parents=True, exist_ok=True)  # Create session-specific directory

    filepath = session_path / filename  # e.g., data/20230509_abcdef12/input_product_info.json

    try:
        # 如果 data_to_save 是 Pydantic 模型实例，先用 .model_dump_json()
        if hasattr(data_to_save, 'model_dump_json') and callable(data_to_save.model_dump_json):
            json_str = data_to_save.model_dump_json(indent=4, exclude_none=True)  # exclude_none for cleaner JSON
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(json_str)
        elif hasattr(data_to_save, 'dict') and callable(
                data_to_save.dict):  # Fallback for Pydantic v1 or other dict-like
            dict_data = data_to_save.dict(exclude_none=True)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(dict_data, f, ensure_ascii=False, indent=4)
        else:  # 假设已经是字典或列表了
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        print(f"数据已保存到: {filepath}")
    except Exception as e:
        print(f"保存数据到 {filepath} 时出错: {e}")


@app.post("/v1/generate_ai_customer_data", response_model=AiCustomerDataResponse)
async def generate_ai_customer_data_endpoint(request_data: ProductInfoRequest):
    product_document = request_data.product_document
    num_profiles_req = request_data.num_customer_profiles
    num_total_questions_per_profile = request_data.num_questions_per_profile

    # 为本次生成创建一个唯一的会话ID和日期字符串
    session_id = uuid.uuid4().hex[:8]  # Shorter UUID for directory name
    session_date_str = datetime.date.today().strftime("%Y%m%d")  # Current date as YYYYMMDD

    # 1. 保存输入的产品信息
    input_data_to_save = {
        "session_id": session_id,
        "generation_date": session_date_str,
        "product_document": product_document,
        "requested_profiles": num_profiles_req,
        "requested_questions_total_per_profile": num_total_questions_per_profile
    }
    save_json_data(input_data_to_save,
                   filename="input_product_info.json",  # Fixed filename within session dir
                   session_id=session_id,
                   session_date_str=session_date_str)

    # 2. 生成产品摘要
    product_summary = await llm_service.generate_product_summary(product_document)
    info_for_llm = product_summary if product_summary and "malformed" not in product_summary.lower() and "error" not in product_summary.lower() else product_document

    # 3. 生成客户画像 (原始字典列表)
    raw_profiles_data = await llm_service.generate_customer_profiles_from_llm(
        info_for_llm,
        num_profiles_req
    )

    # 4. 为每个画像生成两组问题并构建完整的CustomerProfile对象列表
    customer_profiles_list: List[CustomerProfile] = []

    num_b2b_questions = num_total_questions_per_profile // 2
    num_b2c_questions = num_total_questions_per_profile - num_b2b_questions
    if num_total_questions_per_profile == 1 and num_total_questions_per_profile > 0:  # Ensure at least one question type gets one if total is 1
        num_b2b_questions = 0  # Or your preferred logic for a single question
        num_b2c_questions = 1

    for profile_dict in raw_profiles_data[:num_profiles_req]:
        if not isinstance(profile_dict, dict):
            print(f"Skipping invalid raw profile data: {profile_dict}")
            continue

        current_profile_obj = CustomerProfile(
            name=profile_dict.get("name", "Unnamed Profile"),
            description=profile_dict.get("description", "No description provided."),
            country_region=profile_dict.get("country_region"),
            occupation=profile_dict.get("occupation"),
            cognitive_level=profile_dict.get("cognitive_level"),
            main_concerns=profile_dict.get("main_concerns", []),
            potential_needs=profile_dict.get("potential_needs"),
            cultural_background_summary=profile_dict.get("cultural_background_summary"),
            b2b_questions=[],
            b2c_questions=[]
        )

        if num_b2b_questions > 0:
            raw_b2b_q_data = await llm_service.generate_b2b_questions_for_profile(
                profile=current_profile_obj,
                product_info_or_summary=info_for_llm,
                num_questions=num_b2b_questions
            )
            for q_dict in raw_b2b_q_data[:num_b2b_questions]:
                if isinstance(q_dict, dict) and "text" in q_dict:
                    current_profile_obj.b2b_questions.append(GeneratedQuestion(text=q_dict["text"]))

        if num_b2c_questions > 0:
            raw_b2c_q_data = await llm_service.generate_b2c_questions_for_profile(
                profile=current_profile_obj,
                product_info_or_summary=info_for_llm,
                num_questions=num_b2c_questions
            )
            for q_dict in raw_b2c_q_data[:num_b2c_questions]:
                if isinstance(q_dict, dict) and "text" in q_dict:
                    current_profile_obj.b2c_questions.append(GeneratedQuestion(text=q_dict["text"]))

        customer_profiles_list.append(current_profile_obj)

    response_data_obj = AiCustomerDataResponse(
        product_summary=product_summary,
        customer_profiles=customer_profiles_list
    )

    # 5. 保存生成的画像和问题数据
    output_data_to_save = {
        "session_id": session_id,
        "generation_date": session_date_str,
        "product_summary_generated": response_data_obj.product_summary,
        "customer_profiles_generated": [profile.model_dump(exclude_none=True) for profile in
                                        response_data_obj.customer_profiles]  # Convert Pydantic to dicts
    }
    save_json_data(output_data_to_save,
                   filename="generated_customer_data.json",  # Fixed filename
                   session_id=session_id,
                   session_date_str=session_date_str)

    return response_data_obj


@app.get("/", response_class=HTMLResponse)
async def serve_homepage(request: Request):
    return templates.TemplateResponse("ai_customer_generator.html", {"request": request})

# if __name__ == "__main__": ... (remains the same, usually in run.py now)