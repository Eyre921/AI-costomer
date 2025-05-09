# app/pydantic_models.py
import uuid
from pydantic import BaseModel, Field
from typing import List, Optional, Any

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