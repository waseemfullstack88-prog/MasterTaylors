# =============================================================================
# pdf/pdf_generator.py — PDF measurement form generator
# =============================================================================
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import date
import os
import sys

# ─── Font setup ───────────────────────────────────────────────────────────────
# Try to register Urdu-capable font
_URDU_FONT = "Helvetica"  # fallback

def _try_register_font():
    global _URDU_FONT
    # Try Windows system fonts that support Urdu
    candidates = [
        r"C:\Windows\Fonts\urdtype.ttf",    # Urdu Typesetting
        r"C:\Windows\Fonts\ARABTYPE.TTF",   # Arabic Typesetting
        r"C:\Windows\Fonts\arial.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("UrduFont", path))
                _URDU_FONT = "UrduFont"
                return
            except Exception:
                continue

    # Try bundled font in assets/
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bundled = os.path.join(base, "assets", "NotoNastaliqUrdu.ttf")
    if os.path.exists(bundled):
        try:
            pdfmetrics.registerFont(TTFont("UrduFont", bundled))
            _URDU_FONT = "UrduFont"
        except Exception:
            pass


_try_register_font()

# ─── Colours ──────────────────────────────────────────────────────────────────
DARK_NAVY   = colors.HexColor("#0B1829")
GOLD        = colors.HexColor("#D4A017")
GOLD_LIGHT  = colors.HexColor("#F2C030")
WHITE       = colors.white
LIGHT_GRAY  = colors.HexColor("#F5F5F5")
MED_GRAY    = colors.HexColor("#CCCCCC")
DARK_GRAY   = colors.HexColor("#333333")
RED         = colors.HexColor("#C0392B")


def _style(name, parent="Normal", **kwargs):
    s = ParagraphStyle(name, parent=getSampleStyleSheet()[parent], **kwargs)
    return s


def _ur(text):
    """Wrap Urdu text for PDF paragraph — RTL Unicode."""
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except ImportError:
        return text


def generate_measurement_pdf(customer: dict, measurement: dict, output_path: str):
    """Generate a measurement form PDF for a customer."""

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        title=f"Measurement — {customer.get('name','')}",
    )

    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(_build_header(customer))
    story.append(Spacer(1, 6*mm))

    # ── Customer info row ─────────────────────────────────────────────────────
    story.append(_build_customer_info(customer))
    story.append(Spacer(1, 6*mm))

    # ── Measurement form ──────────────────────────────────────────────────────
    story.append(_build_measurement_table(measurement))
    story.append(Spacer(1, 6*mm))

    # ── Checkboxes ────────────────────────────────────────────────────────────
    story.append(_build_checkboxes(measurement))
    story.append(Spacer(1, 6*mm))

    # ── Design / Style notes ──────────────────────────────────────────────────
    story.append(_build_notes(measurement))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 8*mm))
    story.append(_build_footer())

    doc.build(story)
    return output_path


def _build_header(customer: dict):
    """Shop header with name, contact info, serial number."""

    # Shop info paragraph
    shop_style = _style("ShopName", fontSize=22, textColor=WHITE,
                        fontName="Helvetica-Bold", alignment=TA_CENTER,
                        spaceAfter=2)
    sub_style  = _style("ShopSub", fontSize=11, textColor=GOLD_LIGHT,
                        fontName="Helvetica-Oblique", alignment=TA_CENTER,
                        spaceAfter=2)
    cont_style = _style("Contact", fontSize=9, textColor=MED_GRAY,
                        alignment=TA_CENTER, spaceAfter=0)
    serial_style = _style("Serial", fontSize=18, textColor=GOLD,
                          fontName="Helvetica-Bold", alignment=TA_RIGHT)

    shop_p   = Paragraph("Master Taylor's", shop_style)
    sub_p    = Paragraph("&amp; Dress Designer", sub_style)
    cont_p   = Paragraph(
        "Jail Road, Muzaffargarh  ·  0300-9818565  ·  0302-6877253",
        cont_style
    )
    serial_p = Paragraph(
        f"# {customer.get('serial_number','—')}", serial_style
    )
    spec_p   = Paragraph(
        "Shalwar Kameez  ·  Pant Coat  ·  Waist Coat", cont_style
    )

    hdr_data = [[
        [shop_p, sub_p, spec_p, cont_p],
        serial_p,
    ]]
    tbl = Table(hdr_data, colWidths=[13*cm, 4*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), DARK_NAVY),
        ("TOPPADDING",   (0,0), (-1,-1), 14),
        ("BOTTOMPADDING",(0,0), (-1,-1), 14),
        ("LEFTPADDING",  (0,0), (0,-1), 18),
        ("RIGHTPADDING", (-1,0),(-1,-1), 18),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
        ("LINEBELOW",    (0,0), (-1,0), 3, GOLD),
    ]))
    return tbl


