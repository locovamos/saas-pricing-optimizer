from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Runner, trace, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput
import os
from pydantic import BaseModel

load_dotenv(override=True)

deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')

DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

deepseek_client = AsyncOpenAI(base_url=DEEPSEEK_BASE_URL, api_key=deepseek_api_key)
deepseek_model = OpenAIChatCompletionsModel(model="deepseek-chat",openai_client=deepseek_client)

INSTRUCTION = """
You are the Profitability Model Agent for a Micro-SaaS Pricing Optimizer. The user provides a SaaS product description, pricing models to evaluate, and customer behavior data (conversion rates, churn, etc.).

Your task is to estimate the financial metrics for each pricing model:
- Monthly Recurring Revenue (MRR)
- Gross margin %
- Customer Lifetime Value (LTV)
- Payback period on Customer Acquisition Costs (CAC)
- Breakeven point in months

Present the financial projections for each pricing model in a clear, readable format. Explain any key assumptions you make, and highlight which model seems financially strongest.

Example output:
---
For the **Freemium model**:
- Estimated MRR: $12,000
- Gross margin: 78%
- LTV: $350
- CAC payback period: 4 months
- Breakeven in ~6 months

For the **Tiered model**:
- Estimated MRR: $18,500
- Gross margin: 82%
- LTV: $500
- CAC payback period: 3 months
- Breakeven in ~5 months

The Tiered model has stronger financial potential due to higher LTV and faster CAC recovery.
"""

