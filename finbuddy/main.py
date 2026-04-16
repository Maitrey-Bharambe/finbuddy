
import tkinter as tk
from tkinter import ttk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ui.theme as theme


APP_STATE: dict = {
    "df": None,
    "summary": None,
    "csv_path": None,
    "groq_api_key": "",
    "streak": 3,          # mock streak counter
}

def load_env():
    """Simple .env loader to populate APP_STATE."""
    try:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        k, v = line.strip().split("=", 1)
                        if k.strip() == "groq_api_key":
                            APP_STATE["groq_api_key"] = v.strip()
    except Exception as e:
        print(f"Error loading .env: {e}")

load_env()


class WelcomeScreen(tk.Frame):
    def __init__(self, parent, on_start, on_upload, on_skip, **kwargs):
        super().__init__(parent, bg=theme.BG_DARK, **kwargs)
        self._on_start  = on_start
        self._on_upload = on_upload
        self._on_skip   = on_skip
        self._build()

    def _build(self):
        spacer_top = tk.Frame(self, bg=theme.BG_DARK)
        spacer_top.pack(expand=True)

        center = tk.Frame(self, bg=theme.BG_DARK)
        center.pack()

        tk.Label(center, text="💜", font=(theme.FONT_FAMILY, 64), bg=theme.BG_DARK).pack()

        tk.Label(center, text="FinBuddy", font=(theme.FONT_FAMILY, 44, "bold"),
                 fg=theme.PURPLE_LIGHT, bg=theme.BG_DARK).pack(pady=(theme.PAD_SM, 0))

        tk.Label(center, text="A buddy that grows your money",
                 font=(theme.FONT_FAMILY, 16), fg=theme.TEAL, bg=theme.BG_DARK).pack(pady=(4, theme.PAD_XL))

        badges_frame = tk.Frame(center, bg=theme.BG_DARK)
        badges_frame.pack(pady=(0, theme.PAD_XL))
        for badge in ["📊  Smart Analytics", "🤖  AI-Powered Advice", "🚫  Faltu Detector", "🔥  Gamified Goals"]:
            tk.Label(badges_frame, text=badge, font=theme.FONT_BODY,
                     fg=theme.TEXT_MUTED, bg=theme.BG_DARK, padx=theme.PAD_MD).pack(side="left")

        btn_row = tk.Frame(center, bg=theme.BG_DARK)
        btn_row.pack(pady=theme.PAD_MD)

        self._make_big_btn(btn_row, "🚀  Start", self._on_start,
                           bg=theme.PURPLE, fg="#ffffff", hover=theme.PURPLE_LIGHT).pack(
            side="left", padx=theme.PAD_MD)
        self._make_big_btn(btn_row, "📂  Upload CSV", self._on_upload,
                           bg=theme.BG_CARD, fg=theme.TEAL,
                           hover=theme.BG_HOVER).pack(side="left", padx=theme.PAD_MD)
        self._make_big_btn(btn_row, "Continue without data", self._on_skip,
                           bg=theme.BG_DARK, fg=theme.TEXT_MUTED,
                           hover=theme.BG_HOVER).pack(side="left", padx=theme.PAD_MD)

        spacer_bot = tk.Frame(self, bg=theme.BG_DARK)
        spacer_bot.pack(expand=True)

        tk.Label(self, text="Built with Python · Tkinter · Groq AI",
                 font=theme.FONT_TINY, fg=theme.TEXT_DISABLED, bg=theme.BG_DARK).pack(pady=theme.PAD_MD)

    def _make_big_btn(self, parent, text, command, bg, fg, hover):
        btn = tk.Button(parent, text=text, command=command,
                        font=theme.FONT_SUBHEAD, bg=bg, fg=fg,
                        activebackground=hover, activeforeground=fg,
                        bd=0, padx=theme.PAD_XL, pady=theme.PAD_MD,
                        cursor="hand2", relief="flat")
        btn.bind("<Enter>", lambda e: btn.config(bg=hover))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn


class FinBuddyApp(tk.Frame):
    """
    The main application shell containing:
    - A fixed left sidebar with navigation
    - A right content area where screens are swapped in/out
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=theme.BG_DARK, **kwargs)
        self._screens: dict[str, tk.Frame] = {}
        self._active_screen = None
        self._nav_buttons: dict[str, tk.Button] = {}
        self._build()

    def _build(self):
        self._sidebar = tk.Frame(self, bg=theme.BG_CARD, width=theme.SIDEBAR_W,
                            highlightthickness=1,
                            highlightbackground=theme.PURPLE_DIM)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        self._logo_frame = tk.Frame(self._sidebar, bg=theme.BG_CARD, pady=theme.PAD_LG)
        self._logo_frame.pack(fill="x")
        self._logo_icon = tk.Label(self._logo_frame, text="💜", font=(theme.FONT_FAMILY, 22), bg=theme.BG_CARD)
        self._logo_icon.pack()
        self._logo_text = tk.Label(self._logo_frame, text="FinBuddy", font=(theme.FONT_FAMILY, 16, "bold"),
                 fg=theme.PURPLE_LIGHT, bg=theme.BG_CARD)
        self._logo_text.pack()

        self._sep1 = tk.Frame(self._sidebar, bg=theme.PURPLE_DIM, height=1)
        self._sep1.pack(fill="x")

        for icon, label in theme.NAV_ITEMS:
            full = f"{icon}  {label}"
            btn = tk.Button(
                self._sidebar, text=full, font=theme.FONT_BODY,
                bg=theme.BG_CARD, fg=theme.TEXT_MUTED,
                activebackground=theme.BG_HOVER, activeforeground=theme.TEXT_PRIMARY,
                bd=0, anchor="w", padx=theme.PAD_LG, pady=theme.PAD_MD,
                cursor="hand2", relief="flat",
                command=lambda l=label: self.show_screen(l)
            )
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: (
                b.config(bg=theme.BG_HOVER) if b != self._get_active_btn() else None))
            btn.bind("<Leave>", lambda e, b=btn: (
                b.config(bg=theme.BG_HOVER if b == self._get_active_btn() else theme.BG_CARD)))
            self._nav_buttons[label] = btn

        self._footer_spacer = tk.Frame(self._sidebar, bg=theme.BG_CARD)
        self._footer_spacer.pack(expand=True)
        self._sep2 = tk.Frame(self._sidebar, bg=theme.PURPLE_DIM, height=1)
        self._sep2.pack(fill="x")
        self._version_label = tk.Label(self._sidebar, text="v1.0.0", font=theme.FONT_TINY,
                 fg=theme.TEXT_DISABLED, bg=theme.BG_CARD)
        self._version_label.pack(pady=theme.PAD_MD)

        self._content_area = tk.Frame(self, bg=theme.BG_DARK)
        self._content_area.pack(side="left", fill="both", expand=True)

        self._init_screens()
        self.show_screen("Dashboard")

    def _init_screens(self):
        from ui.dashboard   import DashboardScreen
        from ui.upload      import AnalysisScreen
        from ui.faltu_meter import FaltuMeterScreen
        from ui.chatbot     import ChatbotScreen
        from ui.settings    import SettingsScreen

        def _on_data_loaded(summary):
            """Callback when CSV is successfully loaded in AnalysisScreen."""
            APP_STATE["summary"] = summary
            self._screens["Dashboard"].refresh()
            self._screens["Faltu Meter"].refresh()

        self._screens["Dashboard"]   = DashboardScreen(self._content_area, APP_STATE)
        self._screens["Analysis"]    = AnalysisScreen(self._content_area, APP_STATE,
                                                      on_data_loaded=_on_data_loaded)
        self._screens["Faltu Meter"] = FaltuMeterScreen(self._content_area, APP_STATE)
        self._screens["AI Buddy"]    = ChatbotScreen(self._content_area, APP_STATE)
        self._screens["Settings"]    = SettingsScreen(self._content_area, APP_STATE)

    def _get_active_btn(self):
        return self._nav_buttons.get(self._active_screen)

    def show_screen(self, name: str):
        if name not in self._screens:
            return

        # Hide current
        if self._active_screen and self._active_screen in self._screens:
            self._screens[self._active_screen].pack_forget()
            old_btn = self._nav_buttons.get(self._active_screen)
            if old_btn:
                import ui.theme as theme
                old_btn.config(bg=theme.BG_CARD, fg=theme.TEXT_MUTED)

        # Show new
        self._active_screen = name
        self._screens[name].pack(fill="both", expand=True)
        self._screens[name].refresh()

        new_btn = self._nav_buttons.get(name)
        if new_btn:
            import ui.theme as theme
            new_btn.config(bg=theme.BG_HOVER, fg=theme.PURPLE_LIGHT)

    def toggle_theme(self, mode):
        theme.set_theme(mode)
        
        self.config(bg=theme.BG_DARK)
        self._content_area.config(bg=theme.BG_DARK)
        
        self._sidebar.config(bg=theme.BG_CARD, highlightbackground=theme.PURPLE_DIM)
        self._logo_frame.config(bg=theme.BG_CARD)
        self._logo_icon.config(bg=theme.BG_CARD)
        self._logo_text.config(fg=theme.PURPLE_LIGHT, bg=theme.BG_CARD)
        self._sep1.config(bg=theme.PURPLE_DIM)
        self._sep2.config(bg=theme.PURPLE_DIM)
        self._footer_spacer.config(bg=theme.BG_CARD)
        self._version_label.config(fg=theme.TEXT_DISABLED, bg=theme.BG_CARD)

        for screen in self._screens.values():
            screen.pack_forget()
            screen.destroy()
        self._screens.clear()
        self._init_screens()
        
        self.show_screen(self._active_screen)
        
        for label, btn in self._nav_buttons.items():
            btn.config(bg=theme.BG_CARD, fg=theme.TEXT_MUTED, font=theme.FONT_BODY,
                       activebackground=theme.BG_HOVER, activeforeground=theme.TEXT_PRIMARY)
            if label == self._active_screen:
                btn.config(bg=theme.BG_HOVER, fg=theme.PURPLE_LIGHT)


def main():
    root = tk.Tk()
    root.title("FinBuddy 💜")
    root.geometry("1200x760")
    root.minsize(900, 600)
    root.configure(bg=theme.BG_DARK)

    try:
        root.tk.call("tk", "scaling", 1.2)
    except Exception:
        pass

    welcome: WelcomeScreen | None = None
    app_shell: FinBuddyApp | None = None

    def launch_app(upload_immediately=False):
        nonlocal welcome, app_shell
        if welcome:
            welcome.pack_forget()
            welcome.destroy()
            welcome = None

        app_shell = FinBuddyApp(root)
        app_shell.pack(fill="both", expand=True)

        if upload_immediately:
            root.after(200, lambda: app_shell.show_screen("Analysis"))

    welcome = WelcomeScreen(
        root,
        on_start=lambda: launch_app(False),
        on_upload=lambda: launch_app(True),
        on_skip=lambda: launch_app(False),
    )
    welcome.pack(fill="both", expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()