def _build_customer_info(customer: dict):
    lbl_style = _style("InfoLbl", fontSize=9, textColor=colors.gray,
                       fontName="Helvetica-Bold")
    val_style = _style("InfoVal", fontSize=11, textColor=DARK_GRAY,
                       fontName="Helvetica-Bold")
    date_str  = date.today().strftime("%d / %m / %Y")

    data = [[
        [Paragraph("نام / Name", lbl_style),
         Paragraph(customer.get("name","—"), val_style)],
        [Paragraph("موبائل / Phone", lbl_style),
         Paragraph(customer.get("phone","—"), val_style)],
        [Paragraph("تاریخ / Date", lbl_style),
         Paragraph(date_str, val_style)],
    ]]
    tbl = Table(data, colWidths=[6*cm, 5*cm, 4.5*cm])
    tbl.setStyle(TableStyle([
        ("BOX",          (0,0), (-1,-1), 1, MED_GRAY),
        ("INNERGRID",    (0,0), (-1,-1), 0.5, MED_GRAY),
        ("BACKGROUND",   (0,0), (-1,-1), LIGHT_GRAY),
        ("TOPPADDING",   (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0), (-1,-1), 8),
        ("LEFTPADDING",  (0,0), (-1,-1), 10),
    ]))
    return tbl


def _build_measurement_table(meas: dict):
    """Two-column register-style measurement table."""

    hdr_style = _style("MHdr", fontSize=10, textColor=WHITE,
                       fontName="Helvetica-Bold", alignment=TA_CENTER)
    urdu_style = _style("MUrdu", fontSize=11, textColor=DARK_NAVY,
                        fontName=_URDU_FONT, alignment=TA_RIGHT)
    val_style  = _style("MVal", fontSize=12, textColor=DARK_GRAY,
                        fontName="Helvetica-Bold", alignment=TA_CENTER)

    def row(ur, key):
        val = meas.get(key, "") or "—"
        return [Paragraph(_ur(ur), urdu_style), Paragraph(val, val_style)]

    # Left column: Kameez
    kameez = [
        [Paragraph(_ur("قمیض / کرتہ"), hdr_style), ""],
        *[row(ur, k) for ur, k in [
            ("لمبائی",     "length"),
            ("بازو",       "sleeve"),
            ("کندھا",      "shoulder"),
            ("چھاتی",      "chest"),
            ("پیٹ",        "belly"),
            ("گھیرہ",      "ghera"),
            ("کالر سائز",  "collar_size"),
            ("کف سائز",    "cuff_size"),
            ("دامن",       "daman"),
        ]],
    ]

    # Right column: Shalwar
    shalwar = [
        [Paragraph(_ur("شلوار"), hdr_style), ""],
        *[row(ur, k) for ur, k in [
            ("لمبائی",    "trouser_length"),
            ("پائنچہ",    "trouser_bottom"),
            ("کمر",       "waist"),
        ]],
    ]

    def make_inner(rows, col_widths):
        t = Table(rows, colWidths=col_widths)
        t.setStyle(TableStyle([
            ("SPAN",         (0,0), (1,0)),   # Header spans 2 cols
            ("BACKGROUND",   (0,0), (1,0), DARK_NAVY),
            ("TEXTCOLOR",    (0,0), (1,0), WHITE),
            ("FONTNAME",     (0,0), (1,0), "Helvetica-Bold"),
            ("TOPPADDING",   (0,0), (-1,-1), 6),
            ("BOTTOMPADDING",(0,0), (-1,-1), 6),
            ("LEFTPADDING",  (0,0), (-1,-1), 8),
            ("RIGHTPADDING", (0,0), (-1,-1), 8),
            ("ROWBACKGROUNDS",(0,1),(-1,-1), [LIGHT_GRAY, WHITE]),
            ("BOX",          (0,0), (-1,-1), 1, MED_GRAY),
            ("INNERGRID",    (0,0), (-1,-1), 0.5, MED_GRAY),
            ("LINEBELOW",    (0,0),(1,0), 2, GOLD),
            ("ALIGN",        (1,1),(-1,-1), "CENTER"),
        ]))
        return t

    k_tbl = make_inner(kameez, [3.5*cm, 2.5*cm])
    s_tbl = make_inner(shalwar, [3.5*cm, 2.5*cm])

    outer = Table([[k_tbl, s_tbl]], colWidths=[7*cm, 9.5*cm])
    outer.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
    ]))
    return outer


