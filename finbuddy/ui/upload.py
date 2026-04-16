"""
FinBuddy - CSV Upload & Analysis Screen
Handles file selection, data display, and embedded Matplotlib charts.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import threading

import ui.theme as theme
from ui.components import make_label, make_button, make_card, make_separator, NeonProgressBar
from logic.analysis import load_csv, compute_summary, build_ai_context
from api.groq_client import get_ai_response
import pandas as pd
from datetime import datetime


class AnalysisScreen(tk.Frame):
    def __init__(self, parent, app_state: dict, on_data_loaded=None, **kwargs):
        super().__init__(parent, bg=theme.BG_DARK, **kwargs)
        self.app_state = app_state
        self.on_data_loaded = on_data_loaded
        self._build()

    def _build(self):
        # Header
        header = tk.Frame(self, bg=theme.BG_DARK)
        header.pack(fill="x", padx=theme.PAD_XL, pady=(theme.PAD_XL, theme.PAD_MD))

        tk.Label(header, text="📊 Analysis", font=theme.FONT_TITLE,
                 fg=theme.TEXT_PRIMARY, bg=theme.BG_DARK).pack(side="left")
        
        btn_row = tk.Frame(header, bg=theme.BG_DARK)
        btn_row.pack(side="right")

        make_button(btn_row, "➕  Add Manually", self._manual_entry_form,
                    variant="teal").pack(side="left", padx=theme.PAD_SM)
        make_button(btn_row, "📂  Upload CSV", self._upload_csv,
                    variant="primary").pack(side="left")

        make_separator(self).pack(fill="x", padx=theme.PAD_XL, pady=4)

        # Status bar
        self._status_frame = make_card(self)
        self._status_frame.pack(fill="x", padx=theme.PAD_XL, pady=theme.PAD_MD)
        self._status_label = make_label(
            self._status_frame,
            "📂  No file loaded. Click 'Upload CSV' to begin.",
            style="muted"
        )
        self._status_label.pack(padx=theme.PAD_LG, pady=theme.PAD_MD, anchor="w")

        # Scrollable content area
        container = tk.Frame(self, bg=theme.BG_DARK)
        container.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(container, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self._scroll_canvas = tk.Canvas(container, bg=theme.BG_DARK, highlightthickness=0,
                                        yscrollcommand=scrollbar.set)
        self._scroll_canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar.config(command=self._scroll_canvas.yview)

        self._content = tk.Frame(self._scroll_canvas, bg=theme.BG_DARK)
        self._content_id = self._scroll_canvas.create_window(
            (0, 0), window=self._content, anchor="nw")

        self._content.bind("<Configure>", lambda e: self._scroll_canvas.configure(
            scrollregion=self._scroll_canvas.bbox("all")))
        self._scroll_canvas.bind("<Configure>", lambda e: self._scroll_canvas.itemconfig(
            self._content_id, width=e.width))

        # Mousewheel support (only when mouse is over canvas)
        def _on_mousewheel(event):
            self._scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self._scroll_canvas.bind('<Enter>', lambda e: self._scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel))
        self._scroll_canvas.bind('<Leave>', lambda e: self._scroll_canvas.unbind_all("<MouseWheel>"))

        # Initial empty state
        self._show_empty_state()

    def _show_empty_state(self):
        for w in self._content.winfo_children():
            w.destroy()
        frame = tk.Frame(self._content, bg=theme.BG_DARK)
        frame.pack(expand=True, pady=theme.PAD_XL * 2)
        tk.Label(frame, text="📊", font=(theme.FONT_FAMILY, 48), bg=theme.BG_DARK).pack()
        tk.Label(frame, text="Upload a CSV to unlock your financial insights",
                 font=theme.FONT_HEADING, fg=theme.TEXT_MUTED, bg=theme.BG_DARK).pack(pady=theme.PAD_MD)
        tk.Label(frame,
                 text="Expected columns: Date, Category, Amount, Type (Income/Expense)",
                 font=theme.FONT_SMALL, fg=theme.TEXT_DISABLED, bg=theme.BG_DARK).pack()
        make_button(frame, "📂  Upload CSV", self._upload_csv,
                    variant="primary").pack(pady=theme.PAD_SM)
        make_button(frame, "➕  Add Transaction Manually", self._manual_entry_form,
                    variant="teal").pack(pady=theme.PAD_SM)

    def _upload_csv(self):
        path = filedialog.askopenfilename(
            title="Select Financial CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not path:
            return
        self._status_label.config(text=f"⏳ Loading: {path}", fg=theme.TEXT_MUTED)
        self.update_idletasks()
        threading.Thread(target=self._load_file, args=(path,), daemon=True).start()

    def _load_file(self, path: str):
        df, error = load_csv(path)
        if error:
            self.after(0, lambda: self._on_load_error(error))
        else:
            summary = compute_summary(df)
            self.after(0, lambda: self._on_load_success(path, df, summary))

    def _on_load_error(self, error: str):
        self._status_label.config(
            text=f"❌ Error: {error}", fg=theme.DANGER)
        messagebox.showerror("CSV Error", error)

    def _on_load_success(self, path: str, df, summary: dict):
        # Update app_state
        self.app_state["df"] = df
        self.app_state["summary"] = summary
        self.app_state["csv_path"] = path

        fname = path.split("/")[-1].split("\\")[-1]
        self._status_label.config(
            text=f"✅  Loaded: {fname}  |  {len(df)} transactions  |  "
                 f"₹{summary['total_income']:,.0f} income  |  "
                 f"₹{summary['total_expense']:,.0f} expenses",
            fg=theme.SUCCESS
        )

        if self.on_data_loaded:
            self.on_data_loaded(summary)

        self._render_analysis(summary)

    def _render_analysis(self, summary: dict):
        for w in self._content.winfo_children():
            w.destroy()

        # ─── Analysis Header Row ──────────────────────────────────────────
        header_row = tk.Frame(self._content, bg=theme.BG_DARK)
        header_row.pack(fill="x", padx=theme.PAD_XL, pady=(theme.PAD_MD, 0))
        
        make_label(header_row, "Financial Insights", style="heading").pack(side="left")
        
        make_button(header_row, "✨ Get AI Analysis", self._run_ai_analysis,
                    variant="primary", font=theme.FONT_SMALL).pack(side="right")

        # ─── Summary row ──────────────────────────────────────────────────
        row1 = tk.Frame(self._content, bg=theme.BG_DARK)
        row1.pack(fill="x", padx=theme.PAD_XL, pady=theme.PAD_MD)

        for label, value, color in [
            ("💰 Income",   f"₹{summary['total_income']:,.0f}",   theme.SUCCESS),
            ("💸 Expenses", f"₹{summary['total_expense']:,.0f}",  theme.DANGER),
            ("🏦 Savings",  f"₹{summary['savings']:,.0f}",        theme.TEAL),
            ("📈 Rate",     f"{summary['savings_rate']:.1f}%",    theme.PURPLE_LIGHT),
        ]:
            card = make_card(row1, padx=theme.PAD_MD, pady=theme.PAD_MD)
            card.pack(side="left", expand=True, fill="both", padx=6)
            tk.Label(card, text=label, font=theme.FONT_SMALL, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack()
            tk.Label(card, text=value, font=theme.FONT_MED_NUM, fg=color, bg=theme.BG_CARD).pack()

        # ─── Charts ───────────────────────────────────────────────────────
        charts_row = tk.Frame(self._content, bg=theme.BG_DARK)
        charts_row.pack(fill="x", padx=theme.PAD_XL, pady=theme.PAD_MD)

        self._render_pie_chart(charts_row, summary)
        self._render_line_chart(charts_row, summary)

        # ─── Category table ───────────────────────────────────────────────
        table_card = make_card(self._content)
        table_card.pack(fill="x", padx=theme.PAD_XL, pady=theme.PAD_MD)
        make_label(table_card, "📋 Category Breakdown", style="heading").pack(
            anchor="w", padx=theme.PAD_LG, pady=(theme.PAD_LG, theme.PAD_MD))
        make_separator(table_card).pack(fill="x", padx=theme.PAD_LG)

        cats = summary["category_summary"]
        total_exp = summary["total_expense"]
        colors_cycle = [theme.PURPLE_LIGHT, theme.TEAL, theme.WARNING, theme.INFO, theme.DANGER, theme.SUCCESS]

        for i, (cat, amt) in enumerate(cats.items()):
            pct = (amt / total_exp * 100) if total_exp > 0 else 0
            row = tk.Frame(table_card, bg=theme.BG_CARD)
            row.pack(fill="x", padx=theme.PAD_LG, pady=4)

            color = colors_cycle[i % len(colors_cycle)]
            dot = tk.Label(row, text="●", font=theme.FONT_BODY, fg=color, bg=theme.BG_CARD)
            dot.pack(side="left")
            tk.Label(row, text=cat, font=theme.FONT_BODY, fg=theme.TEXT_PRIMARY,
                     bg=theme.BG_CARD, width=20, anchor="w").pack(side="left", padx=8)
            bar = NeonProgressBar(row, width=200, height=10, color=color)
            bar.pack(side="left")
            bar.animate_to(pct)
            tk.Label(row, text=f"₹{amt:,.0f}  ({pct:.1f}%)",
                     font=theme.FONT_SMALL, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(side="left", padx=8)

        tk.Frame(table_card, bg=theme.BG_CARD, height=theme.PAD_LG).pack()
        tk.Frame(self._content, bg=theme.BG_DARK, height=theme.PAD_XL).pack()

    def _render_pie_chart(self, parent, summary):
        try:
            import matplotlib
            matplotlib.use("TkAgg")
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            card = make_card(parent)
            card.pack(side="left", expand=True, fill="both", padx=6)
            make_label(card, "Category Distribution", style="subhead").pack(
                anchor="w", padx=theme.PAD_MD, pady=(theme.PAD_MD, 0))

            cats = summary["category_summary"]
            if cats.empty:
                make_label(card, "No expense data", style="muted").pack(pady=40)
                return

            fig, ax = plt.subplots(figsize=(4.5, 3.5), facecolor=theme.BG_CARD)
            ax.set_facecolor(theme.BG_CARD)

            colors = ["#8A2BE2", "#00FFD1", "#FFD700", "#60A5FA", "#FF4444",
                      "#a855f7", "#34d399", "#f97316"]
            wedges, texts, autotexts = ax.pie(
                cats.values, labels=cats.index,
                colors=colors[:len(cats)],
                autopct="%1.0f%%", startangle=90,
                textprops=dict(color=theme.TEXT_PRIMARY, fontsize=8),
                wedgeprops=dict(linewidth=0.5, edgecolor=theme.BG_DARK)
            )
            for at in autotexts:
                at.set_color(theme.BG_DARK)
                at.set_fontsize(7)

            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=card)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=theme.PAD_SM, pady=theme.PAD_SM)
            plt.close(fig)

        except ImportError:
            make_label(parent, "matplotlib not installed", style="muted").pack()

    def _render_line_chart(self, parent, summary):
        try:
            import matplotlib
            matplotlib.use("TkAgg")
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            card = make_card(parent)
            card.pack(side="left", expand=True, fill="both", padx=6)
            make_label(card, "Monthly Expenses", style="subhead").pack(
                anchor="w", padx=theme.PAD_MD, pady=(theme.PAD_MD, 0))

            monthly = summary["monthly_expense"]
            if monthly.empty:
                make_label(card, "No expense data", style="muted").pack(pady=40)
                return

            fig, ax = plt.subplots(figsize=(4.5, 3.5), facecolor=theme.BG_CARD)
            ax.set_facecolor(theme.BG_CARD)

            x = range(len(monthly))
            labels = [str(p) for p in monthly.index]
            values = monthly.values

            ax.plot(x, values, color=theme.PURPLE_LIGHT, linewidth=2.5, marker="o",
                    markersize=6, markerfacecolor=theme.TEAL, markeredgecolor=theme.TEAL)
            ax.fill_between(x, values, alpha=0.15, color=theme.PURPLE)
            ax.set_xticks(list(x))
            ax.set_xticklabels(labels, rotation=30, ha="right",
                               fontsize=8, color=theme.TEXT_MUTED)
            ax.tick_params(axis="y", colors=theme.TEXT_MUTED, labelsize=8)
            for spine in ax.spines.values():
                spine.set_edgecolor(theme.PURPLE_DIM)
            ax.yaxis.set_major_formatter(
                plt.FuncFormatter(lambda v, _: f"₹{v/1000:.0f}k"))

            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=card)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=theme.PAD_SM, pady=theme.PAD_SM)
            plt.close(fig)

        except ImportError:
            make_label(parent, "matplotlib not installed", style="muted").pack()

    def _manual_entry_form(self):
        """Show a modal to enter a transaction manually."""
        modal = tk.Toplevel(self)
        modal.title("Add Transaction")
        modal.geometry("400x500")
        modal.configure(bg=theme.BG_CARD)
        modal.transient(self.master)
        modal.grab_set()

        # Center relative to parent
        x = self.winfo_rootx() + (self.winfo_width() // 2) - 200
        y = self.winfo_rooty() + (self.winfo_height() // 2) - 250
        modal.geometry(f"+{x}+{y}")

        make_label(modal, "➕ New Transaction", style="heading").pack(pady=theme.PAD_LG)
        
        fields = {}
        for label, key, default in [
            ("Date (YYYY-MM-DD)", "Date", datetime.now().strftime("%Y-%m-%d")),
            ("Category", "Category", "Food & Drinks"),
            ("Amount (₹)", "Amount", ""),
        ]:
            frame = tk.Frame(modal, bg=theme.BG_CARD, padx=theme.PAD_XL)
            frame.pack(fill="x", pady=5)
            make_label(frame, label, style="small").pack(anchor="w")
            entry = tk.Entry(frame, font=theme.FONT_BODY, bg=theme.BG_INPUT, fg=theme.TEXT_PRIMARY,
                             insertbackground=theme.PURPLE_LIGHT, bd=0, highlightthickness=1,
                             highlightbackground=theme.PURPLE_DIM)
            entry.pack(fill="x", ipady=8)
            entry.insert(0, default)
            fields[key] = entry

        # Type radio
        type_frame = tk.Frame(modal, bg=theme.BG_CARD, padx=theme.PAD_XL)
        type_frame.pack(fill="x", pady=10)
        make_label(type_frame, "Type", style="small").pack(anchor="w")
        type_var = tk.StringVar(value="Expense")
        for t in ["Income", "Expense"]:
            tk.Radiobutton(type_frame, text=t, variable=type_var, value=t,
                           bg=theme.BG_CARD, fg=theme.TEXT_PRIMARY, selectcolor=theme.BG_DARK,
                           activebackground=theme.BG_CARD, activeforeground=theme.PURPLE_LIGHT,
                           font=theme.FONT_BODY).pack(side="left", padx=(0, theme.PAD_MD))

        def _save():
            try:
                data = {
                    "Date": pd.to_datetime(fields["Date"].get()),
                    "Category": fields["Category"].get().strip(),
                    "Amount": float(fields["Amount"].get().replace(",", "")),
                    "Type": type_var.get()
                }
                if not data["Category"]: raise ValueError("Category needed")
                
                # Append to current DF or start new
                df = self.app_state.get("df")
                new_row = pd.DataFrame([data])
                if df is None or df.empty:
                    df = new_row
                else:
                    df = pd.concat([df, new_row], ignore_index=True)
                
                self.app_state["df"] = df
                summary = compute_summary(df)
                self.app_state["summary"] = summary
                
                if self.on_data_loaded:
                    self.on_data_loaded(summary)
                
                self._status_label.config(text=f"✅ Added {data['Type']}: {data['Category']} (₹{data['Amount']:,.0f})", fg=theme.SUCCESS)
                self._render_analysis(summary)
                modal.destroy()
            except Exception as e:
                messagebox.showerror("Input Error", f"Invalid input: {e}")

        make_button(modal, "Save Transaction", _save, variant="primary").pack(pady=theme.PAD_XL)

    def _run_ai_analysis(self):
        """Call Groq API to get personalized insights."""
        api_key = self.app_state.get("groq_api_key", "")
        summary = self.app_state.get("summary")
        if not summary:
            messagebox.showwarning("No Data", "Please upload data or add a transaction first.")
            return
        
        if not api_key:
            messagebox.showerror("No API Key", "No Groq API key found in .env file.")
            return

        modal = tk.Toplevel(self)
        modal.title("FinBuddy AI Insights")
        modal.geometry("600x500")
        modal.configure(bg=theme.BG_DARK)
        
        # Center
        x = self.winfo_rootx() + (self.winfo_width() // 2) - 300
        y = self.winfo_rooty() + (self.winfo_height() // 2) - 250
        modal.geometry(f"+{x}+{y}")

        content = tk.Frame(modal, bg=theme.BG_DARK, padx=theme.PAD_XL, pady=theme.PAD_XL)
        content.pack(fill="both", expand=True)
        
        make_label(content, "✨ FinBuddy Analysis", style="title").pack(pady=(0, theme.PAD_MD))
        
        box = tk.Text(content, font=theme.FONT_BODY, bg=theme.BG_CARD, fg=theme.TEXT_PRIMARY,
                      padx=theme.PAD_LG, pady=theme.PAD_LG, wrap="word", bd=0, highlightthickness=1,
                      highlightbackground=theme.PURPLE_DIM)
        box.pack(fill="both", expand=True)
        box.insert("1.0", "⏳ Buddy is thinking... gathering your vibes...")
        box.config(state="disabled")

        def _fetch():
            context = build_ai_context(summary)
            prompt = "Analyze my current financial situation and give me 3 sharp, Gen-Z styled insights and 1 dare to save more. Use the data provided."
            response, error = get_ai_response(prompt, api_key, context)
            
            def _update_ui():
                box.config(state="normal")
                box.delete("1.0", "end")
                if error:
                    box.insert("1.0", f"❌ Error: {response}")
                    box.tag_add("err", "1.0", "end")
                    box.tag_config("err", foreground=theme.DANGER)
                else:
                    box.insert("1.0", response)
                box.config(state="disabled")
            
            self.after(0, _update_ui)

        threading.Thread(target=_fetch, daemon=True).start()
        make_button(content, "Got it, Buddy! 💜", modal.destroy, variant="ghost").pack(pady=theme.PAD_LG)

    def refresh(self):
        """Re-render if data already loaded."""
        summary = self.app_state.get("summary")
        if summary:
            self._render_analysis(summary)
