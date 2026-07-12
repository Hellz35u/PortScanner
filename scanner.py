import socket
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def is_port_open(target, port):
    sock = None
    try:
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((target,port))
    
    except Exception as e:
        print(f"Error opening socket: {e}")
        return None
    
    finally:
        if sock is not None:
            sock.close()
    
    return result == 0

def ports_scanner(target, ports):
    open_ports = []
    
    with ThreadPoolExecutor(max_workers=100) as executor: