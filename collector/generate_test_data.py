import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vpnreport.settings")
django.setup()

from vpn.models import VPNSession


users = [
    "csabi",
    "anna",
    "bela",
    "david",
    "eva",
    "feri",
    "gabriella",
    "istvan"
]

ips = [
    "10.10.1.10",
    "10.10.1.11",
    "10.10.1.12",
    "10.10.1.13",
    "10.10.1.14",
]

now = timezone.now()

for i in range(120):

    user = random.choice(users)
    ip = random.choice(ips)

    start = now - timedelta(days=random.randint(0, 30),
                            hours=random.randint(0, 23))

    duration = random.randint(300, 7200)

    end = start + timedelta(seconds=duration)

    VPNSession.objects.create(
        username=user,
        remote_ip=ip,
        connected_at=start,
        disconnected_at=end,
        duration_seconds=duration
    )

print("Teszt VPN session adatok generálva")
