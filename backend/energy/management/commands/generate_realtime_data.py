from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
import time
from devices.models import Device
from energy.models import EnergyConsumption, DailyStatistics


class Command(BaseCommand):
    help = 'Генерирует данные в реальном времени каждые 5 секунд'

    def add_arguments(self, parser):
        parser.add_argument('--duration', type=int, default=3600, help='Длительность в секундах (по умолчанию 1 час)')

    def handle(self, *args, **options):
        duration = options['duration']
        start_time = time.time()
        counter = 0

        self.stdout.write(self.style.SUCCESS(f'Начал генерацию на {duration} секунд...'))

        while time.time() - start_time < duration:
            counter += 1
            now = timezone.now()
            today = now.date()

            devices = Device.objects.all()

            for device in devices:
                # Генерируем случайное потребление
                if device.power_state == 'on' and device.status == 'online':
                    power = random.uniform(device.rated_power * 0.3, device.rated_power)
                else:
                    power = 0

                # Сохраняем текущее потребление
                device.current_power = power
                device.last_update = now
                device.save()

                # Создаем запись потребления
                EnergyConsumption.objects.create(
                    device=device,
                    power=power,
                    energy=power / 12  # 5 секунд = 1/720 часа, но используем 1/12 для более видимых данных
                )

            # Обновляем суточную статистику каждый час
            if counter % 720 == 0:  # 720 * 5 сек = 1 час
                for device in devices:
                    today_consumptions = EnergyConsumption.objects.filter(
                        device=device,
                        created_at__date=today
                    )

                    if today_consumptions.exists():
                        total_energy = sum(e.energy for e in today_consumptions)
                        powers = [e.power for e in today_consumptions]
                        avg_power = sum(powers) / len(powers) if powers else 0
                        peak_power = max(powers) if powers else 0
                        cost = total_energy * 7.22

                        DailyStatistics.objects.update_or_create(
                            device=device,
                            date=today,
                            defaults={
                                'total_energy': total_energy,
                                'avg_power': avg_power,
                                'peak_power': peak_power,
                                'cost': cost
                            }
                        )

            # Печатаем статус каждые 60 записей (5 минут)
            if counter % 60 == 0:
                self.stdout.write(self.style.SUCCESS(f'Итерация {counter} ({counter * 5} сек)'))

            time.sleep(5)

        self.stdout.write(self.style.SUCCESS('Генерация завершена!'))
