<!-- No personal data: nothing from data/, and test fixtures are invented. -->

**What and why**

**How it was tested** (the failing case before the change, and the checks)

- [ ] `uv run pytest`
- [ ] `uv run ruff check .`
- [ ] `uv run python scripts/check_knowledge.py` (if `knowledge/` changed: also `build_knowledge_index.py`)
- [ ] `docs/safety.md` updated, if a safety rule or flag changed
