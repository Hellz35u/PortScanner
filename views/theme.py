import tkinter as tk

# ── Palette ───────────────────────────────────────────────────────────────────
BG         = "#0a0a0a"
BG_PANEL   = "#111111"
BG_CARD    = "#141414"
BG_INPUT   = "#1c1c1e"
ACCENT     = "#00ff41"
ACCENT_DK  = "#00cc33"
TEXT       = "#f0f0f0"
TEXT_DIM   = "#888888"
TEXT_MUTED = "#3a3a3c"
ERROR      = "#ff453a"
SUCCESS    = "#00ff41"
BORDER     = "#2c2c2e"
BORDER_LT  = "#3a3a3c"

# ── Typography ────────────────────────────────────────────────────────────────
FONT_DISPLAY = ("Helvetica", 22, "bold")
FONT_TITLE   = ("Helvetica", 15, "bold")
FONT_BODY    = ("Helvetica", 12)
FONT_SMALL   = ("Helvetica", 10)
FONT_LABEL   = ("Helvetica", 11)
FONT_CAPS    = ("Helvetica", 9, "bold")
FONT_BTN     = ("Helvetica", 11, "bold")
FONT_MONO    = ("Courier", 12)
FONT_MONO_SM = ("Courier", 10)
FONT_LOGO    = ("Courier", 14, "bold")


# ── Shared Widgets ────────────────────────────────────────────────────────────

class StyledEntry(tk.Frame):
    """Single-line text entry with a neon border that lights up on focus."""

    def __init__(self, parent, show=None, **kwargs):
        # The Frame acts as the border: 1px padding around the inner Entry.
        # Changing the Frame's bg color is what creates the focus highlight.
        super().__init__(parent, bg=BORDER, padx=1, pady=1)
        entry_kw = dict(
            bg=BG_INPUT,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            bd=10,
            font=FONT_BODY,
        )
        if show:
            entry_kw["show"] = show
        entry_kw.update(kwargs)
        self.entry = tk.Entry(self, **entry_kw)
        self.entry.pack(fill="x")
        self.entry.bind("<FocusIn>",  lambda e: self.config(bg=ACCENT))
        self.entry.bind("<FocusOut>", lambda e: self.config(bg=BORDER))

    def get(self):
        return self.entry.get()

    def clear(self):
        self.entry.delete(0, "end")

    def set(self, s):
        self.clear()
        self.entry.insert(0, s)

    def focus(self):
        self.entry.focus_set()


def neon_btn(parent, text, command, primary=True, width=None):
    bg    = ACCENT    if primary else BG_CARD
    fg    = "#000000" if primary else ACCENT
    hover = ACCENT_DK if primary else "#1e1e1e"

    kw = dict(text=text, bg=bg, fg=fg, font=FONT_BTN,
              cursor="hand2", padx=24, pady=11)
    if width:
        kw["width"] = width

    lbl = tk.Label(parent, **kw)
    lbl._bg    = bg
    lbl._hover = hover

    # Use lambda e: command() — NOT after(0, command) — so the function is
    # called with no arguments and not treated as an event handler by tkinter.
    lbl.bind("<Button-1>", lambda e: command())
    lbl.bind("<Enter>",    lambda e: lbl.config(bg=lbl._hover))
    lbl.bind("<Leave>",    lambda e: lbl.config(bg=lbl._bg))
    return lbl


def header(parent, app, title="", back_cmd=None):
    bar = tk.Frame(parent, bg=BG_PANEL, height=52)
    bar.pack(fill="x", side="top")
    bar.pack_propagate(False)

    left = tk.Frame(bar, bg=BG_PANEL)
    left.pack(side="left", fill="y", padx=20)

    tk.Label(left, text="◈ PORTSCANNER", font=FONT_LOGO,
             bg=BG_PANEL, fg=ACCENT).pack(side="left", pady=14)

    if title:
        tk.Label(left, text=f" / {title}", font=FONT_MONO_SM,
                 bg=BG_PANEL, fg=TEXT_DIM).pack(side="left", pady=14)

    right = tk.Frame(bar, bg=BG_PANEL)
    right.pack(side="right", fill="y", padx=16)

    if back_cmd:
        back = tk.Label(right, text="← BACK", font=FONT_CAPS,
                        bg=BG_PANEL, fg=TEXT_DIM, cursor="hand2")
        back.pack(side="right", pady=19, padx=(8, 0))
        back.bind("<Button-1>", lambda e: back_cmd())
        back.bind("<Enter>", lambda e: back.config(fg=ACCENT))
        back.bind("<Leave>", lambda e: back.config(fg=TEXT_DIM))

    if app.current_user:
        tk.Label(right, text=f"[ {app.current_user['username']} ]",
                 font=FONT_MONO_SM, bg=BG_PANEL, fg=TEXT_DIM
                 ).pack(side="right", pady=19, padx=(0, 10))

        out = tk.Label(right, text="LOGOUT", font=FONT_CAPS,
                       bg=BG_PANEL, fg=ERROR, cursor="hand2")
        out.pack(side="right", pady=19)
        out.bind("<Button-1>", lambda e: app.logout())
        out.bind("<Enter>", lambda e: out.config(fg="#ff6b6b"))
        out.bind("<Leave>", lambda e: out.config(fg=ERROR))

    # 1px separator line below the header bar
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x")
    return bar


def separator(parent, pady=0):
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", pady=pady)


def field_label(parent, text):
    return tk.Label(parent, text=text, font=FONT_CAPS,
                    bg=BG, fg=TEXT_DIM, anchor="w")
