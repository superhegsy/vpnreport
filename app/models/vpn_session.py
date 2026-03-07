from django.db import models
from django.utils import timezone


class VPNSession(models.Model):

    username = models.CharField(max_length=100)

    remote_ip = models.GenericIPAddressField()

    vpn_ip = models.GenericIPAddressField(null=True, blank=True)

    connected_at = models.DateTimeField()

    disconnected_at = models.DateTimeField(null=True, blank=True)

    duration_seconds = models.IntegerField(null=True, blank=True)

    country = models.CharField(max_length=100, null=True, blank=True)

    country_code = models.CharField(max_length=2, null=True, blank=True)

    latitude = models.FloatField(null=True, blank=True)

    longitude = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "vpn"

        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["connected_at"]),
        ]

    def duration(self):

        if self.disconnected_at:
            delta = self.disconnected_at - self.connected_at
        else:
            delta = timezone.now() - self.connected_at

        total = int(delta.total_seconds())

        hours = total // 3600
        minutes = (total % 3600) // 60
        seconds = total % 60

        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def __str__(self):
        return f"{self.username} ({self.remote_ip})"


class FortiGateConfig(models.Model):

    name = models.CharField(max_length=100)

    host = models.GenericIPAddressField()

    port = models.IntegerField(default=443)

    api_token = models.CharField(max_length=255)

    poll_interval = models.IntegerField(default=60)

    enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "vpn"

    def __str__(self):
        return self.name
