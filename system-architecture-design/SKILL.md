---
name: system-architecture-design
description: Use when designing, reviewing, or refactoring the architecture of a software or platform system — judging whether it is simple, loosely coupled, and built to last; choosing module/service boundaries; or diagnosing why a system became hard to change. Covers manufacturing (ISA-95/MES) and robotics-runtime systems. Defers to brainstorming for greenfield feature design.
---

# System Architecture Design & Review

Review and harden the architecture of an **existing** system for simplicity, loose coupling, and longevity. This is diagnosis-and-repair, not greenfield design — for new feature/spec design use `superpowers:brainstorming` (it already covers small units, clear interfaces, deep modules). This skill adds what brainstorming does not: measuring an existing system against verified best practices and finding where it has decayed.

Every principle below is sourced; confidence tags and citations live in `resources/principles.md`. Read a resource file only when its step is in play (progressive disclosure).

## The review procedure

Work top to bottom. Stop early only if a higher step already explains the pain.

1. **Scan for facts first.** Run `scripts/architecture_scan.py <path>` to get file sizes, import-boundary violations, and duplicated/vendored trees. Start the review from data, not impressions.
2. **Contract-by-copy detector** *(highest-signal smell — check first)*. Hunt for contracts defined by **copying instead of publishing**: vendored/duplicated trees across repos, hand-mirrored schemas, cross-repo references to `_private` symbols, duplicated constants. This is the dominant cause of "small change → cascading edits." Details + detection recipes in `resources/smells.md`.
3. **Essential vs accidental complexity** (Brooks). For each complex piece: is it from the problem domain, or self-inflicted (god-files, copy-paste, framework churn)? No tool/framework removes essential complexity.
4. **Module depth** (Ousterhout). Deep (small interface, rich implementation) vs shallow (interface ≈ implementation, pass-through)? Flag leaked implementation — and flag **speculative generality**, which is also a smell ("somewhat general-purpose," not maximal).
5. **Loose coupling — the DORA five tests.** Can each unit be (a) changed at scale, (b) completed, (c) deployed/released, (d) tested on-demand, (e) *without* fine-grained coordination with other teams/layers? Any "no" → distributed-monolith risk.
6. **Smell scan** (`resources/smells.md`): god module, shotgun surgery, leaky abstraction, hidden temporal coupling, wrong abstraction (duplication is cheaper than the wrong abstraction), config/deployment drift.
7. **Make it enforceable — fitness functions.** For every "should stay simple/decoupled" goal, name an *automatable* check (file-size gate, import-boundary test, contract-conformance test, RT budget). Evolvability you cannot measure, you will lose.
8. **Pull domain knowledge when relevant:** `resources/isa95-mes.md` for manufacturing/MES/integration; `resources/robotics-runtime.md` for the robot execution stack.
9. **Output:** findings ranked by impact, each with concrete evidence (file:line) and the cheapest fitness function that would have caught it. Where experts disagree, say so — see `resources/contested.md`.

## Scope guards

- New design from scratch → defer to `superpowers:brainstorming`.
- "Just make this code cleaner" with no architectural question → `/simplify` or `/code-review`.
- A specific bug/failure → `superpowers:systematic-debugging`.

---

### Improving this skill (do this every session you use it)

After using this skill, ask: **one-time fix, or forever?** If a correction, example, or edge case should apply every future time, add it here (or to the relevant `resources/` file) now — don't let the lesson evaporate when the chat closes.

**Related skills:** `superpowers:brainstorming` (greenfield design) · `/simplify`, `/code-review` (code-level cleanup) · `superpowers:systematic-debugging` (specific failures).
