#!/usr/bin/env python3

import netifaces
import ipaddress
import paramiko
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_interfaces():
    return [i for i in netifaces.interfaces() if i != 'lo']

def get_ip_netmask(interface):
    addrs = netifaces.ifaddresses(interface)
    if netifaces.AF_INET in addrs:
        ip = addrs[netifaces.AF_INET][0]['addr']
        mask = addrs[netifaces.AF_INET][0]['netmask']
        return ip, mask
    return None, None

def get_all_ips(cidr):
    net = ipaddress.IPv4Network(cidr, strict=False)
    return [str(ip) for ip in net.hosts()]

def ssh_check(ip, user, pwd):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username=user, password=pwd, timeout=3, banner_timeout=3)
        try:
            stdin, stdout, _ = client.exec_command("hostname", timeout=2)
            hostname = stdout.read().decode().strip()
        except:
            hostname = "N/A"
        client.close()
        return {'ip': ip, 'hostname': hostname or "N/A"}
    except:
        return None

def main():
    interfaces = get_interfaces()
    print("Available interfaces:")
    for i, iface in enumerate(interfaces):
        print(f"{i}: {iface}")
    while True:
        try:
            choice = int(input("Select interface: "))
            if 0 <= choice < len(interfaces):
                iface = interfaces[choice]
                break
        except:
            pass
        print("Invalid selection. Try again.")

    user = input("SSH Username (e.g. pi): ").strip()
    pwd = input("SSH Password: ").strip()

    ip, mask = get_ip_netmask(iface)
    if not ip or not mask:
        print(f"Cannot get IP/netmask for {iface}")
        return

    cidr = str(ipaddress.IPv4Network(f"{ip}/{mask}", strict=False))
    targets = get_all_ips(cidr)
    print(f"\nScanning full subnet {cidr} ({len(targets)} IPs)...\n")

    results = []
    max_workers = 50
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(ssh_check, ip, user, pwd): ip for ip in targets}
        for future in tqdm(as_completed(futures), total=len(targets), desc="SSH probing", unit="host"):
            result = future.result()
            if result:
                results.append(result)

    print("\nSSH-connectable devices:\n")
    print(f"{'IP':<16} {'Hostname'}")
    print("-" * 30)
    for d in results:
        print(f"{d['ip']:<16} {d['hostname']}")

if __name__ == "__main__":
    main()
