"""Print a saved menu as a PDF: the week at a glance, each dish once, shopping list.

Needs the optional `pdf` extra (reportlab): `uv sync --extra pdf`. The text comes from the saved
menu and `coach shopping`; nothing is computed here. The file goes to the data directory, because
recipes are the client's own and come from the web (see `coach.recipes`).
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from urllib.parse import urlsplit
from xml.sax.saxutils import escape

from coach.foods import Food, find

INSTALL = "PDF export needs the optional reportlab package: run `uv sync --extra pdf`"
# convention: the look of the printout. A4, 8-9 pt text and 1.8 cm QR codes, to fit a week on a
# few sheets and scan from paper or a phone screen; a deep green for titles and one colour per meal
# (in the order the meals first appear), with its light tint behind that meal's rows and cards.
QR_CM = 1.8
PRIMARY = "#1F4E45"
INK = "#26302D"
MUTED = "#6B726F"
RULE = "#E2E0D8"
PAPER = "#F6F5F0"
MEAL_COLOURS = ("#C9821A", "#5E8C31", "#C4553D", "#2A7F8E", "#4A4E9A", "#8E4A7E")
DASH = "–"  # en dash between the first and last date
LABELS = {
    "es": {
        "menu": "Menú",
        "tupper": "tupper",
        "free": "comida libre",
        "free_left": "quedan para llegar al objetivo",
        "seasoning": "Para aliñar",
        "totals": "Total del día",
        "protein": "proteína",
        "carbs": "hidratos",
        "fat": "grasa",
        "fibre": "fibra",
        "no_data": "sin dato en",
        "shopping": "Lista de la compra",
        "batches": "Tandas a cocinar",
        "servings": "raciones",
        "any_chain": "Cualquier tienda",
        "left_over": "sobran {n} raciones",
        "pantry": "En casa (no se compra)",
        "source": "Receta original",
        "page": "Página",
        "daily_target": "Objetivo diario",
        "quick": "Platos rápidos",
        "dish": "Plato",
        "ingredients": "Ingredientes",
        "one_serving": "1 ración",
        "method": "Preparación",
        "on_days": "Días",
        "recipes": "Recetas",
        "batch_short": "tanda de {n} raciones",
        "date": "{d} de {m} de {y}",
        "day_month": "{d} de {m}",
        "days": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"],
        "months": [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
        ],
    },
    "en": {
        "menu": "Menu",
        "tupper": "lunchbox",
        "free": "free meal",
        "free_left": "left to reach the target",
        "seasoning": "Seasoning",
        "totals": "Day total",
        "protein": "protein",
        "carbs": "carbs",
        "fat": "fat",
        "fibre": "fibre",
        "no_data": "no data for",
        "shopping": "Shopping list",
        "batches": "Batches to cook",
        "servings": "servings",
        "any_chain": "Any store",
        "left_over": "{n} servings left over",
        "pantry": "At home (not bought)",
        "source": "Original recipe",
        "page": "Page",
        "daily_target": "Daily target",
        "quick": "Quick dishes",
        "dish": "Dish",
        "ingredients": "Ingredients",
        "one_serving": "1 serving",
        "method": "Method",
        "on_days": "Days",
        "recipes": "Recipes",
        "batch_short": "batch of {n} servings",
        "date": "{d} {m} {y}",
        "day_month": "{d} {m}",
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "months": [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ],
    },
}


def _text(value) -> str:
    """Markup-safe text that the PDF's built-in Latin-1 font can draw."""
    cleaned = str(value).encode("cp1252", "replace").decode("cp1252")
    return escape(cleaned)


def _number(value, comma: bool) -> str:
    text = f"{float(value):.2f}".rstrip("0").rstrip(".")
    return text.replace(".", ",") if comma else text


def _label(name: str, table: list[Food], language: str) -> str:
    """The food's name in the client's language; a catalogue barcode becomes the product's name."""
    food = find(name, table)
    return (food.name_en if language == "en" else food.name_es) if food else name


