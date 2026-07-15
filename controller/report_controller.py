import json

from models.reports_model import (
    get_reports_by_user_id,
    get_report_by_id,
)


def load_user_reports(user_id):
    # Returns all scan reports belonging to this user, newest first
    reports = get_reports_by_user_id(user_id)
    return {
        "success": True,
        "reports": reports,
    }


def load_report(report_id, user_id):
    # user_id is passed so the model enforces ownership (WHERE id=? AND user_id=?)
    report = get_report_by_id(report_id, user_id)

    if report is None:
        return {
            "success": False,
            "message": "Report not found.",
        }

    return {
        "success": True,
        "report": report,
    }


def export_report_pdf(report_id, user_id, file_path):
    if not file_path:
        return {
            "success": False,
            "message": "No destination file selected.",
        }

    # Fetch with ownership check — users can only export their own reports
    report = get_report_by_id(report_id, user_id)

    if report is None:
        return {
            "success": False,
            "message": "Report not found or access denied.",
        }

    try:
        rep_id, target_ip, open_ports_raw, created_at = report
        # open_ports is stored as JSON text in the database
        open_ports = json.loads(open_ports_raw) if open_ports_raw else []
    except Exception:
        return {
            "success": False,
            "message": "Failed to read report data.",
        }

    report_data = {
        "id":         rep_id,
        "target_ip":  target_ip,
        "open_ports": open_ports,
        "created_at": created_at,
    }

    try:
        # Import lazily so the reports page still opens even if reportlab is missing;
        # only the export action itself will fail with a clear message.
        from services.pdf_exporter import generate_pdf
        generate_pdf(report_data, file_path)
    except ImportError:
        return {
            "success": False,
            "message": "PDF export requires 'reportlab'. Run the app with: .venv/bin/python app.py",
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"PDF generation failed: {e}",
        }

    return {
        "success": True,
        "message": "Report exported successfully.",
        "file_path": file_path,
    }
