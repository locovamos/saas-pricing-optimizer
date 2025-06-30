from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput, ItemHelpers
import os
from pydantic import BaseModel
from profitability_model_agent import profitability_tool
from recommendation_agent import tool_recommend
from user_behavior_agent import tool_user_behave
from openai.types.responses import ResponseTextDeltaEvent
import asyncio

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
1. Pass the user’s description and pricing models to the User Behavior Agent tool.
2. When you get its output, call ProfitabilityModelAgent with that output.
3. When you get its output, call RecommendationAgent with both previous outputs.
4. Return the RecommendationAgent’s output to the user.

Ensure all relevant details are passed between agents. Present the final result clearly, in a helpful tone for a SaaS founder looking for actionable advice.
"""

tools = [profitability_tool, tool_user_behave, tool_recommend]

manager_agent = Agent(name="Orchestrator", instructions=INSTRUCTION, tools=tools, model=deepseek_model)

example_input = """
I’m building a SaaS platform that offers AI-powered customer support chatbots for small e-commerce businesses. The product includes:
- Customizable chatbot templates
- Integration with major e-commerce platforms (Shopify, WooCommerce)
- Analytics dashboard for conversation insights
- Basic support features for free, advanced analytics and integrations on paid plans

Target customers: small online store owners who need affordable automation.

I’m considering three pricing models:
1. Freemium: free basic features, paid upgrade for advanced analytics and integrations.
2. Tiered: Basic ($29/month), Pro ($79/month), and Enterprise ($199/month) tiers.
3. Pay-as-you-go: $0.05 per chatbot conversation beyond 100 free conversations.

What pricing model should I use?
"""

async def test():
    with trace("Testing multi agents"):
        result = Runner.run_streamed(manager_agent, input=example_input)
        print("=== Run starting ===")
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                print(event.data.delta, end="", flush=True)
            if event.type == "raw_response_event":
                continue
            elif event.type == "agent_updated_stream_event":
                print(f"Agent updated: {event.new_agent.name}")
                continue
            elif event.type == "run_item_stream_event":
                if event.item.type == "tool_call_item":
                    print("\n-- Tool was called")
                elif event.item.type == "tool_call_output_item":
                    print(f"\n-- Tool output: {event.item.output}")
                else:
                    pass

    print("\n=== Run complete ===")

asyncio.run(test())