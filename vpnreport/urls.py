from django.contrib import admin
from django.urls import path
from vpn import views

urlpatterns = [

    # =========================
    # ADMIN
    # =========================
    path('admin/', admin.site.urls),

    # =========================
    # DASHBOARD
    # =========================
    path('', views.dashboard, name='dashboard'),

    # =========================
    # REPORTS
    # =========================
    path('report/daily/', views.report_daily, name='report_daily'),
    path('report/weekly/', views.report_weekly, name='report_weekly'),
    path('report/monthly/', views.report_monthly, name='report_monthly'),

    # =========================
    # USER HISTORY
    # =========================
    path('report/user/<str:username>/', views.user_history, name='user_history'),

    # =========================
    # PDF REPORT
    # =========================
    path('report/pdf/<str:period>/', views.report_pdf, name='report_pdf'),

    # =========================
    # LIVE DASHBOARD API
    # =========================
    path('api/live-dashboard/', views.live_dashboard, name='live_dashboard'),

    # =========================
    # DASHBOARD DATA API
    # =========================
    path('api/dashboard-stats/', views.dashboard_stats, name='dashboard_stats'),
    path('api/active-vpn/', views.active_vpn_sessions, name='active_vpn_sessions'),
    path('api/vpn-locations/', views.vpn_locations, name='vpn_locations'),
]
