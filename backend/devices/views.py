from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
import random

from .models import Device, DeviceAction, Schedule
from .serializers import DeviceSerializer, ScheduleSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Включить/выключить устройство"""
        device = self.get_object()
        device.power_state = 'off' if device.power_state == 'on' else 'on'
        device.current_power = random.uniform(0.5, device.rated_power) if device.power_state == 'on' else 0
        device.save()
        
        DeviceAction.objects.create(
            device=device,
            action_type='toggle',
            details={'new_state': device.power_state, 'power': device.current_power}
        )
        
        return Response({
            'status': 'device toggled',
            'device': DeviceSerializer(device).data
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Сводка по всем устройствам"""
        devices = Device.objects.all()
        total_power = sum(d.current_power for d in devices)
        online_count = devices.filter(status='online').count()
        
        return Response({
            'total_devices': devices.count(),
            'online_devices': online_count,
            'offline_devices': devices.count() - online_count,
            'total_current_power': round(total_power, 2),
            'devices': DeviceSerializer(devices, many=True).data
        })

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    
    @action(detail=False, methods=['get'])
    def by_device(self, request):
        """Получить все расписания для устройства"""
        device_id = request.query_params.get('device_id')
        if not device_id:
            return Response({'error': 'device_id required'}, status=400)
        
        schedules = Schedule.objects.filter(device_id=device_id).order_by('time')
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def create_for_device(self, request):
        """Создать расписание для устройства"""
        device_id = request.data.get('device_id')
        time = request.data.get('time')
        action = request.data.get('action')
        
        if not all([device_id, time, action]):
            return Response({'error': 'Missing required fields'}, status=400)
        
        schedule = Schedule.objects.create(
            device_id=device_id,
            time=time,
            action=action,
            enabled=True
        )
        serializer = self.get_serializer(schedule)
        return Response(serializer.data, status=201)
    
    @action(detail=True, methods=['patch'])
    def toggle_enabled(self, request, pk=None):
        """Включить/отключить расписание"""
        schedule = self.get_object()
        schedule.enabled = not schedule.enabled
        schedule.save()
        
        serializer = self.get_serializer(schedule)
        return Response(serializer.data)