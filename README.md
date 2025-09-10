# Micro-SaaS Pricing Optimizer 🚀💸

A compact **multi-agent** CLI orchestrator that recommends SaaS pricing by running a linear pipeline:

**User → Orchestrator (Manager) → User Behavior Agent → Profitability Agent → Recommendation Agent → Founder**

---

## Quickstart⚙️

Assumes you have `uv` installed.

```bash
# create virtual environment
uv venv

# activate the environment (platform-specific)
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# sync/install dependencies from pyproject.toml
uv sync

Create a `.env` (don’t commit it):

```env
OPENAI_API_KEY=sk-...
```

## Run the CLI
```
python manager_agent.py
```

---

## CLI (what you can type) 🖥️

```
/example    # run sample prompt
/stream     # streamed token-by-token output
/once       # non-streamed final output
/history N  # show last N items
/reset      # clear session
/quit       # exit
```

---

## Files (short map) 📁

* `manager_agent.py` — CLI + orchestrator
* `user_behavior_agent.py` — models customer response
* `profitability_model_agent.py` — unit economics
* `recommendation_agent.py` — final recommendation
* `pyproject.toml` — dependencies

---


