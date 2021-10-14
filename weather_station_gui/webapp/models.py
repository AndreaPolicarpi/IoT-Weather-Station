from django.db import models

# Create your models here.

class Sensor(models.Model):
    sensor_id = models.CharField("Sensor ID", max_length=10, unique=True, null=False, blank=False)

    def __str__(self):
        return self.sensor_id