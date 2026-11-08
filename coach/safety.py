"""Screening answers, medications and conditions -> flags that the calculators obey.

Overrides live here, not in skill text: `energy.calorie_target` refuses a deficit when
`no_deficit` is set, `zones.hr_zones` returns RPE zones only when `use_rpe_not_hr` is set, and so
on. Every reason names the knowledge rule that set the flag, in the code-comment format, so a
skill can quote it and a reader can grep it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date

from coach.profile import (
    BETA_BLOCKER,
    BP_MEDICATION,
    GLP1,
    HYPERTENSION,
    NO_NUMBER,
    PLANNING_PREGNANCY,
    PREGNANT,
    SYMPTOM_TOKENS,
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
PARQ = 'recovery-habits.md: "PAR-Q+ 2023 as an optional extra screen"'
ACSM = 'recovery-habits.md: "ACSM 2015 screening algorithm"'
PARQ_THRESHOLDS = 'recovery-habits.md: "PAR-Q+ specific thresholds"'
INJURY = 'recovery-habits.md: "Some pain during exercise is acceptable in chronic, assessed pain"'
CARDIAC = 'recovery-habits.md: "Cardiac warning symptoms: stop and refer"'
BP = 'recovery-habits.md: "Resting BP thresholds to defer or refer"'
UNDER_18 = 'nutrition.md: "Under-18s"'
KNEE = 'recovery-habits.md: "Knee injury: signs of ligament or meniscus damage"'
# The "clearance before any exercise" cell: not exercising regularly, or not answered.
ACSM_STOP = (f"{ACSM}: not exercising regularly", f"{ACSM}: regular exercise not answered")
# The rules whose reasons explain `no_training` and `review_before_vigorous`, respectively.
TRAINING_STOPS = (CARDIAC, BP, ACSM)
VIGOROUS_CAPS = (PARQ_THRESHOLDS, ACSM)

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

# convention: no rule covers dieting while cardiac symptoms or a very high BP await a
# clinician, so the coach holds calories at maintenance until training is cleared (the
# cautious direction; listed in docs/conventions.md).
NO_TRAINING_NO_DEFICIT = "; convention: no deficit until then, calories stay at maintenance"

# docs/safety.md "The deferral line": copied exactly; tests/coach/test_safety.py checks the docs.
DEFERRAL_LINE = {
    "es": "Esto es orientación general de un entrenador automatizado, no consejo médico. Por lo "
    "que me has contado, habla con tu médico (o con el profesional que te indico arriba) antes "
    "de ponerlo en práctica.",
    "en": "This is general guidance from an automated coach, not medical advice. Because of what "
    "you told me, talk to your doctor (or the professional named above) before acting on it.",
}
# recovery-habits.md: "Cardiac warning symptoms: stop and refer" (its first-aid sentence).
EMERGENCY_LINE = {
    "es": "Si tienes dolor en el pecho en reposo, te desmayas, o dolor en el pecho con falta de "
    "aire y sudor, llama ya al {number}.",
    "en": "If you have chest pain at rest, faint, or have chest pain with breathlessness and "
    "sweating, call {number} now.",
}
NO_EMERGENCY_NUMBER = {"es": "número de emergencias local", "en": "local emergency number"}

SYMPTOMS = SYMPTOM_TOKENS  # the tokens `checkin add --symptoms` accepts
# convention: words that suggest a token in free-text check-in notes (es and en, accents
# ignored). A hit is only reported for the skill to ask about; it never sets a flag.
SYMPTOM_WORDS = {
    "chest_pain": (
        "dolor en el pecho",
        "dolor de pecho",
        "opresion en el pecho",
        "presion en el pecho",
        "chest pain",
        "chest tightness",
        "chest pressure",
        "tight chest",
    ),
    "breathless": ("falta de aire", "me ahogo", "short of breath", "breathless"),
    "dizzy": ("mareo", "mareos", "mareada", "mareado", "dizzy", "dizziness", "lightheaded"),
    "faint": ("desmayo", "desmaye", "desmayada", "desmayado", "fainted", "faint", "passed out"),
    "palpitations": ("palpitaciones", "palpitations", "heart racing", "corazon acelerado"),
    "ankle_swelling": ("tobillos hinchados", "swollen ankles", "ankle swelling"),
    "calf_pain": ("dolor de gemelo al caminar", "calf pain when walking"),
    "unusual_fatigue": (
        "unusually tired",
        "unusual tiredness",
        "unusual fatigue",
        "cansancio inusual",
        "cansancio raro",
        "agotamiento inusual",
        "agotada sin motivo",
        "agotado sin motivo",
    ),
}
# convention: other words clients use for a token, accepted by `checkin add --symptoms` (folded,
# spaces as underscores).
SYMPTOM_SYNONYMS = {
    "chest_tightness": "chest_pain",
    "chest_pressure": "chest_pain",
    "tight_chest": "chest_pain",
    "short_of_breath": "breathless",
    "shortness_of_breath": "breathless",
    "breathlessness": "breathless",
    "dizziness": "dizzy",
    "lightheaded": "dizzy",
    "fainted": "faint",
    "fainting": "faint",
    "heart_racing": "palpitations",
    "swollen_ankles": "ankle_swelling",
    "fatigue": "unusual_fatigue",
}
# convention: words for a swollen joint in free-text notes (es and en). A hit is a prompt to ask
# about an injury (KNEE: swelling after a knee injury means stop loading and get it assessed),
# never a cardiac token: ankle swelling without an injury is the cardiac one.
INJURY_WORDS = (
    "swollen",
    "swelling",
    "hinchada",
    "hinchado",
    "hinchazon",
    "inflamada",
    "inflamado",
)
# convention: the names under an injury's `exercises` that pause running (es and en).
RUN_NAMES = ("running", "run", "runs", "correr", "carrera", "carreras", "trotar")

# convention: reasons are listed most urgent first; `instruction` is the first. The order: stop
# training (any reason ending in NO_TRAINING_NO_DEFICIT), out-of-scope and eating-disorder blocks,
# medical hand-offs, referrals, then intensity caps (listed in docs/conventions.md).
PRIORITY = (
    CARDIAC,
    UNDER_18,
    SCOFF,
    MENSTRUAL,
    PREGNANCY_NUTRITION,
    PREGNANCY_ACTIVITY,
    GLP1_RULE,
    BP,
    ACSM,
    PARQ,
    INJURY,
    PARQ_THRESHOLDS,
    PREGNANCY_INTENSITY,
    BETA_BLOCKER_RULE,
)

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
    no_training: bool = False  # no training until a clinician clears it (symptoms, BP, ACSM)
    # ACSM 2015: inactive with known disease, so medical clearance before any exercise. It sets
    # no_training too, but not no_deficit: calories follow the normal rules.
    clearance_before_exercise: bool = False
    cap_moderate: bool = False  # light-to-moderate intensity only
    no_calorie_targets: bool = False  # under-18s: no calorie or macro targets at all
    hold_progression: bool = False  # no added load, reps or intensity until a clinician reviews
    review_before_vigorous: bool = False  # no vigorous or maximal work until a review
    no_all_out_sprints: bool = False  # no SIT or REHIT: some PAR-Q+ answer is YES
    # the number to call in an emergency: the client's own, else their region's, else unknown
    emergency_number: str | None = None
    # logged exercise name -> why its load is paused (an active injury)
    paused_exercises: dict[str, Pause] = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)  # most urgent first
    instruction: str | None = None  # the first reason: what to do above all else
    # intensity caps that a training stop makes moot, kept for the record, not to act on
    superseded: list[str] = field(default_factory=list)
    deferral_line: str | None = None  # with refer_gp: docs/safety.md, in the profile language
    emergency_line: str | None = None  # with cardiac symptoms: when to call the number now


def flags(profile: Profile, today: date | None = None) -> SafetyFlags:
    screening = profile.screening
    out = SafetyFlags(screened="scoff_positive" in screening or "scoff_yes_count" in screening)
    own = None if profile.emergency_number == NO_NUMBER else profile.emergency_number
    out.emergency_number = own or _regional_emergency_number(profile)

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
    _acsm(profile, out)

    if symptomatic(profile):
        out.refer_gp = out.no_training = True
        out.reasons.append(
            f"{CARDIAC}: stop exercising and seek medical evaluation; no training until a "
            f"clinician clears it{NO_TRAINING_NO_DEFICIT}"
        )

    if out.no_training:
        out.hold_progression = True
        # Only a stop for symptoms or a very high BP holds the deficit (the convention says why).
        out.no_deficit = out.no_deficit or any(NO_TRAINING_NO_DEFICIT in r for r in out.reasons)
        # "light-to-moderate" or "moderate" work contradicts "no training": keep it out.
        moot = [
            r
            for r in out.reasons
            if r.startswith(PARQ_THRESHOLDS) or (r.startswith(ACSM) and not r.startswith(ACSM_STOP))
        ]
        if out.cap_moderate:
            moot += [r for r in out.reasons if r.startswith(BP)]
            # The cap is moot, the GP check is not: ask for it at the same visit.
            screening = profile.screening
            reading = (
                f"{screening.get('bp_systolic', '?')}/{screening.get('bp_diastolic', '?')}"
                if "bp_systolic" in screening or "bp_diastolic" in screening
                else "unknown, with known hypertension"
            )
            out.reasons.append(
                f"{BP}: blood pressure {reading}: ask the clinician to check it at the same visit"
            )
        out.superseded = moot
        out.reasons = [r for r in out.reasons if r not in moot]
    out.reasons.sort(key=_priority)
    out.instruction = out.reasons[0] if out.reasons else None
    language = profile.language or "en"
    if out.refer_gp:
        out.deferral_line = DEFERRAL_LINE[language]
    if symptomatic(profile):
        number = out.emergency_number or NO_EMERGENCY_NUMBER[language]
        out.emergency_line = EMERGENCY_LINE[language].format(number=number)
    return out


def _priority(reason: str) -> tuple[bool, int]:
    # A training stop (cardiac, BP 180+ or the ACSM clearance cell) goes first whatever rule set it.
    rank = next((i for i, rule in enumerate(PRIORITY) if reason.startswith(rule)), len(PRIORITY))
    stop = NO_TRAINING_NO_DEFICIT in reason or reason.startswith(ACSM_STOP)
    return not stop, rank


def _has_word(folded: str, words) -> bool:
    return any(re.search(rf"\b{re.escape(w)}\b", folded) for w in words)


def red_flag_words(text: str) -> list[str]:
    """Symptom tokens whose words appear in free text (a prompt to ask, never a flag)."""
    folded = fold(text)
    return [token for token, words in SYMPTOM_WORDS.items() if _has_word(folded, words)]


def injury_words(text: str) -> list[str]:
    """Swollen-joint words in free text, outside the cardiac ankle-swelling phrases."""
    folded = fold(text)
    for phrase in SYMPTOM_WORDS["ankle_swelling"]:
        folded = folded.replace(phrase, " ")
    return [w for w in INJURY_WORDS if _has_word(folded, [w])]


def symptom_token(said: str) -> str | None:
    """A symptom token for what the client said: the token itself or a known synonym."""
    key = fold(said).strip().replace(" ", "_").replace("-", "_")
    return key if key in SYMPTOMS else SYMPTOM_SYNONYMS.get(key)


def running_paused(profile: Profile) -> list[str]:
    """Reasons from active injuries that list running among their exercises."""
    out = []
    for injury in profile.active_injuries():
        if any(fold(e) in RUN_NAMES for e in injury.get("exercises", [])):
            who = injury.get("professional")
            out.append(
                f"{INJURY}: {injury['area']} injury"
                + (
                    f", managed by {who}: running only within the limits {who} set"
                    if who
                    else ": no running until a GP or physiotherapist assesses it"
                )
            )
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
    # A complete ACSM screen is the default entry screen: an unanswered PAR-Q+ no longer caps
    # intensity, but all-out sprints still need every PAR-Q+ answer NO ("PAR-Q+ specific
    # thresholds", a conservative product choice).
    over_age = profile.birth_date is not None and profile.age(today) >= VIGOROUS_REVIEW_AGE
    if any_yes or unanswered:
        out.no_all_out_sprints = True
        why = "a PAR-Q+ YES" if any_yes else "PAR-Q+ not answered"
        out.reasons.append(
            f"{PARQ_THRESHOLDS}: {why}, so no all-out sprint formats (SIT, REHIT); they need "
            "every answer NO"
        )
    if unanswered and not acsm_complete(profile):
        # "Choosing HIIT vs MICT vs SIT": an unscreened client starts with moderate work.
        out.review_before_vigorous = True
        out.reasons.append(
            f"{PARQ_THRESHOLDS}: no entry screen answered, so light-to-moderate work only "
            "until it is"
        )
    elif (any_yes or over_age) and not screening.get("vigorous_reviewed"):
        out.review_before_vigorous = True
        why = "a PAR-Q+ YES" if any_yes else f"aged {VIGOROUS_REVIEW_AGE} or more"
        out.reasons.append(
            f"{PARQ_THRESHOLDS}: {why}, so a qualified exercise professional or clinician "
            "reviews vigorous or maximal work (HIIT, 1RM tests, all-out sprints) before it "
            "starts; light-to-moderate work until then"
        )


def symptomatic(profile: Profile) -> bool:
    """Any warning symptom: stored at /setup (`symptoms`) or at /checkin (`cardiac_symptoms`)."""
    screening = profile.screening
    return bool(screening.get("cardiac_symptoms") or screening.get("symptoms"))


ACSM_ANSWERS = ("regular_exercise", "known_disease", "symptoms")


def acsm_complete(profile: Profile) -> bool:
    """All three ACSM 2015 inputs answered (an empty list is an answer: none)."""
    return all(key in profile.screening for key in ACSM_ANSWERS)


def _acsm(profile: Profile, out: SafetyFlags) -> None:
    # recovery-habits.md: "ACSM 2015 screening algorithm". Symptoms (either cell) are handled with
    # the cardiac rule in `flags`; here only the known-disease cells without symptoms.
    screening = profile.screening
    disease = screening.get("known_disease") or []
    if not disease or symptomatic(profile):
        return
    named = ", ".join(disease)
    active = screening.get("regular_exercise")
    cleared = screening.get("medically_cleared")
    if active and not cleared:
        out.review_before_vigorous = out.refer_gp = True
        out.reasons.append(
            f"{ACSM}: exercising regularly with known {named} disease: continue moderate work; "
            "medical clearance before vigorous work"
        )
    elif not active and not cleared:  # convention: unanswered takes the cautious cell
        out.clearance_before_exercise = out.no_training = out.refer_gp = True
        out.reasons.append(
            f"{ACSM_STOP[active is None]}, with known {named} disease: medical clearance "
            "before any exercise, then start at light-to-moderate intensity"
        )
    elif not active and not screening.get("vigorous_reviewed"):
        out.review_before_vigorous = True
        out.reasons.append(
            f"{ACSM}: cleared after known {named} disease: start at light-to-moderate intensity "
            "and build up; vigorous work after a review"
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
        if profile.has_condition(HYPERTENSION) or profile.has_medication(BP_MEDICATION):
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
            f"change, neurological symptoms or breathlessness){NO_TRAINING_NO_DEFICIT}"
        )
    elif systolic >= BP_NO_TRAINING_SYSTOLIC:
        out.no_training = out.refer_gp = True
        out.reasons.append(
            f"{BP}: {reading}, no training until reviewed by a GP{NO_TRAINING_NO_DEFICIT}"
        )
    elif systolic >= BP_GP_REVIEW[0] or diastolic >= BP_GP_REVIEW[1]:
        out.cap_moderate = out.refer_gp = out.hold_progression = True
        out.reasons.append(
            f"{BP}: {reading}, GP review before starting or progressing; "
            "light-to-moderate work only until BP is controlled"
        )
    elif systolic >= BP_MODERATE_SYSTOLIC:
        out.cap_moderate = out.refer_gp = True
        out.reasons.append(f"{BP}: {reading}, moderate intensity and a GP check")
