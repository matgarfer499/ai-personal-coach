# Roadmap

Known gaps after the third simulated beta (2026-11-08, 4.1/5), deferred on purpose. Each item has
the beta issue IDs it comes from, the personas who asked, and why it waits. IDs: `p3-antonio-N7`
is a beta-3 issue, `p1-lucia-I4` a beta-2 one, `(b1)` a beta-1 one. Persona names are the beta's
invented clients, not real people.

## Running

- **Km and pace for each planned run, and easy-run pace.** `coach runs plan` gives the long-run
  cap, weekly km, easy share, the goal race pace and a Riegel prediction, but not a run-by-run
  schedule. Issues: p6-james-I5 (b2), p6-james-N3. Persona: James. Why it waits: no rule for a
  half-marathon build-up, km per run or easy pace (docs/dropped-claims.md D268, D277); the
  volume rule found gives associations only.
- **Restart volume after a running injury.** The cap after an injury never returns to a spike
  and the new return-to-running rules give start criteria and a walk-run restart, but not a
  starting fraction of pre-injury volume. Issue: p6-james-N8 (the part beyond the cap). Persona:
  James. Why it waits: no review or consensus gives that fraction (D278).
- **Weekly-total km lines in `plan check`.** A line such as "Week total: 20 km" is read as a run.
  Persona: James (review finding). Why it waits: telling a run from a total needs a wording rule
  for plan.md.

## Food and shopping

- **Chickpeas and canned legumes bought dry.** Cooked rice, pasta, lentils and broccoli are bought
  dry or raw; cooked chickpeas and beans stay cooked. Issue: p4-sara-N1 (rest). Persona: Sara.
  Why it waits: no yield row for them yet (D276).
- **Lines split across the client's chains without products.** Issue: p4-sara-N4. Persona: Sara.
  Why it waits: needs a store-product mapping nobody has published.
- **Portions per eater (children, household).** Issue: p4-sara-N10. Persona: Sara. Why it waits:
  no portion rule for children (D275).
- **Confirmation from a 20-35% label kcal mismatch.** Issue: p4-sara-N5. Persona: Sara. Why it
  waits: the 50% refusal is a design value; a lower one would refuse many correct labels.
- **Singular and plural food names ("espinaca").** Issue: p4-sara-N13. Persona: Sara. Why it
  waits: fuzzy matching across the food table; `coach foods search` finds the name today.
- **`base:` with several words.** Issue: p5-elena-N13. Persona: Elena. Why it waits: the skill
  documents one word per base; the parser change is not needed for any menu.

## Evidence and grades

- **Fat and fibre graded strong.** Issue: p5-elena-N10. Persona: Elena. Why it waits: a grade is
  research's call; queued for the next `/research nutrition.md`.
- **"Deficit size" reads 500 kcal as a ceiling.** Issue: p5-elena-N14. Persona: Elena. Why it
  waits: rule wording, needs a research pass.
- **Protein note names the 1.6-2.2 band.** Issue: p5-elena-N9. Persona: Elena. Why it waits: the
  BMI cap already lands an overweight beginner in the rule's 1.6-2.0; only the note's wording.
- **`check_knowledge.py --claims` in CI with a baseline.** Issues: p5-elena-I7 (b1),
  p5-elena-N11. Persona: Elena. Why it waits: it changes `.github/`, which needs Matías.
- **Protein rule cited for a client who cannot train.** Issue: p3-antonio-N9. Persona: Antonio.
  Why it waits: the knowledge base has no protein rule for an adult on a training stop.

## Language

- **Safety reasons, rule citations and the remaining CLI errors in Spanish.** The CLI's own
  sentences (trend, check-in date, weight jump, protein note, menu warnings, stale plan) are now
  Spanish with a decimal comma; rule citations, safety reasons and some errors (`runs add`
  future date, refused logs) are not. Issues: p1-lucia-I5 (b2), p1-lucia-I6 (b1). Personas:
  Lucía, Sara. Why it waits: rule headings are English identifiers that skills and tests grep;
  translating every reason is a large surface, and the skills already say them in plain words.

## Plans and strength

- **Leg, push and pull in every session.** Issue: p5-elena-N3 (that part). Persona: Elena. Why it
  waits: a per-session rule fails valid splits (push-pull-legs); a weekly coverage check needs a
  rule.
- **Rep range per exercise in the PDF.** Persona: Marcus (5-star line). Why it waits: Marcus
  already rates 5; the plan text carries the range.
- **Which sets collided on import.** Personas: Marcus, Elena. Why it waits: a summary feature, not
  a bug; the counts are right.

## Setup and tooling

- **`coach profile set` prints the whole profile.** Issue: p6-james-N14. Persona: James. Why it
  waits: cosmetic.
- **A Claude Code permission allowlist in the repo, and a three-turn /setup example.** Persona:
  Nico. Why it waits: pre-granting permissions on clone is a security choice for the owner; the
  README now explains the prompts.
