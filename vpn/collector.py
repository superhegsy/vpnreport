import requests
from django.utils import timezone
from .models import FortiGateConfig, VPNSession


def collect_fortigate_sessions():

    configs = FortiGateConfig.objects.filter(enabled=True)

    active_users = []

    for cfg in configs:

        url = f"https://{cfg.host}:{cfg.port}/api/v2/monitor/vpn/ipsec"

        headers = {
            "Authorization": f"Bearer {cfg.api_token}"
        }

        try:

            r = requests.get(url, headers=headers, verify=False, timeout=10)
            r.raise_for_status()
            data = r.json()

        except Exception as e:

            print("FortiGate connection error:", e)
            return

        tunnels = data.get("results", [])

        for tunnel in tunnels:

            # csak remote access VPN
            if tunnel.get("type") != "dialup":
                continue

            username = tunnel.get("user")
            remote_ip = tunnel.get("rgwy")

            if not username:
                continue

            active_users.append(username)

            vpn_ip = tunnel.get("tun_id")

            session = VPNSession.objects.filter(
                username=username,
                remote_ip=remote_ip,
                vpn_ip=vpn_ip,
                disconnected_at__isnull=True
            ).first()

            if not session:

                VPNSession.objects.create(
                    username=username,
                    remote_ip=remote_ip,
                    connected_at=timezone.now()
                )

                print(f"New VPN session: {username}")


    # =========================
    # DISCONNECT DETECTION
    # =========================

    open_sessions = VPNSession.objects.filter(disconnected_at__isnull=True)

    for session in open_sessions:

        if session.username not in active_users:

            session.disconnected_at = timezone.now()
            session.save()

            print(f"VPN disconnected: {session.username}")
