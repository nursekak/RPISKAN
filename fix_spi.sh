#!/bin/bash
# Простой скрипт для включения SPI на Raspberry Pi OS

echo "🔧 Включение SPI на Raspberry Pi OS..."

# Проверка, что мы на Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "❌ Это не Raspberry Pi!"
    exit 1
fi

echo "✅ Raspberry Pi обнаружен"

# Проверка текущего состояния
echo "🔍 Проверка текущего состояния SPI..."

if ls /dev/spi* >/dev/null 2>&1; then
    echo "✅ SPI уже включен и работает!"
    ls /dev/spi*
    exit 0
fi

echo "❌ SPI не включен, включаем..."

# Включение SPI через raspi-config
echo "📝 Включение SPI через raspi-config..."
sudo raspi-config nonint do_spi 0

# Альтернативный способ - прямое редактирование
echo "📝 Добавление dtparam=spi=on в /boot/firmware/config.txt..."
if ! grep -q "dtparam=spi=on" /boot/firmware/config.txt; then
    echo "dtparam=spi=on" | sudo tee -a /boot/firmware/config.txt
    echo "✅ SPI добавлен в конфигурацию"
else
    echo "✅ SPI уже в конфигурации"
fi

# Добавление пользователя в группу spi
echo "👤 Добавление пользователя в группу spi..."
sudo usermod -a -G spi $USER

echo ""
echo "🎯 SPI настроен! Теперь нужно:"
echo "1. Перезагрузить Raspberry Pi: sudo reboot"
echo "2. После перезагрузки запустить: python3 quick_start.py"
echo ""
echo "Или перезагрузите сейчас:"
read -p "Перезагрузить сейчас? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Перезагрузка..."
    sudo reboot
fi
