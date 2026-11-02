# =============================================================================
# utils/constants.py — App-wide constants for Master Taylor's
# =============================================================================

APP_TITLE  = "Master Taylor's & Dress Designer"
APP_VERSION = "1.0.0"
WINDOW_SIZE = "1280x800"

# Shop information (from business card)
SHOP_NAME       = "Master Taylor's"
SHOP_SUBTITLE   = "& Dress Designer"
SHOP_ADDRESS    = "Jail Road, Muzaffargarh"
SHOP_PHONE1     = "M. Sadiq: 0300-9818565"
SHOP_PHONE2     = "M. Zubair: 0302-6877253"
SHOP_FACEBOOK   = "Master Taylor"
SHOP_SPECIALTY  = "Shalwar Kameez, Pant Coat, Waist Coat etc"

# ─── Colour Palette ───────────────────────────────────────────────────────────
COLORS = {
    # Backgrounds
    "bg_dark":       "#080D18",
    "bg_medium":     "#0E1525",
    "bg_light":      "#131D30",
    "bg_card":       "#0F1A2C",
    "bg_input":      "#0A1020",

    # Sidebar
    "sidebar_bg":    "#060C19",
    "sidebar_hover": "#12213A",
    "sidebar_active":"#162D52",

    # Gold accent (shop's premium colour)
    "gold":          "#D4A017",
    "gold_light":    "#F2C030",
    "gold_dark":     "#9A7210",
    "gold_bg":       "#120E00",

    # Text
    "text_primary":  "#E8EDF5",
    "text_secondary":"#8A9BB5",
    "text_muted":    "#4A5A70",

    # Status colours
    "green":         "#27AE60",
    "green_light":   "#2ECC71",
    "green_bg":      "#071A0F",
    "orange":        "#D4680D",
    "orange_light":  "#E67E22",
    "orange_bg":     "#1A0900",
    "red":           "#C0392B",
    "red_light":     "#E74C3C",
    "red_bg":        "#1A0400",
    "blue":          "#2471A3",
    "blue_light":    "#2E86C1",
    "blue_bg":       "#040F1A",
    "purple":        "#7D3C98",
    "purple_light":  "#9B59B6",
    "purple_bg":     "#130A1A",
    "teal":          "#1A8A7A",
    "teal_light":    "#1ABC9C",
    "teal_bg":       "#041510",

    # Borders
    "border":        "#1A2840",
    "border_light":  "#243450",

    # Table
    "tbl_bg":        "#0A1020",
    "tbl_selected":  "#1A3A60",
    "tbl_hover":     "#111D30",
    "tbl_header":    "#0D1828",
    "tbl_alt":       "#0C1428",
}

# ─── Fonts ────────────────────────────────────────────────────────────────────
FONTS = {
    "h1":        ("Segoe UI", 28, "bold"),
    "h2":        ("Segoe UI", 22, "bold"),
    "h3":        ("Segoe UI", 17, "bold"),
    "h4":        ("Segoe UI", 14, "bold"),
    "h5":        ("Segoe UI", 12, "bold"),
    "body":      ("Segoe UI", 12),
    "body_sm":   ("Segoe UI", 11),
    "caption":   ("Segoe UI", 10),
    "shop_name": ("Georgia", 24, "bold"),
    "shop_sub":  ("Georgia", 13, "italic"),
    # Urdu – try Urdu Typesetting (Windows default), fallback to Arial Unicode
    "urdu_xl":   ("Urdu Typesetting", 18),
    "urdu_lg":   ("Urdu Typesetting", 15),
    "urdu_md":   ("Urdu Typesetting", 13),
    "urdu_sm":   ("Urdu Typesetting", 11),
}

# ─── Status definitions ───────────────────────────────────────────────────────
ORDER_STATUS_LIST = [
    ("Pending",   "زیر التواء", COLORS["orange"]),
    ("Cutting",   "کٹائی",      COLORS["blue"]),
    ("Stitching", "سلائی",      COLORS["purple"]),
    ("Ready",     "تیار",       COLORS["teal"]),
    ("Delivered", "حوالہ",      COLORS["green"]),
    ("Cancelled", "منسوخ",      COLORS["red"]),
]

ORDER_STATUSES_EN   = [s[0] for s in ORDER_STATUS_LIST]
ORDER_STATUSES_UR   = [s[1] for s in ORDER_STATUS_LIST]
ORDER_STATUS_COLORS = {s[0]: s[2] for s in ORDER_STATUS_LIST}

CLOTHING_TYPES = [
    "شلوار قمیض",
    "پینٹ کوٹ",
    "ویسٹ کوٹ",
    "کرتہ",
    "قمیض",
    "شلوار",
    "دیگر",
]

PAYMENT_METHODS = ["نقد", "آن لائن", "دیگر"]

# ─── Navigation items ────────────────────────────────────────────────────────
NAV_ITEMS = [
    ("dashboard",  "🏠",  "Dashboard",    "ڈیش بورڈ"),
    ("customers",  "👥",  "Customers",    "گاہک"),
    ("orders",     "📦",  "Orders",       "آرڈرز"),
    ("payments",   "💰",  "Payments",     "ادائیگی"),
    ("reports",    "📊",  "Reports",      "رپورٹ"),
    ("backup",     "💾",  "Backup",       "بیک اپ"),
]

# ─── Measurement field labels (Urdu + English key) ───────────────────────────
MEASUREMENT_FIELDS = [
    # (db_column,        urdu_label,         english_label,    placeholder)
    ("length",           "لمبائی",           "Length",         "e.g. 44"),
    ("sleeve",           "بازو",             "Sleeve",         "e.g. 25"),
    ("shoulder",         "کندھا / تیرا",     "Shoulder",       "e.g. 18"),
    ("chest",            "چھاتی",            "Chest",          "e.g. 42"),
    ("belly",            "پیٹ",              "Belly",          "e.g. 40"),
    ("ghera",            "گھیرہ",            "Ghera",          "e.g. 44"),
    ("trouser_length",   "شلوار",            "Trouser Len",    "e.g. 40"),
    ("trouser_bottom",   "پائنچہ",           "Pajama Width",   "e.g. 22"),
    ("waist",            "کمر",              "Waist",          "e.g. 38"),
    ("collar_size",      "کالر",             "Collar Size",    "e.g. 15"),
    ("cuff_size",        "کف",               "Cuff Size",      "e.g. 6"),
    ("daman",            "دامن",             "Daman",          "e.g. 14"),
]

MEASUREMENT_CHECKBOXES = [
    ("cb_collar",        "کالر",             "Collar"),
    ("cb_cuff",          "کف",               "Cuff"),
    ("cb_front_pocket",  "فرنٹ جیب",         "Front Pocket"),
    ("cb_side_pocket",   "سائیڈ جیب",        "Side Pocket"),
    ("cb_trouser_pocket","شلوار جیب",         "Trouser Pocket"),
    ("cb_daman_round",   "گول دامن",          "Round Daman"),
    ("cb_daman_straight","سیدھا دامن",        "Straight Daman"),
    ("cb_embroidery",    "کڑھائی",           "Embroidery"),
    ("cb_special",       "خاص ڈیزائن",       "Special Design"),
]
