import numpy as np
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Max, StdDev, Sum, Count, Q
from ..models import EnergyConsumption, DailyStatistics, AnomalyAlert, SavingRecommendation, AnomalyLog
from devices.models import Device, DeviceAction
from ml_models.detector import predict as ml_predict


def extract_features(device):
    now = timezone.now()
    today = now.date()
    yesterday = today - timedelta(days=1)
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)

    rated = device.rated_power or 1
    load_ratio = device.current_power / rated if rated else 0

    recent_consumption = EnergyConsumption.objects.filter(
        device=device, timestamp__gte=last_24h
    )
    avg_power_24h = recent_consumption.aggregate(Avg('power'))['power__avg'] or 0
    peak_power_24h = recent_consumption.aggregate(Max('power'))['power__max'] or 0

    night_consumption = EnergyConsumption.objects.filter(
        device=device, timestamp__gte=last_24h,
        timestamp__hour__gte=23
    ) | EnergyConsumption.objects.filter(
        device=device, timestamp__gte=last_24h,
        timestamp__hour__lte=6
    )
    total_24h = recent_consumption.aggregate(Sum('energy'))['energy__sum'] or 0
    night_24h = night_consumption.aggregate(Sum('energy'))['energy__sum'] or 0
    night_ratio = night_24h / total_24h if total_24h > 0 else 0

    try:
        power_std = recent_consumption.aggregate(StdDev('power'))['power__std'] or 0
    except Exception:
        values = list(recent_consumption.values_list('power', flat=True))
        power_std = np.std(values) if len(values) > 1 else 0

    last_action = DeviceAction.objects.filter(device=device).first()
    hours_since_toggle = 0
    if last_action:
        delta = now - last_action.timestamp
        hours_since_toggle = delta.total_seconds() / 3600

    stats_7d = DailyStatistics.objects.filter(
        device=device, date__gte=last_7d.date()
    )
    avg_daily_7d = stats_7d.aggregate(Avg('total_energy'))['total_energy__avg'] or 0

    features = [
        load_ratio,
        avg_power_24h / rated if rated else 0,
        peak_power_24h / rated if rated else 0,
        night_ratio,
        min(hours_since_toggle / 24, 1),
        min(power_std / (rated + 0.01), 1),
        min(avg_daily_7d / (rated * 24 + 0.01), 1),
    ]
    return features, {
        'load_ratio': round(load_ratio, 4),
        'avg_power_24h': round(avg_power_24h, 4),
        'peak_power_24h': round(peak_power_24h, 4),
        'night_ratio': round(night_ratio, 4),
        'hours_since_toggle': round(hours_since_toggle, 2),
        'power_std': round(power_std, 4),
        'avg_daily_7d': round(avg_daily_7d, 4),
        'total_24h': round(total_24h, 4),
    }


def _log_anomaly(device, anomaly_type, load_ratio, description):
    AnomalyLog.objects.create(
        device=device,
        anomaly_type=anomaly_type,
        load_ratio=round(load_ratio, 4),
        description=description,
    )


def _close_old_alerts(device, anomaly_type):
    now = timezone.now()
    AnomalyAlert.objects.filter(
        device=device, anomaly_type=anomaly_type, resolved_at__isnull=True
    ).update(resolved_at=now)


def run_anomaly_detection():
    alerts = []

    for device in Device.objects.filter(status='online'):
        features, ctx = extract_features(device)
        result = ml_predict(features)

        if result and result['is_anomaly']:
            desc = _describe_anomaly(device, ctx)
            _close_old_alerts(device, 'ml_anomaly')
            alert = AnomalyAlert.objects.create(
                device=device, anomaly_type='ml_anomaly',
                severity='high' if result['anomaly_score'] > 0.7 else 'medium',
                description=desc, ml_score=result['anomaly_score'],
                current_value=ctx['load_ratio'],
                expected_value=ctx['avg_daily_7d'] / (device.rated_power or 1),
            )
            _log_anomaly(device, 'ml_anomaly', ctx['load_ratio'], desc)
            alerts.append(alert)

        if device.power_state == 'on':
            a = _check_overload(device, ctx)
            b = _check_forgotten(device, ctx)
            c = _check_night_work(device, ctx, timezone.now())
            for a2 in [a, b, c]:
                if a2:
                    alerts.append(a2)

    return alerts


def _check_overload(device, ctx):
    if ctx['load_ratio'] > 0.9:
        _close_old_alerts(device, 'overload')
        desc = f"{device.name} работает на {(ctx['load_ratio']*100):.0f}% от номинала"
        alert = AnomalyAlert.objects.create(
            device=device, anomaly_type='overload', severity='high',
            description=desc, current_value=ctx['load_ratio'], expected_value=0.8,
        )
        _log_anomaly(device, 'overload', ctx['load_ratio'], desc)
        return alert
    return None


