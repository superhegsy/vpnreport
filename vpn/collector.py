import requests
import urllib3
import geoip2.database
import os
import time

from django.utils import timezone
from app.models import FortiGateConfig, VPNSession

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =========================
# GEOIP INIT
# =========================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEOIP_DB = os.path.join(BASE_DIR, "data", "GeoLite2-City.mmdb")

geo_reader = None

if os.path.exists(GEOIP_DB):
    geo_reader = geoip2.database.Reader(GEOIP_DB)
    print("GeoIP database loaded")
else:
    print("GeoIP database not found:", GEOIP_DB)


# =========================
# GEOIP LOOKUP
# =========================

def geo_lookup(ip):

    if not geo_reader:
        return None, None, None, None

    try:

        geo = geo_reader.city(ip)

        country = geo.country.name
        country_code = geo.country.iso_code
        latitude = geo.location.latitude
        longitude = geo.location.longitude

        return country, country_code, latitude, longitude

    except Exception:
        return None, None, None, None


# =========================
# FETCH FORTIGATE SESSIONS
# =========================

def fetch_sessions(cfg):

    url = f"https://{cfg.host}:{cfg.port}/api/v2/monitor/vpn/ipsec"

    headers = {
        "Authorization": f"Bearer {cfg.api_token}"
    }

    try:

        r = requests.get(url, headers=headers, verify=False, timeout=10)
        r.raise_for_status()

        return r.json().get("results", [])

    except Exception as e:

        print(f"FortiGate connection error ({cfg.host}):", e)
        return []


# =========================
# MAIN COLLECTOR
# =========================

def collect_fortigate_sessions():

    configs = FortiGateConfig.objects.filter(enabled=True)

    active_sessions = []

    for cfg in configs:

        tunnels = fetch_sessions(cfg)

        for tunnel in tunnels:

            if tunnel.get("type") != "dialup":
                continue

            username = tunnel.get("user")
            remote_ip = tunnel.get("rgwy")
            vpn_ip = tunnel.get("tun_id")

            if not username or not remote_ip:
                continue

            session_key = f"{username}_{remote_ip}"
            active_sessions.append(session_key)

            country, country_code, latitude, longitude = geo_lookup(remote_ip)

            session = VPNSession.objects.filter(
                username=username,
                remote_ip=remote_ip,
                disconnected_at__isnull=True
            ).first()

            if not session:

                VPNSession.objects.create(
                    username=username,
                    remote_ip=remote_ip,
                    vpn_ip=vpn_ip,
                    connected_at=timezone.now(),
                    country=country,
                    country_code=country_code,
                    latitude=latitude,
                    longitude=longitude
                )

                print(f"New VPN session: {username} ({remote_ip})")

    detect_disconnects(active_sessions)


# =========================
# DISCONNECT DETECTION
# =========================

def detect_disconnects(active_sessions):

    open_sessions = VPNSession.objects.filter(disconnected_at__isnull=True)

    for session in open_sessions:

        key = f"{session.username}_{session.remote_ip}"

        if key not in active_sessions:

            session.disconnected_at = timezone.now()

            if session.connected_at:

                delta = session.disconnected_at - session.connected_at
                session.duration_seconds = int(delta.total_seconds())

            session.save()

            print(f"VPN disconnected: {session.username}")


# =========================
# RUN LOOP
# =========================

def run():

    print("VPN collector started")

    while True:

        try:
            collect_fortigate_sessions()
        except Exception as e:
            print("Collector error:", e)

        time.sleep(5)
