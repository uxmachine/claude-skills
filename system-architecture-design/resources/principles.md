# Principles

The load-bearing principles, each as: **heuristic** → **detection question** → source + confidence. Confidence reflects a deep-research run (28 sources, 25 adversarially verified). Where a verifier added a nuance, it is *load-bearing* — honor it.

## Verified (primary sources)

### 1. Essential vs accidental complexity — *attack the problem, not the toolchain*
- **Heuristic:** Longevity comes from managing the problem's irreducible (essential) complexity and designing for change — never from adopting a new framework/tool. No single technology buys a 10× gain.
- **Detect:** "Is this complexity from the manufacturing/problem domain, or self-inflicted (god-files, copy-paste, framework churn)?"
- Brooks, *No Silver Bullet* (1986). **High** (verbatim-verified). Nuance: the four essential properties are complexity, conformity, changeability, invisibility.

### 2. Deep modules + information hiding
- **Heuristic:** Prefer **deep** modules — a small interface over a rich implementation. Hide implementation; separate what matters from what doesn't.
- **Detect:** "Is this module deep, or shallow (interface ≈ implementation, a pass-through)? Is implementation detail leaking across the boundary?"
- Ousterhout, *A Philosophy of Software Design*. **High** (primary). **Load-bearing nuance:** the target is *somewhat* general-purpose (small interface, current-needs implementation) — NOT maximal generality. Speculative generality / premature abstraction is itself a smell. Avoid both shallow modules *and* over-engineering.

### 3. Loose coupling — the DORA five tests
- **Heuristic:** A loosely coupled unit can be changed, completed, deployed/released, and tested independently, without fine-grained cross-team coordination.
- **Detect (each is yes/no):** Can you (a) make large-scale changes without permission from outside the team? (b) complete work without fine-grained coordination with other teams? (c) deploy/release on your own schedule, independent of dependent services? (d) test on-demand without an integrated environment? (e) deploy in business hours with negligible downtime? Any "no" → coupling risk; "small change → cascading failure across services" = **distributed monolith**.
- dora.dev / *Accelerate* (Forsgren/Humble/Kim). **High** (primary). This is the single best ready-made evolvability rubric.

### 4. Make evolvability measurable — fitness functions
- **Heuristic:** Turn "stays simple/evolvable" into an **automatable** check that guards a named architectural characteristic (tests, metrics, monitoring). Evolvability you cannot measure, you lose.
- **Detect:** "What automated check would fail if this property degraded? If none exists, the property is hope, not architecture."
- Ford/Parsons/Kua, *Building Evolutionary Architectures*. **High** (primary). Nuance: "**automatable**," not necessarily automated — some fitness functions are manual (e.g. regulatory). Watch for "reward hacking" of poorly-chosen functions.

## Added canon — include, but NOT independently re-verified in the research run

Tag these as such when you rely on them; they are well-established but were not adversarially checked here.

- **Hexagonal / ports-and-adapters** (Cockburn): isolate domain logic behind ports; adapters are swappable. *Same idea as the driver/HAL seam in `robotics-runtime.md`.*
- **DDD bounded contexts** (Evans): one model per context; integrate contexts over explicit contracts, not shared internals.
- **The smell catalog** (Fowler, *Refactoring*): god object, shotgun surgery, leaky abstraction, hidden temporal coupling, divergent change. Detection recipes in `smells.md`.
- **The wrong abstraction** (Sandi Metz): "duplication is far cheaper than the wrong abstraction." Prefer inlining/duplication over a forced shared abstraction that fits neither caller. See `contested.md`.
- **KISS / YAGNI — and their failure modes:** KISS misapplied becomes shallow modules and copy-paste; YAGNI misapplied skips the *one* seam that would have made change cheap. Simplicity is fewest moving parts for the essential complexity — not fewest abstractions at any cost.

## The unifying thesis

> Manage essential complexity; hide accidental complexity behind deep, stable interface/abstraction seams; and make loose coupling + evolvability **measurable and enforceable** — not aspirational.
