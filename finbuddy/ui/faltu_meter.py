"""
FinBuddy - Faltu Meter Screen
Shows impulse spending score and breakdown.
"""

import tkinter as tk
import ui.theme as theme
from ui.components import make_label, make_card, make_separator, NeonProgressBar
from logic.faltu_meter import compute_faltu_score


class FaltuMeterScreen(tk.Frame):
    def __init__(self, parent, app_state: dict, **kwargs):
        super().__init__(parent, bg=theme.BG_DARK, **kwargs)
        self.app_state = app_state
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=theme.BG_DARK)
        header.pack(fill="x", padx=theme.PAD_XL, pady=(theme.PAD_XL, theme.PAD_MD))
        tk.Label(header, text="🚫 Faltu Meter", font=theme.FONT_TITLE,
                 fg=theme.TEXT_PRIMARY, bg=theme.BG_DARK).pack(side="left")
        tk.Label(header, text="Are you spending on things that don't matter?",
                 font=theme.FONT_SUBTITLE, fg=theme.TEXT_MUTED, bg=theme.BG_DARK).pack(
            side="left", padx=theme.PAD_LG)

        make_separator(self).pack(fill="x", padx=theme.PAD_XL, pady=4)

        # Scrollable
        container = tk.Frame(self, bg=theme.BG_DARK)
        container.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(container, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        canvas = tk.Canvas(container, bg=theme.BG_DARK, highlightthickness=0,
                           yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar.config(command=canvas.yview)

        content = tk.Frame(canvas, bg=theme.BG_DARK)
        cid = canvas.create_window((0, 0), window=content, anchor="nw")
        
        content.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(cid, width=e.width))

        # Mousewheel support (only when mouse is over canvas)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind('<Enter>', lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind('<Leave>', lambda e: canvas.unbind_all("<MouseWheel>"))

        # Score card
        score_card = make_card(content)
        score_card.pack(fill="x", padx=theme.PAD_XL, pady=theme.PAD_MD)

        inner = tk.Frame(score_card, bg=theme.BG_CARD)
        inner.pack(padx=theme.PAD_XL, pady=theme.PAD_XL)

        # Big score circle (simulated with canvas)
        self._score_canvas = tk.Canvas(inner, width=180, height=180,
                                       bg=theme.BG_CARD, highlightthickness=0)
        self._score_canvas.pack(side="left")
        self._draw_score_ring(0, theme.PURPLE_DIM)

        # Score text + verdict
        right = tk.Frame(inner, bg=theme.BG_CARD)
        right.pack(side="left", padx=theme.PAD_XL, fill="both", expand=True)

        tk.Label(right, text="Faltu Score", font=theme.FONT_SMALL,
                 fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(anchor="w")
        self._verdict_label = tk.Label(right, text="Upload data to calculate",
                                       font=theme.FONT_HEADING, fg=theme.TEXT_MUTED, bg=theme.BG_CARD)
        self._verdict_label.pack(anchor="w", pady=(4, theme.PAD_MD))

        self._message_label = tk.Label(
            right,
            text="Upload a CSV file from the Analysis tab to get your Faltu Score.",
            font=theme.FONT_BODY, fg=theme.TEXT_MUTED, bg=theme.BG_CARD, wraplength=400, justify="left"
        )
        self._message_label.pack(anchor="w")

        # Amount breakdown
        tk.Frame(right, bg=theme.PURPLE_DIM, height=1).pack(fill="x", pady=theme.PAD_MD)
        amounts_row = tk.Frame(right, bg=theme.BG_CARD)
        amounts_row.pack(anchor="w")

        self._faltu_amount_label = tk.Label(amounts_row, text="₹0",
                                            font=theme.FONT_MED_NUM, fg=theme.DANGER, bg=theme.BG_CARD)
        self._faltu_amount_label.pack(side="left")
        tk.Label(amounts_row, text=" spent on unnecessary items",
                 font=theme.FONT_BODY, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(side="left")

        self._faltu_pct_label = tk.Label(right, text="0% of total spending",
                                         font=theme.FONT_SMALL, fg=theme.TEXT_MUTED, bg=theme.BG_CARD)
        self._faltu_pct_label.pack(anchor="w", pady=(4, 0))

        # Progress bar for score
        tk.Frame(score_card, bg=theme.BG_CARD, height=theme.PAD_MD).pack()
        bar_row = tk.Frame(score_card, bg=theme.BG_CARD)
        bar_row.pack(padx=theme.PAD_XL, fill="x", pady=(0, theme.PAD_LG))
        tk.Label(bar_row, text="0", font=theme.FONT_SMALL, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(side="left")
        self._score_bar = NeonProgressBar(bar_row, height=20, color=theme.PURPLE_LIGHT)
        self._score_bar.pack(side="left", fill="x", expand=True, padx=theme.PAD_MD)
        tk.Label(bar_row, text="100", font=theme.FONT_SMALL, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(side="right")

        # Breakdown card
        breakdown_card = make_card(content)
        breakdown_card.pack(fill="x", padx=theme.PAD_XL, pady=theme.PAD_MD)
        make_label(breakdown_card, "🔍 Faltu Spending Breakdown",
                   style="heading").pack(anchor="w", padx=theme.PAD_LG, pady=(theme.PAD_LG, theme.PAD_MD))
        make_separator(breakdown_card).pack(fill="x", padx=theme.PAD_LG)

        self._breakdown_frame = tk.Frame(breakdown_card, bg=theme.BG_CARD)
        self._breakdown_frame.pack(fill="x", padx=theme.PAD_LG, pady=theme.PAD_MD)

        self._no_breakdown_label = make_label(
            self._breakdown_frame,
            "No data loaded yet.",
            style="muted"
        )
        self._no_breakdown_label.pack(pady=theme.PAD_XL)

        # Tips card
        tips_card = make_card(content)
        tips_card.pack(fill="x", padx=theme.PAD_XL, pady=theme.PAD_MD)
        make_label(tips_card, "💡 How to reduce Faltu spending",
                   style="heading").pack(anchor="w", padx=theme.PAD_LG, pady=(theme.PAD_LG, theme.PAD_MD))
        make_separator(tips_card).pack(fill="x", padx=theme.PAD_LG)

        tips = [
            ("🚴", "Cook at home 3x a week", "Save ₹2,000–₹4,000/month on food delivery"),
            ("⏳", "24-hour rule for shopping", "Wait a day before buying non-essentials"),
            ("📱", "Audit subscriptions monthly", "Cancel what you haven't used in 30 days"),
            ("🎯", "Set a fun-money budget", "Guilt-free spend within limits — ₹1,500/month"),
        ]
        for icon, tip, desc in tips:
            row = tk.Frame(tips_card, bg=theme.BG_CARD)
            row.pack(fill="x", padx=theme.PAD_LG, pady=6)
            tk.Label(row, text=icon, font=(theme.FONT_FAMILY, 18), bg=theme.BG_CARD).pack(side="left")
            col = tk.Frame(row, bg=theme.BG_CARD)
            col.pack(side="left", padx=theme.PAD_MD)
            tk.Label(col, text=tip, font=theme.FONT_SUBHEAD, fg=theme.TEXT_PRIMARY, bg=theme.BG_CARD,
                     anchor="w").pack(anchor="w")
            tk.Label(col, text=desc, font=theme.FONT_SMALL, fg=theme.TEXT_MUTED, bg=theme.BG_CARD,
                     anchor="w").pack(anchor="w")

        tk.Frame(tips_card, bg=theme.BG_CARD, height=theme.PAD_LG).pack()
        tk.Frame(content, bg=theme.BG_DARK, height=theme.PAD_XL).pack()

    def _draw_score_ring(self, score: float, color: str):
        """Draw a circular score indicator."""
        c = self._score_canvas
        c.delete("all")
        cx, cy, r = 90, 90, 70

        # Background ring
        c.create_oval(cx - r, cy - r, cx + r, cy + r,
                      outline=theme.PURPLE_DIM, width=10, fill=theme.BG_CARD)

        # Score arc (0=top, clockwise)
        extent = (score / 100) * 270  # max 270 degrees of sweep
        if extent > 0:
            c.create_arc(cx - r, cy - r, cx + r, cy + r,
                         start=135, extent=extent, style="arc",
                         outline=color, width=10)

        # Score text
        c.create_text(cx, cy - 12, text=str(int(score)),
                      font=(theme.FONT_FAMILY, 32, "bold"), fill=color)
        c.create_text(cx, cy + 22, text="/ 100",
                      font=(theme.FONT_FAMILY, 12), fill=theme.TEXT_MUTED)

    def refresh(self):
        summary = self.app_state.get("summary")
        if not summary:
            return

        result = compute_faltu_score(summary["category_summary"],
                                     summary["total_expense"])

        score = result["score"]
        color = result.get("color", theme.PURPLE_LIGHT)

        # Animate ring and bar
        self._draw_score_ring(score, color)
        self._score_bar._color = color
        self._score_bar.animate_to(score)

        self._verdict_label.config(text=result["verdict"], fg=color)
        self._message_label.config(text=result["message"], fg=theme.TEXT_PRIMARY)
        self._faltu_amount_label.config(text=f"₹{result['faltu_amount']:,.0f}")
        self._faltu_pct_label.config(
            text=f"{result['faltu_percent']:.1f}% of total spending")

        # Breakdown
        for w in self._breakdown_frame.winfo_children():
            w.destroy()

        breakdown = result["breakdown"]
        if not breakdown:
            make_label(self._breakdown_frame,
                       "✅  No flagged categories found!", style="success").pack(pady=theme.PAD_LG)
            return

        total_exp = summary["total_expense"]
        for cat, amt in sorted(breakdown.items(), key=lambda x: -x[1]):
            pct = (amt / total_exp * 100) if total_exp > 0 else 0
            row = tk.Frame(self._breakdown_frame, bg=theme.BG_CARD)
            row.pack(fill="x", pady=4)
            tk.Label(row, text="⚠️", font=theme.FONT_BODY, bg=theme.BG_CARD).pack(side="left")
            tk.Label(row, text=cat, font=theme.FONT_BODY, fg=theme.TEXT_PRIMARY,
                     bg=theme.BG_CARD, width=18, anchor="w").pack(side="left", padx=6)
            bar = NeonProgressBar(row, width=200, height=10, color=theme.DANGER)
            bar.pack(side="left")
            bar.animate_to(min(pct * 2, 100))
            tk.Label(row, text=f"₹{amt:,.0f} ({pct:.1f}%)",
                     font=theme.FONT_SMALL, fg=theme.DANGER, bg=theme.BG_CARD).pack(side="left", padx=8)
