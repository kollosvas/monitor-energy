from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from energy.models import EnergyConsumption
from devices.models import Device
from energy.services.anomaly_service import extract_features
from ml_models.train import train


class Command(BaseCommand):
    help = 'Обучает ML-модель для детекции аномалий'

    def handle(self, *args, **options):
        devices = Device.objects.filter(status='online')
        if not devices.exists():
            self.stdout.write(self.style.WARNING('Нет устройств. Сначала запусти generate_sample_data'))
            return

        features_matrix = []
        labels = []

        for device in devices:
            features, ctx = extract_features(device)
            features_matrix.append(features)

            is_normal = (
                ctx['load_ratio'] < 0.8 and
                ctx['night_ratio'] < 0.4 and
                ctx['hours_since_toggle'] < 10
            )
            labels.append(0 if is_normal else 1)

            self.stdout.write(f"  {device.name}: загрузка={ctx['load_ratio']:.2f}, "
                              f"ночь={ctx['night_ratio']:.2f}, часов={ctx['hours_since_toggle']:.1f}")

        path = train(features_matrix)
        self.stdout.write(self.style.SUCCESS(f'Модель обучена и сохранена: {path}'))
        self.stdout.write(self.style.SUCCESS(f'Обработано устройств: {len(features_matrix)}'))
