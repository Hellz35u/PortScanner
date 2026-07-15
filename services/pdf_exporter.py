from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

# ── Palette (mirrors the app's dark cyber theme) ──────────────────────────────
_DARK   = HexColor("#0d0d0d")
_PANEL  = HexColor("#111111")
_CARD   = HexColor("#161616")
_ALT    = HexColor("#1e1e1e")
_ACCENT = HexColor("#00ff41")
_TEXT   = HexColor("#f0f0f0")
_DIM    = HexColor("#888888")
_BORDER = HexColor("#2c2c2e")

# ── Style definitions ─────────────────────────────────────────────────────────

def _make_styles():
    return {
        "title": ParagraphStyle(
            "ps_title",
            fontName="Helvetica-Bold",
            fontSize=18,
            textColor=_ACCENT,
            leading=22,
            alignment=TA_LEFT,
        ),
        "banner_sub": ParagraphStyle(
            "ps_banner_sub",
            fontName="Helvetica",
            fontSize=8,
            textColor=_DIM,
            leading=12,
            alignment=TA_RIGHT,
        ),
        "section": ParagraphStyle(
            "ps_section",
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=_ACCENT,
            leading=10,
            spaceBefore=6,
            spaceAfter=4,
        ),
        "meta_label": ParagraphStyle(
            "ps_meta_label",
            fontName="Helvetica",
            fontSize=7,
            textColor=_DIM,
            leading=9,
        ),
        "meta_value": ParagraphStyle(
            "ps_meta_value",
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=_TEXT,
            leading=14,
        ),
        "col_header": ParagraphStyle(
            "ps_col_hdr",
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=_ACCENT,
            leading=10,
        ),
        "col_port": ParagraphStyle(
            "ps_col_port",
            fontName="Courier-Bold",
            fontSize=10,
            textColor=_TEXT,
            leading=13,
        ),
        "col_service": ParagraphStyle(
            "ps_col_svc",
            fontName="Courier",
            fontSize=10,
            textColor=_TEXT,
            leading=13,
        ),
        "col_status": ParagraphStyle(
            "ps_col_status",
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=_ACCENT,
            leading=10,
        ),
        "no_ports": ParagraphStyle(
            "ps_no_ports",
            fontName="Helvetica",
            fontSize=10,
            textColor=_DIM,
            leading=14,
            alignment=TA_CENTER,
        ),
        "footer": ParagraphStyle(
            "ps_footer",
            fontName="Helvetica",
            fontSize=7,
            textColor=_DIM,
            leading=10,
            alignment=TA_CENTER,
        ),
    }

# ── Public entry point ────────────────────────────────────────────────────────

def generate_pdf(report_data, file_path):
    """
    Generate a styled PDF for a single scan report.

    report_data must contain:
        id         : int
        target_ip  : str
        open_ports : list of {"port": int, "service": str}
        created_at : str
    """
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"PortScanner — Report #{report_data.get('id', '?')}",
        author="PortScanner",
    )

    S = _make_styles()
    story = []

    report_id  = report_data.get("id", "—")
    target_ip  = report_data.get("target_ip", "—")
    created_at = report_data.get("created_at", "—")
    open_ports = report_data.get("open_ports", [])
    port_count = len(open_ports)

    page_w = A4[0] - 4 * cm   # usable width

    # ── Banner ────────────────────────────────────────────────────────────────
    banner_data = [[
        Paragraph("PORTSCANNER", S["title"]),
        Paragraph("SCAN REPORT", S["banner_sub"]),
    ]]
    banner = Table(banner_data, colWidths=[page_w * 0.65, page_w * 0.35])
    banner.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), _PANEL),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW",     (0, 0), (-1, -1), 2.5, _ACCENT),
    ]))
    story.append(banner)
    story.append(Spacer(1, 0.5 * cm))

    # ── Metadata block ────────────────────────────────────────────────────────
    meta_data = [
        [
            Paragraph("REPORT ID",   S["meta_label"]),
            Paragraph("TARGET IP",   S["meta_label"]),
            Paragraph("SCAN DATE",   S["meta_label"]),
            Paragraph("PORTS FOUND", S["meta_label"]),
        ],
        [
            Paragraph(f"#{report_id}",   S["meta_value"]),
            Paragraph(str(target_ip),     S["meta_value"]),
            Paragraph(str(created_at),    S["meta_value"]),
            Paragraph(str(port_count),    S["meta_value"]),
        ],
    ]
    meta_table = Table(
        meta_data,
        colWidths=[page_w * 0.18, page_w * 0.32, page_w * 0.32, page_w * 0.18],
    )
    meta_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), _CARD),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LINEBELOW",     (0, 0), (-1, 0), 0.5, _BORDER),
        ("LINEAFTER",     (0, 0), (-2, -1), 0.5, _BORDER),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.6 * cm))

    # ── Open ports section ────────────────────────────────────────────────────
    story.append(Paragraph("OPEN PORTS", S["section"]))
    story.append(Spacer(1, 0.15 * cm))

    if not open_ports:
        empty_data = [[Paragraph(
            "No open ports were discovered during this scan.", S["no_ports"]
        )]]
        empty_table = Table(empty_data, colWidths=[page_w])
        empty_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), _CARD),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
            ("TOPPADDING",    (0, 0), (-1, -1), 20),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
        ]))
        story.append(empty_table)
    else:
        col_w = [page_w * 0.18, page_w * 0.57, page_w * 0.25]

        table_data = [[
            Paragraph("PORT",    S["col_header"]),
            Paragraph("SERVICE", S["col_header"]),
            Paragraph("STATUS",  S["col_header"]),
        ]]
        for entry in open_ports:
            table_data.append([
                Paragraph(str(entry.get("port", "?")),    S["col_port"]),
                Paragraph(str(entry.get("service", "—")), S["col_service"]),
                Paragraph("OPEN",                          S["col_status"]),
            ])

        ports_table = Table(table_data, colWidths=col_w, repeatRows=1)

        ts = TableStyle([
            # Header row
            ("BACKGROUND",    (0, 0), (-1, 0), _PANEL),
            ("LINEBELOW",     (0, 0), (-1, 0), 1.5, _ACCENT),
            # All cells padding
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            # Row separators
            ("LINEBELOW",     (0, 1), (-1, -1), 0.5, _BORDER),
        ])
        # Alternating row backgrounds
        for i in range(1, len(table_data)):
            bg = _CARD if i % 2 == 1 else _ALT
            ts.add("BACKGROUND", (0, i), (-1, i), bg)

        ports_table.setStyle(ts)
        story.append(ports_table)

    story.append(Spacer(1, 1.2 * cm))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=_BORDER))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        f"Generated by PortScanner  ·  Report #{report_id}  ·  {created_at}",
        S["footer"],
    ))

    doc.build(story)
