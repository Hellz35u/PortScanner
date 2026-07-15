import tkinter as tk
from views import theme as T
from controller.auth_controller import login_user


class LoginView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=T.BG)
        self.app = app
        self._build()

    def _build(self):
        # Left accent bar — 3px neon strip along the left edge
        tk.Frame(self, bg=T.ACCENT, width=3).pack(side="left", fill="y")

        main = tk.Frame(self, bg=T.BG)
        main.pack(fill="both", expand=True)

        # Spacers above and below the card vertically center it on the window
        tk.Frame(main, bg=T.BG).pack(fill="both", expand=True)
        card = tk.Frame(main, bg=T.BG)
        card.pack(fill="x", padx=280)
        tk.Frame(main, bg=T.BG).pack(fill="both", expand=True)

        # ── Logo ──────────────────────────────────────────────────────────────
        tk.Label(card, text="◈ PORTSCANNER",
                 font=("Courier", 24, "bold"), bg=T.BG, fg=T.ACCENT
                 ).pack(pady=(0, 4))
        tk.Label(card, text="CYBER RECONNAISSANCE SUITE",
                 font=("Helvetica", 8), bg=T.BG, fg=T.TEXT_MUTED
                 ).pack(pady=(0, 28))
        tk.Frame(card, bg=T.BORDER, height=1).pack(fill="x", pady=(0, 28))

        # ── Form ──────────────────────────────────────────────────────────────
        tk.Label(card, text="USERNAME", font=T.FONT_CAPS,
                 bg=T.BG, fg=T.TEXT_DIM, anchor="w").pack(fill="x", pady=(0, 6))
        self.usr = T.StyledEntry(card)
        self.usr.pack(fill="x", pady=(0, 18))

        tk.Label(card, text="PASSWORD", font=T.FONT_CAPS,
                 bg=T.BG, fg=T.TEXT_DIM, anchor="w").pack(fill="x", pady=(0, 6))
        self.pwd = T.StyledEntry(card, show="*")
        self.pwd.pack(fill="x", pady=(0, 22))

        # ── Error / feedback label ─────────────────────────────────────────────
        self.msg_var = tk.StringVar()
        tk.Label(card, textvariable=self.msg_var, font=T.FONT_SMALL,
                 bg=T.BG, fg=T.ERROR, wraplength=380, justify="left",
                 anchor="w").pack(fill="x", pady=(0, 10))

        T.neon_btn(card, "AUTHENTICATE", self._login).pack(fill="x", pady=(0, 18))

        # ── Register link ──────────────────────────────────────────────────────
        row = tk.Frame(card, bg=T.BG)
        row.pack()
        tk.Label(row, text="No account?  ", font=T.FONT_SMALL,
                 bg=T.BG, fg=T.TEXT_DIM).pack(side="left")
        lnk = tk.Label(row, text="Create one →", font=("Helvetica", 10),
                       bg=T.BG, fg=T.ACCENT, cursor="hand2")
        lnk.pack(side="left")
        # Defer navigation with after(0) so the click event fully completes
        # before we destroy this frame and build a new one
        lnk.bind("<Button-1>", lambda e: self.after(0, self.app.show_register))
        lnk.bind("<Enter>", lambda e: lnk.config(fg=T.ACCENT_DK))
        lnk.bind("<Leave>", lambda e: lnk.config(fg=T.ACCENT))

        tk.Label(main, text="[ SECURE CONNECTION ]", font=T.FONT_MONO_SM,
                 bg=T.BG, fg=T.TEXT_MUTED).pack(side="bottom", pady=18)

        # ── Keyboard shortcuts ─────────────────────────────────────────────────
        self.usr.entry.bind("<Return>", lambda e: self.pwd.focus())
        self.pwd.entry.bind("<Return>", lambda e: self._login())
        # Guard with winfo_exists() in case the user navigates away in under 100ms
        self.after(100, lambda: self.usr.focus() if self.winfo_exists() else None)

    def _login(self):
        username = self.usr.get().strip()
        password = self.pwd.get()

        if not username:
            self.msg_var.set("⚠  Username is required.")
            return
        if not password:
            self.msg_var.set("⚠  Password is required.")
            return

        try:
            result = login_user(username, password)
        except Exception as ex:
            self.msg_var.set(f"⚠  Backend error: {ex}")
            return

        if result["success"]:
            self.app.current_user = result["user"]
            self.msg_var.set("")
            self.app.show_dashboard()
        else:
            self.msg_var.set(f"⚠  {result['message']}")
            self.pwd.clear()
            self.pwd.focus()
