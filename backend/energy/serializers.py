from rest_framework import serializers
from .models import EnergyConsumption, DailyStatistics


class EnergyConsumptionSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = EnergyConsumption
        fields = ['id', 'device', 'device_name', 'power', 'energy', 'timestamp']


class DailyStatisticsSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = DailyStatistics
        fields = ['id', 'device', 'device_name', 'date', 'total_energy', 
                  'avg_power', 'peak_power', 'cost']
