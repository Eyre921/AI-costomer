# AI Customer Generator

版本：**0.1.0**

**README (Chinese):** [https://github.com/Eyre921/AI-customer/blob/master/README_en.md](https://github.com/Eyre921/AI-customer/blob/master/README_en.md)

**Try it out:** [https://cos.nfeyre.top/](https://cos.nfeyre.top/)

## Overview

The AI Customer Generator is a FastAPI-based web application that leverages a Large Language Model (LLM) to analyze product information and generate diverse, AI-driven customer profiles tailored for foreign trade scenarios. For each profile, it also generates potential B2B (business-to-business) and B2C (business-to-consumer) questions that such a customer might ask. This tool aims to help businesses understand potential international customer segments and anticipate their inquiries.

Generated data, including product summaries, customer profiles, and questions, are saved locally for review and further use.

## Features

* **Product Analysis**: Summarizes key features, advantages, and target customer ideas from provided product information.
* **Customer Profile Generation**: Creates multiple distinct international customer profiles including:

  * Name and description
  * Country/Region
  * Occupation
  * Cognitive level regarding the product
  * Main concerns
  * Potential needs
  * Cultural background summary
* **B2B & B2C Question Generation**: For each generated customer profile, it formulates relevant B2B and B2C questions.
* **Web Interface**: Simple HTML interface to input product information and view results.
* **API Endpoint**: Provides a JSON API for programmatic access.
* **Data Persistence**: Saves all generated inputs and outputs as JSON files, organized by session, in the `data/` directory.
* **Configurable LLM**: Allows configuration of the LLM API endpoint, API key, and model name via environment variables.

## Prerequisites

* Python 3.12+
* pip (Python package installer)
* Access to an LLM API compatible with the OpenAI API format (e.g., SiliconFlow, or OpenAI itself with minor adjustments to `EXTERNAL_API_URL`).

## Setup and Installation

1. **Clone the Repository (if applicable)**:

   ```bash
   git clone https://github.com/Eyre921/AI-costomer.git
   cd ai-customer-generator
   ```

2. **Create and Activate a Virtual Environment**:

   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**:

   Create a `requirements.txt` file with the following content:

   ```txt
   fastapi
   uvicorn[standard]
   pydantic
   httpx
   python-dotenv
   jinja2
   ```

   Then install them:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:

   A template file named `.env.template` is provided in the project root. Copy and rename it to `.env`:

   ```bash
   cp .env.template .env
   ```

   Then open the `.env` file and update it with your actual API configuration:

   ```env
   EXTERNAL_API_URL="https://api.siliconflow.cn/v1/chat/completions"
   EXTERNAL_API_KEY="sk-your_actual_api_key_here"
   DEFAULT_LLM_MODEL="Qwen/Qwen3-14B"
   ```

   * `EXTERNAL_API_URL`: The chat completions endpoint of your LLM provider.

   * `EXTERNAL_API_KEY`: Your API key for the LLM provider.

   * `DEFAULT_LLM_MODEL`: The specific LLM model you want to use.

   > ⚠️ Note: The application will print a warning if the `EXTERNAL_API_KEY` is not set and will use mock data instead.

## Running the Application

1.  **Start the FastAPI Server**:
    Recommended, in the project root directory:
    ```bash
    python run.py
    ```
    Alternatively, in the project root directory (where `app/` is located):
    ```bash
    uvicorn app.main:app --reload
    ```
    The `--reload` flag enables auto-reloading when code changes, which is useful for development.

2. **Access the Application**:

   * **Web Interface**: Open your web browser and go to `http://127.0.0.1:8000/`

## API Endpoint

* **Endpoint**: `POST /v1/generate_ai_customer_data`

* **Description**: Accepts product information and parameters for generation, then returns a product summary, generated customer profiles, and associated B2B/B2C questions.

* **Request Body** (JSON):

  ```json
  {
    "product_document": "Detailed information about the product...",
    "num_customer_profiles": 3,
    "num_questions_per_profile": 6
  }
  ```

* **Response Body** (JSON):

  ```json
  {
    "product_summary": "AI-generated summary of the product...",
    "customer_profiles": [
      {
        "id": "profile-xxxxxxxx",
        "name": "Lila Chen (Taiwan Distributor)",
        "description": "A medium-sized distributor in Taiwan...",
        "country_region": "Taiwan",
        "occupation": "Distributor",
        "cognitive_level": "Intermediate",
        "main_concerns": ["Compliance", "Bulk Pricing", "Packaging"],
        "potential_needs": "Needs products that meet local regulations and can be customized.",
        "cultural_background_summary": "Values clear communication and established trust.",
        "b2b_questions": [
          {"id": "q-xxxxxxxx", "text": "Could you please provide compliance certifications...?"}
        ],
        "b2c_questions": [
          {"id": "q-xxxxxxxx", "text": "How easy is this product for end-users to set up?"}
        ]
      }
    ]
  }
  ```

## Data Storage

* All input product information and the corresponding generated AI data are saved as JSON files.
* Stored in `data/` at the project root.
* Each request creates a session folder: `<YYYYMMDD>_<session_id>`

  * `input_product_info.json`: Initial request parameters and product document.
  * `generated_customer_data.json`: Generated summary and customer profiles with questions.

## Configuration

Settings are managed in `app/config.py` and use `.env` variables:

* `EXTERNAL_API_URL`
* `EXTERNAL_API_KEY`
* `DEFAULT_LLM_MODEL`

Make sure `.env` contains correct values. You can start with `.env.template` and edit as needed.

## Customization

* **LLM Prompts**: Edit `app/prompt_templates.py`
* **Data Structures**: Edit `app/pydantic_models.py`
* **LLM Logic**: Edit `app/llm_service.py`
* **Frontend**: Edit `templates/ai_customer_generator.html` and `static/`

## Troubleshooting

* **`EXTERNAL_API_KEY not set` Warning**:

  * Check `.env` file in root.
* **JSON Parsing Errors**:

  * Likely due to bad output from the LLM.
  * Possible causes:

    * LLM error or rate limit.
    * Input too long, causing token limit overflow.
    * Model doesn’t follow strict formatting.
* **HTTP Errors (401, 429, etc.)**:

  * Check API key, account limits, and logs.


