from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count

from .models import VPNSession


# =========================
# DASHBOARD PAGE
# =========================

def dashboard(request):

    # csak aktív VPN sessionök
    active_sessions = VPNSession.objects.filter(
        disconnected_at__isnull=True
    ).order_by("-connected_at")

    # duration számítás
    now = timezone.now()

    for s in active_sessions:

        delta = now - s.connected_at

        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60

        if hours > 0:
            s.duration = f"{hours}h {minutes}m"
        else:
            s.duration = f"{minutes}m"

    active_users = active_sessions.count()

    today_sessions = VPNSession.objects.filter(
        connected_at__date=timezone.now().date()
    ).count()

    total_sessions = VPNSession.objects.count()

    top_user = (
        VPNSession.objects
        .values("username")
        .annotate(total=Count("id"))
        .order_by("-total")
        .first()
    )

    context = {
        "sessions": active_sessions,
        "active_users": active_users,
        "today_sessions": today_sessions,
        "total_sessions": total_sessions,
        "top_user": top_user
    }

    return render(request, "dashboard.html", context)


# =========================
# REPORT PLACEHOLDERS
# =========================

def report_daily(request):
    return JsonResponse({"status": "daily report placeholder"})


def report_weekly(request):
    return JsonResponse({"status": "weekly report placeholder"})


def report_monthly(request):
    return JsonResponse({"status": "monthly report placeholder"})


# =========================
# VPN LOCATIONS API
# =========================

def vpn_locations(request):

    sessions = (
        VPNSession.objects
        .filter(disconnected_at__isnull=True)
        .values(
            "username",
            "remote_ip",
            "latitude",
            "longitude",
            "country",
            "country_code"
        )
        .distinct()
    )

    data = []

    for s in sessions:

        if not s["latitude"] or not s["longitude"]:
            continue

        data.append({
            "username": s["username"],
            "ip": s["remote_ip"],
            "lat": s["latitude"],
            "lon": s["longitude"],
            "country": s["country"],
            "country_code": s["country_code"]
        })

    return JsonResponse(data, safe=False)


# =========================
# DASHBOARD STATS API
# =========================

def dashboard_stats(request):

    active_users = VPNSession.objects.filter(
        disconnected_at__isnull=True
    ).count()

    today_sessions = VPNSession.objects.filter(
        connected_at__date=timezone.now().date()
    ).count()

    total_sessions = VPNSession.objects.count()

    top_user = (
        VPNSession.objects
        .values("username")
        .annotate(total=Count("id"))
        .order_by("-total")
        .first()
    )

    return JsonResponse({
        "active_users": active_users,
        "today_sessions": today_sessions,
        "total_sessions": total_sessions,
        "top_user": top_user["username"] if top_user else "-"
    })

# =========================
# ACTIVE VPN SESSIONS API
# =========================

def active_vpn_sessions(request):

    sessions = VPNSession.objects.filter(
        disconnected_at__isnull=True
    ).order_by("-connected_at")

    data = []

    now = timezone.now()

    for s in sessions:

        delta = now - s.connected_at
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60

        if hours > 0:
            duration = f"{hours}h {minutes}m"
        else:
            duration = f"{minutes}m"

        data.append({
            "username": s.username,
            "ip": s.remote_ip,
            "country_code": s.country_code,
            "connected_at": s.connected_at.strftime("%Y.%m.%d %H:%M:%S"),
            "duration": duration
        })

    return JsonResponse(data, safe=False)
