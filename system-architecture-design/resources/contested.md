# Where experts disagree

A good review states confidence honestly and flags contested ground rather than asserting one camp as settled. The deep-research run surfaced these live debates; present both sides.

## Microservices vs monolith (and the "distributed monolith" trap)
- The reflexive "decompose into microservices" is contested. **Amazon Prime Video** publicly moved a serverless/microservice monitoring pipeline **back to a monolith** for ~90% cost reduction at scale.
- Takeaway: distribution is a cost, not a virtue. Split along genuine bounded contexts with independent change/deploy needs (DORA tests), not by default. A poorly-split system is a distributed monolith — worse than the monolith it replaced.

## "The wrong abstraction" vs DRY
- Sandi Metz: **"duplication is far cheaper than the wrong abstraction."** Premature DRY — extracting a shared abstraction from superficially-similar code — produces an abstraction that fits no caller and accretes flags.
- Counter-view: real, stable duplication of a single concept (e.g. safety thresholds copied across repos) *is* a defect (see `smells.md` §1, contract-by-copy).
- Reconcile: duplicate **incidental** similarity; publish **essential** shared concepts (a contract/threshold) as one artifact. The test: is it the *same idea* that must change together, or two ideas that merely look alike today?

## Ousterhout's deep modules — not universally accepted
- *A Philosophy of Software Design* has thoughtful critics (e.g. tension with "many small functions" schools, and with some Clean Code advice). The deep-module guidance is strong but is a heuristic, not a law; the verified nuance is "somewhat general-purpose," not maximal generality.

## Fitness functions — practical limits
- Authoring objective fitness functions is genuinely hard; recent critique warns of "reward hacking" (a metric that passes while the property degrades). Use them, but choose what they measure carefully and revisit.

## ROS2 middleware (DDS vs Zenoh vs iceoryx)
- DDS was the documented choice; it is actively contested. Zenoh reduces discovery overhead dramatically; iceoryx offers shared-memory transport. Encode the *substrate-behind-a-seam* pattern, and flag any DDS-specific coupling as future tech-debt rather than betting the architecture on one middleware.

## Unified Namespace — substance vs hype
- The UNS is largely **vendor-driven** (HighByte, HiveMQ, Inductive Automation) and is consensus-in-formation, not a settled standard. A UNS can degrade into a glorified data lake if dumped into without modeling the namespace. Adopt the ISA-95-keyed topic structure deliberately; don't treat "publish everything to MQTT" as architecture.
