"""
FinBuddy - Reusable UI Components
Custom widgets built on top of Tkinter for the FinBuddy theme.
"""

import tkinter as tk
from tkinter import ttk
import ui.theme as theme


def make_card(parent, **kwargs) -> tk.Frame:
    """A styled card frame."""
    defaults = dict(bg=theme.BG_CARD, bd=0, highlightthickness=1,
                    highlightbackground=theme.PURPLE_DIM)
    defaults.update(kwargs)
    return tk.Frame(parent, **defaults)


def make_label(parent, text="", style="body", **kwargs) -> tk.Label:
    """Create a themed label. style: title|heading|body|muted|teal|success|warning|danger"""
    style_map = {
        "title":    dict(font=theme.FONT_TITLE,    fg=theme.TEXT_PRIMARY,  bg=theme.BG_DARK),
        "heading":  dict(font=theme.FONT_HEADING,  fg=theme.TEXT_PRIMARY,  bg=theme.BG_CARD),
        "subhead":  dict(font=theme.FONT_SUBHEAD,  fg=theme.TEXT_PRIMARY,  bg=theme.BG_CARD),
        "body":     dict(font=theme.FONT_BODY,     fg=theme.TEXT_PRIMARY,  bg=theme.BG_CARD),
        "muted":    dict(font=theme.FONT_BODY,     fg=theme.TEXT_MUTED,    bg=theme.BG_CARD),
        "small":    dict(font=theme.FONT_SMALL,    fg=theme.TEXT_MUTED,    bg=theme.BG_CARD),
        "teal":     dict(font=theme.FONT_BODY,     fg=theme.TEAL,          bg=theme.BG_CARD),
        "purple":   dict(font=theme.FONT_BODY,     fg=theme.PURPLE_LIGHT,  bg=theme.BG_CARD),
        "success":  dict(font=theme.FONT_BODY,     fg=theme.SUCCESS,       bg=theme.BG_CARD),
        "warning":  dict(font=theme.FONT_BODY,     fg=theme.WARNING,       bg=theme.BG_CARD),
        "danger":   dict(font=theme.FONT_BODY,     fg=theme.DANGER,        bg=theme.BG_CARD),
        "bignum":   dict(font=theme.FONT_BIG_NUM,  fg=theme.TEAL,          bg=theme.BG_CARD),
        "mednum":   dict(font=theme.FONT_MED_NUM,  fg=theme.TEXT_PRIMARY,  bg=theme.BG_CARD),
    }
    cfg = style_map.get(style, style_map["body"]).copy()
    cfg.update(kwargs)
    return tk.Label(parent, text=text, **cfg)


def make_button(parent, text, command=None, variant="primary", **kwargs) -> tk.Button:
    """
    Create a styled button.
    variant: primary | secondary | ghost | danger
    """
    variants = {
        "primary":   dict(bg=theme.PURPLE,      fg="#ffffff", activebackground=theme.PURPLE_LIGHT, activeforeground="#ffffff"),
        "secondary": dict(bg=theme.BG_HOVER,    fg=theme.TEAL,      activebackground=theme.PURPLE_DIM,  activeforeground=theme.TEAL),
        "ghost":     dict(bg=theme.BG_CARD,     fg=theme.TEXT_MUTED,activebackground=theme.BG_HOVER,    activeforeground=theme.TEXT_PRIMARY),
        "danger":    dict(bg="#3d0808",   fg=theme.DANGER,    activebackground="#550000",   activeforeground=theme.DANGER),
        "teal":      dict(bg="#003d33",   fg=theme.TEAL,      activebackground="#005248",   activeforeground=theme.TEAL),
    }
    cfg = variants.get(variant, variants["primary"]).copy()
    cfg.update(dict(
        font=theme.FONT_SUBHEAD, bd=0, cursor="hand2", padx=theme.PAD_MD, pady=8,
        relief="flat", command=command
    ))
    cfg.update(kwargs)
    return tk.Button(parent, text=text, **cfg)


