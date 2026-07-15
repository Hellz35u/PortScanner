import socket
from concurrent.futures import ThreadPoolExecutor, as_completed


def is_port_open(target_ip, port):
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 0.5 s timeout keeps the scan fast; most closed ports respond immediately
        sock.settimeout(0.5)
        result = sock.connect_ex((target_ip, port))
    except OSError:
        return False
    finally:
        if sock is not None:
            sock.close()

    # connect_ex returns 0 on success (port open), non-zero on refusal/timeout
    return result == 0


def ports_scanner(target_ip, ports):
    open_ports = []

    # 100 threads lets us probe ~200 ports/sec while staying reasonable on resources
    with ThreadPoolExecutor(max_workers=100) as executor:
        # Map each Future back to its port number so we know which port opened
        futures = {executor.submit(is_port_open, target_ip, port): port
                   for port in ports}

        for future in as_completed(futures):
            try:
                if future.result():
                    open_ports.append(futures[future])
            except Exception:
                # A single failed probe should never abort the whole scan
                continue

    # Sort so the results are displayed in ascending port-number order
    return sorted(open_ports)
