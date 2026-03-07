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
        return "0m"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours > 0:
        return f"{hours}h {minutes}m"

    return f"{minutes}m"


# ======================================================
# REPORT DATA
# ======================================================

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

    users_list = []

    for u in users:

        seconds = u["total_duration"] or 0

        users_list.append({
            "username": u["username"],
            "total_sessions": u["total_sessions"],
            "duration": format_duration(seconds)
        })

    return users_list, title


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

        s.duration = format_duration(seconds)

    context = {

        "sessions": active_sessions,

        "active_users": active_sessions.count(),

        "today_sessions": VPNSession.objects.filter(
            connected_at__date=now.date()
        ).count(),

        "week_sessions": VPNSession.objects.filter(
            connected_at__gte=now - timedelta(days=7)
        ).count(),

        "total_sessions": VPNSession.objects.count(),

        "top_user": (
            VPNSession.objects
            .values("username")
            .annotate(total=Count("id"))
            .order_by("-total")
            .first()
        )
    }

    return render(request, "dashboard.html", context)


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
# PDF REPORT
# ======================================================

def report_pdf(request, period):

    users, title = get_report_queryset(period)

    template = get_template("report_pdf.html")

    html = template.render({
        "users": users,
        "title": title,
        "now": timezone.now()
    })

    response = HttpResponse(content_type="application/pdf")

    date_str = timezone.now().strftime("%Y-%m-%d")

    response["Content-Disposition"] = (
        f'attachment; filename="{period}_vpn_report_{date_str}.pdf"'
    )

    pisa.CreatePDF(html, dest=response)

    return response

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
        seconds = int(delta.total_seconds())

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        if hours > 0:
            duration = f"{hours}h {minutes}m"
        else:
            duration = f"{minutes}m"

        data.append({
            "username": s.username,
            "ip": s.remote_ip,
            "country": s.country_code,
            "connected_at": s.connected_at.strftime("%Y.%m.%d %H:%M:%S"),
            "duration": duration,
            "lat": s.latitude,
            "lon": s.longitude
        })

    return JsonResponse({
        "active_users": active_sessions.count(),
        "sessions": data
    })
