from django.contrib import admin
from .models import VPNSession, FortiGateConfig


admin.site.register(VPNSession)


@admin.register(FortiGateConfig)
class FortiGateConfigAdmin(admin.ModelAdmin):

    list_display = ("name", "host", "enabled", "poll_interval")

    search_fields = ("name", "host")
