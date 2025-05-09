# app/main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json  # 确保导入
import pathlib  # 用于路径处理
from typing import List  # 确保导入 List

# 使用相对导入来导入同级模块
from .pydantic_models import (  # <--- 修改
    ProductInfoRequest,
    AiCustomerDataResponse,
    CustomerProfile,
    GeneratedQuestion
)
from . import llm_service  # <--- 修改
from .config import settings  # <--- 修改

app = FastAPI(title=settings.PROJECT_NAME)

# 静态文件和模板目录的路径是相对于项目根目录的
# PROJECT_ROOT_DIR 计算方式假定 main.py 在 app/ 目录下
PROJECT_ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent

app.mount("/static", StaticFiles(directory=PROJECT_ROOT_DIR / "static"), name="static")
templates = Jinja2Templates(directory=PROJECT_ROOT_DIR / "templates")


@app.post("/v1/generate_ai_customer_data", response_model=AiCustomerDataResponse)
async def generate_ai_customer_data_endpoint(request_data: ProductInfoRequest):
    product_document = request_data.product_document
    num_profiles_req = request_data.num_customer_profiles
    num_questions_req = request_data.num_questions_per_profile

    product_summary = await llm_service.generate_product_summary(product_document)
    info_for_profiling = product_summary if product_summary and "malformed" not in product_summary.lower() and "error" not in product_summary.lower() else product_document

    raw_profiles_data = await llm_service.generate_customer_profiles_from_llm(
        info_for_profiling,
        num_profiles_req
    )

    customer_profiles_list: List[CustomerProfile] = []
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
            cultural_background_summary=profile_dict.get("cultural_background_summary"),  # 修正：应该是 profile_dict.get
            questions=[]
        )

        info_for_questions = product_summary if product_summary and "malformed" not in product_summary.lower() and "error" not in product_summary.lower() else product_document
        raw_questions_data = await llm_service.generate_questions_for_profile_from_llm(
            profile=current_profile_obj,
            product_info_or_summary=info_for_questions,
            num_questions=num_questions_req
        )

        for q_dict in raw_questions_data[:num_questions_req]:
            if isinstance(q_dict, dict) and "text" in q_dict:
                current_profile_obj.questions.append(GeneratedQuestion(text=q_dict["text"]))
        customer_profiles_list.append(current_profile_obj)

    return AiCustomerDataResponse(
        product_summary=product_summary,
        customer_profiles=customer_profiles_list
    )


@app.get("/", response_class=HTMLResponse)
async def serve_homepage(request: Request):
    return templates.TemplateResponse("ai_customer_generator.html", {"request": request})