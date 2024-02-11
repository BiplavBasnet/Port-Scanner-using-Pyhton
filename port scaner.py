import socket
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import queue
import logging

TIMEOUT = 5

def scan_port(host, port, timeout):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((host, port))
            if result == 0:
                return port
    except socket.timeout:
        logging.error(f"Timeout scanning port {port}")
    except ConnectionRefusedError:
        logging.debug(f"Port {port} is closed")
    except Exception as e:
        logging.error(f"Error scanning port {port}: {e}")
    return None

def worker(host, port_queue, open_ports, timeout, stop_event):
    while not stop_event.is_set():
        try:
            port = port_queue.get(timeout=1)
            result = scan_port(host, port, timeout)
            if result:
                open_ports.append(result)
        except queue.Empty:
            break

def run_scanner(host, ports, threads, timeout):
    port_queue = queue.SimpleQueue()
    open_ports = []
    stop_event = threading.Event()

    for port in ports:
        port_queue.put(port)

    with ThreadPoolExecutor(max_workers=threads) as executor:
        for _ in range(threads):
            executor.submit(worker, host, port_queue, open_ports, timeout, stop_event)

    stop_event.set()  # Signal worker threads to stop
    return open_ports

if __name__ == "__main__":
    print('''
          
    $$$$$$$\                       $$\                                                                      
    $$  __$$\                      $$ |                                                                     
    $$ |  $$ | $$$$$$\   $$$$$$\ $$$$$$\          $$$$$$$\  $$$$$$$\ $$$$$$\  $$$$$$$\   $$$$$$\   $$$$$$\ 
    $$$$$$$  |$$  __$$\ $$  __$$\\_$$  _|        $$  _____|$$  _____|\____$$\ $$  __$$\ $$  __$$\ $$  __$$\ 
    $$  ____/ $$ /  $$ |$$ |  \__| $$ |          \$$$$$$\  $$ /      $$$$$$$ |$$ |  $$ |$$$$$$$$ |$$ |  \__|
    $$ |      $$ |  $$ |$$ |       $$ |$$\        \____$$\ $$ |     $$  __$$ |$$ |  $$ |$$   ____|$$ |       
    $$ |      \$$$$$$  |$$ |       \$$$$  |      $$$$$$$  |\$$$$$$$\\$$$$$$$ |$$ |  $$ |\$$$$$$$\ $$ |      
    \__|       \______/ \__|        \____/       \_______/  \_______|\_______|\__|  \__| \_______|\__|
    |                                                                                                |
    |--------------------------------------------Coded by Biplav--------------------------------------|''')

    print("\nGithub: https://github.com/BiplavBasnet/Port-Scanner-using-Pyhton.git\n")
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    host = input("Enter Your IP/domain: ")
    try:
        host_ip = socket.gethostbyname(host)
    except socket.gaierror:
        logging.error("Invalid IP/domain. Please try again.")
        sys.exit(1)

    try:
        start_port = int(input("Enter the starting port number: "))
        end_port = int(input("Enter the ending port number: "))
        if not 0 < start_port < 65536 or not 0 < end_port < 65536 or start_port > end_port:
            raise ValueError("Invalid port range. Port numbers should be integers between 1 and 65535, and the starting port should be less than the ending port.")
        ports = range(start_port, end_port + 1)
    except ValueError as e:
        logging.error(str(e))
        sys.exit(1)

    now = datetime.now()
    logging.info(f"Scanning started at: {now.strftime('%H:%M:%S')}")

    open_ports = run_scanner(host_ip, ports, 1024, TIMEOUT)

    if open_ports:
        open_ports.sort()  # Sort open ports for better readability
        logging.info("Open ports: %s", open_ports)
    else:
        logging.info("No open ports found.")
