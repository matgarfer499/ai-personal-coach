"""Print a saved menu as a PDF: days, recipes with a QR code to each source, shopping list.

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
# convention: the page and type sizes of the printout (A4, 10 pt text, 2.4 cm QR codes), chosen to
# print on one sheet per day or two and to scan from a phone screen.
QR_CM = 2.4
LABELS = {
    "es": {
        "menu": "Menú",
        "to": "a",
        "tupper": "tupper",
        "free": "comida libre",
        "free_left": "quedan para llegar al objetivo",
        "batch": "tanda de {n} raciones, se cocina una vez; los ingredientes son de una ración",
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
        "days": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"],
    },
    "en": {
        "menu": "Menu",
        "to": "to",
        "tupper": "lunchbox",
        "free": "free meal",
        "free_left": "left to reach the target",
        "batch": "batch of {n} servings, cooked once; the ingredients are for one serving",
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


def _amount(name: str, amount, table: list[Food], language: str, comma: bool) -> str:
    food = find(name, table)
    label = (food.name_en if language == "en" else food.name_es) if food else name
    unit = getattr(amount, "unit", "g")
    return f"{label}: {_number(amount, comma)} {unit}"


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
    """Write the PDF; raises ValueError naming the extra to install when reportlab is missing."""
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
    body = ParagraphStyle("body", parent=sheet["BodyText"], fontSize=10, leading=13)
    small = ParagraphStyle("small", parent=body, fontSize=9, leading=11, textColor=colors.grey)
    day_style = ParagraphStyle(
        "day", parent=sheet["Heading2"], spaceBefore=6, spaceAfter=4, keepWithNext=1
    )
    meal_style = ParagraphStyle(
        "meal", parent=body, fontName="Helvetica-Bold", fontSize=11, keepWithNext=1
    )
    dish_style = ParagraphStyle("dish", parent=body, fontName="Helvetica-Bold", leftIndent=8)
    indent = ParagraphStyle("indent", parent=body, leftIndent=18)

    def qr_code(url: str):
        widget = QrCodeWidget(url)
        x0, y0, x1, y1 = widget.getBounds()
        size = QR_CM * cm
        drawing = Drawing(size, size, transform=[size / (x1 - x0), 0, 0, size / (y1 - y0), 0, 0])
        drawing.add(widget)
        return drawing

    story = []
    first, last = days[0].date, days[-1].date
    story.append(Paragraph(f"{words['menu']} {first} {words['to']} {last}", sheet["Title"]))
    saved_days = document["days"]
    for day, entry in zip(days, saved_days, strict=True):
        block = [
            Paragraph(f"{words['days'][day.date.weekday()]} {day.date.isoformat()}", day_style)
        ]
        free_left = (entry.get("free_meal") or {}).get("budget", {}).get("kcal")
        for meal, raw_meal in zip(day.meals, entry["meals"], strict=True):
            title = _text(meal.name)
            if meal.tupper:
                title += f" ({words['tupper']})"
            if meal.free:
                title += f": {words['free']}"
                if free_left is not None:
                    title += f", {_number(free_left, comma)} kcal {words['free_left']}"
            heading = [Paragraph(title, meal_style)]
            if meal.free:
                block += heading
            for dish, raw_dish in zip(meal.dishes, raw_meal.get("dishes") or [], strict=True):
                # the meal's title stays with its first dish
                parts = heading + [Paragraph(_text(dish.name), dish_style)]
                heading = []
                if dish.servings > 1:
                    parts.append(Paragraph(words["batch"].format(n=dish.servings), small))
                for name, amount in dish.items:
                    line = _amount(name, amount, table, language, comma)
                    parts.append(Paragraph("&bull; " + _text(line), indent))
                if dish.seasoning:
                    parts.append(
                        Paragraph(
                            f"{words['seasoning']}: {_text(', '.join(dish.seasoning))}", indent
                        )
                    )
                for number, step in enumerate(raw_dish.get("steps") or [], 1):
                    parts.append(Paragraph(f"{number}. {_text(step)}", indent))
                source = str(raw_dish.get("source") or "").strip()
                url = web_link(source)
                if source and not url:  # not a web address: text only, no link or QR code
                    parts.append(Paragraph(f"{words['source']}: {_text(source)}", small))
                if url:
                    link = Paragraph(
                        f'{words["source"]}: <link href="{escape(url, {chr(34): "&quot;"})}" '
                        f'color="blue">{_text(url)}</link>',
                        small,
                    )
                    if qr:
                        table_ = Table([[link, qr_code(url)]], colWidths=[12.5 * cm, 3.4 * cm])
                        table_.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
                        parts.append(table_)
                    else:
                        parts.append(link)
                block.append(KeepTogether(parts))
                block.append(Spacer(1, 4))
        totals, targets = entry.get("totals"), document.get("targets") or {}
        if totals:
            fields = (
                ("kcal", "kcal", "kcal"),
                ("protein_g", words["protein"], "protein_g"),
                ("carbs_g", words["carbs"], None),
                ("fat_g", words["fat"], None),
                ("fibre_g", words["fibre"], "fibre_g"),
            )
            cells = []
            for key, label, target_key in fields:
                text = f"{label} {_number(totals[key], comma)}"
                if target_key and target_key in targets:
                    text += f" / {words['target']} {_number(targets[target_key], comma)}"
                missing = (totals.get("missing") or {}).get(key)
                if missing:
                    text += f" ({words['no_data']}: {', '.join(map(str, missing))})"
                cells.append(text)
            block.append(Paragraph(f"<b>{words['totals']}</b>: {_text('; '.join(cells))}", small))
        story += block
    story.append(PageBreak())
    story.append(Paragraph(words["shopping"], sheet["Title"]))
    for chain, lines in shopping["chains"].items():
        story.append(Paragraph(_text(words["any_chain"] if chain == "any" else chain), day_style))
        rows = [
            [
                Paragraph(_text(line["name"]), body),
                f"{_number(line.get('grams', line.get('ml')), comma)} "
                f"{'g' if 'grams' in line else 'ml'}",
            ]
            for line in lines
        ]
        grid = Table(rows, colWidths=[11 * cm, 4 * cm])
        grid.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.lightgrey)]))
        story.append(grid)
    if shopping["batches"]:
        story.append(Paragraph(words["batches"], day_style))
        for batch in shopping["batches"]:
            line = f"{batch['dish']}: {batch['servings']} {words['servings']}"
            if batch["left_over"]:
                line += f" ({words['left_over'].format(n=batch['left_over'])})"
            story.append(Paragraph("&bull; " + _text(line), body))
    if shopping["pantry_skipped"]:
        story.append(Paragraph(words["pantry"], day_style))
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
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        pageCompression=0,
        title=f"{words['menu']} {first} {words['to']} {last}",
        creator="ai-personal-coach",
    ).build(story, onFirstPage=footer, onLaterPages=footer)


def default_name(first: date) -> str:
    return f"{first.isoformat()}.pdf"
