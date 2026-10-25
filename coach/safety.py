"""Screening answers, medications and conditions -> flags that the calculators obey.

Overrides live here, not in skill text: `energy.calorie_target` refuses a deficit when
`no_deficit` is set, `zones.hr_zones` returns RPE zones only when `use_rpe_not_hr` is set, and so
on. Every reason names the knowledge rule that set the flag, in the code-comment format, so a
skill can quote it and a reader can grep it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from coach.profile import (
    BETA_BLOCKER,
    GLP1,
    HYPERTENSION,
    PLANNING_PREGNANCY,
    PREGNANT,
    Profile,
)
from coach.text import fold

SCOFF = 'nutrition.md: "Eating-disorder screening: brief questions as a prompt"'
GLP1_RULE = 'nutrition.md: "GLP-1 users: protein, training and red flags"'
BETA_BLOCKER_RULE = 'cardio-health.md: "Beta-blockers: no formula-based HR zones"'
PREGNANCY_NUTRITION = 'nutrition.md: "Pregnancy"'
PREGNANCY_ACTIVITY = 'recovery-habits.md: "Default is to be active"'
PREGNANCY_INTENSITY = (
    'recovery-habits.md: "Gauge intensity by talk test and RPE, not a heart-rate cap"'
)
MENSTRUAL = 'nutrition.md: "Menstrual dysfunction: stop and refer"'
PARQ = 'recovery-habits.md: "PAR-Q+ 2023 as the default entry screen"'
PARQ_THRESHOLDS = 'recovery-habits.md: "PAR-Q+ specific thresholds"'
INJURY = 'recovery-habits.md: "Some pain during exercise is acceptable in chronic, assessed pain"'
CARDIAC = 'recovery-habits.md: "Cardiac warning symptoms: stop and refer"'
BP = 'recovery-habits.md: "Resting BP thresholds to defer or refer"'
UNDER_18 = 'nutrition.md: "Under-18s"'

# nutrition.md: "Under-18s" and recovery-habits.md "Adolescents: no deficits": under-18s are
# out of scope (no calorie targets, deficits or weigh-ins).
ADULT_AGE = 18

# nutrition.md: "Eating-disorder screening: brief questions as a prompt": the validated SCOFF
# cut point is 2 or more yes answers ([S349]).
SCOFF_CUT_POINT = 2

# recovery-habits.md: "Resting BP thresholds to defer or refer" (mmHg; a band applies when either
# number reaches it).
BP_NO_EXERCISE = (200, 110)
BP_NO_TRAINING_SYSTOLIC = 180
BP_GP_REVIEW = (160, 90)
BP_MODERATE_SYSTOLIC = 140

# recovery-habits.md: "PAR-Q+ specific thresholds": anyone over 45 (or with any PAR-Q+ YES) gets
# a qualified exercise professional or clinician review before vigorous or maximal work. "Over 45"
# is read as aged 45 or more, the cautious side of the cut-off.
VIGOROUS_REVIEW_AGE = 45


@dataclass
class Pause:
    """Why a lift is paused by an active injury, and whether a professional has assessed it."""

    reasons: list[str]
    assessed: bool


@dataclass
class SafetyFlags:
    screened: bool = False  # the eating-disorder screen has been answered
    no_deficit: bool = False
    no_weight_targets: bool = False  # also no weigh-ins
    hold_deficit: bool = False  # keep the current deficit, never increase it
    use_rpe_not_hr: bool = False
    prescriber_owns_weight: bool = False
    refer_gp: bool = False
    no_training: bool = False  # resting BP too high to train until a doctor reviews it
    cap_moderate: bool = False  # light-to-moderate intensity only
    no_calorie_targets: bool = False  # under-18s: no calorie or macro targets at all
    hold_progression: bool = False  # no added load, reps or intensity until a clinician reviews
    review_before_vigorous: bool = False  # no vigorous or maximal work until a review
    no_all_out_sprints: bool = False  # no SIT or REHIT: some PAR-Q+ answer is YES
    # the number to call in an emergency: the client's own, else their region's, else unknown
    emergency_number: str | None = None
    # logged exercise name -> why its load is paused (an active injury)
    paused_exercises: dict[str, Pause] = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)


def flags(profile: Profile, today: date | None = None) -> SafetyFlags:
    screening = profile.screening
    out = SafetyFlags(screened="scoff_positive" in screening or "scoff_yes_count" in screening)
    out.emergency_number = profile.emergency_number or _regional_emergency_number(profile)

    if profile.birth_date is not None and profile.age(today) < ADULT_AGE:
        out.no_calorie_targets = out.no_deficit = out.no_weight_targets = out.refer_gp = True
        out.reasons.append(
            f"{UNDER_18}: under 18, out of scope: no calorie targets, deficits or weigh-ins; "
            "suggest a paediatrician, GP or paediatric dietitian"
        )

    if eating_disorder_positive(profile):
        out.no_deficit = out.no_weight_targets = out.refer_gp = True
        out.reasons.append(
            f"{SCOFF}: positive screen ({SCOFF_CUT_POINT} or more yes answers) or a warning "
            "sign, so no deficit, weight targets or weigh-ins; "
            "suggest a GP or eating-disorder professional"
        )

    if profile.has_medication(GLP1):
        out.no_deficit = out.prescriber_owns_weight = True
        out.reasons.append(f"{GLP1_RULE}: the prescriber owns the weight plan, no extra deficit")
        if profile.has_condition(PREGNANT) or profile.has_condition(PLANNING_PREGNANCY):
            out.refer_gp = True
            out.reasons.append(
                f"{PREGNANCY_NUTRITION}: GLP-1 user pregnant or planning pregnancy, "
                "contact the prescriber promptly"
            )

    if profile.has_medication(BETA_BLOCKER):
        out.use_rpe_not_hr = True
        out.reasons.append(f"{BETA_BLOCKER_RULE}: prescribe by RPE and the talk test")

    if profile.has_condition(PREGNANT):
        out.no_deficit = out.no_weight_targets = out.prescriber_owns_weight = True
        out.use_rpe_not_hr = out.refer_gp = True
        out.reasons += [
            f"{PREGNANCY_NUTRITION}: no deficit; weight targets belong to the midwife or "
            "obstetrician",
            f"{PREGNANCY_ACTIVITY}: clear the plan with the obstetric care provider",
            f"{PREGNANCY_INTENSITY}: gauge intensity by talk test and RPE",
        ]

    menstrual = screening.get("menstrual")
    if menstrual == "irregular_new":
        out.hold_deficit = out.refer_gp = True
        out.reasons.append(f"{MENSTRUAL}: new irregular periods, stop increasing the deficit")
    elif menstrual == "absent":
        out.no_deficit = out.refer_gp = True
        out.reasons.append(
            f"{MENSTRUAL}: periods absent 3 months or more (or fewer than 6 a year), "
            "stop the deficit and refer"
        )

    if screening.get("parq_followup_yes"):
        out.refer_gp = out.hold_progression = True
        out.reasons.append(f"{PARQ}: follow-up YES, pause intensity progression and refer")

    _vigorous_work(profile, out, today)
    _injuries(profile, out)
    _blood_pressure(profile, out)

    if screening.get("cardiac_symptoms"):
        out.refer_gp = out.no_training = True
        out.reasons.append(
            f"{CARDIAC}: stop exercising and seek medical evaluation; no training until a "
            "clinician clears it"
        )

    if out.no_training:
        out.hold_progression = True
    return out


def _regional_emergency_number(profile: Profile) -> str | None:
    # Imported here: coach.regions imports coach.foods, which imports coach.macros and so this
    # module.
    from coach import regions

    return regions.emergency_number(profile.region)


def eating_disorder_positive(profile: Profile) -> bool:
    """A positive screen: the SCOFF cut point, or a warning sign stored as `scoff_positive`."""
    screening = profile.screening
    return bool(screening.get("scoff_positive")) or (
        screening.get("scoff_yes_count", 0) >= SCOFF_CUT_POINT
    )


def calorie_block_reason(out: SafetyFlags) -> str:
    """The reason that set `no_calorie_targets` (under 18)."""
    return next(r for r in out.reasons if r.startswith(UNDER_18))


def weight_block_reason(out: SafetyFlags) -> str:
    """The reason that set `no_weight_targets` (under 18, a positive screen or pregnancy)."""
    return next(r for r in out.reasons if r.startswith((UNDER_18, SCOFF, PREGNANCY_NUTRITION)))


def _vigorous_work(profile: Profile, out: SafetyFlags, today: date | None) -> None:
    screening = profile.screening
    # Follow-up questions are reached only through a YES on the first seven.
    any_yes = bool(screening.get("parq_any_yes") or screening.get("parq_followup_yes"))
    unanswered = "parq_any_yes" not in screening and not any_yes
    over_age = profile.birth_date is not None and profile.age(today) >= VIGOROUS_REVIEW_AGE
    if any_yes or unanswered:
        out.no_all_out_sprints = True
        why = "a PAR-Q+ YES" if any_yes else "PAR-Q+ not answered"
        out.reasons.append(
            f"{PARQ_THRESHOLDS}: {why}, so no all-out sprint formats (SIT, REHIT); they need "
            "every answer NO"
        )
    if unanswered:
        # "Choosing HIIT vs MICT vs SIT": an unscreened client starts with moderate work.
        out.review_before_vigorous = True
        out.reasons.append(
            f"{PARQ_THRESHOLDS}: PAR-Q+ not answered, so light-to-moderate work only until it is"
        )
    elif (any_yes or over_age) and not screening.get("vigorous_reviewed"):
        out.review_before_vigorous = True
        why = "a PAR-Q+ YES" if any_yes else f"aged {VIGOROUS_REVIEW_AGE} or more"
        out.reasons.append(
            f"{PARQ_THRESHOLDS}: {why}, so a qualified exercise professional or clinician "
            "reviews vigorous or maximal work (HIIT, 1RM tests, all-out sprints) before it "
            "starts; light-to-moderate work until then"
        )


def _injuries(profile: Profile, out: SafetyFlags) -> None:
    # convention: the coach does not progress a lift tied to an active injury; whoever manages
    # the injury decides when it moves. Unassessed, the lift gets no load at all.
    for injury in profile.active_injuries():
        area, who = injury["area"], injury.get("professional")
        if who:
            reason = (
                f"{INJURY}: {area} injury, managed by {who}: no progression; reduce or swap the "
                f"lift within the limits {who} set, who decides when it progresses"
            )
        else:
            out.refer_gp = True
            reason = (
                f"{INJURY}: {area} injury not yet assessed: a GP or physiotherapist assesses it "
                "before it is loaded; stop and refer for sharp or worsening pain"
            )
        out.reasons.append(reason)
        for exercise in injury.get("exercises", []):
            key = next((k for k in out.paused_exercises if fold(k) == fold(exercise)), exercise)
            pause = out.paused_exercises.setdefault(key, Pause([], assessed=True))
            pause.reasons.append(reason)
            pause.assessed = pause.assessed and bool(who)


def _blood_pressure(profile: Profile, out: SafetyFlags) -> None:
    systolic = profile.screening.get("bp_systolic")
    diastolic = profile.screening.get("bp_diastolic")
    if systolic is None and diastolic is None:
        if profile.has_condition(HYPERTENSION):
            out.cap_moderate = out.refer_gp = out.hold_progression = True
            out.reasons.append(
                f"{BP}: BP unknown with known hypertension, so a GP review before starting or "
                "progressing, and light-to-moderate work only"
            )
        return
    reading = f"{systolic or '?'}/{diastolic or '?'}"
    systolic, diastolic = systolic or 0, diastolic or 0
    if systolic >= BP_NO_EXERCISE[0] or diastolic >= BP_NO_EXERCISE[1]:
        out.no_training = out.refer_gp = True
        out.reasons.append(
            f"{BP}: {reading}, no exercise; re-measure after 5-10 min and see a "
            "doctor promptly if it stays high (urgently with headache, chest pain, visual "
            "change, neurological symptoms or breathlessness)"
        )
    elif systolic >= BP_NO_TRAINING_SYSTOLIC:
        out.no_training = out.refer_gp = True
        out.reasons.append(f"{BP}: {reading}, no training until reviewed by a GP")
    elif systolic >= BP_GP_REVIEW[0] or diastolic >= BP_GP_REVIEW[1]:
        out.cap_moderate = out.refer_gp = out.hold_progression = True
        out.reasons.append(
            f"{BP}: {reading}, GP review before starting or progressing; "
            "light-to-moderate work only until BP is controlled"
        )
    elif systolic >= BP_MODERATE_SYSTOLIC:
        out.cap_moderate = out.refer_gp = True
        out.reasons.append(f"{BP}: {reading}, moderate intensity and a GP check")
