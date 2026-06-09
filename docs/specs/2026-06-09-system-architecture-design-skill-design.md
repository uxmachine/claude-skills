# Design Spec — `system-architecture-design` Claude skill

- **Date:** 2026-06-09
- **Status:** Approved design (pre-implementation)
- **Owner:** uko (uxmachine)
- **Repo (target):** `uxmachine/claude-skills` → `~/claude-skills`, symlinked into `~/.claude/skills`
- **Companion doc:** `~/context/ARCHITECTURE_AUDIT_2026-06-09.md` (SMC-specific divergence report; kept OUT of this portable repo)

---

## 1. Problem

SMC's own software stack is, in the user's words, "not long-term, not simple, not KISS." The user wants a reusable Claude skill that, when designing or reviewing a software/platform system, applies the *absolute best practices* for longevity and simplicity — grounded in verified sources, not the model's unverified generalizations.

Secondary asks already resolved out of scope:
- **Troubleshooting, code-simplification, CLAUDE.md organization** are NOT new skills. They are already covered by `superpowers:systematic-debugging`, the built-in `/simplify` + `/code-review`, and `claude-md-management:claude-md-improver` + `/revise-claude-md`. Rebuilding them would violate Rule 3 (don't rebuild; overlapping skills drift).
- **Game design** dropped (no real project; would dilute the trigger).

## 2. Goals / Non-goals

**Goals**
- One focused, portable skill that reviews/diagnoses the architecture of an *existing* software system for simplicity, loose coupling, and longevity.
- Content grounded in primary sources, with source-confidence tagged.
- A small, deterministic tools-layer script (Rule 2 layer 3).
- Carries manufacturing (ISA-95/MES) and robotics-runtime domain knowledge as on-demand resources.

**Non-goals**
- Not a greenfield design skill — defers to `superpowers:brainstorming` for new design.
- Not a mega-skill spanning unrelated domains.
- Not a manufacturing knowledge encyclopedia; domain files are decision-oriented, not exhaustive.
- No bespoke "skill standard / composability contract" meta-framework (rejected as speculative generality).

## 3. Design constraints — the transcript's four rules

From *"How Anthropic Engineers ACTUALLY Prompt Claude Code"* (the design was audited against these):

1. **Prompt skills, not Claude.** A skill encodes a repeatable *task*. → This skill is one task: architecture review. Domain knowledge is a *resource*, not a separate skill, until a domain proves an independent trigger (YAGNI; revisit later).
2. **Skills are more than prompts** — three layers: sharp **description** (trigger), **instructions** (playbook), **tools** (scripts/reference files = the leverage). → A sharp trigger + a small real script + cited reference files. "If you can use code instead of AI, you should."
3. **Composable, not custom.** Small, focused, reusable; don't rebuild. → One skill; defers to / composes with existing skills; no ceremony.
4. **Skills get smarter every session.** → A literal "one-time fix or forever?" update footer in `SKILL.md`.

## 4. Verified research findings the skill encodes

Source-confidence from the deep-research run (28 sources → 25 adversarially verified, 24 confirmed / 1 refuted):

| # | Principle | Source | Confidence |
|---|---|---|---|
| 1 | Essential vs accidental complexity; no silver bullet — attack the problem's complexity, not adopt tools | Brooks, *No Silver Bullet* (1986) | High (primary, verbatim) |
| 2 | Deep modules + information hiding; prefer **"somewhat general-purpose"** (NOT maximal generality — speculative generality is also a smell) | Ousterhout, *A Philosophy of Software Design* | High (primary) |
| 3 | Loose coupling = DORA's five yes/no tests; violation = distributed monolith (small change → cascading edits) | dora.dev / *Accelerate* | High (primary) |
| 4 | Evolvability via fitness functions — **automatable** (not necessarily automated) checks that guard named characteristics | Ford/Parsons/Kua, *Building Evolutionary Architectures* | High (primary) |
| 5 | Standardize on a proven substrate, hide it behind an interchangeable driver seam (rmw/rcl); decouple node granularity from process topology | ROS2 / Macenski et al., *Science Robotics* | High (primary) — encode the **pattern**, not DDS specifically (Zenoh/iceoryx contest it) |
| 6 | Kernel/HAL seam + async/side-load controllers enforce the RT boundary; keep heavy compute off the execution loop | control.ros.org (`ros2_control`) | High (primary) |
| 7 | ISA-95 equipment hierarchy → Unified Namespace topic structure; ISA-95 organizes integrations, not a monolithic MES | HighByte / HiveMQ | High claim, **vendor-sourced** — treat new-age-MES framing as consensus-in-formation |
| 8 | BTs win on modularity/reuse; FSMs on short controlled tasks; blackboard shared-state breaks BT modularity | Iovino/Colledanchise survey | High — **do NOT** encode the refuted O(1)-vs-O(n) scaling claim |
| 9 | L0–L2 runtime should publish to an ISA-95-keyed UNS rather than couple to a specific MES | synthesis (DORA + ISA-95/UNS) | **Medium (inference)** — present as strong default, not proven fact |

**Added canon (NOT independently re-verified in this run; include, tagged):** hexagonal / ports-and-adapters (Cockburn), DDD bounded contexts (Evans), the Fowler refactoring smell catalog (god object, shotgun surgery, leaky abstraction, hidden temporal coupling), KISS/YAGNI failure modes, Sandi Metz "the wrong abstraction (duplication < wrong abstraction)."

## 5. The design

### 5.1 Structure

```
~/claude-skills/
  README.md                       # what this repo is; the Rule-4 "improve every session" habit
  system-architecture-design/
    SKILL.md                      # short: trigger + review procedure, pointing to resources
    resources/
      principles.md               # findings 1-4 + added canon, each cited + confidence-tagged
      smells.md                   # the smell catalog + how to DETECT each (incl. contract-by-copy)
      isa95-mes.md                # honest layer map, UNS, publish-don't-couple (finding 7,9)
      robotics-runtime.md         # HAL seam, plan/execute boundary, RT budget, BT-vs-FSM (5,6,8)
      contested.md                # where experts disagree (Prime Video monolith, wrong-abstraction>DRY, UNS hype, DDS vs Zenoh)
    scripts/
      architecture_scan.py        # SMALL deterministic checks; grows per Rule 4
```

### 5.2 `SKILL.md` — description (Rule 2, layer 1)

> **Use when designing, reviewing, or refactoring the architecture of a software or platform system** — evaluating whether a system is simple, loosely coupled, and built to last; deciding module/service boundaries; or diagnosing why a system has become hard to change. Defers to `superpowers:brainstorming` for greenfield feature design.

Sharp, names the symptom ("hard to change"), and the explicit deferral prevents overlap with brainstorming.

### 5.3 `SKILL.md` — instructions (the review procedure)

A diagnosis playbook for an *existing* system (this is the gap brainstorming does not fill):

1. **Run the scan** (`scripts/architecture_scan.py <path>`) → start from facts (file sizes, import boundaries, duplicated trees), not vibes.
2. **Contract-by-copy detector** (lead finding): hunt for contracts defined by copying instead of publishing — vendored/duplicated trees across repos, hand-mirrored schemas, cross-repo references to `_private` symbols, duplicated constants. This is the highest-signal smell (see `smells.md`).
3. **Essential vs accidental triage** (Brooks): is each piece of complexity from the problem domain, or self-inflicted?
4. **Module-depth check** (Ousterhout): deep vs shallow modules; leaking implementation; flag speculative generality too.
5. **DORA five-test loose-coupling rubric**: can each unit change/test/deploy/release independently without cross-team coordination? Cascading failure on a small change = distributed monolith.
6. **Smell scan** (`smells.md`): god module, shotgun surgery, leaky abstraction, hidden temporal coupling, wrong abstraction, config/deployment drift.
7. **Fitness functions**: for each "stay simple/evolvable" goal, propose an *automatable* check (file-size gate, import-boundary test, contract-conformance test, RT budget).
8. **Pull domain resources** when relevant: `isa95-mes.md` (manufacturing/integration), `robotics-runtime.md` (execution stack).
9. **Output**: prioritized findings with evidence + the cheapest fitness function that would have caught each.

### 5.4 Resources (content outline)

- **`principles.md`** — findings 1–4 + added canon; each with a one-line heuristic, the detection question, and a source + confidence tag.
- **`smells.md`** — the catalog with concrete detection recipes. **Contract-by-copy** is the headline (it is the dominant real-world failure; the SMC audit is the worked example, referenced not embedded).
- **`isa95-mes.md`** — ISA-95 L0–L4 + equipment hierarchy; the pyramid-vs-naming-hierarchy distinction; the honest layer map *as a generic example* (leaf=L0–L1, cell runtime=L2, offline compiler sits above L3, the L3/MES slot is a separate service consuming bundles); UNS/MQTT-Sparkplug topic mapping (adaptable, not rigid 1:1); the **publish-don't-couple** integration default.
- **`robotics-runtime.md`** — substrate-behind-a-driver-seam (pattern, not DDS); composition; `ros2_control` kernel/HAL + RT budget (sum of controller updates < cycle period, else async); planning/execution separation; BT-vs-FSM (task-dependent; blackboard = hidden coupling; **no scaling claim**).
- **`contested.md`** — Prime Video's monolith walk-back; "wrong abstraction" > premature DRY (Metz); UNS-as-data-lake-hype skepticism; DDS vs Zenoh/iceoryx.

### 5.5 Tools layer — `architecture_scan.py` (Rule 2, layer 3)

Deliberately **small**. Three checks, chosen because `smc-skills` already proved them valuable:
1. **File-size / god-file** — flag files over a configurable threshold (~400–500 lines).
2. **Import-boundary** — AST check that designated "core/leaf" packages don't import designated "vendor/heavy" packages (the `test_leaf_purity.py` pattern, generalized; rules via a small config).
3. **Duplicated / vendored tree** — detect a directory that is a near-copy of another path/repo (the cell_ws-vendored-into-Pipeline-runtime smell).

Grows per Rule 4 only when Claude is observed re-running an analysis by hand. No fan-in/out graph, cycles, or CI-detection in v1 (speculative).

### 5.6 Rule-4 loop & invocation flags

- **Footer in `SKILL.md`:** "*After using this skill, ask: one-time fix, or forever? If forever, add the rule/example/edge-case here.*" Plus "Related: `superpowers:brainstorming`, `/simplify`, `superpowers:systematic-debugging`."
- **Invocation flags:** considered. None needed — nothing here is risky (no deploy/send) or agent-only. (`user-invocable: false` / `disable-model-invocation` deliberately unused.)

## 6. Deferred (YAGNI)

- Split `isa95-mes` and/or `robotics-runtime` into their own skills **only when a second independent trigger proves itself** (i.e., you invoke that domain's guidance outside an architecture review, repeatedly).
- Grow `architecture_scan.py` per Rule 4.

## 7. Implementation notes

- `git init` `~/claude-skills`, create `uxmachine/claude-skills` (personal account, NOT the SMC org), commit this spec.
- Symlink `~/claude-skills/system-architecture-design` → `~/.claude/skills/system-architecture-design` (same pattern as `agent-to-agent-sync`).
- Write the SMC audit to `~/context/ARCHITECTURE_AUDIT_2026-06-09.md` (already drafted alongside this spec).
- `revise-docs` at session end: `CLAUDE.md` still calls `Pipeline-runtime` the live Layer B runtime — it is being phased out.

## 8. Risks / open questions

- **Vendor-sourced Pillar 3.** The ISA-95/UNS material leans on vendor blogs (HighByte/HiveMQ). Mitigation: `isa95-mes.md` flags it as consensus-in-formation and cites the community corroboration.
- **Source-confidence honesty.** Added canon (§4) was not re-verified this run. Mitigation: tag it in `principles.md`.
- **The L3/MES boundary** (finding 9) is an inference, not a sourced fact. Mitigation: present as a strong default; the future L3 service is a separate concern.
- **Single-skill bloat.** If the resources + procedure grow, re-evaluate the split (deferred above) before the SKILL.md drifts toward a mega-skill.
