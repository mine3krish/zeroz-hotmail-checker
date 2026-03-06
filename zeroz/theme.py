"""
Centralized color palette, fonts, and customtkinter appearance.
"""

import customtkinter as ctk

# ── Color palette (GitHub-dark inspired) ──────────────────────────────────────

COLORS = {
    "bg":           "#0d1117",
    "bg_dark":      "#010409",
    "surface":      "#161b22",
    "surface_hi":   "#1c2333",
    "border":       "#30363d",
    "accent":       "#58a6ff",
    "accent_hover":  "#79c0ff",

    "green":        "#3fb950",
    "green_dim":    "#1a4731",
    "red":          "#f85149",
    "red_dim":      "#3d1f1f",
    "yellow":       "#d29922",
    "yellow_dim":   "#3d2e00",
    "blue":         "#58a6ff",
    "blue_dim":     "#0d1f3c",
    "magenta":      "#bc8cff",
    "magenta_dim":  "#2a1a4e",
    "grey":         "#8b949e",
    "white":        "#e6edf3",

    "input_bg":     "#21262d",
    "btn":          "#21262d",
    "btn_hover":    "#30363d",

    "good_row":     "#0d2818",
    "good_row_alt": "#102a1c",
    "tfa_row":      "#0d1f3c",
    "bad_row":      "#2d1b1b",
}

# ── Fonts ─────────────────────────────────────────────────────────────────────

FONT_FAMILY = "Segoe UI"
FONT_MONO = "Consolas"

FONTS = {
    "brand":        (FONT_FAMILY, 26, "bold"),
    "brand_sub":    (FONT_FAMILY, 13),
    "section":      (FONT_FAMILY, 13, "bold"),
    "body":         (FONT_FAMILY, 15),
    "body_small":   (FONT_FAMILY, 14),
    "label":        (FONT_FAMILY, 14),
    "label_small":  (FONT_FAMILY, 13),
    "mono":         (FONT_MONO, 14),
    "mono_small":   (FONT_MONO, 13),
    "stat_value":   (FONT_MONO, 20, "bold"),
    "stat_label":   (FONT_FAMILY, 12),
    "btn":          (FONT_FAMILY, 15, "bold"),
    "btn_small":    (FONT_FAMILY, 13),
    "title_bar":    (FONT_FAMILY, 14, "bold"),
    "status":       (FONT_FAMILY, 12),
}

# ── Sizing ────────────────────────────────────────────────────────────────────

CORNER_RADIUS = 10
SIDEBAR_WIDTH = 300
WINDOW_SIZE = (1150, 760)

# ── Result tag → color mapping ────────────────────────────────────────────────

RESULT_COLORS = {
    "GOOD":    COLORS["green"],
    "2FA":     COLORS["blue"],
    "BAD":     COLORS["red"],
    "INVALID": COLORS["yellow"],
    "LOCKED":  COLORS["magenta"],
    "ERROR":   COLORS["grey"],
}

RESULT_BG = {
    "GOOD":    COLORS["good_row"],
    "2FA":     COLORS["tfa_row"],
    "BAD":     COLORS["bad_row"],
    "INVALID": COLORS["yellow_dim"],
    "LOCKED":  COLORS["magenta_dim"],
    "ERROR":   COLORS["surface"],
}


def apply_theme():
    """Configure customtkinter global appearance."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
