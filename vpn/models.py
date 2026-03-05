from django.db import models
from django.utils import timezone


class VPNSession(models.Model):

    username = models.CharField(max_length=100)
    remote_ip = models.GenericIPAddressField()

    connected_at = models.DateTimeField()
    disconnected_at = models.DateTimeField(null=True, blank=True)

    duration_seconds = models.IntegerField(null=True, blank=True)

    country = models.CharField(max_length=100, null=True, blank=True)
    country_code = models.CharField(max_length=2, null=True, blank=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

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
        return f"{self.username} {self.remote_ip}"
