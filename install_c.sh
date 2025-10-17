#!/bin/bash
# Установка зависимостей для C версии FPV Scanner

echo "🔧 Установка зависимостей для C версии FPV Scanner..."

# Обновление системы
echo "📦 Обновление системы..."
sudo apt update && sudo apt upgrade -y

# Установка компилятора и инструментов
echo "🔨 Установка компилятора и инструментов..."
sudo apt install -y gcc make build-essential

# Установка WiringPi
echo "⚡ Установка WiringPi..."
sudo apt install -y wiringpi

# Проверка WiringPi
echo "🔍 Проверка WiringPi..."
if gpio -v >/dev/null 2>&1; then
    echo "✅ WiringPi установлен"
    gpio -v
else
    echo "❌ WiringPi не найден, устанавливаем вручную..."
    
    # Установка из исходников
    cd /tmp
    git clone https://github.com/WiringPi/WiringPi.git
    cd WiringPi
    ./build
    cd -
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
