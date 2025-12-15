from django.db import models


class Dht11(models.Model):
    temp = models.FloatField(null=True)
    hum = models.FloatField(null=True)
    dt = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Temperature: {self.temp}°C, Humidity: {self.hum}% at {self.dt}"


class Incident(models.Model):
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    compteur = models.IntegerField(default=0)
    actif = models.BooleanField(default=True)

    # Opérations correctives avec noms
    nom_op1 = models.CharField(max_length=200, default="Opération Corrective 1")
    op1_checked = models.BooleanField(default=False)
    op1_comment = models.TextField(blank=True, null=True)

    nom_op2 = models.CharField(max_length=200, default="Opération Corrective 2")
    op2_checked = models.BooleanField(default=False)
    op2_comment = models.TextField(blank=True, null=True)

    nom_op3 = models.CharField(max_length=200, default="Opération Corrective 3")
    op3_checked = models.BooleanField(default=False)
    op3_comment = models.TextField(blank=True, null=True)

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