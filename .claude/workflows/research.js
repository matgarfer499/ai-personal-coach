export const meta = {
  name: 'research',
  description: 'Search for and verify evidence for /research (at most 4 searchers + 4 verifiers)',
  whenToUse: 'Run by the /research skill (scriptPath) with args {today, groups: [{label, brief, items}]}',
  phases: [
    { title: 'Search', detail: 'one low-effort agent per group: find and open sources' },
    { title: 'Verify', detail: 'one high-effort agent per group: re-open and try to refute' },
  ],
}

// args: {today: 'YYYY-MM-DD', groups: [{label, brief, items: [string]}]}, at most 4 groups.
// Each group is a knowledge file to refresh, a topic, or a batch of dropped claims; `brief` says
// what to look for (for a file: evidence newer than its "Evidence checked on" date).

const RULES = `Rules (from docs/research-methodology.md, "Rules every agent followed"):
- Population: ordinary adults (beginners, returning lifters, recreational gym-goers), not elite
  athletes. If the evidence comes from a narrower group (young trained men, people with obesity),
  say so in "population".
- Source preference: position stands and guidelines, umbrella reviews, meta-analyses and
  systematic reviews first; single trials and narrative reviews only as support. No blogs, news
  or commercial sites.
- Open it or drop it: every claim needs a source you actually opened (abstract or full text) whose
  text supports the claim and every number in it. Never cite from memory. If you cannot confirm
  it, drop it and say why; do not soften it.
- Grades: strong = position stand or guideline and/or several concordant meta-analyses or an
  umbrella review; moderate = one good meta-analysis, several consistent RCTs, or a position stand
  on limited data; emerging = few trials, mostly observational or mechanistic, or meta-analyses
  that disagree.
- Access: PubMed web pages block bots; read abstracts through NCBI E-utilities
  (https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=PMID&rettype=abstract&retmode=text),
  confirm DOIs through the Crossref API (https://api.crossref.org/works/DOI), use PubMed Central
  for open full text. Keep to about one NCBI request per second.
- Do not edit any file. Return data only. No en or em dashes in any text you return.`

const SOURCE = {
  type: 'object',
  properties: {
    citation: { type: 'string', description: 'Authors. Year. Title. Journal volume(issue):pages' },
    type: { type: 'string', description: 'Guideline, Position stand, Umbrella review, Meta-analysis, Systematic review, RCT, Cohort, Narrative review or Other' },
    doi: { type: 'string', description: 'DOI or "none"' },
    pmid: { type: 'string', description: 'PubMed ID or "none"' },
    url: { type: 'string' },
    opened: { type: 'string', description: 'The exact URL you opened to read it' },
    passage: { type: 'string', description: 'Verbatim passage from the opened text containing every number the claim uses' },
  },
  required: ['citation', 'type', 'doi', 'pmid', 'url', 'opened', 'passage'],
}

const CLAIM = {
  type: 'object',
  properties: {
    item: { type: 'string', description: 'The group item this answers (claim ID, topic or file)' },
    action: { type: 'string', enum: ['new_rule', 'change_rule', 'retire_rule'] },
    file: { type: 'string', description: 'knowledge file, e.g. nutrition.md' },
    heading: { type: 'string', description: 'existing rule heading to change or retire, or the proposed new heading' },
    rule: { type: 'string', description: 'the coaching rule in plain words' },
    evidence: { type: 'string', description: 'what the sources show, with their numbers' },
    grade: { type: 'string', enum: ['strong', 'moderate', 'emerging'] },
    population: { type: 'string' },
    conflicts: { type: 'string', description: 'where evidence conflicts or depends on the person; "none found" if none' },
    sources: { type: 'array', items: SOURCE },
  },
  required: ['item', 'action', 'file', 'heading', 'rule', 'evidence', 'grade', 'population', 'conflicts', 'sources'],
}

const DROP = {
  type: 'object',
  properties: {
    item: { type: 'string' },
    claim: { type: 'string' },
    reason: { type: 'string', description: 'what was searched or opened and why it does not confirm the claim' },
  },
  required: ['item', 'claim', 'reason'],
}

const SEARCH_OUT = {
  type: 'object',
  properties: { candidates: { type: 'array', items: CLAIM }, dropped: { type: 'array', items: DROP } },
  required: ['candidates', 'dropped'],
}

const VERIFY_OUT = {
  type: 'object',
  properties: {
    verified: { type: 'array', items: CLAIM },
    dropped: { type: 'array', items: DROP },
  },
  required: ['verified', 'dropped'],
}

const groups = (args && args.groups) || []
if (groups.length === 0 || groups.length > 4) {
  throw new Error('research workflow needs 1 to 4 groups')
}
log(`${groups.length} groups, ${groups.reduce((n, g) => n + g.items.length, 0)} items`)

const results = await pipeline(
  groups,
  (group) =>
    agent(
      `You are searching the research literature for an evidence-based personal coach (today is ${args.today}).

Group: ${group.label}
What to look for: ${group.brief}
Items:
${group.items.map((item, i) => `${i + 1}. ${item}`).join('\n')}

For each item, search (web search and PubMed E-utilities), open the best sources, and either
propose a rule change backed by sources you opened, with a verbatim passage for every number, or
drop it with the reason. Read the current rule first when the item names one:
\`uv run python -m coach knowledge section FILE "HEADING"\` (never read knowledge/sources.md whole;
grep it by ID if you need a source: grep -n -A6 '^### S123$' knowledge/sources.md).

${RULES}`,
      { label: `search:${group.label}`, phase: 'Search', schema: SEARCH_OUT, effort: 'low' },
    ),
  (found, group) =>
    !found
      ? null
      : found.candidates.length === 0
      ? { verified: [], dropped: found.dropped }
      : agent(
          `You are an independent checker for an evidence-based personal coach (today is ${args.today}).
Another agent proposed the rule changes below. Try to refute each one.

For every candidate: open every source yourself (do not trust the passage given), confirm the
passage is verbatim and contains every number in "rule" and "evidence", confirm the population and
that the grade follows the rubric, and check whether a better or newer source contradicts it.
Verdict per candidate: keep it (return it, corrected if needed: fix numbers, narrow the
population, lower the grade, replace the passage with the verbatim text you read), or drop it
with the reason. Default to dropping when you cannot confirm it.

Candidates (JSON):
${JSON.stringify(found.candidates, null, 2)}

${RULES}`,
          { label: `verify:${group.label}`, phase: 'Verify', schema: VERIFY_OUT, effort: 'high' },
        ).then((checked) =>
          checked
            ? { verified: checked.verified, dropped: [...found.dropped, ...checked.dropped] }
            : // The verifier died: nothing is verified, but the searcher's drops still count.
              { verified: [], dropped: found.dropped, verifier_failed: true },
        ),
)

const ok = results.filter(Boolean)
const failed = groups.filter((_, i) => !results[i] || results[i].verifier_failed).map((g) => g.label)
if (failed.length) log(`${failed.length} group(s) failed; their claims are unverified: ${failed.join(', ')}`)
return {
  verified: ok.flatMap((r) => r.verified),
  dropped: ok.flatMap((r) => r.dropped),
  failed_groups: failed,
}
