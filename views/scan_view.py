import tkinter as tk
from tkinter import ttk
import threading
from views import theme as T
from controller.scan_controller import start_scan


class ScanView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=T.BG)
        self.app = app
        self._scan_thread = None
        self._result      = None   # populated by the worker thread on completion
        self._scan_error  = None   # set if the worker raises an exception
        self._scanning    = False  # True while a scan is in progress
        self._anim_idx    = 0      # index into the button animation frames
        self._build()

    def _build(self):
        T.header(self, self.app, title="NEW SCAN",
                 back_cmd=self.app.show_dashboard)

        # Two-column layout: controls on the left, results table on the right
        body = tk.Frame(self, bg=T.BG)
        body.pack(fill="both", expand=True)

        left = tk.Frame(body, bg=T.BG, width=340)
        left.pack(side="left", fill="y", padx=(40, 20), pady=30)
        left.pack_propagate(False)

        tk.Frame(body, bg=T.BORDER, width=1).pack(side="left", fill="y", pady=30)

        right = tk.Frame(body, bg=T.BG)
        right.pack(side="left", fill="both", expand=True, padx=(20, 40), pady=30)

        self._build_controls(left)
        self._build_results(right)

    # ── Left panel — target and mode selection ────────────────────────────────

    def _build_controls(self, parent):
        tk.Label(parent, text="TARGET", font=T.FONT_CAPS,
                 bg=T.BG, fg=T.ACCENT, anchor="w").pack(fill="x", pady=(0, 8))

        tk.Label(parent, text="IP ADDRESS", font=T.FONT_CAPS,
                 bg=T.BG, fg=T.TEXT_DIM, anchor="w").pack(fill="x", pady=(0, 6))
        self.ip_entry = T.StyledEntry(parent)
        self.ip_entry.pack(fill="x", pady=(0, 24))
        self.ip_entry.focus()

        T.separator(parent, pady=4)

        tk.Label(parent, text="SCAN MODE", font=T.FONT_CAPS,
                 bg=T.BG, fg=T.ACCENT, anchor="w").pack(fill="x", pady=(12, 10))

        self.scan_mode = tk.StringVar(value="quick")
        modes = [
            ("quick",  "Quick Scan",   "Ports 1 – 1024"),
            ("full",   "Full Scan",    "Ports 1 – 65535"),
            ("custom", "Custom Range", "Define port range"),
        ]
        for val, label, hint in modes:
            self._radio(parent, val, label, hint)

        # ── Custom range inputs (hidden unless mode == "custom") ───────────────
        self.custom_frame = tk.Frame(parent, bg=T.BG)
        self.custom_frame.pack(fill="x", pady=(4, 0))

        row = tk.Frame(self.custom_frame, bg=T.BG)
        row.pack(fill="x")

        col1 = tk.Frame(row, bg=T.BG)
        col1.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Label(col1, text="FROM", font=T.FONT_CAPS,
                 bg=T.BG, fg=T.TEXT_DIM, anchor="w").pack(fill="x", pady=(0, 5))
        self.start_port = T.StyledEntry(col1)
        self.start_port.pack(fill="x")

        col2 = tk.Frame(row, bg=T.BG)
        col2.pack(side="left", fill="x", expand=True)
        tk.Label(col2, text="TO", font=T.FONT_CAPS,
                 bg=T.BG, fg=T.TEXT_DIM, anchor="w").pack(fill="x", pady=(0, 5))
        self.end_port = T.StyledEntry(col2)
        self.end_port.pack(fill="x")

        # Start hidden; revealed by _on_mode_change when custom is selected
        self.custom_frame.pack_forget()
        self.scan_mode.trace_add("write", self._on_mode_change)

        T.separator(parent, pady=(16, 4))

        self.scan_btn = T.neon_btn(parent, "▶  START SCAN", self._start_scan)
        self.scan_btn.pack(fill="x", pady=(12, 0))

        self.status_var = tk.StringVar(value="")
        self.status_lbl = tk.Label(parent, textvariable=self.status_var,
                                   font=T.FONT_MONO_SM, bg=T.BG, fg=T.TEXT_DIM,
                                   anchor="w", wraplength=300, justify="left")
        self.status_lbl.pack(fill="x", pady=(10, 0))

    def _radio(self, parent, value, label, hint):
        frame = tk.Frame(parent, bg=T.BG)
        frame.pack(fill="x", pady=3)
        rb = tk.Radiobutton(
            frame, variable=self.scan_mode, value=value,
            bg=T.BG, fg=T.TEXT, selectcolor=T.BG,
            activebackground=T.BG, activeforeground=T.TEXT,
            relief="flat", bd=0, highlightthickness=0,
            font=T.FONT_BODY, text=label,
        )
        rb.pack(side="left")
        tk.Label(frame, text=f"  {hint}", font=T.FONT_MONO_SM,
                 bg=T.BG, fg=T.TEXT_MUTED).pack(side="left", pady=1)

    def _on_mode_change(self, *_):
        if self.scan_mode.get() == "custom":
            self.custom_frame.pack(fill="x", pady=(4, 0))
        else:
            self.custom_frame.pack_forget()

    # ── Right panel — results treeview ────────────────────────────────────────

    def _build_results(self, parent):
        tk.Label(parent, text="RESULTS", font=T.FONT_CAPS,
                 bg=T.BG, fg=T.ACCENT, anchor="w").pack(fill="x", pady=(0, 10))

        self.summary_var = tk.StringVar(value="—  No scan run yet")
        tk.Label(parent, textvariable=self.summary_var,
                 font=T.FONT_MONO_SM, bg=T.BG, fg=T.TEXT_DIM,
                 anchor="w").pack(fill="x", pady=(0, 10))

        tree_frame = tk.Frame(parent, bg=T.BORDER, padx=1, pady=1)
        tree_frame.pack(fill="both", expand=True)

        inner = tk.Frame(tree_frame, bg=T.BG_CARD)
        inner.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(inner, style="Dark.Treeview",
                                 columns=("port", "service"),
                                 show="headings", selectmode="browse")
        self.tree.heading("port",    text="PORT",    anchor="w")
        self.tree.heading("service", text="SERVICE", anchor="w")
        self.tree.column("port",    width=100, stretch=False, anchor="w")
        self.tree.column("service", width=260, stretch=True,  anchor="w")

        vsb = ttk.Scrollbar(inner, orient="vertical",
                            command=self.tree.yview, style="Dark.TScrollbar")
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

    # ── Scan execution ────────────────────────────────────────────────────────

    def _start_scan(self):
        # Ignore additional clicks while a scan is already running
        if self._scanning:
            return

        ip   = self.ip_entry.get().strip()
        mode = self.scan_mode.get()

        if not ip:
            self._set_status("⚠  Please enter a target IP address.", T.ERROR)
            return

        if mode == "custom":
            sp = self.start_port.get().strip()
            ep = self.end_port.get().strip()
            if not sp or not ep:
                self._set_status("⚠  Enter both start and end ports.", T.ERROR)
                return
        else:
            sp = ep = None

        for row in self.tree.get_children():
            self.tree.delete(row)
        self.summary_var.set("—  Scanning…")

        self._scanning   = True
        self._result     = None
        self._scan_error = None

        # Visually disable the button during the scan
        self.scan_btn.config(bg=T.TEXT_MUTED, fg=T.BG,
                             cursor="arrow", text="▶  SCANNING…")
        self.scan_btn.unbind("<Button-1>")

        # Run the scan in a daemon thread so the UI stays responsive.
        # Results are written to self._result; _poll() checks them every 150ms.
        def worker():
            try:
                self._result = start_scan(
                    self.app.current_user["id"], ip, mode, sp, ep
                )
            except Exception as ex:
                self._scan_error = str(ex)

        self._scan_thread = threading.Thread(target=worker, daemon=True)
        self._scan_thread.start()
        self._animate()
        self._poll()

    def _animate(self):
        # Cycle through dot frames to give the button a scanning animation
        if not self._scanning:
            return
        dots = ["▶  SCANNING   ", "▶  SCANNING.  ", "▶  SCANNING.. ", "▶  SCANNING..."]
        self.scan_btn.config(text=dots[self._anim_idx % 4])
        self._anim_idx += 1
        self.after(400, self._animate)

    def _poll(self):
        # Check every 150ms whether the worker thread has finished
        if self._result is not None or self._scan_error is not None:
            self._on_scan_done()
        else:
            self.after(150, self._poll)

    def _on_scan_done(self):
        self._scanning = False

        # Restore the button to its clickable state
        self.scan_btn.config(bg=T.ACCENT, fg="#000000",
                             cursor="hand2", text="▶  START SCAN")
        self.scan_btn.bind("<Button-1>", lambda e: self._start_scan())

        if self._scan_error:
            self._set_status(f"⚠  Error: {self._scan_error}", T.ERROR)
            self.summary_var.set("—  Scan failed.")
            return

        result = self._result

        if not result["success"]:
            self._set_status(f"⚠  {result['message']}", T.ERROR)
            self.summary_var.set("—  Scan failed.")
            return

        ports = result.get("open_ports", [])
        count = len(ports)

        for row in self.tree.get_children():
            self.tree.delete(row)
        for entry in ports:
            self.tree.insert("", "end", values=(entry["port"], entry["service"]))

        if count == 0:
            self.summary_var.set("✓  Scan complete — No open ports found.")
        else:
            self.summary_var.set(
                f"✓  Scan complete — {count} open port{'s' if count != 1 else ''} found."
            )
        self._set_status("", T.TEXT_DIM)

    def _set_status(self, text, color):
        self.status_lbl.config(fg=color)
        self.status_var.set(text)
