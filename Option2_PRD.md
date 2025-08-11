# PRD — Option 2 (MVP + Strands Agents)

## 1. Problem Statement
Legacy systems (Struts/JSP/Java, Oracle, CORBA) hide business logic across UI templates, controllers, PL/SQL, and IDL. Option‑1 solves retrieval + citations but lacks **structured multi‑step reasoning** and **first‑class tool governance**. We need a way to *plan* the answer, call the right tools, verify claims, and refuse if evidence is insufficient—still running locally.

## 2. Goals
1) Raise **answer accuracy** via agentic plans and verification.
2) Keep **local‑first**: no cloud dependence, zero license.
3) Make capabilities **modular**: add/replace tools without re‑writing flows.
4) Preserve **traceability**: return citations and a machine‑readable step trace.

## 3. Non‑Goals (MVP‑2)
- Full cloud adoption (Agents for Bedrock/KB) — optional later.
- Autonomous code migration — out of scope.
- Write access to Oracle — never; read‑only guard required.

## 4. Target Users & Jobs‑to‑Be‑Done
- **Architects**: identify rule sources, impact, owners, migration parity gaps.
- **Developers**: navigate from feature → Struts action → JSP → data source.
- **Analysts/QA**: validate that UI fields map to authoritative DB values.

## 5. Capabilities & Requirements
### R1. Orchestration
- An **AnswerAgent** executes a plan: `retrieve → evidence_gate → (optional) oracle_verify → map_ui(flow) → finalize`.
- Plans are declarative and versioned; each step emits telemetry to the response.

### R2. Tools (must‑have)
- `code_search(query: str) → {hits[]}` — wraps Option‑1 retriever; returns text + repo/path/anchors.
- `oracle_query(sql: str) → {columns[], rows[]}` — read‑only; rejects non‑SELECT.
- `graph_lookup(kind, key) → {nodes, edges}` — resolve Struts action ↔ JSP and file nodes from Neo4j.

### R3. Evidence & Guardrails
- Refuse to finalize if `< min_citations` or if required types (code/sql) are missing.
- Allow per‑question **expects** (from Golden set) to inform verification, but never hard‑code answers.

### R4. API & UI
- `/api/run` unchanged (Option‑2 alternate app). Response includes `final_answer`, `citations[]`, `graph`, and `raw_state.steps`.
- Angular UI works as‑is (Ask + Golden Questions), no CORS changes.

### R5. Observability & Eval
- Include a compact `steps[]` trace: tool name, inputs hash, output sizes, ms.
- Golden runner remains compatible; PASS if Exactness ≥ 0.8, Groundedness ≥ 0.9, Citation rules ok.

### R6. Security
- Oracle: DSN from env; queries must parse as SELECT; enforce `ROWNUM`/`FETCH FIRST` caps.
- File access: only indexed working copy paths; no network fetches.

### R7. Performance
- P95 end‑to‑end ≤ 12s on 100k docs (1–2 tool calls typical).
- Concurrency: 4 in‑flight requests per API instance.

### R8. Packaging
- All inside `traceit-api` container; Strands installed from pinned commit.
- `command:` switchable between `api.app:app` and `api.strands_app:app`.

## 6. Architecture
- **Substrate**: OpenSearch (BM25), Neo4j (relations), local FS.
- **Agent runtime**: Strands plan runner (single agent for MVP; multi‑agent later).
- **Tools**: Python functions annotated with `@tool`, registered at startup.
- **Planner**: static plan with optional branching on evidence thresholds.
- **Response Builder**: citation aggregator (code/sql/doc), mini flow graph, answer formatter.

## 7. Key Flows
**Q: “Where does ‘Specified Amount’ come from?”**
1) `code_search("Specified Amount" + UL + summary.action)` → top hits.
2) If JSP + Struts present → `graph_lookup(action|jsp)` to confirm linkage.
3) Produce SQL template; if safe → `oracle_query("SELECT ... FROM agreement_values WHERE value_type='DEATH BENEFIT AMOUNT' FETCH FIRST 1 ROWS ONLY")`.
4) Finalize with citations (JSP, Struts, SQL). Refuse if not enough evidence.

**Q: “Which Items/Expressions enable documentCenter.action?”**
1) `code_search("documentCenter" + Items + Expressions)`
2) Verify presence of SSC_COLI_Accounts/SSC_Client_Accounts_Business_Life_Documents_Menu in hits.
3) Finalize with code citations.

## 8. Data & Indexing
- Same indexers as Option‑1 (Java, JSP/EL, Struts XML, Oracle metadata).
- Future tool: `diff_analyzer` to compare legacy vs target repos (as‑of view).

## 9. Telemetry & Metrics
- Per step: `tool`, `duration_ms`, `input_tokens` (if any), `output_chars`, `hit_count`.
- Reported in `raw_state.steps` for audit and reproducibility.

## 10. Risks & Mitigations
- **Tool sprawl** → registry & naming convention; lint on startup.
- **SQL misuse** → hard guard: reject non‑SELECT; add `MAX_ROWS`.
- **Latency variance** → cache recent `code_search` results; cap `oracle_query` runtime.
- **Staleness** → delta index script; show index timestamp in UI.

## 11. Rollout Plan & Milestones
- **Week 0–1**: Add Strands deps; implement `code_search`, `oracle_query`, `graph_lookup`; switch API to `strands_app`.
- **Week 2**: Tune plan; get 20 Golden Qs PASS with same thresholds; add step telemetry to UI.
- **Week 3**: Optional `diff_analyzer`, OWNER hints (CODEOWNERS), and “as‑of” view.

## 12. Deliverables
- Source: tools, orchestrator, alt API app, tests.
- Docs: this PRD, operator guide (switching runtime), security note on SQL guard.
- Demos: Golden Questions run‑through + 3 narrative questions.
