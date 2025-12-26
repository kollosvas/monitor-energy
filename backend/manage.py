#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'energy_monitor_api.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Команды при которых нужно применить миграции автоматически
    auto_migrate_commands = ['runserver', 'ensure_tables']
    
    if len(sys.argv) > 1 and sys.argv in auto_migrate_commands:
        try:
            from django.core.management import call_command
            print("🔄 Проверка и применение миграций...")
            call_command('migrate', verbosity=0, interactive=False)
            print("✅ Миграции применены\n")
        except Exception as e:
            print(f"⚠️  Ошибка при миграции: {e}\n")
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
