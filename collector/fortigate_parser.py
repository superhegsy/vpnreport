import os
import django
import re
import geoip2.database
from django.utils import timezone

# =========================
# COUNTRY TRANSLATION
# =========================

COUNTRY_HU = {
    "Italy": "Olaszország",
    "Germany": "Németország",
    "Hungary": "Magyarország",
    "United States": "Egyesült Államok",
    "United Kingdom": "Egyesült Királyság",
    "France": "Franciaország",
    "Spain": "Spanyolország",
    "Netherlands": "Hollandia",
    "Austria": "Ausztria",
    "Switzerland": "Svájc",
    "Poland": "Lengyelország",
    "Romania": "Románia",
    "Slovakia": "Szlovákia",
    "Czechia": "Csehország",
    "China": "Kína",
    "Japan": "Japán",
    "Canada": "Kanada",
    "Australia": "Ausztrália"
}

# =========================
# DJANGO INIT
# =========================

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vpnreport.settings")
django.setup()

from vpn.models import VPNSession


# =========================
# GEOIP DATABASE
# =========================

reader = geoip2.database.Reader("data/GeoLite2-City.mmdb")


# =========================
# LOG PARSER
# =========================

def parse_log(line):

    user_match = re.search(r'user=([^\s]+)', line)
    ip_match = re.search(r'remip=([^\s]+)', line)
    action_match = re.search(r'action=([^\s]+)', line)

    if not user_match or not ip_match or not action_match:
        return

    username = user_match.group(1)
    remote_ip = ip_match.group(1)
    action = action_match.group(1)

    # =========================
    # GEOIP LOOKUP
    # =========================

    country = None
    country_code = None
    lat = None
    lon = None

    try:
        response = reader.city(remote_ip)

        country_en = response.country.name
        country = COUNTRY_HU.get(country_en, country_en)

        country_code = response.country.iso_code

        lat = response.location.latitude
        lon = response.location.longitude

    except Exception:
        pass

    now = timezone.now()

    # =========================
    # VPN CONNECT
    # =========================

    if action == "ipsec-up":

        VPNSession.objects.create(
            username=username,
            remote_ip=remote_ip,
            connected_at=now,
            country=country,
            country_code=country_code,
            latitude=lat,
            longitude=lon
        )

        print(f"VPN UP {username} {remote_ip} {country}")

    # =========================
    # VPN DISCONNECT
    # =========================

    elif action == "ipsec-down":

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
