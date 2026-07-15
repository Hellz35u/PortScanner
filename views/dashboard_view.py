import tkinter as tk
from views import theme as T


class DashboardView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=T.BG)
        self.app = app
        self._build()

    def _build(self):
        T.header(self, self.app, title="DASHBOARD")

        content = tk.Frame(self, bg=T.BG)
        content.pack(fill="both", expand=True, padx=60, pady=50)

        # ── Welcome block ──────────────────────────────────────────────────────
        username = self.app.current_user.get("username", "operator")
        tk.Label(content,
                 text=f"Welcome back, {username}.",
                 font=("Helvetica", 20, "bold"),
                 bg=T.BG, fg=T.TEXT).pack(anchor="w")
        tk.Label(content,
                 text="System ready for reconnaissance.",
                 font=T.FONT_BODY,
                 bg=T.BG, fg=T.TEXT_DIM).pack(anchor="w", pady=(4, 0))

        tk.Frame(content, bg=T.BORDER, height=1).pack(fill="x", pady=36)

        # ── Navigation cards ───────────────────────────────────────────────────
        cards_row = tk.Frame(content, bg=T.BG)
        cards_row.pack(fill="x")
        cards_row.columnconfigure(0, weight=1)
        cards_row.columnconfigure(1, weight=1)

        self._make_card(cards_row, icon="⚡", title="NEW SCAN",
                        desc="Launch a port scan against a target IP address.",
                        command=self.app.show_scan, col=0)
        self._make_card(cards_row, icon="◫",  title="REPORTS",
                        desc="Browse saved scan results and export data.",
                        command=self.app.show_reports, col=1)

        # ── Decorative terminal status block ───────────────────────────────────
        tk.Frame(content, bg=T.BORDER, height=1).pack(fill="x", pady=36)

        term = tk.Frame(content, bg=T.BG_PANEL)
        term.pack(fill="x")
        tk.Frame(term, bg=T.ACCENT, height=2).pack(fill="x")
        inner = tk.Frame(term, bg=T.BG_PANEL)
        inner.pack(fill="x", padx=20, pady=16)

        lines = [
            "$ portscanner --status",
            f"  user      : {username}",
            "  db        : connected",
            "  scanner   : ready",
            "  threads   : 100",
        ]
        for i, line in enumerate(lines):
            color = T.ACCENT if i == 0 else T.TEXT_DIM
            tk.Label(inner, text=line, font=T.FONT_MONO_SM,
                     bg=T.BG_PANEL, fg=color, anchor="w").pack(fill="x")

    def _make_card(self, parent, icon, title, desc, command, col):
        pad = 10 if col == 0 else 0
        outer = tk.Frame(parent, bg=T.BORDER, padx=1, pady=1)
        outer.grid(row=0, column=col, sticky="nsew",
                   padx=(0 if col else 0, pad if col == 0 else 0))

        card = tk.Frame(outer, bg=T.BG_CARD, cursor="hand2")
        card.pack(fill="both", expand=True)

        tk.Frame(card, bg=T.ACCENT, height=2).pack(fill="x")

        body = tk.Frame(card, bg=T.BG_CARD)
        body.pack(fill="both", expand=True, padx=28, pady=28)

        icon_lbl  = tk.Label(body, text=icon, font=("Helvetica", 28),
                             bg=T.BG_CARD, fg=T.ACCENT)
        icon_lbl.pack(anchor="w")

        title_lbl = tk.Label(body, text=title, font=T.FONT_TITLE,
                             bg=T.BG_CARD, fg=T.TEXT)
        title_lbl.pack(anchor="w", pady=(10, 6))

        desc_lbl  = tk.Label(body, text=desc, font=T.FONT_SMALL,
                             bg=T.BG_CARD, fg=T.TEXT_DIM,
                             wraplength=300, justify="left")
        desc_lbl.pack(anchor="w", pady=(0, 20))

        T.neon_btn(body, f"OPEN {title}", command).pack(anchor="w")

        # Bind hover and click to all visible child widgets so the whole card
        # area feels interactive, not just the button inside it
        hover_widgets = [card, body, icon_lbl, title_lbl, desc_lbl]
        for w in hover_widgets:
            w.bind("<Enter>", lambda e, c=card, b=body, i=icon_lbl,
                   t=title_lbl, d=desc_lbl: self._card_hover(c, b, i, t, d, True))
            w.bind("<Leave>", lambda e, c=card, b=body, i=icon_lbl,
                   t=title_lbl, d=desc_lbl: self._card_hover(c, b, i, t, d, False))
            w.bind("<Button-1>", lambda e, cmd=command: self.after(0, cmd))

    def _card_hover(self, card, body, icon, title, desc, on):
        bg = "#1a1a1a" if on else T.BG_CARD
        for w in (card, body, icon, title, desc):
            w.config(bg=bg)
