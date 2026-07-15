import ipaddress


def validate_ip(ip):
    # ipaddress.ip_address() handles edge cases (leading zeros, IPv6, etc.)
    # that a hand-written regex would likely miss
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def validate_port(port):
    # Reject non-numeric strings before converting to int
    if not port.isdigit():
        return False
    return 1 <= int(port) <= 65535


def validate_port_range(start_port, end_port):
    # Ensures the range is valid (start ≤ end) before building the range object
    return int(start_port) <= int(end_port)
