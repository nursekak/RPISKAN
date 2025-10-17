#!/bin/bash
# Исправление проблем с SPI на Raspberry Pi

echo "🔧 Исправление проблем с SPI..."

# Проверка, что мы на Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "❌ Это не Raspberry Pi!"
    exit 1
fi

echo "✅ Raspberry Pi обнаружен"

# 1. Включение SPI
echo "📝 Включение SPI..."
sudo raspi-config nonint do_spi 0

# 2. Добавление пользователя в группу spi
echo "👤 Добавление пользователя в группу spi..."
sudo usermod -a -G spi $USER

# 3. Проверка и создание udev правил
echo "⚙️  Настройка udev правил..."
sudo tee /etc/udev/rules.d/99-spi.rules > /dev/null << 'EOF'
# SPI устройства
SUBSYSTEM=="spidev", GROUP="spi", MODE="0664"
KERNEL=="spidev*", GROUP="spi", MODE="0664"
EOF

# 4. Перезагрузка udev
echo "🔄 Перезагрузка udev..."
sudo udevadm control --reload-rules
sudo udevadm trigger

# 5. Проверка прав на SPI устройства
echo "🔍 Проверка прав на SPI устройства..."
if [ -e /dev/spi0.0 ]; then
    echo "✅ SPI устройства найдены"
    ls -la /dev/spi*
    
    # Установка правильных прав
    sudo chmod 666 /dev/spi*
    sudo chown root:spi /dev/spi*
    
    echo "✅ Права на SPI устройства установлены"
else
    echo "❌ SPI устройства не найдены"
    echo "⚠️  Требуется перезагрузка: sudo reboot"
fi

# 6. Проверка групп пользователя
echo "👥 Проверка групп пользователя..."
groups $USER

# 7. Создание тестового скрипта
echo "🧪 Создание тестового скрипта..."
cat > test_spi.py << 'EOF'
#!/usr/bin/env python3
import spidev
import time

try:
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 1000000
    spi.mode = 0
    
    print("✅ SPI тест успешен!")
    print(f"SPI устройство: {spi.bus}, {spi.device}")
    
    # Простой тест
    test_data = [0x01, 0x02, 0x03]
    response = spi.xfer2(test_data)
    print(f"Отправлено: {test_data}")
    print(f"Получено: {response}")
    
    spi.close()
    
except Exception as e:
    print(f"❌ Ошибка SPI теста: {e}")
    print("Возможные решения:")
    print("1. sudo reboot")
    print("2. sudo usermod -a -G spi $USER")
    print("3. Выйдите и войдите снова")
EOF

chmod +x test_spi.py

echo ""
echo "🎯 Результат:"
echo "============="

# Запуск теста
echo "🧪 Запуск SPI теста..."
python3 test_spi.py

echo ""
echo "📋 Следующие шаги:"
echo "1. Если тест прошел успешно - SPI готов к работе"
echo "2. Если есть ошибки - выполните: sudo reboot"
echo "3. После перезагрузки запустите: python3 test_spi.py"
echo "4. Для запуска сканера: python3 quick_start.py"
