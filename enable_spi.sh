#!/bin/bash
# Скрипт для включения SPI на Raspberry Pi

echo "🔧 Включение SPI на Raspberry Pi..."

# Проверка, что мы на Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "⚠️  Этот скрипт предназначен для Raspberry Pi"
    exit 1
fi

# Проверка текущего состояния SPI
if grep -q "dtparam=spi=on" /boot/config.txt; then
    echo "✅ SPI уже включен в /boot/config.txt"
else
    echo "📝 Добавление dtparam=spi=on в /boot/config.txt..."
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
    echo "✅ SPI включен в конфигурации"
fi

# Проверка SPI устройств
echo "🔍 Проверка SPI устройств..."
if ls /dev/spi* >/dev/null 2>&1; then
    echo "✅ SPI устройства обнаружены:"
    ls /dev/spi*
else
    echo "⚠️  SPI устройства не обнаружены"
    echo "   Перезагрузите Raspberry Pi: sudo reboot"
fi

# Проверка прав доступа
echo "🔐 Проверка прав доступа..."
if groups $USER | grep -q spi; then
    echo "✅ Пользователь $USER в группе spi"
else
    echo "📝 Добавление пользователя в группу spi..."
    sudo usermod -a -G spi $USER
    echo "✅ Пользователь добавлен в группу spi"
    echo "⚠️  Выйдите и войдите снова для применения изменений"
fi

echo ""
echo "🎯 Готово! Теперь можно запускать сканер:"
echo "   python3 quick_start.py"
echo ""
echo "Если SPI все еще не работает, перезагрузите Pi:"
echo "   sudo reboot"
