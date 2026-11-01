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
# convention: the page and type sizes of the printout (A4, 9 pt text, 1.8 cm QR codes), chosen to
# fit a week on a few sheets and to scan from paper or a phone screen.
QR_CM = 1.8
LABELS = {
    "es": {
        "menu": "Menú",
        "to": "a",
        "tupper": "tupper",
        "free": "comida libre",
        "free_left": "quedan para llegar al objetivo",
        "seasoning": "Para aliñar",
        "totals": "Total del día",
        "target": "objetivo",
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
        "source": "Receta",
        "page": "Página",
        "daily_target": "Objetivo diario",
        "quick": "Platos rápidos",
        "dish": "Plato",
        "ingredients": "Ingredientes",
        "on_days": "Días",
        "recipes": "Recetas",
        "batch_short": "tanda de {n} raciones; cantidades por ración",
        "days": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"],
    },
    "en": {
        "menu": "Menu",
        "to": "to",
        "tupper": "lunchbox",
        "free": "free meal",
        "free_left": "left to reach the target",
        "seasoning": "Seasoning",
        "totals": "Day total",
        "target": "target",
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
        "source": "Recipe",
        "page": "Page",
        "daily_target": "Daily target",
        "quick": "Quick dishes",
        "dish": "Dish",
        "ingredients": "Ingredients",
        "on_days": "Days",
        "recipes": "Recipes",
        "batch_short": "batch of {n} servings; amounts per serving",
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
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


def _amount(name: str, amount, table: list[Food], language: str, comma: bool) -> str:
    unit = getattr(amount, "unit", "g")
    return f"{_label(name, table, language)} {_number(amount, comma)} {unit}"


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

    Page one is the week at a glance; then each dish once, however many days it is eaten: quick
    dishes (no steps, no source) in one table, recipes with their steps and source; then the
    shopping list.
    """
    try:
        from reportlab.graphics.barcode.qr import QrCodeWidget
        from reportlab.graphics.shapes import Drawing
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
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
    sheet = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=sheet["BodyText"], fontSize=9, leading=11.5)
    cell = ParagraphStyle("cell", parent=body, fontSize=8, leading=10)
    head = ParagraphStyle("head", parent=cell, fontName="Helvetica-Bold")
    small = ParagraphStyle("small", parent=cell, textColor=colors.grey)
    section = ParagraphStyle(
        "section", parent=sheet["Heading2"], spaceBefore=10, spaceAfter=6, keepWithNext=1
    )
    recipe_style = ParagraphStyle(
        "recipe", parent=body, fontName="Helvetica-Bold", fontSize=10.5, spaceBefore=8
    )
    width = A4[0] - 4 * cm - 12  # 2 cm margins, less the frame's 6 pt padding on each side
    grid_style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    header_style = [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEEEEE"))]

    def qr_code(url: str):
        widget = QrCodeWidget(url)
        x0, y0, x1, y1 = widget.getBounds()
        size = QR_CM * cm
        drawing = Drawing(size, size, transform=[size / (x1 - x0), 0, 0, size / (y1 - y0), 0, 0])
        drawing.add(widget)
        return drawing

    def short(day: date) -> str:
        return f"{words['days'][day.weekday()][:3]} {day.day}"

    first, last = days[0].date, days[-1].date
    saved_days = document["days"]
    targets = document.get("targets") or {}
    story = [Paragraph(f"{words['menu']} {first} {words['to']} {last}", sheet["Title"])]

    # Week at a glance: a row per day, a column per meal name in the order they first appear.
    meal_names: list[str] = []
    for day in days:
        for meal in day.meals:
            if meal.name not in meal_names:
                meal_names.append(meal.name)
    rows = [
        [Paragraph("", head)]
        + [Paragraph(_text(name), head) for name in meal_names]
        + [Paragraph(words["totals"], head)]
    ]
    missing: dict[str, list[str]] = {}
    for day, entry in zip(days, saved_days, strict=True):
        free_left = (entry.get("free_meal") or {}).get("budget", {}).get("kcal")
        row = [Paragraph(f"<b>{short(day.date)}</b>", cell)]
        for name in meal_names:
            parts = []
            for meal in (m for m in day.meals if m.name == name):
                if meal.free:
                    text = words["free"]
                    if free_left is not None:
                        text += f", {_number(free_left, comma)} kcal {words['free_left']}"
                else:
                    text = "<br/>".join(_text(dish.name) for dish in meal.dishes)
                if meal.tupper:
                    text += f' <font color="grey">({words["tupper"]})</font>'
                parts.append(text)
            row.append(Paragraph("<br/>".join(parts), cell))
        totals = entry.get("totals")
        if totals:
            row.append(
                Paragraph(
                    f"{_number(totals['kcal'], comma)} kcal<br/>"
                    f"{words['protein']} {_number(totals['protein_g'], comma)} g<br/>"
                    f"{words['fibre']} {_number(totals['fibre_g'], comma)} g",
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
    side = 1.3 * cm, 2.8 * cm
    meal_width = (width - sum(side)) / max(len(meal_names), 1)
    week = Table(
        rows, colWidths=[side[0]] + [meal_width] * len(meal_names) + [side[1]], repeatRows=1
    )
    week.setStyle(TableStyle(grid_style + header_style))
    story.append(week)
    goal = [
        f"{label} {_number(targets[key], comma)}{unit}"
        for key, label, unit in (
            ("kcal", "kcal", ""),
            ("protein_g", words["protein"], " g"),
            ("fibre_g", words["fibre"], " g"),
        )
        if key in targets
    ]
    if goal:
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<b>{words['daily_target']}</b>: {' · '.join(goal)}", small))
    nutrients = {
        "protein_g": words["protein"],
        "carbs_g": words["carbs"],
        "fat_g": words["fat"],
        "fibre_g": words["fibre"],
    }
    for key, labels in missing.items():
        nutrient = nutrients.get(key, key)
        story.append(
            Paragraph(_text(f"{nutrient}, {words['no_data']}: {', '.join(labels)}"), small)
        )

    # Each dish once, with the days it is eaten.
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
                    key, {"dish": dish, "steps": steps, "source": source, "dates": []}
                )
                if day.date not in group["dates"]:
                    group["dates"].append(day.date)

    def ingredients(dish, separator: str) -> str:
        return separator.join(
            _text(_amount(name, amount, table, language, comma)) for name, amount in dish.items
        )

    def seasoning(dish) -> str:
        if not dish.seasoning:
            return ""
        return (
            f"<br/><font color='grey'>{words['seasoning']}: "
            f"{_text(', '.join(dish.seasoning))}</font>"
        )

    def on_days(group) -> str:
        return ", ".join(short(d) for d in group["dates"])

    quick = [g for g in groups.values() if not g["steps"] and not g["source"]]
    if quick:
        story.append(Paragraph(words["quick"], section))
        rows = [
            [
                Paragraph(words["dish"], head),
                Paragraph(words["ingredients"], head),
                Paragraph(words["on_days"], head),
            ]
        ]
        for group in quick:
            dish = group["dish"]
            name = f"<b>{_text(dish.name)}</b>" + seasoning(dish)
            rows.append(
                [
                    Paragraph(name, cell),
                    Paragraph(ingredients(dish, " · "), cell),
                    Paragraph(on_days(group), cell),
                ]
            )
        grid = Table(rows, colWidths=[5.2 * cm, width - 8.2 * cm, 3 * cm], repeatRows=1)
        grid.setStyle(TableStyle(grid_style + header_style))
        story.append(grid)

    recipes = [g for g in groups.values() if g["steps"] or g["source"]]
    if recipes:
        story.append(Paragraph(words["recipes"], section))
    for group in recipes:
        dish, source = group["dish"], group["source"]
        meta = f"{words['on_days']}: {on_days(group)}"
        if dish.servings > 1:
            meta += " · " + words["batch_short"].format(n=dish.servings)
        left = ingredients(dish, "<br/>") + seasoning(dish)
        steps = "<br/>".join(f"{n}. {_text(step)}" for n, step in enumerate(group["steps"], 1))
        url = web_link(source)
        show_qr = bool(qr and url)
        qr_width = (QR_CM + 0.4) * cm if show_qr else 0
        row = [Paragraph(left, cell), Paragraph(steps, cell)]
        widths = [5.6 * cm, width - 5.6 * cm - qr_width]
        if show_qr:
            row.append(qr_code(url))
            widths.append(qr_width)
        # splitInRow: a recipe taller than a page splits instead of raising LayoutError
        layout = Table([row], colWidths=widths, splitInRow=1)
        layout.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (0, -1), 0),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ]
            )
        )
        parts = [
            Paragraph(_text(dish.name), recipe_style),
            Paragraph(meta, small),
            layout,
        ]
        if source and not url:  # not a web address: text only, no link or QR code
            parts.append(Paragraph(f"{words['source']}: {_text(source)}", small))
        if url:
            parts.append(
                Paragraph(
                    f'{words["source"]}: <link href="{escape(url, {chr(34): "&quot;"})}" '
                    f'color="blue">{_text(url)}</link>',
                    small,
                )
            )
        story.append(KeepTogether(parts))

    story.append(PageBreak())
    story.append(Paragraph(words["shopping"], sheet["Title"]))
    for chain, lines in shopping["chains"].items():
        story.append(Paragraph(_text(words["any_chain"] if chain == "any" else chain), section))
        entries = [
            (
                Paragraph(_text(line["name"]), cell),
                f"{_number(line.get('grams', line.get('ml')), comma)} "
                f"{'g' if 'grams' in line else 'ml'}",
            )
            for line in lines
        ]
        half = (len(entries) + 1) // 2  # two columns: first half left, second half right
        rows = [
            [*entries[i], "", *(entries[i + half] if i + half < len(entries) else ("", ""))]
            for i in range(half)
        ]
        grid = Table(rows, colWidths=[5.6 * cm, 2 * cm, 0.8 * cm, 5.6 * cm, 2 * cm])
        grid.setStyle(
            TableStyle(
                [
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ("LINEBELOW", (0, 0), (1, -1), 0.25, colors.lightgrey),
                    ("LINEBELOW", (3, 0), (4, -1), 0.25, colors.lightgrey),
                ]
            )
        )
        story.append(grid)
    # only dishes with a recipe are cooked; a fruit bowl or a shake eaten on several days is not
    cooked = {group["dish"].name for group in recipes}
    batches = [batch for batch in shopping["batches"] if batch["dish"] in cooked]
    if batches:
        story.append(Paragraph(words["batches"], section))
        for batch in batches:
            line = f"{batch['dish']}: {batch['servings']} {words['servings']}"
            if batch["left_over"]:
                line += f" ({words['left_over'].format(n=batch['left_over'])})"
            story.append(Paragraph("&bull; " + _text(line), body))
    if shopping["pantry_skipped"]:
        story.append(Paragraph(words["pantry"], section))
        story.append(Paragraph(_text(", ".join(shopping["pantry_skipped"])), body))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"{words['page']} {doc.page}")
        canvas.restoreState()

    path.parent.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.8 * cm,
        pageCompression=0,
        title=f"{words['menu']} {first} {words['to']} {last}",
        creator="ai-personal-coach",
    ).build(story, onFirstPage=footer, onLaterPages=footer)


def default_name(first: date) -> str:
    return f"{first.isoformat()}.pdf"
