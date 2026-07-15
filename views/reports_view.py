import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from views import theme as T
from controller.report_controller import load_user_reports, load_report, export_report_pdf


class ReportsView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=T.BG)
        self.app = app
        self._reports = []   # cached list from the last successful load
        self._build()
        self._load_reports()

    def _build(self):
        T.header(self, self.app, title="REPORTS",
                 back_cmd=self.app.show_dashboard)

        body = tk.Frame(self, bg=T.BG)
        body.pack(fill="both", expand=True, padx=40, pady=24)

        # ── Top: scan history list ─────────────────────────────────────────────
        top = tk.Frame(body, bg=T.BG)
        top.pack(fill="both", expand=True)

        tk.Label(top, text="SCAN HISTORY", font=T.FONT_CAPS,
                 bg=T.BG, fg=T.ACCENT, anchor="w").pack(fill="x", pady=(0, 8))

        list_frame = tk.Frame(top, bg=T.BORDER, padx=1, pady=1)
        list_frame.pack(fill="both", expand=True)
        inner_top = tk.Frame(list_frame, bg=T.BG_CARD)
        inner_top.pack(fill="both", expand=True)

        self.list_tree = ttk.Treeview(inner_top, style="Dark.Treeview",
                                      columns=("id", "ip", "ports", "date"),
                                      show="headings", selectmode="browse", height=8)
        self.list_tree.heading("id",    text="#",          anchor="w")
        self.list_tree.heading("ip",    text="TARGET IP",  anchor="w")
        self.list_tree.heading("ports", text="OPEN PORTS", anchor="w")
        self.list_tree.heading("date",  text="DATE",       anchor="w")
        self.list_tree.column("id",    width=50,  stretch=False, anchor="w")
        self.list_tree.column("ip",    width=180, stretch=False, anchor="w")
        self.list_tree.column("ports", width=120, stretch=False, anchor="w")
        self.list_tree.column("date",  width=200, stretch=True,  anchor="w")

        vsb_list = ttk.Scrollbar(inner_top, orient="vertical",
                                 command=self.list_tree.yview, style="Dark.TScrollbar")
        self.list_tree.configure(yscrollcommand=vsb_list.set)
        self.list_tree.pack(side="left", fill="both", expand=True)
        vsb_list.pack(side="right", fill="y")

        self.list_tree.bind("<<TreeviewSelect>>", self._on_select)

        self.list_status = tk.StringVar(value="Loading…")
        tk.Label(top, textvariable=self.list_status, font=T.FONT_MONO_SM,
                 bg=T.BG, fg=T.TEXT_DIM, anchor="w").pack(fill="x", pady=(6, 0))

        T.separator(body, pady=14)

        # ── Bottom: detail panel for the selected report ───────────────────────
        bottom = tk.Frame(body, bg=T.BG)
        bottom.pack(fill="both", expand=True)

        detail_hdr = tk.Frame(bottom, bg=T.BG)
        detail_hdr.pack(fill="x", pady=(0, 8))

        tk.Label(detail_hdr, text="SCAN DETAIL", font=T.FONT_CAPS,
                 bg=T.BG, fg=T.ACCENT, anchor="w").pack(side="left")

        self.export_btn = T.neon_btn(detail_hdr, "⬇  EXPORT TO PDF",
                                     self._export_pdf, primary=False)
        self.export_btn.pack(side="right", padx=(8, 0))

        self.detail_meta = tk.StringVar(value="Select a report above to view details.")
        tk.Label(detail_hdr, textvariable=self.detail_meta, font=T.FONT_MONO_SM,
                 bg=T.BG, fg=T.TEXT_DIM, anchor="e").pack(side="right")

        detail_frame = tk.Frame(bottom, bg=T.BORDER, padx=1, pady=1)
        detail_frame.pack(fill="both", expand=True)
        inner_bot = tk.Frame(detail_frame, bg=T.BG_CARD)
        inner_bot.pack(fill="both", expand=True)

        self.detail_tree = ttk.Treeview(inner_bot, style="Dark.Treeview",
                                        columns=("port", "service"),
                                        show="headings", selectmode="browse", height=6)
        self.detail_tree.heading("port",    text="PORT",    anchor="w")
        self.detail_tree.heading("service", text="SERVICE", anchor="w")
        self.detail_tree.column("port",    width=120, stretch=False, anchor="w")
        self.detail_tree.column("service", width=300, stretch=True,  anchor="w")

        vsb_detail = ttk.Scrollbar(inner_bot, orient="vertical",
                                   command=self.detail_tree.yview, style="Dark.TScrollbar")
        self.detail_tree.configure(yscrollcommand=vsb_detail.set)
        self.detail_tree.pack(side="left", fill="both", expand=True)
        vsb_detail.pack(side="right", fill="y")

    def _load_reports(self):
        try:
            result = load_user_reports(self.app.current_user["id"])
        except Exception as ex:
            self.list_status.set(f"⚠  Could not load reports: {ex}")
            return

        if not result["success"]:
            self.list_status.set(f"⚠  {result.get('message', 'Unknown error')}")
            return

        reports = result.get("reports", []) or []
        # Cache for use in _on_select's fallback path
        self._reports = reports

        for row in self.list_tree.get_children():
            self.list_tree.delete(row)

        if not reports:
            self.list_status.set("—  No scans saved yet. Run a scan first.")
            return

        for rep in reports:
            rep_id, target_ip, open_ports_raw, created_at = rep
            try:
                port_count = len(json.loads(open_ports_raw)) if open_ports_raw else 0
            except (json.JSONDecodeError, TypeError):
                port_count = "?"
            self.list_tree.insert("", "end", iid=str(rep_id),
                                  values=(rep_id, target_ip, port_count, created_at))

        count = len(reports)
        self.list_status.set(
            f"✓  {count} scan report{'s' if count != 1 else ''} found."
        )

    def _on_select(self, event):
        sel = self.list_tree.selection()
        if not sel:
            return

        rep_id = int(sel[0])

        for row in self.detail_tree.get_children():
            self.detail_tree.delete(row)

        open_ports = None
        meta_text  = ""

        # Try the controller first (enforces ownership via user_id)
        try:
            result = load_report(rep_id, self.app.current_user["id"])
            if result["success"]:
                _, target_ip, open_ports_raw, created_at = result["report"]
                open_ports = json.loads(open_ports_raw) if open_ports_raw else []
                meta_text  = f"{target_ip}  ·  {created_at}"
        except Exception:
            pass

        # Fall back to the in-memory cache if the controller call failed
        if open_ports is None:
            for rep in self._reports:
                if rep[0] == rep_id:
                    _, target_ip, open_ports_raw, created_at = rep
                    try:
                        open_ports = json.loads(open_ports_raw) if open_ports_raw else []
                    except (json.JSONDecodeError, TypeError):
                        open_ports = []
                    meta_text = f"{target_ip}  ·  {created_at}"
                    break

        if open_ports is None:
            self.detail_meta.set("Could not load report detail.")
            return

        self.detail_meta.set(meta_text)

        if not open_ports:
            self.detail_tree.insert("", "end", values=("—", "No open ports found"))
            return

        for entry in open_ports:
            self.detail_tree.insert("", "end",
                                    values=(entry.get("port", "?"),
                                            entry.get("service", "unknown")))

    def _export_pdf(self):
        sel = self.list_tree.selection()
        if not sel:
            messagebox.showwarning("No Report Selected",
                                   "Please select a report from the list before exporting.")
            return

        report_id = int(sel[0])
        user_id   = self.app.current_user["id"]

        # Default save location: exports/user_<id>/ inside the project root
        export_dir = os.path.normpath(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "exports", f"user_{user_id}",
        ))
        os.makedirs(export_dir, exist_ok=True)

        file_path = filedialog.asksaveasfilename(
            title="Export Report as PDF",
            initialdir=export_dir,
            initialfile=f"scan_report_{report_id}.pdf",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )

        if not file_path:
            return   # user cancelled — nothing to do

        result = export_report_pdf(report_id, user_id, file_path)

        if result["success"]:
            messagebox.showinfo("Export Successful",
                                f"Report saved to:\n{result['file_path']}")
        else:
            messagebox.showerror("Export Failed",
                                 result.get("message", "An unexpected error occurred."))
