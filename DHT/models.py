from django.db import models
class Dht11(models.Model):
    temp = models.FloatField(null=True)
    hum = models.FloatField(null=True)
    dt = models.DateTimeField(auto_now_add=True,null=True)
# Create your models here.
    def __str__(self):
        return f"Temperature: {self.temp}°C, Humidity: {self.hum}% at {self.dt}"
