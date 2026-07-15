import tkinter as tk
from views import theme as T
from controller.auth_controller import register_user, login_user


class RegisterView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=T.BG)
        self.app = app
        self._build()

    def _build(self):
        # Left accent bar — 3px neon strip along the left edge
        tk.Frame(self, bg=T.ACCENT, width=3).pack(side="left", fill="y")

        main = tk.Frame(self, bg=T.BG)
        main.pack(fill="both", expand=True)

        # Spacers vertically center the card on the window
        tk.Frame(main, bg=T.BG).pack(fill="both", expand=True)
        card = tk.Frame(main, bg=T.BG)
        card.pack(fill="x", padx=280)
        tk.Frame(main, bg=T.BG).pack(fill="both", expand=True)

        # ── Logo ──────────────────────────────────────────────────────────────
        tk.Label(card, text="◈ PORTSCANNER",
                 font=("Courier", 24, "bold"), bg=T.BG, fg=T.ACCENT
                 ).pack(pady=(0, 4))
        tk.Label(card, text="CREATE ACCOUNT",
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
        self.pwd.pack(fill="x", pady=(0, 18))

        tk.Label(card, text="CONFIRM PASSWORD", font=T.FONT_CAPS,
                 bg=T.BG, fg=T.TEXT_DIM, anchor="w").pack(fill="x", pady=(0, 6))
        self.pwd2 = T.StyledEntry(card, show="*")
        self.pwd2.pack(fill="x", pady=(0, 22))

        # ── Feedback label ─────────────────────────────────────────────────────
        self.msg_var = tk.StringVar()
        self.msg_lbl = tk.Label(card, textvariable=self.msg_var,
                                font=T.FONT_SMALL, bg=T.BG, fg=T.ERROR,
                                wraplength=380, justify="left", anchor="w")
        self.msg_lbl.pack(fill="x", pady=(0, 10))

        T.neon_btn(card, "CREATE ACCOUNT", self._register).pack(fill="x", pady=(0, 18))

        # ── Login link ─────────────────────────────────────────────────────────
        row = tk.Frame(card, bg=T.BG)
        row.pack()
        tk.Label(row, text="Already have an account?  ", font=T.FONT_SMALL,
                 bg=T.BG, fg=T.TEXT_DIM).pack(side="left")
        lnk = tk.Label(row, text="Sign in →", font=("Helvetica", 10),
                       bg=T.BG, fg=T.ACCENT, cursor="hand2")
        lnk.pack(side="left")
        # Use app.after (on the root Tk window) so the callback survives even
        # if this frame is in the middle of being destroyed when the event fires
        lnk.bind("<Button-1>", lambda e: self.app.after(0, self.app.show_login))
        lnk.bind("<Enter>", lambda e: lnk.config(fg=T.ACCENT_DK))
        lnk.bind("<Leave>", lambda e: lnk.config(fg=T.ACCENT))

        tk.Label(main, text="[ SECURE CONNECTION ]", font=T.FONT_MONO_SM,
                 bg=T.BG, fg=T.TEXT_MUTED).pack(side="bottom", pady=18)

        # ── Keyboard shortcuts ─────────────────────────────────────────────────
        self.usr.entry.bind("<Return>", lambda e: self.pwd.focus())
        self.pwd.entry.bind("<Return>", lambda e: self.pwd2.focus())
        self.pwd2.entry.bind("<Return>", lambda e: self._register())
        self.after(100, lambda: self.usr.focus() if self.winfo_exists() else None)

    def _register(self, event=None):
        # Guard against double invocation (e.g. pressing Enter and clicking
        # the button at the same time would call _register() twice)
        if getattr(self, '_pending', False):
            return

        username = self.usr.get().strip()
        password = self.pwd.get()
        confirm  = self.pwd2.get()

        if not username:
            self._error("⚠  Username is required.")
            return
        if len(username) < 3:
            self._error("⚠  Username must be at least 3 characters.")
            return
        if not password:
            self._error("⚠  Password is required.")
            return
        if len(password) < 4:
            self._error("⚠  Password must be at least 4 characters.")
            return
        if password != confirm:
            self._error("⚠  Passwords do not match.")
            self.pwd2.clear()
            self.pwd2.focus()
            return

        # Lock submissions while the backend call is in progress
        self._pending = True

        try:
            result = register_user(username, password)
        except Exception as ex:
            self._pending = False
            self._error(f"⚠  Backend error: {ex}")
            return

        if result["success"]:
            # Auto-login immediately after registration so the user doesn't
            # have to re-enter their credentials on the login screen
            try:
                login_result = login_user(username, password)
            except Exception:
                login_result = {"success": False}

            if login_result["success"]:
                self.app.current_user = login_result["user"]
                self._success("✓  Account created. Welcome!")
                # Schedule on the root window so it fires even if this frame
                # gets destroyed before the 800ms delay elapses
                self.app.after(800, self.app.show_dashboard)
            else:
                self._success("✓  Account created. Redirecting to login…")
                self.app.after(1200, self.app.show_login)
        else:
            self._pending = False
            self._error(f"⚠  {result['message']}")

    def _error(self, text):
        self.msg_lbl.config(fg=T.ERROR)
        self.msg_var.set(text)

    def _success(self, text):
        self.msg_lbl.config(fg=T.SUCCESS)
        self.msg_var.set(text)
