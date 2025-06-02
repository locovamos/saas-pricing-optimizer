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
You are the Manager Agent for a Micro-SaaS Pricing Optimizer. Your task is to guide the user through the process of selecting the best pricing model for their SaaS business. The user will provide:
- A description of their SaaS product (features, audience, market)
- Pricing models they are considering (e.g., freemium, tiered, pay-as-you-go)

Your process:
1. Pass the user’s description and pricing models to the User Behavior Agent.
2. Pass the User Behavior Agent’s output to the Profitability Model Agent.
3. Pass both outputs to the Recommendation Agent for the final recommendation.
4. Return the Recommendation Agent’s output to the user.

Ensure all relevant details are passed between agents. Present the final result clearly, in a helpful tone for a SaaS founder looking for actionable advice.
"""