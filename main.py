from database import initialize_database, login, register
from reports import save_scan_results
from scanner import ports_scanner
from scan_modes import get_full_scan, get_quick_scan, get_custom_scan
from validators import validate_ip, validate_port, validate_port_range
from services import get_service_name

initialize_database()

print("[1] - Login")
print("[2] - Register")

authentication_choice = input("Enter your choice: ")


if authentication_choice == "1":
    username = input("Enter username: ")
    password = input("Enter password: ")

    current_user = login(username, password)
    
    if current_user is None:
        exit()
    
elif authentication_choice == "2":
    username = input("Enter username: ")
    password = input("Enter password: ")

    if register(username, password):
        print("Registration completed successfully")

        current_user = login(username, password)

        if current_user is None:
            exit()
    else:
        print("Username already exists.")
        exit()


print(
    "Choose scan mode:\n"
    "[1] - Quick Scan (1 - 1024)\n"
    "[2] - Full Scan (1 - 65535)\n"
    "[3] - Custom Scan\n"
    "[4] - Exit"
)

choice = input("Enter your choice: ")

match choice:
    case "1":
        ports = get_quick_scan()

    case "2":
        ports = get_full_scan()

    case "3":
        start_port = input("Enter starting port: ")
        end_port = input("Enter ending port: ")

        if not validate_port(start_port):
            print("Starting port must be a number between 1 and 65535.")
            exit()

        if not validate_port(end_port):
            print("Ending port must be a number between 1 and 65535.")
            exit()

        if not validate_port_range(start_port, end_port):
            print("Starting port must be smaller than or equal to ending port.")
            exit()

        ports = get_custom_scan(start_port, end_port)

    case "4":
        print("Goodbye :)")
        exit()

    case _:
        print("Invalid choice.")
        exit()


ip = input("Enter IP: ")

if not validate_ip(ip):
    print("Invalid IP address.")
    exit()


print(f"Scanning IP: {ip}...")


open_ports = []
open_port_numbers = ports_scanner(ip, ports)


for port in open_port_numbers:
    service = get_service_name(port)

    open_ports.append({
        "port": port,
        "service": service
    })

    print(f"Port {port} is OPEN — Service: {service}")


if save_scan_results(
    current_user["id"],
    ip,
    open_ports
):
    print("Scan results saved successfully.")
else:
    print("Failed to save scan results.")

