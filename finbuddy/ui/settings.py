"""
FinBuddy - Settings Screen
API key configuration and app preferences.
"""

import tkinter as tk
import ui.theme as theme
from ui.components import make_label, make_button, make_card, make_separator


class SettingsScreen(tk.Frame):
    def __init__(self, parent, app_state: dict, **kwargs):
        super().__init__(parent, bg=theme.BG_DARK, **kwargs)
        self.app_state = app_state
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=theme.BG_DARK)
        header.pack(fill="x", padx=theme.PAD_XL, pady=(theme.PAD_XL, theme.PAD_MD))
        tk.Label(header, text="⚙️ Settings", font=theme.FONT_TITLE,
                 fg=theme.TEXT_PRIMARY, bg=theme.BG_DARK).pack(side="left")

        make_separator(self).pack(fill="x", padx=theme.PAD_XL, pady=4)

        content = tk.Frame(self, bg=theme.BG_DARK)
        content.pack(fill="both", expand=True, padx=theme.PAD_XL, pady=theme.PAD_MD)

        # ─── Appearance Card ──────────────────────────────────────────────
        theme_card = make_card(content)
        theme_card.pack(fill="x", pady=theme.PAD_MD)

        make_label(theme_card, "🎨 Appearance", style="heading").pack(
            anchor="w", padx=theme.PAD_LG, pady=(theme.PAD_LG, theme.PAD_MD))
        make_separator(theme_card).pack(fill="x", padx=theme.PAD_LG)

        mode_row = tk.Frame(theme_card, bg=theme.BG_CARD)
        mode_row.pack(fill="x", padx=theme.PAD_LG, pady=theme.PAD_MD)
        
        make_label(mode_row, "Theme Mode", style="body").pack(side="left")
        
        self._mode_var = tk.StringVar(value=theme.THEME_MODE)
        
        def _on_toggle():
            new_mode = self._mode_var.get()
            # The structure is: SettingsScreen -> content_area -> FinBuddyApp
            # We call the toggle_theme method on FinBuddyApp
            if hasattr(self.master.master, "toggle_theme"):
                self.master.master.toggle_theme(new_mode)

        for text, value in [("🌙 Dark", "dark"), ("☀️ Light", "light")]:
            tk.Radiobutton(mode_row, text=text, variable=self._mode_var, value=value,
                           bg=theme.BG_CARD, fg=theme.TEXT_PRIMARY, selectcolor=theme.BG_DARK,
                           activebackground=theme.BG_CARD, activeforeground=theme.PURPLE_LIGHT,
                           font=theme.FONT_BODY, command=_on_toggle,
                           indicatoron=0, padx=theme.PAD_MD, pady=5).pack(side="left", padx=(theme.PAD_MD, 0))


        # ─── About Card ────────────────────────────────────────────────────
        about_card = make_card(content)
        about_card.pack(fill="x", pady=theme.PAD_MD)
        make_label(about_card, "ℹ️ About FinBuddy", style="heading").pack(
            anchor="w", padx=theme.PAD_LG, pady=(theme.PAD_LG, theme.PAD_MD))
        make_separator(about_card).pack(fill="x", padx=theme.PAD_LG)

        about_info = [
            ("Version", "1.0.0"),
            ("Built with", "Python · Tkinter · Pandas · Matplotlib · Groq"),
            ("Theme", "Light/Dark Futuristic · Neon Purple"),
            ("CSV format", "Date, Category, Amount, Type (Income/Expense)"),
        ]
        for label, value in about_info:
            row = tk.Frame(about_card, bg=theme.BG_CARD)
            row.pack(fill="x", padx=theme.PAD_LG, pady=5)
            tk.Label(row, text=label, font=theme.FONT_SUBHEAD, fg=theme.TEXT_MUTED,
                     bg=theme.BG_CARD, width=16, anchor="w").pack(side="left")
            tk.Label(row, text=value, font=theme.FONT_BODY, fg=theme.TEXT_PRIMARY,
                     bg=theme.BG_CARD, anchor="w").pack(side="left")

        tk.Frame(about_card, bg=theme.BG_CARD, height=theme.PAD_LG).pack()

        # ─── Sample CSV tip ────────────────────────────────────────────────
        tip_card = make_card(content)
        tip_card.pack(fill="x", pady=theme.PAD_MD)
        make_label(tip_card, "📂 Sample CSV", style="heading").pack(
            anchor="w", padx=theme.PAD_LG, pady=(theme.PAD_LG, theme.PAD_MD))
        make_separator(tip_card).pack(fill="x", padx=theme.PAD_LG)
        tk.Label(tip_card,
                 text="A sample.csv file is included in the data/ folder.\n"
                      "Use it to explore FinBuddy without your own data.",
                 font=theme.FONT_BODY, fg=theme.TEXT_MUTED, bg=theme.BG_CARD, justify="left").pack(
            anchor="w", padx=theme.PAD_LG, pady=theme.PAD_MD)
        tk.Frame(tip_card, bg=theme.BG_CARD, height=theme.PAD_MD).pack()

    def refresh(self):
        pass
