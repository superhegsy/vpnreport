from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone

from django.db.models import Count
from django.db.models.functions import TruncDate

from datetime import timedelta

from xhtml2pdf import pisa

from .models import VPNSession


# =========================
# DASHBOARD
# =========================

def dashboard(request):

    sessions = VPNSession.objects.all().order_by("-connected_at")[:20]

    active_users = VPNSession.objects.filter(
        disconnected_at__isnull=True
    ).count()

    today_sessions = VPNSession.objects.filter(
        connected_at__date=timezone.now().date()
    ).count()

    total_sessions = VPNSession.objects.count()

    top_users = (
        VPNSession.objects
        .values("username")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    top_user = top_users.first()

    daily_stats = (
        VPNSession.objects
        .annotate(day=TruncDate("connected_at"))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )

    # 🌍 ország statisztika (grafikonhoz)
    country_stats = (
        VPNSession.objects
        .values("country")
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )

    context = {
        "sessions": sessions,
        "active_users": active_users,
        "today_sessions": today_sessions,
        "total_sessions": total_sessions,
        "top_user": top_user,
        "top_users": top_users,
        "daily_stats": daily_stats,
        "country_stats": country_stats
    }

    return render(request, "dashboard.html", context)


# =========================
# PDF REPORT GENERATOR
# =========================

def vpn_report_pdf(request, period):

    now = timezone.now()

    if period == "daily":
        start_date = now - timedelta(days=1)

    elif period == "weekly":
        start_date = now - timedelta(days=7)

    elif period == "monthly":
        start_date = now - timedelta(days=30)

    else:
        start_date = None

    if start_date:
        sessions = VPNSession.objects.filter(
            connected_at__gte=start_date
        )
    else:
        sessions = VPNSession.objects.all()

    html = render_to_string("report.html", {
        "sessions": sessions,
        "period": period
    })

    response = HttpResponse(content_type="application/pdf")

    response['Content-Disposition'] = (
        f'attachment; filename="vpn_report_{period}.pdf"'
    )

    pisa.CreatePDF(html, dest=response)

    return response


# =========================
# REPORT ROUTES
# =========================

def report_daily(request):
    return vpn_report_pdf(request, "daily")


def report_weekly(request):
    return vpn_report_pdf(request, "weekly")


def report_monthly(request):
    return vpn_report_pdf(request, "monthly")


# =========================
# MAP API (Leaflet)
# =========================

def vpn_locations(request):

    sessions = VPNSession.objects.exclude(
        latitude__isnull=True,
        longitude__isnull=True
    )

    data = []

    for s in sessions:

        data.append({
            "username": s.username,
            "ip": s.remote_ip,
            "lat": s.latitude,
            "lon": s.longitude,
            "country": s.country
        })

    return JsonResponse(data, safe=False)
