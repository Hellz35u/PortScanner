def get_full_scan():
    # All 65535 TCP ports
    return range(1, 65536)


def get_quick_scan():
    # Well-known / privileged ports only (IANA registered range)
    return range(1, 1025)


def get_custom_scan(start_port, end_port):
    # +1 makes the range inclusive on both ends
    return range(int(start_port), int(end_port) + 1)
