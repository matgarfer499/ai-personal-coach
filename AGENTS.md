# Agent guide

This file is for coding agents other than Claude Code (Codex, OpenCode, Gemini CLI, Cursor and
others). It is a pointer, not a second copy: the canonical instructions live in the files below,
and nothing here overrides them. Claude Code reads them directly.

## Where the instructions are

1. **Rules for working in this repo:** [`CLAUDE.md`](CLAUDE.md). They apply to every agent: test
   first, the four checks, privacy of `data/`, constants that cite a knowledge rule, the
   knowledge format and the safety rules.
2. **The coach's commands:** one Markdown file per command in `.claude/skills/<name>/SKILL.md`
   (`setup`, `checkin`, `import`, `plan`, `review`, `menu`, `research`). When the client types
   `/plan`, or asks for what a skill's `description` covers, read that file and follow it step
   by step. Do not copy the skills elsewhere; edit them in place.
3. **The numbers:** every number comes from the `coach` package, never from the model:
   `uv run python -m coach <command> ... --json`. The CLI does not depend on the agent.
4. **The evidence:** read `knowledge/index.md` first, then only the sections you need. Grep
   `knowledge/sources.md` by ID; never read it whole.
5. **Safety:** [`docs/safety.md`](docs/safety.md). End advice with its deferral line when a red
   flag fired, and never prescribe below the calorie floors or a deficit after a positive screen.

## What only works in Claude Code

- **`/research`** runs `.claude/workflows/research.js` through Claude Code's Workflow tool (one
  agent searches, an independent one tries to refute each claim). Other agents cannot run that
  step yet; do not improvise a replacement that skips the independent check.
- **Settings:** the `env` block in `.claude/settings.local.json` is read by Claude Code only. With
  another agent, export `COACH_DATA_DIR` and `COACH_OFF_CONTACT` in the shell that starts it.
- **Skill discovery:** `.claude/skills/` is where Claude Code finds the commands. If your agent
  discovers skills in another folder, point it at this one (in your own copy) rather than
  duplicating the files.

## Before you rely on it

The skills were written and tested with Claude. Some protections are instructions rather than
code (asking the screening questions, spotting red flags in conversation, naming the right
professional), so they depend on the model following the skill. `docs/safety.md`, "What protects
what", lists which is which. With another agent, try the red-flag personas in
[`docs/testing-guide.md`](docs/testing-guide.md) before using it for yourself.
