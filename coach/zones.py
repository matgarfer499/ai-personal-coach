"""Heart-rate and effort zones (ACSM 2011), with the overrides that replace HR with RPE."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from coach import safety
from coach.profile import (
    BETA_BLOCKER,
    HEART_DISEASE,
    HR_MAX_RANGE,
    HR_REST_RANGE,
    PREGNANT,
    Profile,
)
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
# Very light is below 30% HRR, 57% HRmax and RPE 9; near-maximal is 90% HRR, 96% HRmax and RPE 18
# or more. The vigorous HRR band stops at 84%, not 89%, so near-maximal starts at 85%: the rule's
# labelled convention that keeps both inside the 2011 and the GETP 10th-edition tables. The open
# ends are the scales' own: 0% HRR (resting HR) or 0% HRmax, 100%, and Borg 6 and 20.
ACSM_BANDS = {
    "very_light": {"hrr": (0.0, 0.29), "hrmax": (0.0, 0.56), "rpe": (6, 8)},
    "light": {"hrr": (0.30, 0.39), "hrmax": (0.57, 0.63), "rpe": (9, 11)},
    "moderate": {"hrr": (0.40, 0.59), "hrmax": (0.64, 0.76), "rpe": (12, 13)},
    "vigorous": {"hrr": (0.60, 0.84), "hrmax": (0.77, 0.95), "rpe": (14, 17)},
    "near_maximal": {"hrr": (0.85, 1.0), "hrmax": (0.96, 1.0), "rpe": (18, 20)},
}
# The zones the caps hide: cap_moderate and review_before_vigorous allow neither.
ABOVE_MODERATE = ("vigorous", "near_maximal")
# The RPE-only paths (beta-blocker, pregnancy) keep the three bands their rules speak to.
RPE_ONLY_ZONES = ("light", "moderate", "vigorous")
# cardio-health.md: "0-10 effort scale and talk-test anchors": moderate can talk but not sing;
# vigorous only a few words without pausing. convention: "very_light" = can talk and sing with
# ease, "light" = can talk and sing, "near_maximal" = cannot speak; the rule gives no text.
TALK_TEST = {
    "very_light": "can talk and sing with ease",
    "light": "can talk and sing",
    "moderate": "can talk, but not sing",
    "vigorous": "only a few words without pausing for breath",
    "near_maximal": "cannot speak",
}
# The same cardio-health.md: "0-10 effort scale and talk-test anchors" wording, in Spanish.
TALK_TEST_ES = {
    "very_light": "puedes hablar y cantar sin esfuerzo",
    "light": "puedes hablar y cantar",
    "moderate": "puedes hablar, pero no cantar",
    "vigorous": "solo unas palabras sin parar a respirar",
    "near_maximal": "no puedes hablar",
}
# recovery-habits.md: "Gauge intensity by talk test and RPE, not a heart-rate cap": moderate is
# RPE 13-14 in pregnancy (the source's number). "Vigorous work: avoid near-maximal efforts":
# never RPE 18 or more. convention: light runs up to that moderate band (9-12) and vigorous
# spans the rest of the ACSM vigorous band (15-17).
PREGNANCY_RPE = {"light": (9, 12), "moderate": (13, 14), "vigorous": (15, 17)}

# cardio-health.md: "RPE as the anchor under beta-blockade": no sustained vigorous work (RPE 14
# or more) without medical clearance, so every band stops at 13.
BETA_BLOCKER_MAX_RPE = 13


@dataclass
class Zone:
    name: str
    rpe: tuple[int, int]
    talk_test: str
    bpm: tuple[int | None, int] | None = None  # a None floor: no lower limit


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


def all_zones(
    profile: Profile,
    flags: SafetyFlags,
    hr_rest: int | None = None,
    hr_max: int | None = None,
    today: date | None = None,
) -> Zones:
    """Every zone the method allows, before the intensity caps. Only for describing logged
    runs (`coach runs week`); prescribe from `hr_zones`, which applies the caps."""
    _check(hr_rest, HR_REST_RANGE, "resting HR")
    _check(hr_max, HR_MAX_RANGE, "HRmax")

    if flags.no_training:
        return Zones(
            method="no_training",
            zones=[],
            notes=safety.stop_reasons(flags),
        )

    if profile.has_condition(HEART_DISEASE):
        return Zones(
            method="cardiac_team",
            zones=[],
            notes=[f"{BANDS_RULE}: with known heart disease, use the zones the cardiac team sets"],
        )

    if flags.use_rpe_not_hr:
        notes = [r for r in flags.reasons if r.startswith(RPE_REASON_RULES)]
        rpe = {name: ACSM_BANDS[name]["rpe"] for name in RPE_ONLY_ZONES}
        names = list(RPE_ONLY_ZONES)
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
        # %HRmax has no floor for very light: print only its top ("under 107"), not "0 bpm".
        floor = None if low == 0 else round(low)
        zones.append(Zone(name, band["rpe"], TALK_TEST[name], (floor, round(high))))
    # convention: printed bands are whole bpm, so each zone runs up to one below the next one's
    # floor; rounding the rule's percentages separately left a 1-2 bpm gap between bands.
    for zone, above in zip(zones, zones[1:], strict=False):
        zone.bpm = (zone.bpm[0], above.bpm[0] - 1)
    return Zones(
        method="hrr" if hr_rest is not None else "hrmax",
        zones=zones,
        hr_max=peak,
        hr_max_source=source,
        hr_rest=hr_rest,
        notes=notes,
    )


def zone_for(zones: list[Zone], hr: float) -> Zone | None:
    """The bpm zone a heart rate falls in: the highest zone starting at or below it, so the
    1 bpm gaps rounding leaves between bands, and rates above HRmax, still land in one. The
    lowest zone has no floor here: an average under resting HR is still very light."""
    bpm = [z for z in zones if z.bpm]
    return next((z for z in reversed(bpm[1:]) if z.bpm[0] <= hr), bpm[0] if bpm else None)


def hr_zones(
    profile: Profile,
    flags: SafetyFlags,
    hr_rest: int | None = None,
    hr_max: int | None = None,
    today: date | None = None,
) -> Zones:
    result = all_zones(profile, flags, hr_rest, hr_max, today)
    # Each cap removes the vigorous and near-maximal zones and says which rule did it.
    rules = ((safety.BP,) if flags.cap_moderate else ()) + (
        safety.VIGOROUS_CAPS if flags.review_before_vigorous else ()
    )
    if rules and result.zones:
        result.zones = [z for z in result.zones if z.name not in ABOVE_MODERATE]
        result.notes += [r for r in flags.reasons if r.startswith(rules)]
    if profile.language == "es":  # the talk test is shown to the client as is
        for zone in result.zones:
            zone.talk_test = TALK_TEST_ES[zone.name]
    return result
