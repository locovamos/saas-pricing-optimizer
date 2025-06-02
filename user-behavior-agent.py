from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Runner, trace, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput
import os
from pydantic import BaseModel

load_dotenv(override=True)

google_api_key = os.getenv('GEMINI_API_KEY')

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

google_client = AsyncOpenAI(api_key=google_api_key, base_url=GEMINI_BASE_URL)
google_model = OpenAIChatCompletionsModel(model="gemini-2.0-flash",openai_client=google_client)

INSTRUCTION = """
You are the User Behavior Agent for a Micro-SaaS Pricing Optimizer. The user will provide a description of their SaaS product (features, target audience, market) and a list of potential pricing models (e.g., freemium, tiered, pay-as-you-go).

Your task is to simulate realistic customer behavior for each pricing model:
- Predict how users might respond in terms of:
  - Conversion rates (free to paid)
  - Churn rates
  - Willingness to pay (low, medium, high)
  - Upgrade/downgrade likelihood

Output a clear explanation of your estimates for each pricing model, with percentages and reasoning. Be realistic and reference SaaS industry benchmarks where appropriate.

Example output:
---
For the **Freemium model**, expect a conversion rate of ~12%, churn rate of ~5%, and a medium willingness to pay. This model typically attracts many free users but has a low conversion to paid.  
For the **Tiered model**, expect a conversion rate of ~18%, churn rate of ~4%, and a high willingness to pay, as it segments customers effectively.
"""