def _quantity(amount, comma: bool) -> str:
    return f"{_number(amount, comma)} {getattr(amount, 'unit', 'g')}"


def _date_range(first: date, last: date, words: dict) -> str:
    """'2 – 8 de noviembre de 2026', naming the month and year only where they change."""

    def full(day: date) -> str:
        return words["date"].format(d=day.day, m=words["months"][day.month - 1], y=day.year)

    if first == last:
        return full(last)
    if (first.year, first.month) == (last.year, last.month):
        start = str(first.day)
    elif first.year == last.year:
        start = words["day_month"].format(d=first.day, m=words["months"][first.month - 1])
    else:
        start = full(first)
    return f"{start} {DASH} {full(last)}"


def web_link(source: str) -> str | None:
    """`source` when it is an http or https address with a host, else None."""
    source = source.strip()
    parts = urlsplit(source)
    return source if parts.scheme in ("http", "https") and parts.hostname else None


def write(
    path: Path,
    document: dict,
    days: list,
    table: list[Food],
    shopping: dict,
    language: str | None,
    qr: bool = True,
) -> None:
    """Write the PDF; raises ValueError naming the extra to install when reportlab is missing.

    Page one is the week at a glance; then each dish once, however many days it is eaten, grouped
    by meal: quick dishes (no steps, no source) in one table, recipes as cards with their steps and
    source; then the shopping list with a box to tick per line.
    """
    try:
        from reportlab.graphics.barcode.qr import QrCodeWidget
        from reportlab.graphics.shapes import Drawing, Rect
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            KeepTogether,
            PageBreak,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ImportError:
        raise ValueError(INSTALL) from None

    language = language if language in LABELS else "es"
    words = LABELS[language]
    comma = language == "es"
    width = A4[0] - 4 * cm - 12  # 2 cm margins, less the frame's 6 pt padding on each side

    def colour(hex_code: str):
        return colors.HexColor(hex_code)

    def tint(hex_code: str, amount: float = 0.86):
        """The colour mixed with white: 0 is the colour, 1 is white."""
        base = colour(hex_code)
        return colors.Color(*(c + (1 - c) * amount for c in (base.red, base.green, base.blue)))

    def style(name: str, **options) -> ParagraphStyle:
        defaults = {"fontName": "Helvetica", "fontSize": 8, "leading": 10.5, "textColor": INK}
        return ParagraphStyle(name, **{**defaults, **options})

    body = style("body", fontSize=9, leading=12)
    cell = style("cell")
    muted = style("muted", textColor=colour(MUTED))
    tiny = style("tiny", fontSize=7, leading=9, textColor=colour(MUTED))
    on_dark = style("on_dark", fontName="Helvetica-Bold", textColor=colors.white)
    section = style(
        "section",
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=colour(PRIMARY),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=1,
    )
    card_title = style("card_title", fontName="Helvetica-Bold", fontSize=10.5, leading=13)
    step_style = style("step", leading=10.5, spaceAfter=2.5)

    def heading(text: str):
        return Paragraph(_text(text), section)

    def meal_heading(text: str, hex_code: str):
        return Paragraph(
            _text(text),
            style(
                f"meal-{hex_code}",
                fontName="Helvetica-Bold",
                fontSize=11,
                leading=14,
                textColor=colour(hex_code),
                spaceBefore=8,
                spaceAfter=5,
                keepWithNext=1,
            ),
        )

    def qr_code(url: str):
        widget = QrCodeWidget(url, barFillColor=colour(INK))
        x0, y0, x1, y1 = widget.getBounds()
        size = QR_CM * cm
        drawing = Drawing(size, size, transform=[size / (x1 - x0), 0, 0, size / (y1 - y0), 0, 0])
        drawing.add(widget)
        return drawing

    def tick_box():
        drawing = Drawing(8, 8)
        drawing.add(Rect(0, 0, 8, 8, strokeColor=colour(MUTED), fillColor=None, strokeWidth=0.7))
        return drawing

    def short(day: date) -> str:
        return f"{words['days'][day.weekday()][:3]} {day.day}"

    first, last = days[0].date, days[-1].date
    dates = _date_range(first, last, words)
    saved_days = document["days"]
    targets = document.get("targets") or {}

    meal_names: list[str] = []
    for day in days:
        for meal in day.meals:
            if meal.name not in meal_names:
                meal_names.append(meal.name)
    meal_colour = {name: MEAL_COLOURS[i % len(MEAL_COLOURS)] for i, name in enumerate(meal_names)}

    # Banner: the dates and the daily target.
    goal = [
        (f"{_number(targets[key], comma)}{unit}", label)
        for key, label, unit in (
            ("kcal", "kcal", ""),
            ("protein_g", words["protein"], " g"),
            ("fibre_g", words["fibre"], " g"),
        )
        if key in targets
    ]
    light = style("light", fontSize=8, leading=10, textColor=tint(PRIMARY, 0.7))
    banner_rows = [
        [Paragraph(words["menu"].upper(), light)],
        [
            Paragraph(
                _text(dates),
                style(
                    "dates",
                    fontName="Helvetica-Bold",
                    fontSize=20,
                    leading=24,
                    textColor=colors.white,
                ),
            )
        ],
    ]
    if goal:
        pill = style("pill", textColor=colors.white)
        pills = Table(
            [
                [
                    Paragraph(
                        f"<b>{_text(value)}</b> {_text(label)}",
                        pill,
                    )
                    for value, label in goal
                ]
            ],
            colWidths=[3.8 * cm] * len(goal),
            hAlign="LEFT",
        )
        pills.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), tint(PRIMARY, 0.18)),
                    ("LINEAFTER", (0, 0), (-2, -1), 3, colour(PRIMARY)),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        banner_rows += [[Paragraph(words["daily_target"], light)], [pills]]
    banner = Table(banner_rows, colWidths=[width])
    banner.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colour(PRIMARY)),
                ("ROUNDEDCORNERS", [8, 8, 8, 8]),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (-1, 0), 12),
                ("TOPPADDING", (0, 1), (-1, -1), 1),
                ("BOTTOMPADDING", (0, -1), (-1, -1), 14),
            ]
        )
    )
    story = [banner, Spacer(1, 12)]

    # Week at a glance: a row per day, a column per meal in its colour.
    rows = [
        [Paragraph("", on_dark)]
        + [Paragraph(_text(name), on_dark) for name in meal_names]
        + [Paragraph(words["totals"], on_dark)]
    ]
    missing: dict[str, list[str]] = {}
    for day, entry in zip(days, saved_days, strict=True):
        free_left = (entry.get("free_meal") or {}).get("budget", {}).get("kcal")
        row = [Paragraph(f'<font color="{PRIMARY}"><b>{short(day.date)}</b></font>', cell)]
        for name in meal_names:
            parts = []
            for meal in (m for m in day.meals if m.name == name):
                if meal.free:
                    text = f"<i>{words['free']}</i>"
                    if free_left is not None:
                        text += f", {_number(free_left, comma)} kcal {words['free_left']}"
                else:
                    text = "<br/>".join(_text(dish.name) for dish in meal.dishes)
                if meal.tupper:
                    text += (
                        f'<br/><font size="6.5" color="{meal_colour[name]}">'
                        f"&bull; {words['tupper']}</font>"
                    )
                parts.append(text)
            row.append(Paragraph("<br/>".join(parts), cell))
        totals = entry.get("totals")
        if totals:
            row.append(
                Paragraph(
                    f"<b>{_number(totals['kcal'], comma)}</b> kcal<br/>"
                    f'<font size="7" color="{MUTED}">'
                    f"{_number(totals['protein_g'], comma)} g {words['protein']}<br/>"
                    f"{_number(totals['fibre_g'], comma)} g {words['fibre']}</font>",
                    cell,
                )
            )
            for key, names in (totals.get("missing") or {}).items():
                for name in names:
                    label = _label(str(name), table, language)
                    if label not in missing.setdefault(key, []):
                        missing[key].append(label)
        else:
            row.append("")
        rows.append(row)
    side = 1.3 * cm, 2.6 * cm
    meal_width = (width - sum(side)) / max(len(meal_names), 1)
    week = Table(
        rows, colWidths=[side[0]] + [meal_width] * len(meal_names) + [side[1]], repeatRows=1
    )
    week_style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (0, 0), (0, 0), colour(PRIMARY)),
        ("BACKGROUND", (-1, 0), (-1, 0), colour(PRIMARY)),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, colour(RULE)),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]
    for i, name in enumerate(meal_names, 1):
        week_style.append(("BACKGROUND", (i, 0), (i, 0), colour(meal_colour[name])))
    for r in range(2, len(rows), 2):
        week_style.append(("BACKGROUND", (0, r), (-1, r), colour(PAPER)))
    week.setStyle(TableStyle(week_style))
    story.append(week)
    nutrients = {
        "protein_g": words["protein"],
        "carbs_g": words["carbs"],
        "fat_g": words["fat"],
        "fibre_g": words["fibre"],
    }
    if missing:
        story.append(Spacer(1, 4))
    for key, labels in missing.items():
        nutrient = nutrients.get(key, key)
        story.append(Paragraph(_text(f"{nutrient}, {words['no_data']}: {', '.join(labels)}"), tiny))

    # Each dish once, with the days it is eaten, under the meal it first appears in.
    groups: dict[tuple, dict] = {}
    for day, entry in zip(days, saved_days, strict=True):
        for meal, raw_meal in zip(day.meals, entry["meals"], strict=True):
            for dish, raw in zip(meal.dishes, raw_meal.get("dishes") or [], strict=True):
                steps = tuple(str(step) for step in raw.get("steps") or [])
                source = str(raw.get("source") or "").strip()
                key = (
                    dish.name,
                    dish.servings,
                    tuple(dish.items),
                    tuple(dish.seasoning),
                    steps,
                    source,
                )
                group = groups.setdefault(
                    key,
                    {
                        "dish": dish,
                        "meal": meal.name,
                        "steps": steps,
                        "source": source,
                        "dates": [],
                    },
                )
                if day.date not in group["dates"]:
                    group["dates"].append(day.date)

    def by_meal(selected: list[dict]) -> list[tuple[str, list[dict]]]:
        return [
            (name, [g for g in selected if g["meal"] == name])
            for name in meal_names
            if any(g["meal"] == name for g in selected)
        ]

    def on_days(group) -> str:
        return ", ".join(short(d) for d in group["dates"])

    def seasoning(dish) -> str:
        if not dish.seasoning:
            return ""
        return (
            f'<font color="{MUTED}">{words["seasoning"]}: {_text(", ".join(dish.seasoning))}</font>'
        )

    quick = [g for g in groups.values() if not g["steps"] and not g["source"]]
    if quick:
        story.append(heading(words["quick"]))
        rows = [
            [
                Paragraph(words["dish"], on_dark),
                Paragraph(words["ingredients"], on_dark),
                Paragraph(words["on_days"], on_dark),
            ]
        ]
        quick_style = [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("BACKGROUND", (0, 0), (-1, 0), colour(PRIMARY)),
            ("ROUNDEDCORNERS", [6, 6, 6, 6]),
        ]
        for name, selected in by_meal(quick):
            hex_code = meal_colour[name]
            quick_style += [
                ("SPAN", (0, len(rows)), (-1, len(rows))),
                ("BACKGROUND", (0, len(rows)), (-1, len(rows)), tint(hex_code)),
            ]
            rows.append([Paragraph(f'<font color="{hex_code}"><b>{_text(name)}</b></font>', cell)])
            for group in selected:
                dish = group["dish"]
                name_cell = f"<b>{_text(dish.name)}</b>"
                if dish.seasoning:
                    name_cell += f"<br/>{seasoning(dish)}"
                items = " &nbsp;&middot;&nbsp; ".join(
                    f"{_text(_label(n, table, language))} <b>{_quantity(a, comma)}</b>"
                    for n, a in dish.items
                )
                quick_style.append(
                    ("LINEBELOW", (0, len(rows)), (-1, len(rows)), 0.4, colour(RULE))
                )
                rows.append(
                    [
                        Paragraph(name_cell, cell),
                        Paragraph(items, cell),
                        Paragraph(on_days(group), muted),
                    ]
                )
        grid = Table(rows, colWidths=[5.2 * cm, width - 8 * cm, 2.8 * cm], repeatRows=1)
        grid.setStyle(TableStyle(quick_style))
        story.append(grid)

    recipes = [g for g in groups.values() if g["steps"] or g["source"]]
    pending: list = []  # headings and the batches table, kept on the page of the next card
    if recipes:
        pending.append(heading(words["recipes"]))
    # only dishes with a recipe are cooked; a fruit bowl or a shake eaten on several days is not
    cooked = {group["dish"].name for group in recipes}
    batches = [batch for batch in shopping["batches"] if batch["dish"] in cooked]
    if batches:
        rows = []
        for batch in batches:
            note = words["left_over"].format(n=batch["left_over"]) if batch["left_over"] else ""
            rows.append(
                [
                    Paragraph(f"<b>{_text(batch['dish'])}</b>", cell),
                    Paragraph(f"{batch['servings']} {words['servings']}", cell),
                    Paragraph(_text(note), muted),
                ]
            )
        grid = Table(rows, colWidths=[width - 6 * cm, 2.6 * cm, 3.4 * cm])
        grid.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colour(PAPER)),
                    ("ROUNDEDCORNERS", [6, 6, 6, 6]),
                    ("LINEBELOW", (0, 0), (-1, -2), 0.4, colour(RULE)),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        pending += [meal_heading(words["batches"], PRIMARY), grid, Spacer(1, 4)]
    for name, selected in by_meal(recipes):
        hex_code = meal_colour[name]
        pending.append(meal_heading(name, hex_code))
        for group in selected:
            dish, source = group["dish"], group["source"]
            meta = f"{words['on_days']}: {on_days(group)}"
            if dish.servings > 1:
                meta += " &nbsp;&middot;&nbsp; " + words["batch_short"].format(n=dish.servings)
            head = [
                Paragraph(_text(dish.name), card_title),
                Paragraph(meta, muted),
            ]
            ingredients = [
                Paragraph(
                    f'<font color="{hex_code}"><b>{words["ingredients"].upper()}</b></font>'
                    f" &nbsp;{words['one_serving']}",
                    tiny,
                ),
                Spacer(1, 3),
            ] + [
                Paragraph(
                    f"<b>{_quantity(a, comma)}</b>&nbsp; {_text(_label(n, table, language))}", cell
                )
                for n, a in dish.items
            ]
            if dish.seasoning:
                ingredients += [Spacer(1, 3), Paragraph(seasoning(dish), tiny)]
            method = []
            if group["steps"]:
                method = [
                    Paragraph(
                        f'<font color="{hex_code}"><b>{words["method"].upper()}</b></font>', tiny
                    ),
                    Spacer(1, 3),
                ] + [
                    Paragraph(
                        f'<font color="{hex_code}"><b>{n}</b></font>&nbsp;&nbsp; {_text(step)}',
                        step_style,
                    )
                    for n, step in enumerate(group["steps"], 1)
                ]
            url = web_link(source)
            show_qr = bool(qr and url)
            qr_width = (QR_CM + 0.5) * cm if show_qr else 0
            # a recipe with a source but no steps gives the method column to the ingredients
            text_widths = [5.4 * cm, width - 5.4 * cm - qr_width] if method else [width - qr_width]
            widths = text_widths + ([qr_width] if show_qr else [])
            columns = len(widths)
            content = (
                [ingredients] + ([method] if method else []) + ([qr_code(url)] if show_qr else [])
            )
            card_rows = [[head] + [""] * (columns - 1), content]
            if url:
                link = (
                    f'{words["source"]}: <link href="{escape(url, {chr(34): "&quot;"})}" '
                    f'color="{PRIMARY}">{_text(url)}</link>'
                )
            elif source:  # not a web address: text only, no link or QR code
                link = f"{words['source']}: {_text(source)}"
            else:
                link = ""
            if link:
                card_rows.append([Paragraph(link, tiny)] + [""] * (columns - 1))
            card = Table(card_rows, colWidths=widths, splitInRow=1)
            card_style = [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("SPAN", (0, 0), (-1, 0)),
                ("BACKGROUND", (0, 0), (-1, 0), tint(hex_code)),
                ("BACKGROUND", (0, 1), (0, 1), colour(PAPER)),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("BOX", (0, 0), (-1, -1), 0.5, colour(RULE)),
                ("LINEABOVE", (0, 0), (-1, 0), 2.5, colour(hex_code)),
            ]
            if link:
                card_style += [
                    ("SPAN", (0, -1), (-1, -1)),
                    ("LINEABOVE", (0, -1), (-1, -1), 0.4, colour(RULE)),
                ]
            card.setStyle(TableStyle(card_style))
            story.append(KeepTogether([*pending, card, Spacer(1, 8)]))
            pending = []

    # Shopping list on its own page, a box to tick per line.
    story.append(PageBreak())
    title = Table(
        [
            [
                Paragraph(
                    words["shopping"],
                    style(
                        "shop",
                        fontName="Helvetica-Bold",
                        fontSize=17,
                        leading=21,
                        textColor=colors.white,
                    ),
                )
            ],
            [Paragraph(_text(dates), light)],
        ],
        colWidths=[width],
    )
    title.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colour(PRIMARY)),
                ("ROUNDEDCORNERS", [8, 8, 8, 8]),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
            ]
        )
    )
    story.append(title)
    for chain, lines in shopping["chains"].items():
        story.append(heading(words["any_chain"] if chain == "any" else chain))
        amount = style("amount", alignment=2)
        entries = [
            (
                tick_box(),
                Paragraph(_text(line["name"]), cell),
                Paragraph(
                    f"<b>{_number(line.get('grams', line.get('ml')), comma)} "
                    f"{'g' if 'grams' in line else 'ml'}</b>",
                    amount,
                ),
            )
            for line in lines
        ]
        half = (len(entries) + 1) // 2  # two columns: first half left, second half right
        rows = [
            [*entries[i], "", *(entries[i + half] if i + half < len(entries) else ("", "", ""))]
            for i in range(half)
        ]
        column = [0.55 * cm, 5.1 * cm, 1.9 * cm]
        grid = Table(rows, colWidths=[*column, 0.7 * cm, *column], hAlign="LEFT")
        right = len(entries) - half  # rows with an entry in the right column
        grid.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("LINEBELOW", (0, 0), (2, -1), 0.4, colour(RULE)),
                ]
                + ([("LINEBELOW", (4, 0), (6, right - 1), 0.4, colour(RULE))] if right else [])
            )
        )
        story.append(grid)
    if shopping["pantry_skipped"]:
        story.append(heading(words["pantry"]))
        story.append(Paragraph(_text(", ".join(shopping["pantry_skipped"])), body))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colour(RULE))
        canvas.setLineWidth(0.5)
        canvas.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
        canvas.setFillColor(colour(MUTED))
        canvas.setFont("Helvetica", 7.5)
        canvas.drawString(2 * cm, 1.1 * cm, f"{words['menu']} · {dates}")
        canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"{words['page']} {doc.page}")
        canvas.restoreState()

    path.parent.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.6 * cm,
        bottomMargin=2 * cm,
        pageCompression=0,
        title=f"{words['menu']} {dates}",
        creator="ai-personal-coach",
    ).build(story, onFirstPage=footer, onLaterPages=footer)


def default_name(first: date) -> str:
    return f"{first.isoformat()}.pdf"
