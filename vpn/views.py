from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count, Sum
from django.core.paginator import Paginator
from django.template.loader import get_template

from datetime import timedelta
from xhtml2pdf import pisa

from app.models import VPNSession


# ======================================================
# HELPERS
# ======================================================

def format_duration(seconds):
    if not seconds:
        return "0h 0m"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    return f"{hours}h {minutes}m"


def get_report_queryset(period):

    now = timezone.now()

    if period == "daily":
        sessions = VPNSession.objects.filter(
            connected_at__date=now.date(),
            disconnected_at__isnull=False
        )
        title = "Napi VPN riport"

    elif period == "weekly":
        sessions = VPNSession.objects.filter(
            connected_at__gte=now - timedelta(days=7),
            disconnected_at__isnull=False
        )
        title = "Heti VPN riport"

    elif period == "monthly":
        sessions = VPNSession.objects.filter(
            connected_at__gte=now - timedelta(days=30),
            disconnected_at__isnull=False
        )
        title = "Havi VPN riport"

    else:
        sessions = VPNSession.objects.none()
        title = "VPN riport"

    users = (
        sessions
        .values("username")
        .annotate(
            total_sessions=Count("id"),
            total_duration=Sum("duration_seconds")
        )
        .order_by("-total_duration")
    )

    return users, title


# ======================================================
# DASHBOARD
# ======================================================

def dashboard(request):

    active_sessions = VPNSession.objects.filter(
        disconnected_at__isnull=True
    ).order_by("-connected_at")

    now = timezone.now()

    for s in active_sessions:

        delta = now - s.connected_at
        seconds = int(delta.total_seconds())

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        if hours > 0:
            s.duration = f"{hours}h {minutes}m"
        else:
            s.duration = f"{minutes}m"

    active_users = active_sessions.count()

    today_sessions = VPNSession.objects.filter(
        connected_at__date=now.date()
    ).count()

    week_sessions = VPNSession.objects.filter(
        connected_at__gte=now - timedelta(days=7)
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
        "week_sessions": week_sessions,
        "total_sessions": total_sessions,
        "top_user": top_user
    }

    return render(request, "dashboard.html", context)


# ======================================================
# API - VPN LOCATIONS
# ======================================================

def vpn_locations(request):

    sessions = VPNSession.objects.filter(
        disconnected_at__isnull=True
    )

    data = []

    for s in sessions:

        if not s.latitude or not s.longitude:
            continue

        data.append({
            "username": s.username,
            "ip": s.remote_ip,
            "lat": s.latitude,
            "lon": s.longitude,
            "country": s.country,
            "country_code": s.country_code
        })

    return JsonResponse(data, safe=False)


# ======================================================
# API - DASHBOARD STATS
# ======================================================

def dashboard_stats(request):

    now = timezone.now()

    active_users = VPNSession.objects.filter(
        disconnected_at__isnull=True
    ).count()

    today_sessions = VPNSession.objects.filter(
        connected_at__date=now.date()
    ).count()

    week_sessions = VPNSession.objects.filter(
        connected_at__gte=now - timedelta(days=7)
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
        "week_sessions": week_sessions,
        "total_sessions": total_sessions,
        "top_user": top_user["username"] if top_user else "-"
    })


# ======================================================
# API - ACTIVE VPN SESSIONS
# ======================================================

def active_vpn_sessions(request):

    sessions = VPNSession.objects.filter(
        disconnected_at__isnull=True
    ).order_by("-connected_at")

    now = timezone.now()

    data = []

    for s in sessions:

        delta = now - s.connected_at
        seconds = int(delta.total_seconds())

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        duration = f"{hours}h {minutes}m" if hours else f"{minutes}m"

        data.append({
            "username": s.username,
            "ip": s.remote_ip,
            "country_code": s.country_code,
            "connected_at": s.connected_at.strftime("%Y.%m.%d %H:%M:%S"),
            "connected_at_iso": s.connected_at.isoformat(),
            "duration": duration
        })

    return JsonResponse(data, safe=False)


# ======================================================
# REPORT PAGES
# ======================================================

def report_daily(request):

    users, title = get_report_queryset("daily")

    return render(request, "report.html", {
        "users": users,
        "title": title,
        "period": "daily"
    })


def report_weekly(request):

    users, title = get_report_queryset("weekly")

    return render(request, "report.html", {
        "users": users,
        "title": title,
        "period": "weekly"
    })


def report_monthly(request):

    users, title = get_report_queryset("monthly")

    return render(request, "report.html", {
        "users": users,
        "title": title,
        "period": "monthly"
    })


# ======================================================
# USER HISTORY
# ======================================================

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


# ======================================================
# LIVE DASHBOARD API
# ======================================================

def live_dashboard(request):

    active_sessions = VPNSession.objects.filter(
        disconnected_at__isnull=True
    )

    now = timezone.now()

    data = []

    for s in active_sessions:

        delta = now - s.connected_at
        minutes = int(delta.total_seconds() / 60)

        data.append({
            "username": s.username,
            "ip": s.remote_ip,
            "country": s.country_code,
            "connected_at": s.connected_at.strftime("%Y.%m.%d %H:%M:%S"),
            "duration": f"{minutes}m",
            "lat": s.latitude,
            "lon": s.longitude
        })

    return JsonResponse({
        "active_users": active_sessions.count(),
        "sessions": data
    })


# ======================================================
# PDF REPORT
# ======================================================

def report_pdf(request, period):

    users, title = get_report_queryset(period)

    template = get_template("report_pdf.html")

    html = template.render({
        "users": users,
        "title": title
    })

    response = HttpResponse(content_type="application/pdf")

    date_str = timezone.now().strftime("%Y-%m-%d")

    response["Content-Disposition"] = (
        f'attachment; filename="{period}_vpn_report_{date_str}.pdf"'
    )

    pisa.CreatePDF(html, dest=response)

    return response
