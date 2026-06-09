# Smell catalog — with detection recipes

Each smell: what it is → how to **detect** it (something you can actually grep/measure) → the fix direction. Ordered by real-world signal.

## 1. Contract-by-copy *(the dominant smell — check first)*

A contract (schema, interface, constant set) is defined by **copying** it into the consumer instead of **publishing** one artifact both sides import. Every variant below is a distributed monolith: a small change forces synchronized edits across files/repos.

**Detect:**
- Vendored/duplicated trees: a directory that is a near-copy of another repo's package (run `architecture_scan.py`, "duplicate trees"). Watch for a README phrase like "kept in sync manually."
- Hand-mirrored schemas: comments like "mirrors X", "field-for-field", "matches the validator in <other repo>".
- Cross-repo references to `_private` symbols: a schema/doc that cites another repo's `_underscore` function or constant as its source of truth.
- Duplicated constants: the same tuning/threshold values typed into two+ repos.

**Fix:** publish ONE versioned artifact (a schema package, a hashed interface) that both sides import; guard it with a conformance fitness function. The proven local example: a leaf package that exposes a hashed, language-neutral interface both producer and consumer import, with an AST test enforcing the import boundary.

## 2. God module / god file

One file/class doing many unrelated jobs; the natural home for hidden temporal coupling.

**Detect:** `architecture_scan.py` file-size gate (>~400–500 lines is a flag, not a verdict). Then check: how many distinct responsibilities? How many top-level defs? Is it the file everyone edits (high churn)?
**Fix:** extract cohesive units behind small interfaces (Ousterhout deep modules). Add a file-size fitness gate to stop regrowth.

## 3. Shotgun surgery

One conceptual change forces edits in many files/repos — e.g. renaming an identifier, adding one parameter, changing a registry shape.

**Detect:** grep the conceptual token (an ID format, a field name, a parse block) — if the same logic appears at N sites, it's WET. Ask "if I rename this one thing, how many files change?"
**Fix:** centralize the concept in one module everyone imports; pick one canonical shape and reject the others.

## 4. Leaky abstraction

The interface forces callers to know the implementation (you must call things in a magic order, or pass implementation-shaped params).

**Detect:** does using the module require reading its internals? Does a change to internals break callers? If yes, the boundary is wrong.
**Fix:** deepen the module — move the leaked detail behind the interface.

## 5. Hidden temporal coupling

Correct behavior depends on call order, but nothing enforces it (init must run before use; A before B).

**Detect:** look for required call sequences not encoded in types/lifecycle; comments like "must call X first."
**Fix:** encode the order (builder/lifecycle states, or fold the steps into one deep call). Fail-closed if violated.

## 6. Wrong abstraction

A shared abstraction was extracted from superficially-similar code; now it fits neither caller and grows flags/params per caller.

**Detect:** an abstraction with boolean/mode params that select caller-specific behavior; callers passing "null/none" for half the interface.
**Fix:** inline it back; duplication is cheaper than the wrong abstraction (Metz). Re-extract only when the real shared concept is clear. See `contested.md`.

## 7. Config / deployment drift

The deployed/source-of-truth artifact doesn't match reality: dev-machine absolute paths committed, a safety gate that resolves to `$HOME` and silently skips, stale docs pointing at moved files, half-tracked data dirs.

**Detect:** grep committed artifacts for `/home/`, developer emails, wrong org names, hardcoded hosts. Check whether safety gates **fail-closed** or **warn-and-skip** when a path/dependency is missing.
**Fix:** template tokens rewritten at install; resolve dependencies by import not path; make gates fail-closed; CI grep-gate against forbidden strings.

## 8. Distributed monolith

Services/layers that must be deployed together — the worst of both worlds (network boundaries *and* lockstep coupling). The aggregate result of smells 1, 3, and tight inter-layer coupling.

**Detect:** apply the DORA five tests (`principles.md` §3) across layer boundaries. If a change in layer A routinely forces a synchronized redeploy of B, it's a distributed monolith.
**Fix:** stable published contracts between layers (events/UNS topics, versioned schemas); never bind to another layer's internals.
