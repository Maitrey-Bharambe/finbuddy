"""
FinBuddy - AI Chatbot Screen
Chat UI powered by Groq API for financial Q&A.
"""

import tkinter as tk
import threading
from datetime import datetime

import ui.theme as theme
from ui.components import make_label, make_button, make_card, make_separator
from api.groq_client import get_ai_response
from logic.analysis import build_ai_context


QUICK_PROMPTS = [
    "Analyze my spending",
    "How can I save more?",
    "What's my biggest expense?",
    "Give me a 30-day savings plan",
    "Am I spending too much on food?",
]


class ChatbotScreen(tk.Frame):
    def __init__(self, parent, app_state: dict, **kwargs):
        super().__init__(parent, bg=theme.BG_DARK, **kwargs)
        self.app_state = app_state
        self._chat_history = []
        self._build()

    def _build(self):
        # Header
        header = tk.Frame(self, bg=theme.BG_DARK)
        header.pack(fill="x", padx=theme.PAD_XL, pady=(theme.PAD_XL, theme.PAD_MD))
        tk.Label(header, text="🤖 AI Buddy", font=theme.FONT_TITLE,
                 fg=theme.TEXT_PRIMARY, bg=theme.BG_DARK).pack(side="left")
        status = tk.Frame(header, bg=theme.BG_CARD, padx=10, pady=4)
        status.pack(side="right")
        self._status_dot = tk.Label(status, text="●", font=(theme.FONT_FAMILY, 10),
                                    fg=theme.TEAL, bg=theme.BG_CARD)
        self._status_dot.pack(side="left")
        tk.Label(status, text="Groq LLM", font=theme.FONT_SMALL,
                 fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(side="left", padx=4)

        make_separator(self).pack(fill="x", padx=theme.PAD_XL, pady=4)

        # Chat area
        chat_frame = tk.Frame(self, bg=theme.BG_DARK)
        chat_frame.pack(fill="both", expand=True, padx=theme.PAD_XL, pady=(0, 0))

        # Messages canvas with scrollbar
        msg_canvas = tk.Canvas(chat_frame, bg=theme.BG_DARK, highlightthickness=0)
        scrollbar = tk.Scrollbar(chat_frame, orient="vertical", command=msg_canvas.yview)
        self._msg_frame = tk.Frame(msg_canvas, bg=theme.BG_DARK)
        self._msg_frame_id = msg_canvas.create_window((0, 0), window=self._msg_frame,
                                                       anchor="nw")

        self._msg_frame.bind("<Configure>", lambda e: (
            msg_canvas.configure(scrollregion=msg_canvas.bbox("all")),
        ))
        msg_canvas.bind("<Configure>", lambda e: msg_canvas.itemconfig(
            self._msg_frame_id, width=e.width))
        msg_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        msg_canvas.pack(side="left", fill="both", expand=True)
        self._msg_canvas = msg_canvas

        # Mousewheel support (only when mouse is over canvas)
        def _on_mousewheel(event):
            msg_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        msg_canvas.bind('<Enter>', lambda e: msg_canvas.bind_all("<MouseWheel>", _on_mousewheel))
        msg_canvas.bind('<Leave>', lambda e: msg_canvas.unbind_all("<MouseWheel>"))

        # ─── Welcome message ──────────────────────────────────────────────
        self._add_bot_message(
            "Hey! 👋 I'm FinBuddy — your AI financial advisor.\n\n"
            "Upload a CSV from the Analysis tab and I'll give you personalised insights. "
            "Or just ask me anything about money, savings, or budgeting!"
        )

        # ─── Quick prompts ────────────────────────────────────────────────
        quick_frame = tk.Frame(self, bg=theme.BG_DARK)
        quick_frame.pack(fill="x", padx=theme.PAD_XL, pady=(theme.PAD_MD, 0))
        tk.Label(quick_frame, text="Quick prompts:", font=theme.FONT_SMALL,
                 fg=theme.TEXT_MUTED, bg=theme.BG_DARK).pack(side="left")
        for prompt in QUICK_PROMPTS:
            btn = tk.Button(quick_frame, text=prompt, font=theme.FONT_TINY,
                            bg=theme.BG_HOVER, fg=theme.PURPLE_LIGHT, activebackground=theme.PURPLE_DIM,
                            activeforeground=theme.TEXT_PRIMARY, bd=0, padx=8, pady=4,
                            cursor="hand2",
                            command=lambda p=prompt: self._quick_send(p))
            btn.pack(side="left", padx=3)

        # ─── Input area ───────────────────────────────────────────────────
        input_frame = tk.Frame(self, bg=theme.BG_DARK)
        input_frame.pack(fill="x", padx=theme.PAD_XL, pady=theme.PAD_MD)

        input_card = make_card(input_frame)
        input_card.pack(fill="x")
        inner = tk.Frame(input_card, bg=theme.BG_CARD)
        inner.pack(fill="x", padx=theme.PAD_MD, pady=theme.PAD_MD)

        self._input_var = tk.StringVar()
        self._input_box = tk.Entry(inner, textvariable=self._input_var,
                                   font=theme.FONT_BODY, bg=theme.BG_INPUT, fg=theme.TEXT_PRIMARY,
                                   insertbackground=theme.PURPLE_LIGHT, bd=0, relief="flat",
                                   highlightthickness=0)
        self._input_box.pack(side="left", fill="both", expand=True,
                             ipady=10, padx=(theme.PAD_MD, 0))
        self._input_box.insert(0, "Ask FinBuddy anything...")
        self._input_box.config(fg=theme.TEXT_DISABLED)
        self._input_box.bind("<FocusIn>", self._on_input_focus)
        self._input_box.bind("<FocusOut>", self._on_input_blur)
        self._input_box.bind("<Return>", lambda e: self._send_message())

        self._send_btn = make_button(inner, "Send →", self._send_message,
                                     variant="primary")
        self._send_btn.pack(side="right", padx=theme.PAD_MD)

        make_separator(self).pack(fill="x", padx=theme.PAD_XL, pady=(0, 4))

    def _on_input_focus(self, event):
        if self._input_box.get() == "Ask FinBuddy anything...":
            self._input_box.delete(0, "end")
            self._input_box.config(fg=theme.TEXT_PRIMARY)

    def _on_input_blur(self, event):
        if not self._input_box.get():
            self._input_box.insert(0, "Ask FinBuddy anything...")
            self._input_box.config(fg=theme.TEXT_DISABLED)

    def _quick_send(self, text: str):
        self._input_box.delete(0, "end")
        self._input_box.insert(0, text)
        self._input_box.config(fg=theme.TEXT_PRIMARY)
        self._send_message()

    def _send_message(self):
        text = self._input_var.get().strip()
        if not text or text == "Ask FinBuddy anything...":
            return

        self._input_box.delete(0, "end")
        self._add_user_message(text)
        self._input_box.config(state="disabled")
        self._send_btn.config(state="disabled")
        self._add_typing_indicator()

        api_key = self.app_state.get("groq_api_key", "")
        summary = self.app_state.get("summary")
        context = build_ai_context(summary) if summary else ""

        def _worker():
            response, error = get_ai_response(text, api_key, context)
            self.after(0, lambda: self._on_response(response))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_response(self, response: str):
        self._remove_typing_indicator()
        self._add_bot_message(response)
        self._input_box.config(state="normal")
        self._send_btn.config(state="normal")
        self._scroll_to_bottom()

    def _add_user_message(self, text: str):
        self._render_message(text, role="user")
        self._chat_history.append({"role": "user", "text": text})
        self._scroll_to_bottom()

    def _add_bot_message(self, text: str):
        self._render_message(text, role="bot")
        self._chat_history.append({"role": "bot", "text": text})
        self._scroll_to_bottom()

    def _render_message(self, text: str, role: str):
        outer = tk.Frame(self._msg_frame, bg=theme.BG_DARK)
        outer.pack(fill="x", padx=theme.PAD_MD, pady=4)

        if role == "user":
            bubble = tk.Frame(outer, bg=theme.PURPLE_DIM, padx=14, pady=10)
            bubble.pack(side="right")
            tk.Label(bubble, text=text, font=theme.FONT_BODY, fg=theme.TEXT_PRIMARY,
                     bg=theme.PURPLE_DIM, wraplength=480, justify="left",
                     anchor="w").pack()
        else:
            row = tk.Frame(outer, bg=theme.BG_DARK)
            row.pack(side="left", fill="x")
            tk.Label(row, text="🤖", font=(theme.FONT_FAMILY, 16), bg=theme.BG_DARK).pack(
                side="left", anchor="n", padx=(0, 8))
            bubble = tk.Frame(row, bg=theme.BG_CARD, padx=14, pady=10,
                              highlightthickness=1, highlightbackground=theme.PURPLE_DIM)
            bubble.pack(side="left", fill="x")
            tk.Label(bubble, text=text, font=theme.FONT_BODY, fg=theme.TEXT_PRIMARY,
                     bg=theme.BG_CARD, wraplength=520, justify="left", anchor="w").pack()

    def _add_typing_indicator(self):
        self._typing_frame = tk.Frame(self._msg_frame, bg=theme.BG_DARK)
        self._typing_frame.pack(fill="x", padx=theme.PAD_MD, pady=4, anchor="w")
        row = tk.Frame(self._typing_frame, bg=theme.BG_DARK)
        row.pack(side="left")
        tk.Label(row, text="🤖", font=(theme.FONT_FAMILY, 16), bg=theme.BG_DARK).pack(side="left", padx=(0, 8))
        bubble = tk.Frame(row, bg=theme.BG_CARD, padx=14, pady=10,
                          highlightthickness=1, highlightbackground=theme.PURPLE_DIM)
        bubble.pack(side="left")
        self._typing_label = tk.Label(bubble, text="Thinking...",
                                      font=theme.FONT_BODY, fg=theme.PURPLE_LIGHT, bg=theme.BG_CARD)
        self._typing_label.pack()
        self._animate_typing()
        self._scroll_to_bottom()

    def _animate_typing(self, count=0):
        dots = "." * (count % 4)
        if hasattr(self, "_typing_label") and self._typing_label.winfo_exists():
            self._typing_label.config(text=f"Thinking{dots}")
            self._typing_anim_id = self.after(400, lambda: self._animate_typing(count + 1))

    def _remove_typing_indicator(self):
        if hasattr(self, "_typing_anim_id"):
            self.after_cancel(self._typing_anim_id)
        if hasattr(self, "_typing_frame") and self._typing_frame.winfo_exists():
            self._typing_frame.destroy()

    def _scroll_to_bottom(self):
        self.after(50, lambda: self._msg_canvas.yview_moveto(1.0))

    def refresh(self):
        pass
