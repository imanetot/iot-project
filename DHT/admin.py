from django.contrib import admin
from .models import Dht11

@admin.register(Dht11)
class Dht11Admin(admin.ModelAdmin):
    list_display = ['id', 'temp', 'hum', 'dt']
    list_filter = ['dt']
    search_fields = ['temp', 'hum']
    ordering = ['-dt']