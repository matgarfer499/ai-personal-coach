# Roadmap

Known gaps after the fourth and last simulated beta (2026-11-08, 4.1/5). This is not a backlog:
the coach is a base of graded, sourced rules meant to be extended for each case (see the README's
Scope section), and these items are examples of extensions someone could add, with the beta issue
IDs they come from, the personas who asked, and why they were left out. IDs: `p3-antonio-F2` is a
beta-4 issue, `p3-antonio-N7` a beta-3 one, `p1-lucia-I4` a beta-2 one, `(b1)` a beta-1 one.
Persona names are the beta's invented clients, not real people.

## Check-in notes

- **Past-tense and progressive symptom phrases.** The notes scan finds present-tense phrases ("me
  duele el pecho", "me aprieta el pecho") but not "me dolió el pecho", "me sigue apretando el
  pecho", "me costó respirar", "se me cierra el pecho" or "se me aceleró el corazón". Issues:
  p1-lucia-F2, p1-lucia-F3, p3-antonio-F2. Personas: Lucía, Antonio. Why it waits: the scan is a
  prompt to ask, never a flag, and /checkin asks about chest pain, breathlessness and palpitations
  at every check-in; covering verb forms needs a general rule for Spanish conjugation, not a list
  of the phrases the beta used. Decided without Matías (safety).
- **"no tuve ningún mareo" read as dizziness.** Issue: p1-lucia-F4. Persona: Lucía. Why it waits:
  a false positive on the safe side (the coach asks once); "ningún" after a verb needs a wider
  negation rule.

## Running

- **Km and pace for each planned run, and easy-run pace.** `coach runs plan` gives the long-run
  cap, weekly km, easy share, the goal race pace and a Riegel prediction, but not a run-by-run
  schedule. Issues: p6-james-I5 (b2), p6-james-N3, p6-james-F4. Persona: James. Why it waits: no rule for a
  half-marathon build-up, km per run or easy pace (docs/dropped-claims.md D268, D277); the
  volume rule found gives associations only.
- **Restart volume after a running injury.** The cap after an injury never returns to a spike
  and the new return-to-running rules give start criteria and a walk-run restart, but not a
  starting fraction of pre-injury volume. Issue: p6-james-N8 (the part beyond the cap). Persona:
  James. Why it waits: no review or consensus gives that fraction (D278). The weekly ceiling still
  comes from the last weeks, a spike week included (p6-james-F5).
- **Taper with no recent runs, and the race distance stored to one decimal.** Issues:
  p6-james-F9, p6-james-F7. Persona: James. Why it waits: the taper needs a reference week to
  scale; 21.1 km is the rounding the CLI shows everywhere.
- **What to do while a fatigue stop holds.** One confirmed unusual-fatigue answer stops all
  training, deload and taper numbers. Issues: p6-james-F10, p6-james-N7. Persona: James. Why it
  waits: by design (recovery-habits.md "Cardiac warning symptoms: stop and refer"); a waiting
  line is wording for the skill.
- **Vigorous runs described by zone or pace in `plan check`.** A bullet such as "6 km at race
  pace, vigorous zone" passes while `coach safety` caps intensity. Issue: p6-james-F2. Persona:
  James. Why it waits: the check reads format words (HIIT, sprints, 1RM); zone and pace words need
  a wording rule for plan.md; the plan skill already caps intensity. Decided without Matías
  (safety).
- **Long-run cap printed 8.05 by `runs plan` and 8.1 by `plan check`.** Issue: p6-james-F3.
  Persona: James. Why it waits: a 0.05 km display difference.
- **Weekly-total km lines in `plan check`.** A line such as "Week total: 20 km" is read as a run.
  Persona: James (review finding). Why it waits: telling a run from a total needs a wording rule
  for plan.md.

## Food and shopping

- **Chickpeas and canned legumes bought dry.** Cooked rice, pasta, lentils and broccoli are bought
  dry or raw; cooked chickpeas and beans stay cooked. Issue: p4-sara-N1 (rest). Persona: Sara.
  Why it waits: no yield row for them yet (D276).
- **Lines split across the client's chains without products.** Issues: p4-sara-N4, p4-sara-F2. Persona: Sara.
  Why it waits: needs a store-product mapping nobody has published.
- **Portions per eater (children, household).** Issues: p4-sara-N10, p4-sara-F3. Persona: Sara. Why it waits:
  no portion rule for children (D275).
- **Confirmation from a 20-35% label kcal mismatch.** Issues: p4-sara-N5, p4-sara-F4. Persona: Sara. Why it
  waits: the 50% refusal is a design value; a lower one would refuse many correct labels.
- **Singular and plural food names ("espinaca").** Issue: p4-sara-N13. Persona: Sara. Why it
  waits: fuzzy matching across the food table; `coach foods search` finds the name today.
- **Salt and sodium in menus for clients with high blood pressure.** /menu treats salt as free
  seasoning and menus do not track sodium, while /plan gives the under-5 g salt guidance. Issues:
  p3-antonio-F3, p3-antonio-F9. Persona: Antonio. Why it waits: a sodium-restricted diet is a case
  extension (food table sodium, a menu limit), like gluten-free or lactose-free menus. Decided
  without Matías (safety, low).
- **Menu and product conveniences.** A plain snack repeated daily (an apple) counts as a dish
  repeat; an unknown food gives no suggestion; the PDF path is relative; no `products remove`; a
  product added with `--replaces` keeps the English food name; `base:` is not checked against the
  dish's items. Issues: p5-elena-F9, p5-elena-F8, p4-sara-F7, p4-sara-F8, p4-sara-F10,
  p4-sara-F12. Personas: Elena, Sara. Why it waits: none gives a wrong number; `coach foods
  search` and `--replace` cover them today.
- **`base:` with several words.** Issue: p5-elena-N13. Persona: Elena. Why it waits: the skill
  documents one word per base; the parser change is not needed for any menu.

## Evidence and grades

- **Fat and fibre graded strong.** Issues: p5-elena-N10, p5-elena-F4. Persona: Elena. Why it waits: a grade is
  research's call; queued for the next `/research nutrition.md`.
- **"Deficit size" reads 500 kcal as a ceiling.** Issue: p5-elena-N14. Persona: Elena. Why it
  waits: rule wording, needs a research pass.
- **Protein note names the 1.6-2.2 band.** Issues: p5-elena-N9, p5-elena-F5. Persona: Elena. Why it waits: the
  BMI cap already lands an overweight beginner in the rule's 1.6-2.0; only the note's wording.
- **`check_knowledge.py --claims` in CI with a baseline.** Issues: p5-elena-I7 (b1),
  p5-elena-N11, p5-elena-F3. Persona: Elena. Why it waits: it changes `.github/`, which needs Matías.
- **Protein rule cited for a client who cannot train.** Issues: p3-antonio-N9, p3-antonio-F8. Persona: Antonio.
  Why it waits: the knowledge base has no protein rule for an adult on a training stop.

## Language

- **Safety reasons, rule citations and the remaining CLI errors in Spanish.** The CLI's own
  sentences (trend, check-in date, weight jump, protein note, menu warnings, stale plan) are now
  Spanish with a decimal comma; rule citations, safety reasons and some errors (`runs add`
  future date, refused logs) are not. Issues: p1-lucia-I5 (b2), p1-lucia-I6 (b1), p1-lucia-F6,
  p4-sara-F6. Personas: Lucía, Sara. Why it waits: rule headings are English identifiers that skills and tests grep;
  translating every reason is a large surface, and the skills already say them in plain words.

## Plans and strength

- **Leg, push and pull in every session.** Issues: p5-elena-N3 (that part), p5-elena-F2. Persona: Elena. Why it
  waits: a per-session rule fails valid splits (push-pull-legs); a weekly coverage check needs a
  rule.
- **Rep range per exercise in the PDF.** Issue: p2-marcus-F5. Persona: Marcus (5-star line). Why it waits: Marcus
  already rates 5; the plan text carries the range.
- **Sets per lift and the rep-range line in `plan check`.** plan.md and plan-week.yaml can
  disagree on sets per lift, and a `rep_range` header that disagrees with the bullets passes.
  Issues: p2-marcus-F2, p2-marcus-F7, p2-marcus-N9. Persona: Marcus. Why it waits: Marcus rates
  5; lifts and session counts are compared.
- **`# ` headings give 0 sessions with no hint, and weekly sets per muscle for a split.** Issues:
  p2-marcus-F1, p2-marcus-F8. Persona: Marcus. Why it waits: plan/SKILL.md writes `## `; a hint
  per muscle needs a coverage rule.
- **Plate-rounded loads after an lbs import.** Suggested loads show 82.51 kg. Issue: p2-marcus-F6.
  Persona: Marcus. Why it waits: cosmetic; the figure is exact.
- **The suspension and the way back in plain words.** The "Plan suspendido" section names a
  training week the plan may not have, the way to lift it is shown as a command, and after the
  clearance the deficit returns while a BP check is still due. Issues: p3-antonio-F7,
  p1-lucia-F7, p3-antonio-F6. Personas: Antonio, Lucía. Why it waits: wording; the skills say it
  in plain words and the BP reason stays in `coach safety`.
- **Which sets collided on import.** Personas: Marcus, Elena. Why it waits: a summary feature, not
  a bug; the counts are right.

## Review and trend

- **A fuller /review after a pause, and trend notes.** After a pause the review gives little; the
  trend shows "faltan 0 pesajes" and gives no note on a single weigh-in far from the rest.
  Issues: p1-lucia-F10, p1-lucia-F8, p6-james-F6. Personas: Lucía, James. Why it waits: the
  check-in already questions a far weigh-in; wording and a summary feature.

## Setup and tooling

- **Ask how fast a "mild" fat-loss goal should be.** /setup stores fat_loss and the coach gives
  the 500 kcal deficit without asking. Issue: p4-sara-F9. Persona: Sara. Why it waits: the deficit
  size rule is queued for research (p5-elena-N14 above).
- **README first-run steps, an English /setup example, login state in `coach doctor`, where
  plan-week.yaml lives.** Issues: p7-nuevo-F2, p7-nuevo-F4, p7-nuevo-F6, p7-nuevo-F8. Persona:
  Nico. Why it waits: documentation; `doctor` cannot see a Claude login.

- **`coach profile set` prints the whole profile.** Issue: p6-james-N14. Persona: James. Why it
  waits: cosmetic.
- **A Claude Code permission allowlist in the repo, and a three-turn /setup example.** Persona:
  Nico. Why it waits: pre-granting permissions on clone is a security choice for the owner; the
  README now explains the prompts. Issue: p7-nuevo-F5.
