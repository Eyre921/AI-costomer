# app/prompt_templates.py
from typing import List, Optional

# --- 系统角色定义 ---
PRODUCT_ANALYST_SYSTEM_PROMPT = "You are a senior product analyst. Your task is to understand the provided product information and extract its core features, main advantages, preliminary target customer profile ideas, and suitable foreign trade scenarios. Respond in JSON format with a single key 'product_summary'. The summary should be concise and informative, and the value of 'product_summary' should be a single string if possible, or a structured object if necessary."
MARKET_ANALYSIS_EXPERT_SYSTEM_PROMPT = "You are an AI assistant that generates JSON data representing customer profiles for foreign trade scenarios based on product information. Output ONLY the JSON array of profiles."
CUSTOMER_ROLEPLAYER_SYSTEM_PROMPT = "You are an AI assistant that generates JSON data representing a list of questions a specific customer profile would ask. Output ONLY the JSON array of question objects."

# --- 用户提示模板 ---
def get_product_summary_user_prompt(product_document: str) -> str:
    return f"Product Information:\n```\n{product_document}\n```"

def get_profile_generation_user_prompt(
    product_info_or_summary: str,
    num_profiles: int
) -> str:
    return f"""
You are an experienced foreign trade market analysis expert. Based on the following product information:
Product Info/Summary: {product_info_or_summary}

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
Example of a single profile object:
{{
  "name": "Example Buyer (Country)",
  "description": "Detailed description here.",
  "country_region": "Country Name",
  "occupation": "Occupation Type",
  "cognitive_level": "Novice",
  "main_concerns": ["Concern1", "Concern2"],
  "potential_needs": "Specific need description.",
  "cultural_background_summary": "Cultural notes."
}}
"""

def get_question_generation_user_prompt(
    profile_name: str,
    profile_description: str,
    profile_main_concerns: Optional[List[str]],
    product_info_or_summary: str,
    num_questions: int
) -> str:
    concerns_str = ', '.join(profile_main_concerns) if profile_main_concerns else 'not specified'
    return f"""
You are now role-playing as the customer: '{profile_name}'.
Your background is: {profile_description}
Your main concerns are: {concerns_str}.
You are considering purchasing a product with the following summary: '{product_info_or_summary}'.

Please generate {num_questions} distinct questions you would ask sequentially about this product.
The questions should be relevant to your customer profile (concerns, needs, background) and typical for foreign trade interactions (e.g., about price, logistics, technical specs, after-sales service, compliance).
The questions should exhibit a logical flow or continuity.
Respond with a JSON array of question objects, where each object has a "text" key containing the question string.
ONLY output the JSON array.
Example:
[
  {{"text": "First question about product feature X related to my concern?"}},
  {{"text": "Follow-up question about pricing for feature X?"}}
]
"""