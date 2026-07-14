import sqlite3
import json
from datetime import datetime

def save_scan_results(user_id, ip, open_ports):
    conn = None

    try:
        conn = sqlite3.connect("port_scanner.db")
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        
        open_ports_json = json.dumps(open_ports)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn.execute(
            """INSERT INTO reports(
                user_id,
                target_ip, 
                open_ports, 
                created_at
            )
            VALUES(?, ?, ?, ?)""",
            (
                user_id,
                ip,
                open_ports_json,
                created_at
            )
        )
        conn.commit()
        return True
    
    except sqlite3.Error as e:
        print(f"Failed to save scan results: {e}")
        return False
    
    finally:
        if conn is not None:
            conn.close()
    
def get_reports_by_user_id(user_id):
    conn = sqlite3.connect("port_scanner.db")
    cursor = conn.cursor()

    conn.execute(
        """
        SELECT id, target_ip, open_ports, created_at
        FROM reports
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (user_id)
    )
    reports = cursor.fetchall()
    conn.close()

    return reports

def get_report_by_id(id):
    conn = sqlite3.connect("port_scanner.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, target_ip, open_ports, created_at
        FROM reports
        WHERE id = ?
        """,
        (id)
    )
    report = cursor.fetchone()
    conn.close()

    return report



