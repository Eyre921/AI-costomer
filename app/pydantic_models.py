# app/pydantic_models.py
import uuid
from pydantic import BaseModel, Field
from typing import List, Optional, Any

class ProductInfoRequest(BaseModel):
    product_document: str
    num_customer_profiles: int = Field(default=3, ge=1, le=10) # 默认生成3个画像
    # 每个画像的总问题数，后端会尝试均分给B2B和B2C
    num_questions_per_profile: int = Field(default=6, ge=2, le=10) # 总问题数，确保是偶数方便均分或稍作调整

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
    b2b_questions: List[GeneratedQuestion] = [] # 面向B端的问题
    b2c_questions: List[GeneratedQuestion] = [] # 面向C端的问题

class AiCustomerDataResponse(BaseModel):
    product_summary: Optional[str] = None
    customer_profiles: List[CustomerProfile]