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
# HELPER
# ======================================================

def format_duration(seconds):

    if not seconds:
        return "0h 0m"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    return f"{hours}h {minutes}m"


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

        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60

        if hours > 0:
            s.duration = f"{hours}h {minutes}m"
        else:
            s.duration = f"{minutes}m"

    # =========================
    # STATISZTIKA
    # =========================

    active_users = active_sessions.count()

    today_sessions = VPNSession.objects.filter(
        connected_at__date=timezone.now().date()
    ).count()

    week_sessions = VPNSession.objects.filter(
        connected_at__gte=timezone.now() - timedelta(days=7)
    ).count()

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
        "top_user": top_user
    }

    return render(request, "dashboard.html", context)


# ======================================================
# API - VPN LOCATIONS
# ======================================================

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


# ======================================================
# API - DASHBOARD STATS
# ======================================================

def dashboard_stats(request):

    active_users = VPNSession.objects.filter(
        disconnected_at__isnull=True
    ).count()

    today_sessions = VPNSession.objects.filter(
        connected_at__date=timezone.now().date()
    ).count()

    week_sessions = VPNSession.objects.filter(
        connected_at__gte=timezone.now() - timedelta(days=7)
    ).count()

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
        "top_user": top_user["username"] if top_user else "-"
    })


# ======================================================
# API - ACTIVE VPN SESSIONS
# ======================================================

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


# ======================================================
# REPORTS
# ======================================================

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
        "title": "Napi VPN riport",
        "period": "daily"
    })


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
        "title": "Heti VPN riport",
        "period": "weekly"
    })


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
        "title": "Havi VPN riport",
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
# PDF REPORT
# ======================================================

def report_pdf(request, period):

    period_hu = {
        "daily": "Napi",
        "weekly": "Heti",
        "monthly": "Havi"
    }.get(period, period)

    now = timezone.now()

    if period == "daily":

        sessions = VPNSession.objects.filter(
            connected_at__date=now.date(),
            disconnected_at__isnull=False
        )

    elif period == "weekly":

        start = now - timedelta(days=7)

        sessions = VPNSession.objects.filter(
            connected_at__gte=start,
            disconnected_at__isnull=False
        )

    elif period == "monthly":

        start = now - timedelta(days=30)

        sessions = VPNSession.objects.filter(
            connected_at__gte=start,
            disconnected_at__isnull=False
        )

    else:

        sessions = VPNSession.objects.none()

    for s in sessions:
        s.duration = format_duration(s.duration_seconds)

    user_summary = (
        sessions
        .values("username")
        .annotate(
            total_sessions=Count("id"),
            total_duration=Sum("duration_seconds")
        )
        .order_by("-total_duration")
    )

    for u in user_summary:
        u["duration"] = format_duration(u["total_duration"])

    top_user = user_summary[0]["username"] if user_summary else "-"

    template = get_template("report_pdf.html")

    html = template.render({
        "sessions": sessions,
        "user_summary": user_summary,
        "period": period,
        "period_hu": period_hu,
        "now": now,
        "top_user": top_user
    })

    response = HttpResponse(content_type="application/pdf")

    response["Content-Disposition"] = f'attachment; filename="vpn_{period_hu}_riport.pdf"'

    pisa.CreatePDF(html, dest=response)

    return response
