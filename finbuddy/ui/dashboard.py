"""
FinBuddy - Dashboard Screen
Overview panel with stats, savings jars, and streak counter.
"""

import tkinter as tk
import ui.theme as theme
from ui.components import StatCard, NeonProgressBar, make_label, make_card, make_separator


class DashboardScreen(tk.Frame):
    def __init__(self, parent, app_state: dict, **kwargs):
        super().__init__(parent, bg=theme.BG_DARK, **kwargs)
        self.app_state = app_state
        self._build()

    def _build(self):
        # Header
        header = tk.Frame(self, bg=theme.BG_DARK)
        header.pack(fill="x", padx=theme.PAD_XL, pady=(theme.PAD_XL, theme.PAD_MD))

        tk.Label(header, text="Dashboard", font=theme.FONT_TITLE,
                 fg=theme.TEXT_PRIMARY, bg=theme.BG_DARK).pack(side="left")

        streak_frame = tk.Frame(header, bg=theme.BG_CARD, padx=12, pady=6,
                                highlightthickness=1, highlightbackground=theme.PURPLE_DIM)
        streak_frame.pack(side="right")
        tk.Label(streak_frame, text="🔥", font=(theme.FONT_FAMILY, 18), bg=theme.BG_CARD).pack(side="left")
        self._streak_label = tk.Label(streak_frame, text="0 day streak",
                                      font=theme.FONT_SUBHEAD, fg=theme.WARNING, bg=theme.BG_CARD)
        self._streak_label.pack(side="left", padx=4)

        make_separator(self).pack(fill="x", padx=theme.PAD_XL, pady=4)

        # Scrollable content
        scroll_canvas = tk.Canvas(self, bg=theme.BG_DARK, highlightthickness=0)
        scroll_canvas.pack(fill="both", expand=True)
        content = tk.Frame(scroll_canvas, bg=theme.BG_DARK)
        scroll_canvas.create_window((0, 0), window=content, anchor="nw")

        content.bind("<Configure>", lambda e: scroll_canvas.configure(
            scrollregion=scroll_canvas.bbox("all")))

        # ─── Top Stats Row ────────────────────────────────────────────────
        stats_row = tk.Frame(content, bg=theme.BG_DARK)
        stats_row.pack(fill="x", padx=theme.PAD_XL, pady=theme.PAD_MD)
        stats_row.columnconfigure((0, 1, 2, 3), weight=1, uniform="col")

        self._income_card = StatCard(stats_row, "💰 Total Income", "₹0",
                                     "No data loaded", value_color=theme.SUCCESS)
        self._income_card.grid(row=0, column=0, padx=6, pady=4, sticky="ew")

        self._expense_card = StatCard(stats_row, "💸 Total Expense", "₹0",
                                      "No data loaded", value_color=theme.DANGER)
        self._expense_card.grid(row=0, column=1, padx=6, pady=4, sticky="ew")

        self._savings_card = StatCard(stats_row, "🏦 Savings", "₹0",
                                      "0% savings rate", value_color=theme.TEAL)
        self._savings_card.grid(row=0, column=2, padx=6, pady=4, sticky="ew")

        self._txn_card = StatCard(stats_row, "📋 Transactions", "0",
                                  "Upload CSV to begin", value_color=theme.PURPLE_LIGHT)
        self._txn_card.grid(row=0, column=3, padx=6, pady=4, sticky="ew")

        # ─── Savings Jars ─────────────────────────────────────────────────
        jars_card = make_card(content)
        jars_card.pack(fill="x", padx=theme.PAD_XL, pady=theme.PAD_MD)
        make_label(jars_card, "🏺 Savings Jars", style="heading").pack(
            anchor="w", padx=theme.PAD_LG, pady=(theme.PAD_LG, theme.PAD_MD))
        make_separator(jars_card).pack(fill="x", padx=theme.PAD_LG, pady=4)

        jars_inner = tk.Frame(jars_card, bg=theme.BG_CARD)
        jars_inner.pack(fill="x", padx=theme.PAD_LG, pady=theme.PAD_MD)

        self._jars = {}
        jar_defs = [
            ("Emergency Fund", theme.TEAL,         0),
            ("Travel",         theme.PURPLE_LIGHT, 0),
            ("Investment",     theme.WARNING,      0),
            ("Gadget Fund",    theme.INFO,         0),
        ]
        for i, (name, color, initial) in enumerate(jar_defs):
            row = tk.Frame(jars_inner, bg=theme.BG_CARD)
            row.pack(fill="x", pady=6)
            tk.Label(row, text=name, font=theme.FONT_BODY, fg=theme.TEXT_PRIMARY,
                     bg=theme.BG_CARD, width=18, anchor="w").pack(side="left")
            bar = NeonProgressBar(row, width=300, height=14, color=color)
            bar.pack(side="left", padx=theme.PAD_MD)
            pct_label = tk.Label(row, text="0%", font=theme.FONT_SMALL,
                                 fg=theme.TEXT_MUTED, bg=theme.BG_CARD)
            pct_label.pack(side="left")
            self._jars[name] = (bar, pct_label)

        # ─── Top Categories ───────────────────────────────────────────────
        cats_card = make_card(content)
        cats_card.pack(fill="x", padx=theme.PAD_XL, pady=theme.PAD_MD)
        make_label(cats_card, "📈 Top Spending Categories", style="heading").pack(
            anchor="w", padx=theme.PAD_LG, pady=(theme.PAD_LG, theme.PAD_MD))
        make_separator(cats_card).pack(fill="x", padx=theme.PAD_LG, pady=4)

        self._cats_frame = tk.Frame(cats_card, bg=theme.BG_CARD)
        self._cats_frame.pack(fill="x", padx=theme.PAD_LG, pady=theme.PAD_MD)

        self._no_data_label = make_label(
            self._cats_frame,
            "📂  Upload a CSV file to see your spending breakdown",
            style="muted"
        )
        self._no_data_label.pack(pady=theme.PAD_XL)

        # ─── Bottom padding ────────────────────────────────────────────────
        tk.Frame(content, bg=theme.BG_DARK, height=theme.PAD_XL).pack()

    def refresh(self):
        """Called whenever app_state changes to update all displayed values."""
        summary = self.app_state.get("summary")
        streak = self.app_state.get("streak", 1)

        self._streak_label.config(text=f"{streak} day streak")

        if not summary:
            return

        # Update stat cards
        income = summary["total_income"]
        expense = summary["total_expense"]
        savings = summary["savings"]
        rate = summary["savings_rate"]
        num_txn = summary["num_transactions"]

        self._income_card.update_value(f"₹{income:,.0f}", theme.SUCCESS)
        self._expense_card.update_value(f"₹{expense:,.0f}", theme.DANGER)
        self._savings_card.update_value(
            f"₹{savings:,.0f}",
            theme.SUCCESS if savings >= 0 else theme.DANGER
        )
        self._savings_card._val_label.master  # just a ref check
        # Update savings sub label manually
        self._txn_card.update_value(str(num_txn))

        # Savings jars — mock allocation of actual savings
        jar_allocs = [
            ("Emergency Fund", 30),
            ("Travel",          20),
            ("Investment",      35),
            ("Gadget Fund",     15),
        ]
        for name, alloc_pct in jar_allocs:
            if name in self._jars:
                bar, lbl = self._jars[name]
                # Display fill based on savings rate relative to allocation
                fill = min(100, (rate / 100) * alloc_pct * 3)
                bar.animate_to(fill)
                lbl.config(text=f"{fill:.0f}%")

        # Top categories
        for widget in self._cats_frame.winfo_children():
            widget.destroy()

        cats = summary["category_summary"]
        if cats.empty:
            make_label(self._cats_frame,
                       "No expense data found.", style="muted").pack(pady=theme.PAD_LG)
            return

        max_amt = cats.max()
        colors = [theme.PURPLE_LIGHT, theme.TEAL, theme.WARNING, theme.INFO, theme.DANGER]

        for i, (cat, amt) in enumerate(cats.head(6).items()):
            row = tk.Frame(self._cats_frame, bg=theme.BG_CARD)
            row.pack(fill="x", pady=5)

            color = colors[i % len(colors)]
            tk.Label(row, text=cat, font=theme.FONT_BODY, fg=theme.TEXT_PRIMARY,
                     bg=theme.BG_CARD, width=20, anchor="w").pack(side="left")
            bar = NeonProgressBar(row, width=220, height=12, color=color)
            bar.pack(side="left", padx=theme.PAD_MD)
            bar.animate_to((amt / max_amt) * 100 if max_amt > 0 else 0)
            tk.Label(row, text=f"₹{amt:,.0f}", font=theme.FONT_SMALL,
                     fg=color, bg=theme.BG_CARD).pack(side="left")
