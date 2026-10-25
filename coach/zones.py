"""Heart-rate and effort zones (ACSM 2011), with the overrides that replace HR with RPE."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from coach import safety
from coach.profile import BETA_BLOCKER, HEART_DISEASE, PREGNANT, Profile
from coach.safety import PREGNANCY_INTENSITY, SafetyFlags

BANDS_RULE = 'cardio-health.md: "ACSM intensity bands"'
HRMAX_RULE = 'cardio-health.md: "HRmax: formulas and setting the anchor"'
BETA_RULE = 'cardio-health.md: "RPE as the anchor under beta-blockade"'
PREGNANCY_VIGOROUS_RULE = 'recovery-habits.md: "Vigorous work: avoid near-maximal efforts"'

# Flag reasons that explain why zones are RPE-only.
RPE_REASON_RULES = (safety.BETA_BLOCKER_RULE, safety.PREGNANCY_INTENSITY)

# cardio-health.md: "HRmax: formulas and setting the anchor": Tanaka 208 - 0.7 x age.
TANAKA_INTERCEPT, TANAKA_SLOPE = 208, 0.7

# cardio-health.md: "ACSM intensity bands" (Garber 2011, Table 5): %HRR, %HRmax, Borg RPE 6-20.
# The vigorous HRR band stops at 84%, not 89%: the rule's labelled convention that keeps it
# inside both the 2011 and the GETP 10th-edition tables.
ACSM_BANDS = {
    "light": {"hrr": (0.30, 0.39), "hrmax": (0.57, 0.63), "rpe": (9, 11)},
    "moderate": {"hrr": (0.40, 0.59), "hrmax": (0.64, 0.76), "rpe": (12, 13)},
    "vigorous": {"hrr": (0.60, 0.84), "hrmax": (0.77, 0.95), "rpe": (14, 17)},
}
# cardio-health.md: "0-10 effort scale and talk-test anchors": moderate can talk but not sing;
# vigorous only a few words without pausing. convention: "light" = can talk and sing.
TALK_TEST = {
    "light": "can talk and sing",
    "moderate": "can talk, but not sing",
    "vigorous": "only a few words without pausing for breath",
}
# recovery-habits.md: "Gauge intensity by talk test and RPE, not a heart-rate cap": moderate is
# RPE 13-14 in pregnancy (the source's number). "Vigorous work: avoid near-maximal efforts":
# never RPE 18 or more. convention: light runs up to that moderate band (9-12) and vigorous
# spans the rest of the ACSM vigorous band (15-17).
PREGNANCY_RPE = {"light": (9, 12), "moderate": (13, 14), "vigorous": (15, 17)}

# cardio-health.md: "RPE as the anchor under beta-blockade": no sustained vigorous work (RPE 14
# or more) without medical clearance, so every band stops at 13.
BETA_BLOCKER_MAX_RPE = 13

# Plausibility limits for typed-in heart rates (convention: input validation, not coaching).
HR_REST_RANGE = (30, 120)
HR_MAX_RANGE = (100, 230)


@dataclass
class Zone:
    name: str
    rpe: tuple[int, int]
    talk_test: str
    bpm: tuple[int, int] | None = None


@dataclass
class Zones:
    method: str  # hrr | hrmax | rpe | cardiac_team
    zones: list[Zone]
    hr_max: int | None = None
    hr_max_source: str | None = None  # measured | tanaka
    hr_rest: int | None = None
    notes: list[str] = field(default_factory=list)


def tanaka(age: int) -> float:
    return TANAKA_INTERCEPT - TANAKA_SLOPE * age


def _check(value: int | None, limits: tuple[int, int], name: str) -> None:
    if value is not None and not limits[0] <= value <= limits[1]:
        raise ValueError(f"{name} {value} bpm is outside {limits[0]}-{limits[1]}")


def _rpe_zones(names: list[str], rpe: dict[str, tuple[int, int]]) -> list[Zone]:
    return [Zone(name, rpe[name], TALK_TEST[name]) for name in names]


def _hr_zones(
    profile: Profile,
    flags: SafetyFlags,
    hr_rest: int | None = None,
    hr_max: int | None = None,
    today: date | None = None,
) -> Zones:
    _check(hr_rest, HR_REST_RANGE, "resting HR")
    _check(hr_max, HR_MAX_RANGE, "HRmax")

    if flags.no_training:
        return Zones(
            method="no_training",
            zones=[],
            notes=[r for r in flags.reasons if r.startswith((safety.CARDIAC, safety.BP))],
        )

    if profile.has_condition(HEART_DISEASE):
        return Zones(
            method="cardiac_team",
            zones=[],
            notes=[f"{BANDS_RULE}: with known heart disease, use the zones the cardiac team sets"],
        )

    if flags.use_rpe_not_hr:
        notes = [r for r in flags.reasons if r.startswith(RPE_REASON_RULES)]
        rpe = {name: band["rpe"] for name, band in ACSM_BANDS.items()}
        names = list(ACSM_BANDS)
        if profile.has_condition(PREGNANT):
            rpe = PREGNANCY_RPE
            notes += [
                f"{PREGNANCY_INTENSITY}: moderate is RPE 13-14 or talk but not sing; "
                "HR is secondary",
                f"{PREGNANCY_VIGOROUS_RULE}: vigorous only if already vigorously active "
                "before pregnancy; never RPE 18 or more",
            ]
        if profile.has_medication(BETA_BLOCKER):
            names = ["light", "moderate"]
            rpe = {n: (low, min(high, BETA_BLOCKER_MAX_RPE)) for n, (low, high) in rpe.items()}
            notes.append(
                f"{BETA_RULE}: no sustained vigorous work (RPE 14 or more) without medical "
                "clearance; start at the low end of moderate"
            )
        return Zones("rpe", _rpe_zones(names, rpe), notes=notes)

    if hr_max is not None:
        source, peak = "measured", hr_max
    else:
        source, peak = "tanaka", round(tanaka(profile.age(today)))
    if hr_rest is not None and hr_rest >= peak:
        raise ValueError(f"resting HR {hr_rest} must be below HRmax {peak}")

    notes = [f"{BANDS_RULE}: zones are approximate; check them against RPE and the talk test"]
    if source == "tanaka":
        notes.append(
            f"{HRMAX_RULE}: HRmax from Tanaka is a rough start and can be off by 20+ bpm; "
            "use an observed all-out peak when you have one"
        )
    zones = []
    for name, band in ACSM_BANDS.items():
        if hr_rest is not None:
            low, high = (hr_rest + p * (peak - hr_rest) for p in band["hrr"])
        else:
            low, high = (p * peak for p in band["hrmax"])
        zones.append(Zone(name, band["rpe"], TALK_TEST[name], (round(low), round(high))))
    return Zones(
        method="hrr" if hr_rest is not None else "hrmax",
        zones=zones,
        hr_max=peak,
        hr_max_source=source,
        hr_rest=hr_rest,
        notes=notes,
    )


def hr_zones(
    profile: Profile,
    flags: SafetyFlags,
    hr_rest: int | None = None,
    hr_max: int | None = None,
    today: date | None = None,
) -> Zones:
    result = _hr_zones(profile, flags, hr_rest, hr_max, today)
    # Each cap removes the vigorous zone and says which rule did it.
    caps = {safety.BP: flags.cap_moderate, safety.PARQ_THRESHOLDS: flags.review_before_vigorous}
    rules = tuple(rule for rule, on in caps.items() if on)
    if rules and result.zones:
        result.zones = [z for z in result.zones if z.name != "vigorous"]
        result.notes += [r for r in flags.reasons if r.startswith(rules)]
    return result
