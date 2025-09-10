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

# run the CLI
python manager_agent.py

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

* Linear, deterministic multi-agent flow — easy to extend but intentionally simple.
* Want me to: add the screenshot into `docs/architecture.png`, produce a single-file `pyproject.toml` snippet tuned to your imports, or create a tiny CI/test example? Pick one and I’ll generate it.
