from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Avg, Max, Min
from datetime import timedelta, date
import random
from .models import EnergyConsumption, DailyStatistics
from .serializers import EnergyConsumptionSerializer, DailyStatisticsSerializer
from devices.models import Device


class EnergyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EnergyConsumption.objects.all()
    serializer_class = EnergyConsumptionSerializer
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Текущее потребление всех устройств"""
        today = timezone.now().date()
        devices = Device.objects.all()
        
        data = []
        for device in devices:
            daily = DailyStatistics.objects.filter(device=device, date=today).first()
            data.append({
                'id': device.id,
                'name': device.name,
                'device_type': device.device_type,
                'current_power': device.current_power,
                'daily_consumption': daily.total_energy if daily else 0,
                'status': device.status,
                'power_state': device.power_state,
            })
        
        total_power = sum(d['current_power'] for d in data)
        
        return Response({
            'timestamp': timezone.now(),
            'total_power': round(total_power, 2),
            'devices': data
        })
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Потребление за текущий день"""
        today = timezone.now().date()
        stats = DailyStatistics.objects.filter(date=today)
        
        total_energy = stats.aggregate(Sum('total_energy'))['total_energy__sum'] or 0
        total_cost = stats.aggregate(Sum('cost'))['cost__sum'] or 0
        
        return Response({
            'date': today,
            'total_energy': round(total_energy, 2),
            'total_cost': round(total_cost, 2),
            'devices': DailyStatisticsSerializer(stats, many=True).data
        })
    
    @action(detail=False, methods=['get'])
    def hourly(self, request):
        """Почасовые данные"""
        date_str = request.query_params.get('date')
        target_date = timezone.now().date() if not date_str else timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        
        consumptions = EnergyConsumption.objects.filter(
            timestamp__date=target_date
        ).order_by('timestamp')
        
        hourly_data = []
        for hour in range(24):
            start = timezone.make_aware(timezone.datetime.combine(target_date, timezone.datetime.min.time())) + timedelta(hours=hour)
            end = start + timedelta(hours=1)
            
            hour_consumptions = consumptions.filter(timestamp__gte=start, timestamp__lt=end)
            power = hour_consumptions.aggregate(Avg('power'))['power__avg'] or random.uniform(2, 8)
            
            hourly_data.append({
                'hour': f"{hour:02d}:00",
                'power': round(power, 2),
                'energy': round(power * 1.0, 2)
            })
        
        return Response({
            'date': target_date,
            'data': hourly_data
        })
    
    @action(detail=False, methods=['get'])
    def daily(self, request):
        """Суточные данные за месяц"""
        year = int(request.query_params.get('year', timezone.now().year))
        month = int(request.query_params.get('month', timezone.now().month))
        
        from datetime import date as date_class
        first_day = date_class(year, month, 1)
        if month == 12:
            last_day = date_class(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date_class(year, month + 1, 1) - timedelta(days=1)
        
        stats = DailyStatistics.objects.filter(
            date__gte=first_day,
            date__lte=last_day
        ).order_by('date')
        
        data = []
        current = first_day
        while current <= last_day:
            day_stats = stats.filter(date=current)
            total = day_stats.aggregate(Sum('total_energy'))['total_energy__sum'] or 0
            cost = day_stats.aggregate(Sum('cost'))['cost__sum'] or 0
            
            data.append({
                'date': str(current),
                'day': current.day,
                'energy': round(total, 2),
                'cost': round(cost, 2)
            })
            current += timedelta(days=1)
        
        return Response({
            'month': month,
            'year': year,
            'data': data
        })
    
    @action(detail=False, methods=['get'])
    def monthly(self, request):
        """Месячные данные за год"""
        year = int(request.query_params.get('year', timezone.now().year))
        
        from datetime import date as date_class
        data = []
        month_names = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 
                       'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дец']
        
        for month in range(1, 13):
            first_day = date_class(year, month, 1)
            if month == 12:
                last_day = date_class(year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = date_class(year, month + 1, 1) - timedelta(days=1)
            
            stats = DailyStatistics.objects.filter(
                date__gte=first_day,
                date__lte=last_day
            )
            
            total = stats.aggregate(Sum('total_energy'))['total_energy__sum'] or 0
            cost = stats.aggregate(Sum('cost'))['cost__sum'] or 0
            avg_power = stats.aggregate(Avg('avg_power'))['avg_power__avg'] or 0
            
            data.append({
                'month': month,
                'month_name': month_names[month - 1],
                'energy': round(total, 2),
                'cost': round(cost, 2),
                'avg_power': round(avg_power, 2)
            })
        
        return Response({
            'year': year,
            'data': data
        })
    
    @action(detail=False, methods=['get'])
    def top_consumers(self, request):
        """Топ потребителей"""
        today = timezone.now().date()
        stats = DailyStatistics.objects.filter(date=today).order_by('-total_energy')[:5]
        
        data = [
            {
                'device_name': s.device.name,
                'energy': round(s.total_energy, 2),
                'percentage': 0
            }
            for s in stats
        ]
        
        total = sum(d['energy'] for d in data)
        for d in data:
            d['percentage'] = round((d['energy'] / total * 100) if total > 0 else 0, 1)
        
        return Response({
            'date': today,
            'total_energy': round(total, 2),
            'consumers': data
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Общая статистика"""
        today = timezone.now().date()
        stats = DailyStatistics.objects.filter(date=today)
        
        consumption_data = stats.aggregate(
            total=Sum('total_energy'),
            avg=Avg('avg_power'),
            peak=Max('peak_power'),
            min=Min('peak_power')
        )
        
        cost = stats.aggregate(Sum('cost'))['cost__sum'] or 0
        
        return Response({
            'date': today,
            'total_energy': round(consumption_data['total'] or 0, 2),
            'avg_power': round(consumption_data['avg'] or 0, 2),
            'peak_power': round(consumption_data['peak'] or 0, 2),
            'min_power': round(consumption_data['min'] or 0, 2),
            'total_cost': round(cost, 2),
            'devices_count': DailyStatistics.objects.filter(date=today).count()
        })
    
    @action(detail=False, methods=['get'])
    def forecast(self, request):
        """Прогноз затрат на следующий месяц"""
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        recent_stats = DailyStatistics.objects.filter(date__gte=thirty_days_ago)
        
        avg_daily = recent_stats.aggregate(Avg('total_energy'))['total_energy__avg'] or 0
        avg_cost_daily = recent_stats.aggregate(Avg('cost'))['cost__avg'] or 0
        
        forecast_energy = round(avg_daily * 30, 2)
        forecast_cost = round(avg_cost_daily * 30, 2)
        
        return Response({
            'next_month_energy': forecast_energy,
            'next_month_cost': forecast_cost,
            'daily_average': round(avg_daily, 2),
            'confidence': 82
        })
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """Экспорт данных"""
        format_type = request.query_params.get('format', 'csv')
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        
        stats = DailyStatistics.objects.filter(
            date__gte=thirty_days_ago
        ).order_by('date')
        
        data = []
        for stat in stats:
            data.append({
                'date': str(stat.date),
                'device': stat.device.name,
                'energy': stat.total_energy,
                'cost': stat.cost,
                'avg_power': stat.avg_power
            })
        
        return Response({
            'format': format_type,
            'records': len(data),
            'data': data
        })
