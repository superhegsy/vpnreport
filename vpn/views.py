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

from datetime import timedelta
from django.core.paginator import Paginator
from django.db.models import Sum


# =========================
# DAILY REPORT
# =========================

def report_daily(request):

    today = timezone.now().date()

    sessions = VPNSession.objects.filter(
        connected_at__date=today,
        disconnected_at__isnull=False
    )

    users = (
        sessions
        .values("username")
        .annotate(
            total_sessions=Count("id"),
            total_duration=Sum("duration_seconds")
        )
        .order_by("-total_duration")
    )

    return render(request, "report.html", {
        "users": users,
        "title": "Napi VPN riport"
    })


# =========================
# WEEKLY REPORT
# =========================

def report_weekly(request):

    start = timezone.now() - timedelta(days=7)

    sessions = VPNSession.objects.filter(
        connected_at__gte=start,
        disconnected_at__isnull=False
    )

    users = (
        sessions
        .values("username")
        .annotate(
            total_sessions=Count("id"),
            total_duration=Sum("duration_seconds")
        )
        .order_by("-total_duration")
    )

    return render(request, "report.html", {
        "users": users,
        "title": "Heti VPN riport"
    })


# =========================
# MONTHLY REPORT
# =========================

def report_monthly(request):

    start = timezone.now() - timedelta(days=30)

    sessions = VPNSession.objects.filter(
        connected_at__gte=start,
        disconnected_at__isnull=False
    )

    users = (
        sessions
        .values("username")
        .annotate(
            total_sessions=Count("id"),
            total_duration=Sum("duration_seconds")
        )
        .order_by("-total_duration")
    )

    return render(request, "report.html", {
        "users": users,
        "title": "Havi VPN riport"
    })


# =========================
# USER HISTORY
# =========================

def user_history(request, username):

    sessions = VPNSession.objects.filter(
        username=username,
        disconnected_at__isnull=False
    ).order_by("-connected_at")

    paginator = Paginator(sessions, 50)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    return render(request, "user_history.html", {
        "username": username,
        "sessions": page_obj
    })

