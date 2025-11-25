from rest_framework import serializers
from . models import Dht11
class DHT11serialize(serializers.ModelSerializer):
    class Meta :
        model = Dht11
        fields = '__all__'

    def to_representation(self, instance):
        """Personnaliser la sortie JSON pour inclure temp et hum"""
        representation = super().to_representation(instance)
        # S'assurer que les noms des champs sont corrects
        return {
            'id': representation.get('id'),
            'temp': representation.get('temp'),
            'hum': representation.get('hum'),
            'temperature': representation.get('temp'),  # Alias pour compatibilité
            'humidity': representation.get('hum'),  # Alias pour compatibilité
            'dt': representation.get('dt')
        }