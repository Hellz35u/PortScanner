from models.reports_model import save_scan_results
from services.scanner_service import ports_scanner
from services.scan_modes import get_quick_scan, get_full_scan, get_custom_scan
from services.service_names import get_service_name
from utils.validators import validate_ip, validate_port, validate_port_range


def start_scan(user_id, target_ip, scan_mode, start_port=None, end_port=None):
    # Validate the IP before doing any network work
    if not validate_ip(target_ip):
        return {
            "success": False,
            "message": "Invalid IP Address",
        }

    # Select the port range based on the chosen scan mode
    if scan_mode == "quick":
        ports = get_quick_scan()

    elif scan_mode == "full":
        ports = get_full_scan()

    elif scan_mode == "custom":
        if not validate_port(start_port):
            return {
                "success": False,
                "message": "Invalid starting port.",
            }
        if not validate_port(end_port):
            return {
                "success": False,
                "message": "Invalid ending port.",
            }
        if not validate_port_range(start_port, end_port):
            return {
                "success": False,
                "message": "Starting port must be smaller than or equal to ending port.",
            }
        ports = get_custom_scan(start_port, end_port)

    else:
        return {
            "success": False,
            "message": "Invalid scan mode",
        }

    # Run the concurrent TCP scan; result is a sorted list of open port numbers
    open_port_numbers = ports_scanner(target_ip, ports)

    # Enrich each port number with its well-known service name before returning
    open_ports = []
    for port in open_port_numbers:
        service_name = get_service_name(port)
        open_ports.append({
            "port":    port,
            "service": service_name,
        })

    # Persist results so they appear in the Reports view
    saved = save_scan_results(user_id, target_ip, open_ports)

    if not saved:
        return {
            "success": False,
            "message": "Scan completed, but the results could not be saved.",
        }

    return {
        "success":    True,
        "message":    "Scan completed successfully.",
        "open_ports": open_ports,
    }
