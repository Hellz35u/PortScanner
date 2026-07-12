import ipaddress

def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    
    except ValueError:
        return False

def validate_port(port):
    if not port.isdigit():
        return False
    
    port = int(port)

    return 1 <= port <= 65535

def validate_port_range(start_port, end_port):
    return int(start_port) <= int(end_port)