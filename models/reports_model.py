import json
from datetime import datetime
from models.database import get_connection


def save_scan_results(user_id, ip, open_ports):
    # Serialize the list of {port, service} dicts to JSON for storage
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO reports (user_id, target_ip, open_ports, created_at)
               VALUES (?, ?, ?, ?)""",
            (user_id, ip, json.dumps(open_ports),
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Failed to save scan results: {e}")
        return False
    finally:
        if conn:
            conn.close()


def get_reports_by_user_id(user_id):
    # Results ordered newest-first so the Reports view shows recent scans at the top
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, target_ip, open_ports, created_at
           FROM reports
           WHERE user_id = ?
           ORDER BY created_at DESC""",
        (user_id,),
    )
    reports = cursor.fetchall()
    conn.close()
    return reports


def get_report_by_id(report_id, user_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    if user_id is not None:
        # Include user_id in the WHERE clause to enforce ownership —
        # a user cannot fetch another user's report even if they know the ID.
        cursor.execute(
            """SELECT id, target_ip, open_ports, created_at
               FROM reports WHERE id = ? AND user_id = ?""",
            (report_id, user_id),
        )
    else:
        cursor.execute(
            """SELECT id, target_ip, open_ports, created_at
               FROM reports WHERE id = ?""",
            (report_id,),
        )

    report = cursor.fetchone()
    conn.close()
    return report
