
def get_full_scan():
    return range(1,65536)

def get_quick_scan():
    return range(1,1025)

def get_custom_scan(start_port, end_port):
    return range(start_port, end_port + 1)

