from django.contrib import admin
from .models import EnergyConsumption, DailyStatistics


@admin.register(EnergyConsumption)
class EnergyConsumptionAdmin(admin.ModelAdmin):
    list_display = ['device', 'power', 'energy', 'timestamp']
    list_filter = ['device', 'timestamp']
    search_fields = ['device__name']
    readonly_fields = ['timestamp']


@admin.register(DailyStatistics)
class DailyStatisticsAdmin(admin.ModelAdmin):
    list_display = ['device', 'date', 'total_energy', 'avg_power', 'peak_power', 'cost']
    list_filter = ['date', 'device']
    search_fields = ['device__name']
