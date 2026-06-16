# Building a 24/7 Personal Agent — Architecture & Research Report

> Deep-research synthesis, 2026-06-16. Sourced from 7 parallel research tracks
> (frameworks, build-your-own architecture, multi-agent orchestration, durability/ops,
> failure modes, I/O & integrations, security & self-improvement). Every non-obvious
> claim is linked to a source. Confidence is flagged where it matters.

---

## 0. TL;DR — the honest verdict

You asked for a single agent ("him") that does *everything*, *24/7*, autonomously —
reachable on WhatsApp/voice, sees your images, knows your location, plugs into Gmail,
Notion, GitHub, Apple, browses the web, has deep persistent memory, runs many things at
once, resists prompt injection, talks like you, and gets better by itself.

Almost all of that is buildable in 2026. **Two parts of the dream are not, and pretending
otherwise is how these projects die:**

1. **"Fully autonomous, does everything, unsupervised."** The reliability math kills it.
   Per-step success compounds: even 95%/step → **~8% over 50 steps**
   ([compound-error](https://highlandedge.com/resources/insights/compound-error-problem/)).
   METR's frontier-agent data: near-100% success on tasks under ~4 min of human work, but
   **<10% on tasks over 4 hours**, and the "reliable" (80%) horizon is ~5× shorter than the
   headline 50% number — measured in *hours*, not days
   ([METR](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/),
   [limitations](https://metr.org/notes/2026-01-22-time-horizon-limitations/)). Gartner
   expects **>40% of agentic-AI projects cancelled by 2027**
   ([Gartner](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027)).
   → **Reframe to:** an always-*available*, event-driven assistant with **narrow, verified
   skills** and **human checkpoints on anything irreversible**. "24/7" = always listening +
   durable + self-healing, NOT "left alone to act without oversight."

2. **"Has access to everything AND reads untrusted content AND can send/post."** That is
   exactly Simon Willison's **lethal trifecta** — private data + untrusted content + an
   exfiltration channel — and **there is no robust general defense**; OpenAI calls it a
   "frontier security challenge," Anthropic calls it "far from solved"
   ([lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/),
   [Anthropic](https://www.anthropic.com/research/prompt-injection-defenses)). Your agent
   has all three by default. This is the single biggest design constraint and Section 7
   is built around breaking the trifecta architecturally.

**Recommended shape:** a **hybrid** — own your control loop, lean on a managed agent loop
for reasoning/context, put a **durable-execution engine underneath** for the 24/7 backbone,
a **dedicated memory service**, **MCP** for all integrations, and a **messaging gateway**.
Don't build a monolith from scratch; don't surrender to one all-in-one framework either.

---

## 1. Your requirements → how each is met

| You said | Mechanism | Status |
|---|---|---|
| Talk on WhatsApp | WhatsApp Business Cloud API (or Telegram) gateway | ✅ with a caveat (§6) |
| Call him (voice) | OpenAI Realtime API over SIP + Twilio trunk, or STT→LLM→TTS | ✅ |
| Send/receive audio | STT (Deepgram/Whisper/ElevenLabs) → text → Claude | ✅ (Claude has no native audio in) |
| Send/receive pictures | Claude vision (PNG/JPEG/WebP/GIF, ≤10 MB, ≤8000px) | ✅ |
| Have my location always | OwnTracks → your backend (MQTT/HTTP) | ✅ (not iOS Shortcuts) |
| Access Notion/Gmail/GitHub | MCP servers (GitHub MCP is GA; Notion/Gmail official+community) | ✅ |
| Access Apple/iCloud | CalDAV/CardDAV + app-specific password only | ⚠️ partial (§6) |
| Browser | Computer-use / browser-use agent (sandboxed, untrusted!) | ✅ but highest-risk surface |
| Memory + deep research | Memory service (Letta-style tiers) + research subagents | ✅ core of the design |
| Many things at once | Durable workflows + orchestrator-worker subagents | ✅ with single-writer rule |
| Prompt-injection resistance | Break the trifecta: quarantine, scoping, egress allowlist, HITL | ⚠️ mitigate, never "solve" |
| Very consistent | Durable execution + step verification + narrow tools | ✅ |
| Talks like me | Few-shot exemplars + retrieval of your writing (not fine-tune) | ✅ structured text; weaker on informal voice |
| Learns / evolves | Skill library + reflection + memory (frozen base model) | ✅ memory-based, not weight updates |

---

## 2. Build vs. buy — framework landscape

The field splits into **agent frameworks** (give you an agent loop/abstraction) and
**durable-execution engines** (give you crash-proof long-running state). You want one of each.

**Agent frameworks** ([comparison](https://dev.to/cristian_iridon_286794874/langgraph-vs-crewai-vs-autogen-in-2026-pick-the-right-ai-agent-framework-or-skip-frameworks-4m2c)):
- **LangGraph** — graph/state-machine; the production default; built-in checkpointing
  (InMemory/SQLite/Postgres), `interrupt()` for human-in-the-loop, LangSmith tracing.
  Steepest learning curve. ([persistence docs](https://docs.langchain.com/oss/python/langgraph/persistence))
- **CrewAI** — role-based "crews" + event-driven "Flows"; fastest to prototype; `@persist`
  for flow state; weaker delegation tracing; no per-task checkpoint recovery.
  ([Flows](https://docs.crewai.com/en/concepts/flows))
- **Claude Agent SDK** — the same managed agent loop + 20+ tools + auto context **compaction**
  + resumable JSONL **sessions** that power Claude Code; subagents via the Agent tool with
  per-agent tool restrictions. Closest to "an agent engine in a box," Python/TS.
  ([overview](https://code.claude.com/docs/en/agent-sdk/overview)) — **recommended core.**
- **OpenAI Agents SDK** — Agents/Handoffs/Guardrails/Tracing; durability comes from the
  **Temporal** integration (GA Mar 23 2026). ([Temporal×OpenAI](https://temporal.io/blog/announcing-openai-agents-sdk-integration))
- **AutoGen/AG2** — conversational multi-agent; Microsoft has pivoted to the new *Microsoft
  Agent Framework*, community maintains **AG2**. ([AG2](https://github.com/ag2ai/ag2))
- **Letta (ex-MemGPT)** — not an orchestrator; a **memory-centric agent runtime** (see §4).
- **AutoGPT/BabyAGI** — legacy; BabyAGI archived to a "sandbox"
  ([aiwiki](https://aiwiki.ai/wiki/babyagi)). The autonomous-loop era faded *because* of the
  reliability problems in §8. Don't build on these.

**Durable execution engines** — the 24/7 backbone:
- **Temporal** — event-log + deterministic replay; never re-runs completed steps; holds state
  for "even years"; $300M Series D Feb 2026. ([learn](https://learn.temporal.io/tutorials/python/background-check/durable-execution/),
  [determinism](https://jack-vanlightly.com/blog/2025/11/24/demystifying-determinism-in-durable-execution))
- **DBOS** — runs **in-process as a library** (Postgres/SQLite), "zero new infrastructure,"
  has a `DBOSAgent` wrapper. Lowest ops burden for a solo build.
  ([DBOS](https://www.dbos.dev/blog/durable-execution-crashproof-ai-agents))
- **Inngest / Restate / Trigger.dev** — durable steps + cron + webhooks; `step.ai.infer`
  avoids paying for compute while waiting on the LLM. ([Inngest](https://www.inngest.com/blog/durable-execution-key-to-harnessing-ai-agents))

> ⚠️ **"Checkpoints ≠ durable execution."** LangGraph/CrewAI checkpointing resumes from the
> last step *within a runtime*; Temporal-style durability adds exactly-once replay, retries,
> and timers across crashes/deploys — a stronger guarantee
> ([Diagrid](https://www.diagrid.io/blog/checkpoints-are-not-durable-execution-why-langgraph-crewai-google-adk-and-others-fall-short-for-production-agent-workflows),
> partisan source but the technical distinction holds). For a true 24/7 agent, put a durable
> engine under the agent loop.

**Recommendation:** **Claude Agent SDK** for the reasoning loop + context management,
**DBOS or Temporal** underneath for durability, **MCP** for tools, your own thin control
layer (§3). This is the "own your control flow, don't adopt a monolith" path that Anthropic
and the 12-factor authors both advocate.

---

## 3. The engine — control loop & build-your-own principles

Core loop: **assemble context → LLM reasons & picks action → execute → observe → repeat**
until a stop condition ([agent loop](https://blogs.oracle.com/developers/what-is-the-ai-agent-loop-the-core-architecture-behind-autonomous-ai-systems)).
A production **harness** must add governance the bare loop lacks: **max steps, recursion-depth
limits, per-step cost ceilings, timeouts** — or it loops forever and burns money (§5, the $47K
incident).

Anthropic's guidance ([Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)):
- Distinguish **workflows** (predefined code paths) from **agents** (LLM directs itself). Use
  the simplest that works; don't default to a fully autonomous agent.
- Five composable patterns: **prompt chaining, routing, parallelization, orchestrator-workers,
  evaluator-optimizer**.
- Three principles: **keep it simple, prioritize transparency** (show planning steps),
  **invest in the agent-computer interface** (tool docs/testing matter as much as prompts).

**Single-agent patterns** (pick by tolerable failure mode):
- **ReAct** (interleave thought/action/observation) — adaptive, higher token cost, weak on
  long horizons. ([ReAct](https://arxiv.org/abs/2210.03629))
- **Plan-and-Execute** — plan up front, cheaper at >3 steps, brittle if early results
  invalidate the plan (mitigate with replanning).
- **Reflexion** — verbal self-critique stored in episodic memory across trials; learning
  without weight updates. ([Reflexion](https://arxiv.org/abs/2303.11366))

**[12-Factor Agents](https://github.com/humanlayer/12-factor-agents)** (HumanLayer/Dex Horthy)
— the build-your-own bible. The load-bearing factors for you: own your prompts; **own your
context window**; tools are just structured outputs; **contact humans via a tool call**; own
your control flow; **compact errors into context** so the model self-corrects; **small focused
agents** beat monoliths; trigger from anywhere; make the agent a **stateless reducer**
(compute next state from input state → launch/pause/resume becomes trivial, and it composes
perfectly with a durable engine).

---

## 4. Memory — the part you said matters most

This is the spine of a personal agent. The dominant model is **MemGPT/Letta's "LLM-as-OS"**
([Letta](https://docs.letta.com/core-concepts/)):
- **Core memory** — always in context (like RAM): who you are, your preferences, your voice.
- **Recall memory** — searchable conversation history.
- **Archival memory** — external vector store queried via tool calls (like disk).
- The agent **self-edits** its own core memory blocks via tool calls (active, not passive RAG).
- **Sleep-time agents** reflect during idle periods to reorganize memory and derive "learned
  context" ([sleep-time](https://docs.letta.com/guides/agents/architectures/sleeptime/)) —
  perfect for a 24/7 system that has downtime.

Hard constraints from the research:
- **Context rot is architectural, not a bug.** Chroma tested 18 frontier models — *all*
  degrade as input grows, well before the window limit; lost-in-the-middle causes 30%+
  accuracy drops ([context rot](https://www.trychroma.com/research/context-rot)). → You
  cannot "just use a huge context window." Curate aggressively.
- Anthropic's three strategies for window exhaustion: **compaction** (summarize + restart),
  **structured note-taking** (write to external NOTES/todo), **sub-agents** (each with a clean
  window) ([context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).
- Memory grows unbounded vs. context limits → you **must** consolidate/summarize; removing
  reflection in Generative Agents collapsed behavior within ~48 simulated hours.
- **Design tension:** Letta's self-editing memory is adaptive but quality depends on model
  judgment; Mem0-style explicit extraction is more deterministic. No consensus yet.

**Recommendation:** a standalone **Memory Service** (own it, don't bury it in a framework):
tiered store (Postgres + pgvector for archival, structured tables for facts/preferences),
self-edit tools, and a nightly **sleep-time consolidation** job (a natural durable cron).
Treat your personalization corpus as private data — it's an exfiltration prize (§7).

---

## 5. Multi-agent & 24/7 operations

**The multi-agent debate is real — don't skip it:**
- **PRO (Anthropic):** orchestrator-worker (lead plans, spawns 3–5 parallel subagents,
  separate citation pass) beat single-agent by **90.2%** on their research eval — but used
  **~15× more tokens**, and token usage alone explained ~80% of the variance. Wins on
  **breadth-first, read-heavy, parallelizable** work ([Anthropic](https://www.anthropic.com/engineering/built-multi-agent-research-system)).
- **ANTI (Cognition, "Don't Build Multi-Agents"):** parallel writers make **conflicting
  implicit decisions** → fragile output; default to **single-threaded** with shared full
  context ([Cognition](https://cognition.ai/blog/dont-build-multi-agents)).
- **Reconciliation (their own 2026 update):** multi-agent works when agents contribute
  *intelligence* but **writes stay single-threaded** — the **single-writer** rule
  ([update](https://cognition.ai/blog/multi-agents-working)).

→ **For you:** use subagents for **research/reading/parallel lookup** (where they shine), keep
**all writes/actions single-threaded** through one supervisor that holds coherent context.
LangGraph Supervisor or the Claude Agent SDK's subagent tool both implement this.
**MCP connects agents to tools; A2A connects agents to agents** — you mainly need MCP.

**24/7 durability & ops:**
- Durable execution = each step in an **event log**; on crash a worker **replays** history and
  resumes at the next uncompleted step, never re-running completed side effects
  ([Temporal](https://learn.temporal.io/tutorials/python/background-check/durable-execution/)).
- **Triggers:** cron + **event triggers** (new email, GitHub PR, Stripe, Slack) + condition
  filters so the agent acts on signal, not noise
  ([scheduling](https://dev.to/thedailyagent/how-to-schedule-ai-agents-that-run-themselves-1a2f)).
- **Human-in-the-loop as a durable wait:** the workflow pauses (days if needed) on a signal
  without consuming compute — ideal for "approve before sending."
- **Observability:** OpenTelemetry **GenAI semantic conventions** (`gen_ai.*`) are CNCF-backed;
  an agentic extension is still *experimental*
  ([OTel issue #2664](https://github.com/open-telemetry/semantic-conventions/issues/2664)).
  Langfuse (OSS, self-host) or LangSmith (deep LangGraph integration) for traces.
- **⚠️ Observability ≠ governance.** The canonical Nov-2025 incident: four agents ping-ponged
  in an **infinite loop for 11 days → $47,000 bill**; dashboards showed "healthy" the whole
  time. Token-budget *alerts* are not *enforcement* — you need **hard caps that terminate
  before the next API call**, per-session token budgets, and tool-level sanity limits (e.g.,
  a search tool that errors after N calls)
  ([$47K forensics](https://clyro.dev/blog/the-47k-loop-a-complete-forensic-analysis/),
  [alerts≠enforcement](https://dev.to/waxell/the-47000-agent-loop-why-token-budget-alerts-arent-budget-enforcement-389i)).

---

## 6. I/O & integrations — the body

**WhatsApp** — *the dominant constraint:* the **24-hour window**. Inside 24h of your last
message you can send free-form text/media; outside it you may send **only Meta-pre-approved
template messages** (per-message billing since Jul 1 2025)
([24h rule](https://www.enchant.com/whatsapp-business-platform-24-hour-rule),
[pricing](https://chat2desk.com/en/blog/articles/whatsapp-business-api-billing-to-change)).
So a WhatsApp agent **cannot freely "text you first" after a quiet day** without a template.
Media: images ≤5 MB (JPEG/PNG), audio ≤16 MB (incl. OGG/OPUS)
([media types](https://docs.aws.amazon.com/social-messaging/latest/userguide/supported-media-types.html)).
**Telegram Bot API** has **no 24h window, no template approval, is free**, supports voice/photo/
**live location** natively, files ≤20 MB download / 50 MB upload (2 GB self-hosted)
([Telegram](https://core.telegram.org/bots/api)). → **Start on Telegram for friction-free
two-way + proactive messaging; add WhatsApp later** for ubiquity, living with templates.

**Voice (calls):** **OpenAI Realtime API** (`gpt-realtime`) is speech-to-speech with native
interruption, over WebRTC/WebSocket/**SIP**; point a real phone number at it via **Twilio**
SIP trunk ([SIP guide](https://platform.openai.com/docs/guides/realtime-sip),
[Twilio](https://www.twilio.com/en-us/blog/developers/twilio-openai-realtime-api-resources)).
~500 ms first-byte, ~800 ms voice-to-voice feels natural; 60-min session cap. Pipeline
alternative (Deepgram/ElevenLabs STT → LLM → ElevenLabs TTS) gives more voice control at
higher latency.

**Vision/audio:** **Claude vision** takes PNG/JPEG/WebP/GIF, ≤10 MB/image, ≤8000×8000px, ≤100
images/req ([vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)).
**Claude has no native live audio input** — transcribe voice notes to text first
([multimodal](https://www.datastudios.org/post/multimodal-input-processing-in-ai-chatbots-chatgpt-claude-gemini-text-image-audio-video)).

**Accounts via MCP:** MCP is the de-facto connector standard — **200+ connectors** (Gmail,
Notion, GitHub, Calendar, Drive) since Jul 2025
([connectors](https://dev.to/arshtechpro/claude-connectors-explained-how-to-give-claude-access-to-your-tools-471k)).
Claude's MCP connector takes **remote HTTPS servers only** (no local STDIO), tool-calls only,
OAuth 2.1 + PKCE ([MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector)).
**GitHub remote MCP is GA** ([GitHub](https://github.blog/changelog/2025-09-04-remote-github-mcp-server-is-now-generally-available/)).
**⚠️ Apple/iCloud is partially closed:** no REST API, no OAuth — **CalDAV/CardDAV + an
app-specific password** only; no sanctioned iMessage/Mail/Notes API
([iCloud](https://www.onecal.io/blog/how-to-integrate-icloud-calendar-api-into-your-app),
[CalDAV](https://www.aurinko.io/blog/caldav-apple-calendar-integration/)). Plan for limited
Apple coverage.

**Live location:** iOS Shortcuts can't reliably stream location in the background; Google Maps
Timeline went **on-device-only in late 2024** (no cloud API). **OwnTracks** is the purpose-built
answer — publishes continuously to your backend via MQTT/HTTP "Move mode"
([OwnTracks](https://owntracks.org/booklet/features/location/)).

---

## 7. Security — break the lethal trifecta (non-negotiable)

Your agent has **private data + untrusted content (emails, web, docs) + send/post ability** =
the **lethal trifecta**, and **no model-level defense is robust**
([trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)). Even Anthropic's
hardened browser agent was still hijacked ~1% of the time *against known attacks* and they call
that "meaningful risk, not solved" ([defenses](https://www.anthropic.com/research/prompt-injection-defenses)).
The model **cannot intrinsically tell** an attacker-planted instruction from a real one once
it's in context.

**Defense-in-depth (shrinks, never closes, the gap):**
1. **Break the trifecta architecturally** — quarantine untrusted-content processing from
   privileged action. **Dual-LLM / CaMeL** pattern: a privileged LLM emits a *plan as code*; a
   custom interpreter tracks **provenance/capabilities** on every value and enforces data-flow
   policy **deterministically, outside the model** ([CaMeL](https://arxiv.org/pdf/2503.18813),
   [explainer](https://simonwillison.net/2025/Apr/11/camel/)). CaMeL defended ~67% of AgentDojo
   attacks at a real utility/token cost — partial, not magic.
2. **Egress allowlist** — so even a successful injection can't exfiltrate (no arbitrary URLs,
   no sending to unknown addresses).
3. **Capability/least-privilege scoping** — per-task tokens, not standing god-mode access.
4. **Human-in-the-loop confirmation on every sensitive/irreversible action** — sending email,
   sharing files, pushing code, spending money, revealing location. This is *required* because
   no automated defense is reliable.
5. The **browser** is your highest-risk surface (untrusted by definition) — sandbox it, and
   never let browser-derived content drive privileged actions without a checkpoint.
6. **Self-improvement is a poisoning surface:** an injection can persist as a learned "skill"
   or memorized instruction ([agent-skills injections](https://arxiv.org/pdf/2510.26328)).
   Treat learned skills/memories with the same scoping as tools.

---

## 8. Personalization, self-improvement & failure modes

**Talk like you:** use **few-shot exemplars + retrieval of your own past writing** (LaMP
"retrieve-then-prompt"); **avoid per-user fine-tuning** (impractical, few samples,
catastrophic forgetting). Empirical limit (EMNLP 2025, 40k+ generations): LLMs match style in
**structured** text (email) but **fail at informal voice** (chat/forums) — "a fundamental gap"
([study](https://arxiv.org/abs/2509.14543)). Expect good email-you, weaker casual-you.

**Get better by itself (without retraining):** **skill library** of reusable, code-described,
retrievable behaviors (Voyager: 3.3×/2.3×/15.3× gains from the library + curriculum +
self-verification, base model **frozen** ([Voyager](https://arxiv.org/abs/2305.16291))) +
**Reflexion** verbal self-critique in episodic memory + **evals-driven** prompt/tool iteration.
**Realistic limit:** "learning" = memory/skill/prompt accumulation around a frozen model. True
online weight updates cause **catastrophic forgetting** and aren't done in most deployments
([forgetting](https://www.cognizant.com/us/en/ai-lab/blog/overcoming-forgetting-in-llm-fine-tuning)).

**Failure modes to design against** (the reason for narrow scope + verification + checkpoints):
error cascading/trajectory collapse over long horizons; state loss & context drift; **silent
tool-call corruption** (model improvises around a broken response); benchmark scores overstate
production reliability — **pass^k decays exponentially** (tau-bench best agent >60% pass@1 →
<25% at pass^8 ([tau-bench](https://arxiv.org/pdf/2406.12045))); MAST catalogs **14 multi-agent
failure modes** including infinite loops/unaware termination
([MAST](https://arxiv.org/abs/2503.13657)). Mitigations: **scope narrowly, verify every step,
tiered green/yellow/red human checkpoints, least-privilege tools, checkpoint+rollback**.

---

## 9. Recommended architecture & phased roadmap

```
                    ┌─────────────────────────────────────────────┐
   Telegram/WhatsApp │  GATEWAY  (messaging, voice/SIP, webhooks)   │
   Voice (SIP)──────▶│  + STT/TTS  + OwnTracks location ingest      │
                    └───────────────┬─────────────────────────────┘
                                    │ events
                    ┌───────────────▼─────────────────────────────┐
                    │  DURABLE ENGINE  (DBOS/Temporal)             │
                    │  cron • event triggers • retries • replay    │
                    │  HARD budget caps • timeouts • HITL waits    │
                    └───────────────┬─────────────────────────────┘
                                    │
                    ┌───────────────▼─────────────────────────────┐
                    │  SUPERVISOR AGENT  (Claude Agent SDK loop)   │
                    │  single-writer • own control flow            │
                    │  context compaction • step verification      │
                    └───┬───────────────┬──────────────┬──────────┘
        read-only       │               │              │  privileged actions
      research subagents │       MEMORY SERVICE         │  (HITL-gated)
       (parallel) ◀──────┘   core/recall/archival       └──▶ MCP tools
                            sleep-time consolidation         (Gmail/Notion/
       BROWSER (sandbox,    ↑ private data — protect          GitHub/Calendar)
       untrusted, gated)    │ + CaMeL-style egress policy ◀── SECURITY LAYER
```

**Phase 1 — Skeleton (talk + remember).** Telegram gateway ↔ Claude Agent SDK loop; Memory
Service (Postgres+pgvector, core/archival); session persistence; hard cost caps from day one.
*You can talk to him and he remembers.*

**Phase 2 — Durable + scheduled.** Wrap the loop in DBOS/Temporal; add cron + event triggers;
sleep-time memory consolidation; OTel tracing. *He survives crashes and acts on schedule.*

**Phase 3 — Integrations (gated).** MCP for Gmail/Notion/GitHub/Calendar; **all writes behind
HITL confirmation**; egress allowlist. CalDAV for Apple. OwnTracks for location. *He reads your
world; you approve before he acts on it.*

**Phase 4 — Senses.** Voice via Realtime+SIP; vision for images; STT for voice notes; WhatsApp
(with templates). *You can call him and send pictures.*

**Phase 5 — Research & multi-agent.** Parallel read-only research subagents (single-writer
preserved); browser in a sandbox, gated. *He runs deep research and many lookups at once.*

**Phase 6 — Learns.** Skill library + reflection + eval harness; per-domain personalization
from your writing. *He gets measurably better at the things you repeat.*

Cross-cutting from Phase 1: hard budget caps, HITL on irreversible actions, least-privilege
tokens, full tracing. These are not a later "hardening" phase — they're load-bearing from the
first commit.

---

## 10. Sourcing caveat

The web-fetch layer was rate-limited (HTTP 403) for much of this research, so many extractions
come from search-result summaries that quote the primary sources rather than full-page reads.
Heavily cross-corroborated facts (lethal trifecta, the $47K loop, METR horizons, Anthropic's
90.2%/15×, Letta memory tiers, WhatsApp 24h rule, MCP connector limits) are high-confidence.
Specific single-source figures (token multipliers, leaderboard scores, funding numbers) should
be re-verified against primaries before you rely on them for decisions. 2026 benchmark numbers
move fast.
