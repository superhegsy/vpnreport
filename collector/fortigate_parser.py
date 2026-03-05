import os
import django
import re
import geoip2.database
from django.utils import timezone

# Django init
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vpnreport.settings")
django.setup()

from vpn.models import VPNSession


# GeoIP adatbázis
reader = geoip2.database.Reader("data/GeoLite2-City.mmdb")


def parse_log(line):

    user_match = re.search(r'user=([^\s]+)', line)
    ip_match = re.search(r'remip=([^\s]+)', line)
    action_match = re.search(r'action=([^\s]+)', line)

    if not user_match or not ip_match or not action_match:
        return

    username = user_match.group(1)
    remote_ip = ip_match.group(1)
    action = action_match.group(1)

    # GeoIP lookup
    try:
        response = reader.city(remote_ip)

        country = response.country.name
        lat = response.location.latitude
        lon = response.location.longitude

    except Exception:
        country = None
        lat = None
        lon = None

    now = timezone.now()

    # VPN kapcsolat létrejött
    if action == "ipsec-up":

        VPNSession.objects.create(
            username=username,
            remote_ip=remote_ip,
            connected_at=now,
            country=country,
            latitude=lat,
            longitude=lon
        )

        print(f"VPN UP {username} {remote_ip} {country}")

    # VPN bontás
    if action == "ipsec-down":

        session = VPNSession.objects.filter(
            username=username,
            remote_ip=remote_ip,
            disconnected_at__isnull=True
        ).last()

        if session:

            session.disconnected_at = now
            session.duration_seconds = int(
                (session.disconnected_at - session.connected_at).total_seconds()
            )

            session.save()

            print(f"VPN DOWN {username}")
