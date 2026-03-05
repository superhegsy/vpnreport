from django.db import models


class VPNSession(models.Model):
    username = models.CharField(max_length=100)
    remote_ip = models.GenericIPAddressField()

    connected_at = models.DateTimeField()
    disconnected_at = models.DateTimeField(null=True, blank=True)

    duration_seconds = models.IntegerField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    def __str__(self):
        return f"{self.username} {self.remote_ip}"
