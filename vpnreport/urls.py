"""
URL configuration for vpnreport project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from vpn import views


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.dashboard),

    path('report/daily/', views.report_daily),
    path('report/weekly/', views.report_weekly),
    path('report/monthly/', views.report_monthly),

    path('api/vpn-locations/', views.vpn_locations),
    path('api/dashboard-stats/', views.dashboard_stats),
    path('api/active-vpn/', views.active_vpn_sessions),
]
