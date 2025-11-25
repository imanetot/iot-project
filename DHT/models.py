from django.db import models
class Dht11(models.Model):
    temp = models.FloatField(null=True)
    hum = models.FloatField(null=True)
    dt = models.DateTimeField(auto_now_add=True,null=True)
# Create your models here.
    def __str__(self):
        return f"Temperature: {self.temp}°C, Humidity: {self.hum}% at {self.dt}"


class Incident(models.Model):
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    compteur = models.IntegerField(default=0)
    actif = models.BooleanField(default=True)

    # Opérations correctives
    op1_checked = models.BooleanField(default=False)
    op1_comment = models.TextField(blank=True)
    op2_checked = models.BooleanField(default=False)
    op2_comment = models.TextField(blank=True)
    op3_checked = models.BooleanField(default=False)
    op3_comment = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_debut']

    def __str__(self):
        return f"Incident {self.id} - Compteur: {self.compteur}"


class ArchiveIncident(models.Model):
    date = models.DateField(auto_now_add=True)
    nombre_incidents = models.IntegerField(default=0)

    class Meta:
        unique_together = ['date']
        ordering = ['-date']