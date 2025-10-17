#!/bin/bash
# Скрипт для проверки конфигурации Raspberry Pi

echo "🔍 Проверка конфигурации Raspberry Pi..."

# Проверка версии Raspberry Pi OS
echo "📋 Информация о системе:"
if [ -f /etc/os-release ]; then
    grep "PRETTY_NAME" /etc/os-release
fi

# Проверка существования конфигурационных файлов
echo ""
echo "📁 Проверка конфигурационных файлов:"

if [ -f /boot/firmware/config.txt ]; then
    echo "✅ Найден: /boot/firmware/config.txt (новое расположение)"
    CONFIG_FILE="/boot/firmware/config.txt"
elif [ -f /boot/config.txt ]; then
    echo "✅ Найден: /boot/config.txt (старое расположение)"
    CONFIG_FILE="/boot/config.txt"
else
    echo "❌ Конфигурационный файл не найден!"
    exit 1
fi

# Проверка SPI настроек
echo ""
echo "🔌 Проверка SPI настроек:"

if grep -q "dtparam=spi=on" "$CONFIG_FILE"; then
    echo "✅ SPI включен в $CONFIG_FILE"
else
    echo "❌ SPI не включен в $CONFIG_FILE"
    echo "🔧 Для включения SPI:"
    echo "   echo 'dtparam=spi=on' | sudo tee -a $CONFIG_FILE"
    echo "   sudo reboot"
fi

# Проверка SPI устройств
echo ""
echo "🔍 Проверка SPI устройств:"
if ls /dev/spi* >/dev/null 2>&1; then
    echo "✅ SPI устройства обнаружены:"
    ls /dev/spi*
else
    echo "❌ SPI устройства не обнаружены"
    echo "   Возможно, нужно перезагрузить Raspberry Pi"
fi

# Проверка WiringPi
echo ""
echo "⚡ Проверка WiringPi:"
if command -v gpio >/dev/null 2>&1; then
    echo "✅ WiringPi установлен"
    gpio -v
else
    echo "❌ WiringPi не установлен"
    echo "🔧 Установите: sudo apt install wiringpi"
fi

# Проверка прав доступа
echo ""
echo "👤 Проверка прав доступа:"
if groups $USER | grep -q spi; then
    echo "✅ Пользователь $USER в группе spi"
else
    echo "❌ Пользователь $USER не в группе spi"
    echo "🔧 Добавьте в группу: sudo usermod -a -G spi $USER"
fi

# Рекомендации
echo ""
echo "💡 Рекомендации:"
if [ ! -f /dev/spi0.0 ]; then
    echo "1. Включите SPI: sudo raspi-config"
    echo "2. Или добавьте в $CONFIG_FILE: dtparam=spi=on"
    echo "3. Перезагрузите: sudo reboot"
fi

if ! command -v gpio >/dev/null 2>&1; then
    echo "4. Установите WiringPi: sudo apt install wiringpi"
fi

if ! groups $USER | grep -q spi; then
    echo "5. Добавьте в группу spi: sudo usermod -a -G spi $USER"
    echo "6. Выйдите и войдите снова"
fi

echo ""
echo "🎯 После исправления запустите:"
echo "   python3 quick_start.py"
