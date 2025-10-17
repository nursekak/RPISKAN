#!/bin/bash
# Простое включение SPI для Raspberry Pi OS

echo "🔧 Включение SPI на Raspberry Pi OS..."

# Включение SPI через raspi-config
sudo raspi-config nonint do_spi 0

# Альтернативный способ - прямое редактирование
if ! grep -q "dtparam=spi=on" /boot/firmware/config.txt; then
    echo "dtparam=spi=on" | sudo tee -a /boot/firmware/config.txt
fi

# Добавление пользователя в группу spi
sudo usermod -a -G spi $USER

echo "✅ SPI включен!"
echo "🔄 Перезагрузите Raspberry Pi:"
echo "sudo reboot"
