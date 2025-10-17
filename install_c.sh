#!/bin/bash
# Установка зависимостей для C версии FPV Scanner

echo "🔧 Установка зависимостей для C версии FPV Scanner..."

# Обновление системы
echo "📦 Обновление системы..."
sudo apt update && sudo apt upgrade -y

# Установка компилятора и инструментов
echo "🔨 Установка компилятора и инструментов..."
sudo apt install -y gcc make build-essential

# Установка альтернативных библиотек GPIO
echo "⚡ Установка библиотек GPIO..."

# Установка pigpio (современная альтернатива)
sudo apt install -y pigpio python3-pigpio

# Установка RPi.GPIO для Python
sudo apt install -y python3-rpi.gpio

# Установка spidev для SPI
sudo apt install -y python3-spidev

# Проверка доступных библиотек
echo "🔍 Проверка библиотек GPIO..."
if python3 -c "import RPi.GPIO" 2>/dev/null; then
    echo "✅ RPi.GPIO доступен"
else
    echo "❌ RPi.GPIO не найден"
fi

if python3 -c "import spidev" 2>/dev/null; then
    echo "✅ spidev доступен"
else
    echo "❌ spidev не найден"
fi

# Включение SPI
echo "🔌 Включение SPI..."
if ! grep -q "dtparam=spi=on" /boot/firmware/config.txt; then
    echo "dtparam=spi=on" | sudo tee -a /boot/firmware/config.txt
    echo "✅ SPI включен в /boot/firmware/config.txt"
else
    echo "✅ SPI уже включен"
fi

# Добавление пользователя в группу spi
echo "👤 Настройка прав доступа..."
sudo usermod -a -G spi $USER

# Проверка SPI
echo "🔍 Проверка SPI..."
if ls /dev/spi* >/dev/null 2>&1; then
    echo "✅ SPI устройства обнаружены:"
    ls /dev/spi*
else
    echo "⚠️  SPI устройства не обнаружены"
    echo "   Перезагрузите Raspberry Pi: sudo reboot"
fi

# Компиляция сканера
echo "🔨 Компиляция FPV Scanner..."
if make; then
    echo "✅ Компиляция успешна"
else
    echo "❌ Ошибка компиляции"
    echo "Проверьте установку WiringPi"
    exit 1
fi

# Установка в систему
echo "📦 Установка в систему..."
sudo make install

echo ""
echo "🎉 Установка завершена!"
echo ""
echo "🚀 Запуск сканера:"
echo "   sudo fpv_scanner"
echo ""
echo "🔧 Или через Makefile:"
echo "   make run"
echo ""
echo "⚠️  ВАЖНО: Перезагрузите Raspberry Pi для применения изменений:"
echo "   sudo reboot"
