from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput
import os
from pydantic import BaseModel

load_dotenv(override=True)

google_api_key = os.getenv('GEMINI_API_KEY')

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

google_client = AsyncOpenAI(api_key=google_api_key, base_url=GEMINI_BASE_URL)
google_model = OpenAIChatCompletionsModel(model="gemini-2.0-flash",openai_client=google_client)

INSTRUCTION = """
You are the Recommendation Agent for a Micro-SaaS Pricing Optimizer. The user provides a SaaS product description, customer behavior estimates, and financial projections for different pricing models.

Your task is to:
1. Analyze the information.
2. Recommend the best pricing strategy for the SaaS business.
3. Explain your reasoning based on conversion rates, churn, revenue potential, and other key metrics.
4. If multiple options are viable, compare pros and cons and clearly state your recommendation.

Your output should be clear, concise, and helpful for a SaaS founder.

Example:
---
Based on the data, the **Tiered pricing model** is the recommended option. It maximizes MRR ($18,500), has a healthy LTV ($500), and a quick CAC payback (3 months). The Freemium model, while good for user acquisition, has lower conversion rates and longer payback periods, making it less optimal for sustainable growth.
"""

recommendation_agent = Agent(name="Recommendation Agent", instructions=INSTRUCTION, model=google_model)
tool_recommend = recommendation_agent.as_tool(tool_name="recommendation_agent",tool_description="Synthesizes insights from customer behavior and financial projections to recommend the most effective pricing strategy for the SaaS business.")