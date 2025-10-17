#!/bin/bash
# Скрипт установки для Raspberry Pi 4 RX5808 FPV Scanner
# Автоматическая установка всех зависимостей

echo "🚁 Установка Raspberry Pi 4 RX5808 FPV Scanner"
echo "=============================================="

# Проверка, что мы на Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "⚠️  Внимание: Этот скрипт предназначен для Raspberry Pi"
    read -p "Продолжить установку? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Обновление системы
echo "📦 Обновление системы..."
sudo apt update && sudo apt upgrade -y

# Установка основных пакетов
echo "🔧 Установка основных пакетов..."
sudo apt install -y python3-pip python3-dev python3-venv
sudo apt install -y python3-opencv python3-pil python3-pil.imagetk
sudo apt install -y python3-rpi.gpio python3-spidev
sudo apt install -y git vim nano

# Установка дополнительных Python пакетов
echo "🐍 Установка Python пакетов..."
pip3 install numpy pillow

# Включение SPI
echo "⚡ Включение SPI..."
if ! grep -q "dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
    echo "✅ SPI включен в /boot/config.txt"
else
    echo "✅ SPI уже включен"
fi

# Включение I2C (для будущих расширений)
if ! grep -q "dtparam=i2c_arm=on" /boot/config.txt; then
    echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
    echo "✅ I2C включен в /boot/config.txt"
fi

# Создание директории для логов
echo "📁 Создание директорий..."
sudo mkdir -p /var/log
sudo touch /var/log/rpi_scanner.log
sudo chmod 666 /var/log/rpi_scanner.log

# Установка прав на GPIO
echo "🔐 Настройка прав доступа..."
sudo usermod -a -G gpio $USER
sudo usermod -a -G spi $USER

# Проверка USB Video DVR
echo "📹 Проверка USB Video DVR..."
if ls /dev/video* >/dev/null 2>&1; then
    echo "✅ USB Video DVR обнаружен:"
    ls /dev/video*
else
    echo "⚠️  USB Video DVR не обнаружен"
    echo "   Подключите USB Video DVR и перезапустите скрипт"
fi

# Проверка SPI
echo "🔌 Проверка SPI..."
if ls /dev/spi* >/dev/null 2>&1; then
    echo "✅ SPI устройства обнаружены:"
    ls /dev/spi*
else
    echo "⚠️  SPI устройства не обнаружены"
    echo "   Перезагрузите Raspberry Pi после установки"
fi

# Создание ярлыка для запуска
echo "🚀 Создание ярлыка запуска..."
cat > ~/Desktop/FPV_Scanner.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=FPV Scanner
Comment=Raspberry Pi RX5808 FPV Scanner
Exec=python3 $(pwd)/src/simple_scanner.py
Icon=applications-multimedia
Terminal=true
Categories=AudioVideo;
EOF

chmod +x ~/Desktop/FPV_Scanner.desktop

# Создание скрипта быстрого запуска
echo "⚡ Создание скрипта быстрого запуска..."
cat > start_scanner.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🚁 Запуск FPV Scanner..."
python3 quick_start.py
EOF

chmod +x start_scanner.sh

# Тест оборудования
echo "🧪 Тестирование оборудования..."
python3 examples/test_hardware.py

echo ""
echo "🎉 Установка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Подключите RX5808 согласно схеме в docs/RPI_WIRING.md"
echo "2. Подключите USB Video DVR"
echo "3. Подключите антенну 5.8 ГГц"
echo "4. Перезагрузите Raspberry Pi: sudo reboot"
echo "5. Запустите сканер: ./start_scanner.sh"
echo ""
echo "🔧 Полезные команды:"
echo "   Тест оборудования: python3 examples/test_hardware.py"
echo "   Меню выбора: python3 quick_start.py"
echo "   Простой сканер: python3 src/simple_scanner.py"
echo ""
echo "📚 Документация:"
echo "   README_RU.md - основная документация"
echo "   docs/RPI_WIRING.md - схема подключения"
echo "   docs/QUICK_WIRING.md - быстрая схема"
echo ""
echo "🎯 Готово к перехвату FPV дронов!"
