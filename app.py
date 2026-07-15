import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))

# Inject the venv's site-packages into sys.path so dependencies like reportlab
# and bcrypt are available even when the app is launched with the system Python.
_site = os.path.join(
    _here, ".venv", "lib",
    f"python{sys.version_info.major}.{sys.version_info.minor}",
    "site-packages",
)
if os.path.isdir(_site) and _site not in sys.path:
    sys.path.insert(0, _site)

import tkinter as tk
from tkinter import ttk

# Fix the working directory so all relative paths (e.g. data/port_scanner.db)
# resolve correctly regardless of where the user launched the script from.
os.chdir(_here)

from models.database import initialize_database


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.current_user = None   # set on login, cleared on logout
        self._setup_window()
        self._setup_ttk_styles()
        self._container = tk.Frame(self, bg="#0a0a0a")
        self._container.pack(fill="both", expand=True)
        self.show_login()

    def _setup_window(self):
        self.title("PortScanner")
        self.configure(bg="#0a0a0a")
        self.resizable(False, False)
        w, h = 960, 680
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        # Center the window on whatever screen the user has
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    def _setup_ttk_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("Dark.Treeview",
            background="#141414",
            foreground="#f0f0f0",
            rowheight=28,
            fieldbackground="#141414",
            borderwidth=0,
            font=("Courier", 10),
        )
        style.configure("Dark.Treeview.Heading",
            background="#111111",
            foreground="#00ff41",
            font=("Helvetica", 9, "bold"),
            relief="flat",
            borderwidth=0,
        )
        style.map("Dark.Treeview",
            background=[("selected", "#00ff41")],
            foreground=[("selected", "#000000")],
        )
        style.configure("Dark.TScrollbar",
            background="#1c1c1e",
            troughcolor="#0a0a0a",
            arrowcolor="#3a3a3c",
            borderwidth=0,
            relief="flat",
        )
        style.map("Dark.TScrollbar",
            background=[("active", "#2c2c2e")],
        )
        # ttk looks up "Vertical.Dark.TScrollbar" when style="Dark.TScrollbar"
        # is used on a vertical Scrollbar. Without this registration it raises
        # TclError: Layout Vertical.Dark.TScrollbar not found.
        style.layout("Vertical.Dark.TScrollbar",
                     style.layout("Vertical.TScrollbar"))

    def _clear(self):
        # Destroy all child widgets inside the container before rendering a new view
        for w in self._container.winfo_children():
            w.destroy()

    # ── Navigation ────────────────────────────────────────────────────────────

    def show_login(self):
        self._clear()
        from views.login_view import LoginView
        LoginView(self._container, self).pack(fill="both", expand=True)

    def show_register(self):
        self._clear()
        from views.register_view import RegisterView
        RegisterView(self._container, self).pack(fill="both", expand=True)

    def show_dashboard(self):
        self._clear()
        from views.dashboard_view import DashboardView
        DashboardView(self._container, self).pack(fill="both", expand=True)

    def show_scan(self):
        self._clear()
        from views.scan_view import ScanView
        ScanView(self._container, self).pack(fill="both", expand=True)

    def show_reports(self):
        self._clear()
        from views.reports_view import ReportsView
        ReportsView(self._container, self).pack(fill="both", expand=True)

    def logout(self):
        self.current_user = None
        self.show_login()


if __name__ == "__main__":
    initialize_database()
    app = App()
    app.mainloop()