def _check_forgotten(device, ctx):
    if ctx['hours_since_toggle'] > 12:
        _close_old_alerts(device, 'forgotten')
        desc = f"{device.name} включено более {int(ctx['hours_since_toggle'])}ч без переключения"
        alert = AnomalyAlert.objects.create(
            device=device, anomaly_type='forgotten', severity='medium',
            description=desc, current_value=ctx['hours_since_toggle'], expected_value=8,
        )
        _log_anomaly(device, 'forgotten', ctx['load_ratio'], desc)
        return alert
    return None


def _check_night_work(device, ctx, now):
    hour = now.hour
    if hour >= 1 and hour <= 5 and device.power_state == 'on' \
            and device.device_type in ('climate', 'appliance', 'other'):
        _close_old_alerts(device, 'night_work')
        desc = f"{device.name} работает в {hour}ч ночи — возможно, стоит отключить"
        alert = AnomalyAlert.objects.create(
            device=device, anomaly_type='night_work', severity='low',
            description=desc, current_value=1, expected_value=0,
        )
        _log_anomaly(device, 'night_work', ctx['load_ratio'], desc)
        return alert
    return None


def _describe_anomaly(device, ctx):
    if ctx['load_ratio'] > 0.8:
        return f"{device.name}: аномально высокая загрузка ({(ctx['load_ratio']*100):.0f}%)"
    if ctx['night_ratio'] > 0.5:
        return f"{device.name}: {(ctx['night_ratio']*100):.0f}% потребления приходится на ночь"
    return f"{device.name}: необычный паттерн потребления (оценка ML)"


def generate_saving_scenarios():
    now = timezone.now()
    last_7d = now - timedelta(days=7)
    scenarios = []

    for device in Device.objects.filter(status='online'):
        # --- Анализируем логи за последние 7 дней ---
        recent_logs = AnomalyLog.objects.filter(
            device=device, created_at__gte=last_7d
        )
        overload_count = recent_logs.filter(anomaly_type='overload').count()
        night_count = recent_logs.filter(anomaly_type='night_work').count()
        forgotten_count = recent_logs.filter(anomaly_type='forgotten').count()

        # Рекомендация 1: перегрузка > 90%
        if overload_count > 0:
            title = f"Проверьте {device.name} на неисправность"
            description = (f"За последние 7 дней зафиксировано {overload_count} случаев перегрузки "
                          f"(>90% от номинала). Рекомендуется проверить устройство на неисправность "
                          f"или перегрев.")
            rec, created = SavingRecommendation.objects.get_or_create(
                device=device, scenario_type='replacement',
                defaults=dict(title=title, description=description,
                              current_cost=0, estimated_savings=0,
                              savings_percent=0),
            )
            if created:
                scenarios.append(rec)

        # Рекомендация 2: работа в ночное время
        if night_count > 0:
            title = f"Отключите {device.name} в ночное время"
            description = (f"За последние 7 дней зафиксировано {night_count} случаев работы "
                          f"в ночные часы. Отключение на ночь снизит потребление и продлит "
                          f"срок службы.")
            rec, created = SavingRecommendation.objects.get_or_create(
                device=device, scenario_type='night_shift',
                defaults=dict(title=title, description=description,
                              current_cost=0, estimated_savings=0,
                              savings_percent=0),
            )
            if created:
                scenarios.append(rec)

        # Рекомендация 3: забытое устройство
        if forgotten_count > 0:
            title = f"Настройте расписание для {device.name}"
            description = (f"Устройство было оставлено включённым более 12ч {forgotten_count} раз "
                          f"за последние 7 дней. Автоматическое расписание решит проблему.")
            rec, created = SavingRecommendation.objects.get_or_create(
                device=device, scenario_type='schedule',
                defaults=dict(title=title, description=description,
                              current_cost=0, estimated_savings=0,
                              savings_percent=0),
            )
            if created:
                scenarios.append(rec)

        # --- Старая логика (стоимостные рекомендации) ---
        stats = DailyStatistics.objects.filter(
            device=device, date__gte=last_7d.date()
        )
        total_cost = stats.aggregate(Sum('cost'))['cost__sum'] or 0
        monthly_cost = (total_cost / max(len(stats), 1)) * 30

        if device.device_type in ('climate', 'light', 'other') and monthly_cost > 100 \
                and not SavingRecommendation.objects.filter(
                    device=device, scenario_type='schedule',
                    title__startswith='Настройте расписание').exists():
            rec, created = SavingRecommendation.objects.get_or_create(
                device=device, scenario_type='schedule',
                defaults=dict(
                    title=f'Настроить расписание для {device.name}',
                    description='Отключение на 8ч/день сэкономит до 30%',
                    current_cost=round(monthly_cost, 2),
                    estimated_savings=round(monthly_cost * 0.3, 2),
                    savings_percent=30,
                ),
            )
            if created:
                scenarios.append(rec)

    return list(SavingRecommendation.objects.filter(
        device__status='online'
    ).select_related('device'))