def _build_checkboxes(meas: dict):
    """Render checkbox options as a table row."""

    lbl_s = _style("CbLbl", fontSize=9, textColor=colors.gray, fontName="Helvetica-Bold")
    chk_s = _style("Chk", fontSize=10, textColor=DARK_GRAY)
    urdu_s = _style("CbUrdu", fontSize=10, fontName=_URDU_FONT,
                    textColor=DARK_NAVY, alignment=TA_RIGHT)

    boxes = [
        ("cb_collar",         "کالر"),
        ("cb_cuff",           "کف"),
        ("cb_front_pocket",   "فرنٹ جیب"),
        ("cb_side_pocket",    "سائیڈ جیب"),
        ("cb_trouser_pocket", "شلوار جیب"),
        ("cb_daman_round",    "گول دامن"),
        ("cb_daman_straight", "سیدھا دامن"),
        ("cb_embroidery",     "کڑھائی"),
        ("cb_special",        "خاص ڈیزائن"),
    ]

    def cell(key, ur):
        checked = int(meas.get(key, 0) or 0)
        box = "☑" if checked else "☐"
        return [Paragraph(_ur(ur), urdu_s),
                Paragraph(box, chk_s)]

    rows_data = [
        [Paragraph("Style Options / اختیارات", _style(
            "SOH", fontSize=10, fontName="Helvetica-Bold",
            textColor=WHITE, alignment=TA_CENTER
        ))] + [""] * (len(boxes) - 1),
        [item for pair in [cell(k, u) for k,u in boxes] for item in pair],
    ]

    # 9 columns, alternating label/checkbox
    col_w = [1.6*cm, 0.7*cm] * len(boxes)
    col_w = col_w[:16]  # limit

    header_row = [Paragraph("Style Options / اختیارات",
                             _style("SOH2", fontSize=10,
                                    fontName="Helvetica-Bold",
                                    textColor=WHITE, alignment=TA_CENTER))]
    data_row   = []
    for key, ur in boxes:
        checked = int(meas.get(key, 0) or 0)
        box_sym = "☑" if checked else "☐"
        data_row.append(Paragraph(_ur(ur), urdu_s))
        data_row.append(Paragraph(box_sym, chk_s))

    col_widths_cb = [1.8*cm, 0.6*cm] * len(boxes)
    total_w = sum(col_widths_cb)
    scale   = 17.0 * cm / total_w
    col_widths_cb = [w * scale for w in col_widths_cb]

    tbl = Table(
        [[""] * (2 * len(boxes)), data_row],
        colWidths=col_widths_cb,
        rowHeights=[18, 30]
    )
    tbl.setStyle(TableStyle([
        ("SPAN",         (0, 0), (-1, 0)),
        ("BACKGROUND",   (0, 0), (-1, 0), DARK_NAVY),
        ("BACKGROUND",   (0, 1), (-1, 1), LIGHT_GRAY),
        ("BOX",          (0, 0), (-1, -1), 1, MED_GRAY),
        ("INNERGRID",    (0, 0), (-1, -1), 0.5, MED_GRAY),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("LINEBELOW",    (0, 0), (-1, 0), 2, GOLD),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return tbl


def _build_notes(meas: dict):
    """Design / additional notes section."""

    lbl_s   = _style("NLbl", fontSize=10, fontName="Helvetica-Bold",
                     textColor=DARK_NAVY)
    urdu_s  = _style("NUrdu", fontSize=11, fontName=_URDU_FONT,
                     textColor=DARK_NAVY, alignment=TA_RIGHT)
    val_s   = _style("NVal", fontSize=10, textColor=DARK_GRAY,
                     leading=14)

    design   = meas.get("design_notes","") or "—"
    addl     = meas.get("additional_notes","") or "—"

    data = [
        [Paragraph(_ur("ڈیزائن / اسٹائل نوٹ"), urdu_s),
         Paragraph(design, val_s)],
        [Paragraph(_ur("اضافی تفصیل"), urdu_s),
         Paragraph(addl, val_s)],
    ]
    tbl = Table(data, colWidths=[4*cm, 13.5*cm])
    tbl.setStyle(TableStyle([
        ("BOX",          (0,0), (-1,-1), 1, MED_GRAY),
        ("INNERGRID",    (0,0), (-1,-1), 0.5, MED_GRAY),
        ("BACKGROUND",   (0,0), (0,-1), colors.HexColor("#EEE8D0")),
        ("TOPPADDING",   (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0), (-1,-1), 8),
        ("LEFTPADDING",  (0,0), (-1,-1), 10),
    ]))
    return tbl


def _build_footer():
    foot_s = _style("Footer", fontSize=8, textColor=colors.gray,
                    alignment=TA_CENTER)
    return Paragraph(
        "Master Taylor's &amp; Dress Designer  ·  Jail Road, Muzaffargarh  "
        "·  0300-9818565  ·  0302-6877253",
        foot_s
    )
