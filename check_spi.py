#!/usr/bin/env python3
"""
Проверка SPI на Raspberry Pi
"""

import os
import subprocess
import sys

def check_spi_module():
    """Проверка модуля spidev"""
    try:
        import spidev
        print("✅ spidev модуль доступен")
        return True
    except ImportError:
        print("❌ spidev модуль не найден!")
        print("🔧 Установите: sudo apt install python3-spidev")
        return False

def check_spi_devices():
    """Проверка SPI устройств"""
    try:
        result = subprocess.run(['ls', '/dev/spi*'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ SPI устройства не найдены!")
            print("🔧 Для включения SPI:")
            print("   1. sudo raspi-config")
            print("   2. Выберите: 3 Interface Options → P4 SPI → Yes")
            print("   3. sudo reboot")
            return False
        else:
            print("✅ SPI устройства обнаружены:")
            print(result.stdout.strip())
            return True
    except Exception as e:
        print(f"⚠️  Ошибка проверки SPI устройств: {e}")
        return False

def check_spi_config():
    """Проверка конфигурации SPI"""
    config_files = [
        '/boot/firmware/config.txt',  # Новое расположение
        '/boot/config.txt'            # Старое расположение
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"📁 Найден конфиг: {config_file}")
            try:
                with open(config_file, 'r') as f:
                    content = f.read()
                    if 'dtparam=spi=on' in content:
                        print("✅ SPI включен в конфигурации")
                        return True
                    else:
                        print("❌ SPI не включен в конфигурации")
                        return False
            except Exception as e:
                print(f"⚠️  Ошибка чтения конфига: {e}")
                return False
    
    print("❌ Конфигурационные файлы не найдены")
    return False

def test_spi_communication():
    """Тест SPI коммуникации"""
    try:
        import spidev
        spi = spidev.SpiDev()
        spi.open(0, 0)  # SPI bus 0, device 0
        spi.max_speed_hz = 1000000
        spi.mode = 0
        
        # Простой тест записи/чтения
        test_data = [0x01, 0x02, 0x03]
        response = spi.xfer2(test_data)
        
        print("✅ SPI коммуникация работает")
        spi.close()
        return True
    except PermissionError:
        print("❌ Нет прав доступа к SPI устройствам")
        print("🔧 Решение: sudo usermod -a -G spi $USER")
        print("   Затем выйдите и войдите снова")
        return False
    except Exception as e:
        print(f"❌ Ошибка SPI коммуникации: {e}")
        return False

def check_spi_permissions():
    """Проверка прав доступа к SPI"""
    try:
        import os
        import grp
        
        # Проверка группы spi
        try:
            spi_group = grp.getgrnam('spi')
            current_groups = os.getgroups()
            
            if spi_group.gr_gid in current_groups:
                print("✅ Пользователь в группе spi")
                return True
            else:
                print("❌ Пользователь НЕ в группе spi")
                print("🔧 Решение: sudo usermod -a -G spi $USER")
                print("   Затем выйдите и войдите снова")
                return False
        except KeyError:
            print("❌ Группа spi не найдена")
            return False
    except Exception as e:
        print(f"⚠️  Ошибка проверки прав: {e}")
        return False

def main():
    """Главная функция проверки"""
    print("🔍 Проверка SPI на Raspberry Pi")
    print("=" * 40)
    
    checks = [
        ("Модуль spidev", check_spi_module),
        ("SPI устройства", check_spi_devices),
        ("Конфигурация SPI", check_spi_config),
        ("Права доступа SPI", check_spi_permissions),
        ("SPI коммуникация", test_spi_communication)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"\n🔍 Проверка: {name}")
        if check_func():
            passed += 1
        else:
            print(f"❌ {name} - НЕ ПРОЙДЕНА")
    
    print(f"\n📊 Результат: {passed}/{total} проверок пройдено")
    
    if passed == total:
        print("🎉 SPI полностью настроен и готов к работе!")
        return True
    else:
        print("⚠️  SPI требует настройки")
        print("\n🔧 Рекомендации:")
        print("1. Включите SPI: sudo raspi-config")
        print("2. Установите spidev: sudo apt install python3-spidev")
        print("3. Перезагрузите: sudo reboot")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
