import socket
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vpnreport.settings")
django.setup()

from fortigate_parser import parse_log

UDP_IP = "0.0.0.0"
UDP_PORT = 5514

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Syslog server listening on port {UDP_PORT}")

while True:

    data, addr = sock.recvfrom(4096)

    message = data.decode("utf-8", errors="ignore")

    print("LOG:", message)

    parse_log(message)
