"""
FinBuddy - Theme & Style Constants
Central source of truth for all UI colors, fonts, and dimensions.
"""

# ─── Theme State ──────────────────────────────────────────────────────────────
THEME_MODE = "dark"

# ─── Palettes ─────────────────────────────────────────────────────────────────
DARK_PALETTE = {
    "BG_DARK":      "#0a0a0f",
    "BG_CARD":      "#12121a",
    "BG_HOVER":     "#1a1a26",
    "BG_INPUT":     "#0f0f18",
    "TEXT_PRIMARY": "#f0f0f8",
    "TEXT_MUTED":   "#888899",
    "TEXT_DISABLED":"#44445a",
    "PURPLE_DIM":   "#3d1361",
}

LIGHT_PALETTE = {
    "BG_DARK":      "#f0f2f5",
    "BG_CARD":      "#ffffff",
    "BG_HOVER":     "#f8f9fa",
    "BG_INPUT":     "#ffffff",
    "TEXT_PRIMARY": "#1a1a1a",
    "TEXT_MUTED":   "#64748b",
    "TEXT_DISABLED":"#94a3b8",
    "PURPLE_DIM":   "#e9d5ff",
}

# ─── Shared Colors (Neon vibes preserved) ─────────────────────────────────────
PURPLE       = "#8A2BE2"   
PURPLE_LIGHT = "#a855f7"   
PURPLE_GLOW  = "#6d28d9"   
TEAL         = "#0d9488" # Slightly deeper teal for better contrast in light mode
TEAL_LIGHT   = "#00FFD1"
SUCCESS = "#059669"
WARNING = "#d97706"
DANGER  = "#dc2626"
INFO    = "#2563eb"

# Initialize global variables with dark palette
BG_DARK      = DARK_PALETTE["BG_DARK"]
BG_CARD      = DARK_PALETTE["BG_CARD"]
BG_HOVER     = DARK_PALETTE["BG_HOVER"]
BG_INPUT     = DARK_PALETTE["BG_INPUT"]
TEXT_PRIMARY  = DARK_PALETTE["TEXT_PRIMARY"]
TEXT_MUTED    = DARK_PALETTE["TEXT_MUTED"]
TEXT_DISABLED = DARK_PALETTE["TEXT_DISABLED"]
PURPLE_DIM   = DARK_PALETTE["PURPLE_DIM"]

def set_theme(mode):
    """Update global theme constants. (Note: Only works if imported as a module, not via *)"""
    global THEME_MODE, BG_DARK, BG_CARD, BG_HOVER, BG_INPUT, TEXT_PRIMARY, TEXT_MUTED, TEXT_DISABLED, PURPLE_DIM
    THEME_MODE = mode
    p = LIGHT_PALETTE if mode == "light" else DARK_PALETTE
    BG_DARK      = p["BG_DARK"]
    BG_CARD      = p["BG_CARD"]
    BG_HOVER     = p["BG_HOVER"]
    BG_INPUT     = p["BG_INPUT"]
    TEXT_PRIMARY  = p["TEXT_PRIMARY"]
    TEXT_MUTED    = p["TEXT_MUTED"]
    TEXT_DISABLED = p["TEXT_DISABLED"]
    PURPLE_DIM   = p["PURPLE_DIM"]

# ─── Typography ───────────────────────────────────────────────────────────────
FONT_FAMILY   = "Helvetica"
FONT_MONO     = "Courier"

FONT_TITLE    = (FONT_FAMILY, 28, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 14)
FONT_HEADING  = (FONT_FAMILY, 16, "bold")
FONT_SUBHEAD  = (FONT_FAMILY, 13, "bold")
FONT_BODY     = (FONT_FAMILY, 11)
FONT_SMALL    = (FONT_FAMILY, 10)
FONT_TINY     = (FONT_FAMILY, 9)
FONT_MONO_SM  = (FONT_MONO, 10)
FONT_BIG_NUM  = (FONT_FAMILY, 22, "bold")
FONT_MED_NUM  = (FONT_FAMILY, 16, "bold")

# ─── Spacing & Dimensions ─────────────────────────────────────────────────────
PAD_SM   = 8
PAD_MD   = 14
PAD_LG   = 20
PAD_XL   = 32

SIDEBAR_W = 200
CARD_RADIUS = 4   

# ─── Nav Items ────────────────────────────────────────────────────────────────
NAV_ITEMS = [
    ("🏠", "Dashboard"),
    ("📊", "Analysis"),
    ("🚫", "Faltu Meter"),
    ("🤖", "AI Buddy"),
    ("⚙️", "Settings"),
]
