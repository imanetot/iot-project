from django.http import HttpResponse
from django.http import JsonResponse
from django.utils import timezone
from .models import Dht11
import csv
from .serializers import DHT11serialize
from django.shortcuts import render
from .models import Dht11

def graphique(request):
    data = Dht11.objects.all()
    return render(request, 'chart.html', {'data': data})

def test(request):
    return HttpResponse('IoT Project')

def table(request):
    derniere_ligne = Dht11.objects.last()
    derniere_date = Dht11.objects.last().dt
    delta_temps = timezone.now()
    difference_minutes = delta_temps.seconds // 60
    temps_ecoule = ' il y a ' + str(difference_minutes) + ' min'
    if difference_minutes> 60:
        temps_ecoule = ('il y ' + str(difference_minutes // 60) + 'h' +
                        str(difference_minutes % 60) + 'min')
        valeurs = {'date': temps_ecoule, 'id': derniere_ligne.id, 'temp':
            derniere_ligne.temp, 'hum': derniere_ligne.hum}
        return render(request, 'value.html', {'valeurs': valeurs})

def download_csv(request):
    # Create the HTTP response with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dht.csv"'

    # Create a CSV writer
    writer = csv.writer(response)

    # Write header row
    writer.writerow(['id', 'temp', 'hum', 'dt'])

    # Query all Dht11 objects and extract desired fields
    model_values = Dht11.objects.values_list('id', 'temp', 'hum', 'dt')

    # Write data rows
    for row in model_values:
        writer.writerow(row)

    return response
def dashboard(request):
    # Rend juste la page; les données sont chargées via JS
    return render(request, "dashboard.html")

def latest_json(request):
    # Fournit la dernière mesure en JSON (sans passer par api.py)
    last = Dht11.objects.order_by('-dt').values('temp', 'hum', 'dt').first()
    if not last:
        return JsonResponse({"detail": "no data"}, status=404)
    return JsonResponse({
        "temperature": last["temp"],
        "humidity":    last["hum"],
        "timestamp":   last["dt"].isoformat()
    })
# Create your views here.
