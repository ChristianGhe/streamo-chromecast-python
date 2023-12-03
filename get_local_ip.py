import socket


# Get local IP address
def get_local_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()
    print("Local IP address: " + ip_address)
    return ip_address


if __name__ == '__main__':
    get_local_ip_address()
