from django.http import HttpResponse
from django.http import JsonResponse
from django.utils import timezone
from .models import Dht11
import csv
from .serializers import DHT11serialize
from django.shortcuts import render
from .models import Dht11
import datetime


def index_view(request):
    """Page d'accueil - redirige vers le dashboard"""
    return render(request, 'dashboard.html')


def graphique(request):
    """Ancienne page graphique - garde pour compatibilité"""
    data = Dht11.objects.all()
    return render(request, 'chart.html', {'data': data})


def test(request):
    return HttpResponse('IoT Project')


def table(request):
    """Ancienne page table - garde pour compatibilité"""
    derniere_ligne = Dht11.objects.last()
    if not derniere_ligne:
        return render(request, 'value.html', {'valeurs': None})

    derniere_date = derniere_ligne.dt
    delta_temps = timezone.now() - derniere_date
    difference_minutes = delta_temps.seconds // 60

    temps_ecoule = ' il y a ' + str(difference_minutes) + ' min'
    if difference_minutes > 60:
        temps_ecoule = ('il y a ' + str(difference_minutes // 60) + 'h ' +
                        str(difference_minutes % 60) + 'min')

    valeurs = {
        'date': temps_ecoule,
        'id': derniere_ligne.id,
        'temp': derniere_ligne.temp,
        'hum': derniere_ligne.hum
    }
    return render(request, 'value.html', {'valeurs': valeurs})


def download_csv(request):
    """Téléchargement CSV de toutes les données"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dht11_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Temperature (°C)', 'Humidite (%)', 'Date et Heure'])

    model_values = Dht11.objects.values_list('id', 'temp', 'hum', 'dt')
    for row in model_values:
        writer.writerow(row)

    return response


def dashboard(request):
    """Dashboard principal - page d'accueil"""
    return render(request, "dashboard.html")


def graph_temp(request):
    """Page graphique température"""
    return render(request, "graph_temp.html")


def graph_hum(request):
    """Page graphique humidité"""
    return render(request, "graph_hum.html")


def latest_json(request):
    """API - Dernière mesure en JSON"""
    last = Dht11.objects.order_by('-dt').values('temp', 'hum', 'dt').first()
    if not last:
        return JsonResponse({"detail": "Aucune donnée disponible"}, status=404)
    return JsonResponse({
        "temperature": last["temp"],
        "humidity": last["hum"],
        "timestamp": last["dt"].isoformat()
    })


def chart_data(request):
    """API - Toutes les données pour graphiques"""
    dht = Dht11.objects.all().order_by('dt')
    data = {
        'temps': [dt.dt.isoformat() for dt in dht],
        'temperature': [temp.temp for temp in dht],
        'humidity': [hum.hum for hum in dht]
    }
    return JsonResponse(data)


def chart_data_jour(request):
    """API - Données des dernières 24h"""
    now = timezone.now()
    last_24_hours = now - timezone.timedelta(hours=24)
    dht = Dht11.objects.filter(dt__range=(last_24_hours, now)).order_by('dt')

    data = {
        'temps': [dt.dt.isoformat() for dt in dht],
        'temperature': [temp.temp for temp in dht],
        'humidity': [hum.hum for hum in dht]
    }
    return JsonResponse(data)


def chart_data_semaine(request):
    """API - Données de la dernière semaine"""
    date_debut_semaine = timezone.now() - datetime.timedelta(days=7)
    dht = Dht11.objects.filter(dt__gte=date_debut_semaine).order_by('dt')

    data = {
        'temps': [dt.dt.isoformat() for dt in dht],
        'temperature': [temp.temp for temp in dht],
        'humidity': [hum.hum for hum in dht]
    }
    return JsonResponse(data)


def chart_data_mois(request):
    """API - Données du dernier mois"""
    date_debut_mois = timezone.now() - datetime.timedelta(days=30)
    dht = Dht11.objects.filter(dt__gte=date_debut_mois).order_by('dt')

    data = {
        'temps': [dt.dt.isoformat() for dt in dht],
        'temperature': [temp.temp for temp in dht],
        'humidity': [hum.hum for hum in dht]
    }
    return JsonResponse(data)


from .models import Incident, ArchiveIncident


def incident_status(request):
    """API - Statut incident actuel"""
    incident = Incident.objects.filter(actif=True).first()

    if incident:
        return JsonResponse({
            "incident_actif": True,
            "compteur": incident.compteur,
            "date_debut": incident.date_debut.isoformat(),
            "op1_checked": incident.op1_checked,
            "op1_comment": incident.op1_comment,
            "op2_checked": incident.op2_checked,
            "op2_comment": incident.op2_comment,
            "op3_checked": incident.op3_checked,
            "op3_comment": incident.op3_comment,
        })
    else:
        return JsonResponse({
            "incident_actif": False,
            "compteur": 0
        })


def update_incident(request):
    """API - Mettre à jour incident"""
    if request.method == 'POST':
        incident = Incident.objects.filter(actif=True).first()
        if not incident:
            return JsonResponse({"error": "Aucun incident actif"}, status=400)

        import json
        data = json.loads(request.body)

        if 'op1_checked' in data:
            incident.op1_checked = data['op1_checked']
        if 'op1_comment' in data:
            incident.op1_comment = data['op1_comment']
        if 'op2_checked' in data:
            incident.op2_checked = data['op2_checked']
        if 'op2_comment' in data:
            incident.op2_comment = data['op2_comment']
        if 'op3_checked' in data:
            incident.op3_checked = data['op3_checked']
        if 'op3_comment' in data:
            incident.op3_comment = data['op3_comment']

        incident.save()
        return JsonResponse({"success": True})

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)


def archive_incidents(request):
    """Page archive des incidents"""
    archives = ArchiveIncident.objects.all()
    return render(request, 'archive_incidents.html', {'archives': archives})