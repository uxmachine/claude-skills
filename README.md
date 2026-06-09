# claude-skills

Personal Claude Code skills (uxmachine). Each top-level directory is one skill, symlinked into `~/.claude/skills/`.

## Skills

- **`system-architecture-design`** — review/diagnose the architecture of an existing software or platform system for simplicity, loose coupling, and longevity. Grounded in verified sources (Brooks, Ousterhout, DORA, evolutionary architecture, ROS2/`ros2_control`, ISA-95/UNS). Carries manufacturing (ISA-95/MES) and robotics-runtime domain knowledge as on-demand resources, and ships a small deterministic `architecture_scan.py` (file-size / import-boundary / duplicated-tree checks) with its own test.

## Install (symlink a skill into Claude Code)

```sh
ln -s "$PWD/system-architecture-design" ~/.claude/skills/system-architecture-design
```

## Run the scan tool's test

```sh
python3 -m pytest system-architecture-design/tests -q
```
(No third-party dependencies — standard library only.)

## House rules (how these skills stay good)

These follow the four rules from *"How Anthropic Engineers ACTUALLY Prompt Claude Code"*:

1. **Skills, not prompts** — repeatable tasks live here as skills, not as one-off chat prompts.
2. **More than prompts** — invest in the tools layer (scripts + reference files), not just the instructions.
3. **Composable, not custom** — small focused skills that defer to each other; never one mega-skill. Don't rebuild what `superpowers`/built-ins already do (`brainstorming`, `systematic-debugging`, `/simplify`, `claude-md-improver`).
4. **Smarter every session** — after using a skill, ask *"one-time fix, or forever?"* If forever, write the rule/example/edge-case into the skill **now**. The compounding loop is the whole point.

## Scope

These are *meta* skills for how I work — deliberately **not** SMC product code, and **not** in the SMC org. Domain knowledge inside a skill stays general/portable; org-specific audits live outside this repo.
