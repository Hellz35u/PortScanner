from reports import save_scan_results
from scanner import ports_scanner
from scan_modes import get_full_scan, get_quick_scan, get_custom_scan
from validators import validate_ip, validate_port, validate_port_range
from services import get_service_name

choice = int(input("Chose scan mode:\n [1] - Quick Scan(1 - 1024)\n [2] - Full Scan(1 - 65535)\n [3] - Custom Scan\n [4] - EXIT\n Enter your choice number: "))

match choice:
    case 1:
        ports = get_quick_scan()
    
    case 2:
        ports = get_full_scan()

    case 3:
        start_port = input("Enter Starting port:")
        end_port = input("Enter Ending port:")
        ports = get_custom_scan(start_port, end_port)
        
        if not validate_port(start_port):
            print("start port must be a number between 1 - 65535")
            exit()
        
        if not validate_port(end_port):
            print("end port must be a number between 1 - 65535")
            exit()

        if not not validate_port_range(start_port, end_port):
            print("Starting port must be smaller than or equal to Ending port")
            exit()
    
    case 4:
        print("Good bye:)")
    
    case _:
        print("Invalid Choice")
    

ip = input("Enter IP:")

if not validate_ip(ip):
    print("Invalid IP Address")
    exit()

print(f"Scanning IP: {ip}. . .")

open_ports = []
open_port_numbers = ports_scanner(ip, ports)

for port in open_port_numbers:
    service = get_service_name(port)
    open_ports.append({
        "port":port,
        "service": service
    })

    print(f"Port {port} is OPEN on Service {service}")

save_scan_results(ip, open_ports)

