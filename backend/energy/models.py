from django.db import models
from devices.models import Device


class EnergyConsumption(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='consumption', verbose_name='Устройство')
    power = models.FloatField(verbose_name='Мощность (кВт)')
    energy = models.FloatField(verbose_name='Энергия (кВт·ч)')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Время')
    
    class Meta:
        indexes = [
            models.Index(fields=['device', 'timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['device']),
        ]
        ordering = ['-timestamp']
        verbose_name = 'Потребление энергии'
        verbose_name_plural = 'Потребления энергии'
    
    def __str__(self):
        return f"{self.device.name} - {self.power}кВ"


class DailyStatistics(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='daily_stats', verbose_name='Устройство')
    date = models.DateField(verbose_name='Дата')
    total_energy = models.FloatField(verbose_name='Общая энергия (кВт·ч)')
    avg_power = models.FloatField(verbose_name='Средняя мощность (кВт)')
    peak_power = models.FloatField(verbose_name='Пиковая мощность (кВт)')
    cost = models.FloatField(verbose_name='Стоимость (₽)')
    
    class Meta:
        unique_together = ['device', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['device', 'date']),
        ]
        verbose_name = 'Суточная статистика'
        verbose_name_plural = 'Суточные статистики'
    
    def __str__(self):
        return f"{self.device.name} - {self.date}"