class NeonProgressBar(tk.Canvas):
    """
    A custom neon-style horizontal progress bar.
    """
    def __init__(self, parent, width=200, height=18, color=None, bg_color=None, **kwargs):
        color = color or theme.PURPLE
        bg_color = bg_color or theme.BG_CARD
        super().__init__(parent, width=width, height=height,
                         bg=bg_color, highlightthickness=0, **kwargs)
        self._canvas_width = width
        self._canvas_height = height
        self._color = color
        self._bg_color = bg_color
        self._value = 0
        self._draw(0)

    def _draw(self, pct: float):
        self.delete("all")
        r = self._canvas_height // 2
        # Track
        self.create_rectangle(0, 2, self._canvas_width, self._canvas_height - 2,
                               fill="#1a1a26", outline="#2a2a3e")
        # Fill
        fill_w = max(r * 2, int(self._canvas_width * pct / 100))
        if fill_w > 0:
            self.create_rectangle(0, 2, fill_w, self._canvas_height - 2,
                                   fill=self._color, outline="")
            # Glow highlight
            self.create_rectangle(0, 2, fill_w, 6,
                                   fill=self._brighten(self._color), outline="")

    def _brighten(self, hex_color: str) -> str:
        """Return a slightly brighter version of a hex color."""
        try:
            r = min(255, int(hex_color[1:3], 16) + 40)
            g = min(255, int(hex_color[3:5], 16) + 40)
            b = min(255, int(hex_color[5:7], 16) + 40)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color

    def set_value(self, value: float):
        """Set progress bar value (0-100)."""
        self._value = max(0, min(100, value))
        self._draw(self._value)

    def animate_to(self, target: float, steps: int = 30, delay: int = 16):
        """Animate the bar to a target value."""
        target = max(0, min(100, target))
        step_size = (target - self._value) / max(steps, 1)

        def _step(current_val, remaining):
            if remaining <= 0:
                self.set_value(target)
                return
            current_val += step_size
            self.set_value(current_val)
            self.after(delay, lambda: _step(current_val, remaining - 1))

        _step(self._value, steps)


class StatCard(tk.Frame):
    """A compact stat card with label, value, and optional sub-label."""
    def __init__(self, parent, label, value, sub="", value_color=None, **kwargs):
        value_color = value_color or theme.TEAL
        super().__init__(parent, bg=theme.BG_CARD, bd=0,
                         highlightthickness=1, highlightbackground=theme.PURPLE_DIM,
                         **kwargs)
        tk.Label(self, text=label, font=theme.FONT_SMALL, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(
            anchor="w", padx=theme.PAD_MD, pady=(theme.PAD_MD, 2))
        self._val_label = tk.Label(self, text=value, font=theme.FONT_BIG_NUM,
                                   fg=value_color, bg=theme.BG_CARD)
        self._val_label.pack(anchor="w", padx=theme.PAD_MD)
        if sub:
            tk.Label(self, text=sub, font=theme.FONT_TINY, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(
                anchor="w", padx=theme.PAD_MD, pady=(0, theme.PAD_MD))
        else:
            tk.Label(self, text="", font=theme.FONT_TINY, bg=theme.BG_CARD).pack(pady=(0, theme.PAD_SM))

    def update_value(self, value, color=None):
        self._val_label.config(text=value)
        if color:
            self._val_label.config(fg=color)


def make_separator(parent, orientation="horizontal") -> tk.Frame:
    if orientation == "horizontal":
        return tk.Frame(parent, bg=theme.PURPLE_DIM, height=1)
    return tk.Frame(parent, bg=theme.PURPLE_DIM, width=1)


def scrollable_frame(parent, **kwargs) -> tuple[tk.Canvas, tk.Frame]:
    """
    Returns (canvas, inner_frame). Pack the canvas in the parent,
    use inner_frame as the scrollable container.
    """
    bg = kwargs.get("bg", theme.BG_CARD)
    canvas = tk.Canvas(parent, bg=bg, highlightthickness=0)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg=bg)

    inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")

    def _on_configure(e):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(inner_id, width=canvas.winfo_width())

    inner.bind("<Configure>", _on_configure)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    def _on_mousewheel(e):
        canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    return canvas, inner
