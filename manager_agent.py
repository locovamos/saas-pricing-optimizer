# manager_runner_loop.py
import os
import asyncio
import uuid
from dotenv import load_dotenv

from agents import Agent, Runner, OpenAIConversationsSession
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel
from openai.types.responses import ResponseTextDeltaEvent

from profitability_model_agent import profitability_tool
from recommendation_agent import tool_recommend
from user_behavior_agent import tool_user_behave

load_dotenv(override=True)

# ---------------------------
# Model / client configuration
# ---------------------------
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

deepseek_client = AsyncOpenAI(base_url=DEEPSEEK_BASE_URL, api_key=deepseek_api_key)
deepseek_model = OpenAIChatCompletionsModel(model="deepseek-chat", openai_client=deepseek_client)

# ---------------------------
# Orchestrator agent
# ---------------------------
INSTRUCTION = """
You are the Manager Agent for a Micro-SaaS Pricing Optimizer. Your task is to guide the user
through selecting the best pricing model for their SaaS business. The user will provide:
 - A description of their product (features, audience, market)
 - Pricing models they're considering

Process:
1. Call the User Behavior Agent with the user's description + pricing models.
2. Call the Profitability Model Agent with the User Behavior output.
3. Call the Recommendation Agent with both previous outputs.
4. Return the Recommendation Agent's output to the user in an actionable, founder-friendly way.
"""

tools = [profitability_tool, tool_user_behave, tool_recommend]
manager_agent = Agent(name="Orchestrator", instructions=INSTRUCTION, tools=tools, model="gpt-4o-mini")
# ---------------------------
# Example prompt
# ---------------------------
EXAMPLE_INPUT = """
I’m building a SaaS platform that offers AI-powered customer support chatbots for small e-commerce businesses.
Features:
- Customizable chatbot templates
- Integrations (Shopify, WooCommerce)
- Analytics dashboard
- Free basic plan; paid advanced analytics/integrations

Target customers: small online store owners.

Pricing models considered:
1. Freemium
2. Tiered (Basic $29, Pro $79, Enterprise $199)
3. Pay-as-you-go ($0.05 per conversation after 100 free)
What pricing model should I use?
"""

# ---------------------------
# Utilities to inspect session
# ---------------------------
async def print_history(session, limit=None):
    items = await session.get_items(limit=limit) if limit else await session.get_items()
    print("\n--- Session history (most recent last) ---")
    for idx, it in enumerate(items, 1):
        role = it.get("role", "<no-role>")
        content = it.get("content", "<no-content>")
        summary = content if len(content) <= 300 else content[:300] + "…"
        print(f"{idx}. {role}: {summary}")
    print("--- end history ---\n")
    return items

# ---------------------------
# Helper to stream a run result (prints deltas and tool events)
# ---------------------------
async def stream_run_and_print(run_result):
    """
    Given a run result returned by Runner.run_streamed(...),
    consume its stream_events and print them.
    """
    async for event in run_result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
            continue

        if event.type == "agent_updated_stream_event":
            print(f"\n\n[Agent updated to: {event.new_agent.name}]")
            continue

        if event.type == "run_item_stream_event":
            item = event.item
            if item.type == "tool_call_item":
                print(f"\n\n-- Tool called: {getattr(item, 'tool_name', '<tool>')}")
            elif item.type == "tool_call_output_item":
                print(f"\n-- Tool output: {item.output}")

# ---------------------------
# Non-streamed runner helper
# ---------------------------
async def run_once_and_print(agent: Agent, user_text: str, session):
    result = await Runner.run(agent, user_text,session=session)
    print("\n=== Non-streamed final output ===\n")
    print(result.final_output)
    print()
    print("\n=== End ===\n")
    return result

# ---------------------------
# Interactive loop (Runner calls always happen inside this loop)
# ---------------------------
async def interactive_loop():
    """
    Main interactive loop. Every time through the loop we invoke Runner (streamed or non-streamed).
    When the user issues /quit we return so the caller can clear the session.
    """
    print("Commands:")
    print("  /example     - run example prompt")
    print("  /stream      - switch to streamed mode")
    print("  /once        - switch to non-streamed mode")
    print("  /history N   - show latest N items (omit N for all)")
    print("  /latest N    - raw latest N items")
    print("  /reset       - clear session")
    print("  /quit        - quit and clear session\n")

    mode_stream = True
    session = OpenAIConversationsSession()

    while True:
        # blocking input on a thread so the event loop stays responsive
        raw = await asyncio.to_thread(input, "You> ")
        if not raw.strip():
            continue

        cmd = raw.strip()

        if cmd.lower() == "/quit":
            print("Quitting — session will be cleared now.")
            return

        if cmd.lower() == "/example":
            user_text = EXAMPLE_INPUT
        elif cmd.lower() == "/stream":
            mode_stream = True
            print("[Switched to streamed mode]")
            continue
        elif cmd.lower() == "/once":
            mode_stream = False
            print("[Switched to non-streamed mode]")
            continue
        elif cmd.lower().startswith("/history"):
            parts = cmd.split()
            limit = None
            if len(parts) > 1 and parts[1].isdigit():
                limit = int(parts[1])
            await print_history(session, limit=limit)
            continue
        elif cmd.lower().startswith("/latest"):
            parts = cmd.split()
            n = 1
            if len(parts) > 1 and parts[1].isdigit():
                n = int(parts[1])
            items = await session.get_items(limit=n)
            print(f"\n--- Latest {n} items raw ---")
            for i, it in enumerate(items, 1):
                print(f"{i}. role={it.get('role')} content={it.get('content')}\n")
            continue
        elif cmd.lower() == "/reset":
            try:
                await session.clear_session()
                print("[Session cleared via session.clear_session()]")
            except Exception:
                new_id = f"session-{uuid.uuid4().hex[:8]}"
                session = OpenAIConversationsSession()
                print(f"[Created new local session object with id {session.session_id}]")
            continue
        else:
            # treat as normal user text input
            user_text = raw

        # --- RUNNER is invoked here inside the loop (always) ---
        if mode_stream:
            print("\n=== Streamed run starting ===\n")
            run_result = Runner.run_streamed(manager_agent, input=user_text, session=session)
            # consume and print streamed events
            await stream_run_and_print(run_result)
            print("\n\n=== Streamed run complete ===\n")
        else:
            await run_once_and_print(manager_agent, user_text, session)

# ---------------------------
# Top-level main: create session and ensure clearing on exit
# ---------------------------
async def main():
    await interactive_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted — exiting. Session clear was attempted.")
