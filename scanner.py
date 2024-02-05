import sys
import ipaddress
import socket
import paramiko
import concurrent.futures
import time

def scan_ssh_server(ip):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(str(ip), username='root', password='root', timeout=2, banner_timeout=2)
        server_version = client.get_transport().remote_version
        print(f"SSH server found at {ip}:")
        print(f"  - Version: {server_version}")
        print(f"  - Supported authentication methods: {client.auth_none} {client.auth_password} {client.auth_publickey}")
        client.close()
    except (paramiko.AuthenticationException) as e:
        print(f"Response {ip}: {e}")
        try:
            sock = socket.socket()
            sock.settimeout(2)
            sock.connect((str(ip), 22))
            banner = sock.recv(1024).decode('ascii', errors='ignore').strip()
            print(f"Trying to get banner: {ip}:")
            print(f" - {banner}")
            sock.close()
        except (Exception) as e:
            print(f"Banner from SSH server at {e}:")
    except socket.timeout:
        pass
    except Exception as e:
        print(f"An error occurred while scanning {ip}: {e}")

def scan_ssh_servers(start_ip, end_ip):
    start_ip_obj = ipaddress.ip_address(start_ip)
    end_ip_obj = ipaddress.ip_address(end_ip)

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        for ip in ipaddress.summarize_address_range(start_ip_obj, end_ip_obj):
            ip_network = ipaddress.ip_network(ip)
            for ip in ip_network.hosts():
                executor.submit(scan_ssh_server, ip)

    end_time = time.time()
    duration = end_time - start_time
    print(f"Scanning completed in {duration:.2f} seconds.")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python scanner.py [start_ip] [end_ip]")
    else:
        start_ip = sys.argv[1]
        end_ip = sys.argv[2]
        scan_ssh_servers(start_ip, end_ip)