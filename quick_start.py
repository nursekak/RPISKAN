#!/usr/bin/env python3
"""
Быстрый запуск FPV сканера
Минимальный интерфейс для быстрого перехвата дронов
"""

import sys
import os
import subprocess

def check_requirements():
    """Проверка требований системы"""
    print("🔍 Проверка системы...")
    
    # Проверка Python
    if sys.version_info < (3, 6):
        print("❌ Требуется Python 3.6 или выше")
        return False
    
    # Проверка модулей
    required_modules = ['RPi.GPIO', 'spidev', 'cv2', 'PIL', 'tkinter']
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'RPi.GPIO':
                import RPi.GPIO
            elif module == 'spidev':
                import spidev
            elif module == 'cv2':
                import cv2
            elif module == 'PIL':
                from PIL import Image
            elif module == 'tkinter':
                import tkinter
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Отсутствуют модули: {', '.join(missing_modules)}")
        print("Запустите: ./install.sh")
        return False
    
    # Проверка SPI
    try:
        result = subprocess.run(['ls', '/dev/spi*'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ SPI не включен!")
            print("🔧 Для включения SPI запустите:")
            print("   chmod +x fix_spi.sh")
            print("   ./fix_spi.sh")
            return False
        else:
            print("✅ SPI устройства обнаружены")
    except:
        print("⚠️  Не удалось проверить SPI")
    
    # Проверка видео устройства
    try:
        result = subprocess.run(['ls', '/dev/video*'], capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠️  USB Video DVR не обнаружен")
        else:
            print("✅ USB Video DVR обнаружен")
    except:
        print("⚠️  Не удалось проверить видео устройство")
    
    print("✅ Система готова")
    return True

def show_menu():
    """Показать меню выбора"""
    print("\n🚁 FPV Scanner - Быстрый запуск")
    print("=" * 40)
    print("1. 🧪 Тест оборудования")
    print("2. 🎯 Простой сканер Python (рекомендуется)")
    print("3. ⚡ C сканер простой (рекомендуется)")
    print("4. 🚀 C сканер нативный")
    print("5. 📊 Только сканирование (без GUI)")
    print("6. ⚡ Включить SPI")
    print("7. 🔧 Настройки")
    print("8. ❌ Выход")
    print("=" * 40)

def run_hardware_test():
    """Запуск теста оборудования"""
    print("🧪 Запуск теста оборудования...")
    try:
        subprocess.run([sys.executable, 'examples/test_hardware.py'])
    except Exception as e:
        print(f"❌ Ошибка запуска теста: {e}")

def run_simple_scanner():
    """Запуск простого сканера"""
    print("🎯 Запуск простого сканера...")
    try:
        subprocess.run([sys.executable, 'src/simple_scanner.py'])
    except Exception as e:
        print(f"❌ Ошибка запуска сканера: {e}")

def run_advanced_scanner():
    """Запуск продвинутого сканера"""
    print("⚙️ Продвинутый сканер недоступен (удален для упрощения)")
    print("Используйте простой сканер (опция 2)")

def run_c_simple_scanner():
    """Запуск простого C сканера"""
    print("⚡ Запуск простого C сканера...")
    try:
        # Проверка, скомпилирован ли простой C сканер
        if os.path.exists('fpv_scanner_simple'):
            subprocess.run(['sudo', './fpv_scanner_simple'])
        else:
            print("❌ Простой C сканер не скомпилирован")
            print("Скомпилируйте: make")
    except Exception as e:
        print(f"❌ Ошибка запуска простого C сканера: {e}")

def run_c_native_scanner():
    """Запуск нативного C сканера"""
    print("🚀 Запуск нативного C сканера...")
    try:
        if os.path.exists('fpv_scanner_native'):
            subprocess.run(['sudo', './fpv_scanner_native'])
        else:
            print("❌ Нативный C сканер не скомпилирован")
            print("Скомпилируйте: make fpv_scanner_native")
    except Exception as e:
        print(f"❌ Ошибка запуска нативного C сканера: {e}")

def run_headless_scanner():
    """Запуск сканера без GUI"""
    print("📊 Запуск сканера без GUI...")
    print("(Функция в разработке)")
    # Здесь можно добавить консольную версию сканера

def enable_spi():
    """Включение SPI"""
    print("⚡ Включение SPI на Raspberry Pi OS...")
    print("Выберите способ включения SPI:")
    print("1. Через raspi-config (рекомендуется)")
    print("2. Через командную строку")
    print("3. Ручное редактирование")
    print("4. Автоматический скрипт")
    
    choice = input("Выберите способ (1-4): ").strip()
    
    if choice == '1':
        print("🔧 Запуск raspi-config...")
        print("В меню выберите: 3 Interface Options → P4 SPI → Yes → Finish")
        subprocess.run(['sudo', 'raspi-config'])
    elif choice == '2':
        print("🔧 Включение SPI через командную строку...")
        subprocess.run(['sudo', 'raspi-config', 'nonint', 'do_spi', '0'])
        print("✅ SPI включен! Перезагрузите Raspberry Pi: sudo reboot")
    elif choice == '3':
        print("🔧 Ручное редактирование...")
        print("Откройте: sudo nano /boot/firmware/config.txt")
        print("Добавьте строку: dtparam=spi=on")
        print("Сохраните: Ctrl+X, Y, Enter")
        print("Перезагрузите: sudo reboot")
    elif choice == '4':
        try:
            subprocess.run(['chmod', '+x', 'fix_spi.sh'])
            subprocess.run(['./fix_spi.sh'])
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            print("Попробуйте способ 2 или 3")
    else:
        print("❌ Неверный выбор")

def show_settings():
    """Показать настройки"""
    print("\n🔧 Настройки системы:")
    print("-" * 30)
    
    # Проверка конфигурации
    config_file = "config/scanner_config.json"
    if os.path.exists(config_file):
        print(f"✅ Конфигурация: {config_file}")
    else:
        print("❌ Файл конфигурации не найден")
    
    # Проверка GPIO
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        print("✅ GPIO доступен")
        GPIO.cleanup()
    except:
        print("❌ GPIO недоступен")
    
    # Проверка SPI
    try:
        import spidev
        spi = spidev.SpiDev()
        print("✅ SPI доступен")
    except:
        print("❌ SPI недоступен")
    
    # Проверка видео
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Видео устройство доступно")
            cap.release()
        else:
            print("❌ Видео устройство недоступно")
    except:
        print("❌ OpenCV недоступен")

def main():
    """Главная функция"""
    print("🚁 Raspberry Pi 4 RX5808 FPV Scanner")
    print("Быстрый запуск для перехвата дронов на 5.8 ГГц")
    
    # Проверка требований
    if not check_requirements():
        print("\n❌ Система не готова. Запустите установку:")
        print("   ./install.sh")
        return
    
    while True:
        show_menu()
        
        try:
            choice = input("\nВыберите опцию (1-8): ").strip()
            
            if choice == '1':
                run_hardware_test()
            elif choice == '2':
                run_simple_scanner()
            elif choice == '3':
                run_c_simple_scanner()
            elif choice == '4':
                run_c_native_scanner()
            elif choice == '5':
                run_headless_scanner()
            elif choice == '6':
                enable_spi()
            elif choice == '7':
                show_settings()
            elif choice == '8':
                print("👋 До свидания!")
                break
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
                
        except KeyboardInterrupt:
            print("\n👋 Выход...")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
