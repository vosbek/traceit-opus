# Option 2 — Executive Overview (Strands SDK on top of Local MVP)

## What it is
A local, Podman-run migration assistant that keeps Option‑1’s substrate (OpenSearch + Neo4j + our indexers) but adds the **AWS Strands Agents SDK** for agentic planning, tool orchestration, verification, and cleaner hand‑off to production paths later. No cloud is required; Strands runs inside our API container.

## Why it matters
- **Higher answer quality**: multi‑step plans (retrieve → verify in Oracle → align JSP/Struts → answer with citations).
- **Determinism with guardrails**: explicit tools, read‑only SQL guard, refusal without evidence.
- **Composable**: new tools (diff analyzer, lineage probe, owners) can be snapped in without touching the core.
- **Future‑proof**: same patterns port cleanly to AWS runtimes if the enterprise later wants managed ops.

## What changes vs Option 1
- Adds a Strands **orchestrator agent** and a **tool registry** (code_search, oracle_query, graph_lookup, etc.).
- The API gains an alternate app (`api/strands_app.py`); UI stays the same.
- The Golden Questions flow calls the same `/api/run`, but the agent executes a plan and validates citations before finalizing.

## Business value
Fewer wrong answers, faster onboarding, and a safer path to enterprise rollout—while staying local and license‑free.
