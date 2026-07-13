import os
import json
from datetime import datetime

def save_scan_results(ip, open_ports):
    scan_results = {
        "ip" : ip,
        "scan_time" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "open_ports" : open_ports
    }

    os.makedirs("results",exist_ok=True)
    
    file_name = datetime.now().strftime("scan_%Y-%m-%d_%H-%M-%S.json")
    file_path = os.path.join("results", file_name)

    try:
        with open(file_path,"w") as file:
            json.dump(scan_results, file, indent=4)

    except OSError as e:
        print(f"Failed save scan results: {e}")
        return False
    
    return True
    

