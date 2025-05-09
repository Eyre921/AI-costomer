# app/prompt_templates.py
from typing import List, Optional

# --- 系统角色定义 ---
PRODUCT_ANALYST_SYSTEM_PROMPT = (
    "You are a senior product analyst. Analyze product info. "
    "Your response MUST be a single valid JSON object. This object MUST contain a key named 'product_summary'. "
    "The value of 'product_summary' should be a concise string covering core features, advantages, target customers, and trade scenarios. "
    "Example: {\"product_summary\": \"Efficient solar panel, great for off-grid use...\"}. "
    "NO other text. If unable to summarize, output an empty JSON object: {}"
)

MARKET_ANALYSIS_EXPERT_SYSTEM_PROMPT = (
    "AI generating customer profiles for foreign trade. "
    "Output MUST be a valid JSON array of profile objects (e.g., [{\"name\": \"N1\", ...}, {\"name\": \"N2\", ...}]). "
    "Each profile object structure is defined in the user prompt. "
    "NO other text. If unable to generate profiles, output an empty JSON array: []"
)

B2B_QUESTION_GENERATION_SYSTEM_PROMPT = (
    "AI generating B2B questions based on customer profile & product info. "
    "Output MUST be a JSON array of question objects: [{\"text\": \"Question 1...\"}, {\"text\": \"Question 2...\"}]. "
    "Questions should be professional, business-focused. "
    "NO other text. If unable to generate questions, output an empty JSON array: []"
)

B2C_QUESTION_GENERATION_SYSTEM_PROMPT = (
    "AI generating B2C questions based on customer profile & product info. "
    "Output MUST be a JSON array of question objects: [{\"text\": \"Question 1...\"}, {\"text\": \"Question 2...\"}]. "
    "Questions should be casual, consumer-focused. "
    "NO other text. If unable to generate questions, output an empty JSON array: []"
)

# --- 用户提示模板 ---
# 用户提示模板函数 (get_product_summary_user_prompt, get_profile_generation_user_prompt,
# get_b2b_question_generation_user_prompt, get_b2c_question_generation_user_prompt)
# 中的固定文本部分相对简洁，主要长度来自于注入的 product_info_or_summary。
# 因此，保持这些函数与上一版本类似即可，关键在于控制注入内容的长度。
# 这里为了完整性，列出与上一版本一致的用户提示模板函数：

def get_product_summary_user_prompt(product_document: str) -> str:
    return f"Product Information:\n```\n{product_document}\n```\nGenerate the product summary as a JSON object according to the system instructions."

def get_profile_generation_user_prompt(
    product_info_or_summary: str,
    num_profiles: int
) -> str:
    return f"""
You are an experienced foreign trade market analysis expert. Based on the following product information:
Product Info/Summary: {product_info_or_summary}

Please generate {num_profiles} distinct potential international customer profiles for this product in English.
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
Your entire response MUST be ONLY a JSON array of these customer profile objects.
Do not include any other text, introductions, or explanations before or after the JSON array.
If no profiles can be generated, output an empty array: []
"""

def get_b2b_question_generation_user_prompt(
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

Please generate {num_questions} distinct B2B (business-to-business) questions in English you would ask sequentially about this product.
These questions should be professional, relevant to your customer profile and typical for foreign trade B2B interactions.
Focus on aspects like: technical specifications for business application, bulk purchasing, payment terms for businesses, shipping and logistics for larger orders, partnership opportunities, long-term support, and compliance for commercial use.
The questions should exhibit a logical flow or continuity.

Respond with a JSON array of question objects. Each object MUST have a "text" key with the question string as its value.
Your entire response MUST be ONLY this JSON array. Do not include any other text, introductions, or explanations.
For example, if generating {num_questions} questions:
[
  {{"text": "First B2B question about specifications..."}},
  {{"text": "Second B2B question about bulk pricing..."}}
  // ... and so on for {num_questions} questions
]
If no relevant questions can be generated, output an empty JSON array: []
"""

def get_b2c_question_generation_user_prompt(
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

Please generate {num_questions} distinct B2C (business-to-consumer) questions you would ask sequentially about this product in English, as if you were having a casual chat with customer service.
These questions should be relevant to your customer profile and reflect everyday consumer inquiries for personal use.
Focus on aspects like: ease of use, personal benefits, appearance/aesthetics, return policy for an individual item, basic troubleshooting, comparison with popular alternatives for personal use, and 'how will this make my life easier/better?'.
The questions should exhibit a logical flow or continuity.

Respond with a JSON array of question objects. Each object MUST have a "text" key with the question string as its value.
Your entire response MUST be ONLY this JSON array. Do not include any other text, introductions, or explanations.
For example, if generating {num_questions} questions:
[
  {{"text": "First B2C question about usability..."}},
  {{"text": "Second B2C question about returns..."}}
  // ... and so on for {num_questions} questions
]
If no relevant questions can be generated, output an empty JSON array: []
"""