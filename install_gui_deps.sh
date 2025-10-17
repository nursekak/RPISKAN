#!/bin/bash
# Установка зависимостей для GUI FPV Scanner

echo "🔧 Установка зависимостей для GUI FPV Scanner..."

# Проверка, что мы на Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "❌ Это не Raspberry Pi!"
    exit 1
fi

echo "✅ Raspberry Pi обнаружен"

# Обновление пакетов
echo "📦 Обновление списка пакетов..."
sudo apt update

# Установка GTK3 и зависимостей
echo "🎨 Установка GTK3 и зависимостей..."
sudo apt install -y \
    libgtk-3-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libatk1.0-dev \
    libgdk-pixbuf2.0-dev \
    libglib2.0-dev \
    pkg-config

# Установка дополнительных библиотек
echo "📚 Установка дополнительных библиотек..."
sudo apt install -y \
    libpthread-stubs0-dev \
    build-essential \
    cmake

# Проверка установки GTK3
echo "🔍 Проверка установки GTK3..."
if pkg-config --exists gtk+-3.0; then
    echo "✅ GTK3 установлен успешно"
    echo "Версия GTK3: $(pkg-config --modversion gtk+-3.0)"
else
    echo "❌ GTK3 не найден"
    exit 1
fi

# Проверка компилятора
echo "🔍 Проверка компилятора..."
if command -v gcc &> /dev/null; then
    echo "✅ GCC найден: $(gcc --version | head -n1)"
else
    echo "❌ GCC не найден"
    exit 1
fi

# Проверка pkg-config
echo "🔍 Проверка pkg-config..."
if command -v pkg-config &> /dev/null; then
    echo "✅ pkg-config найден: $(pkg-config --version)"
else
    echo "❌ pkg-config не найден"
    exit 1
fi

echo ""
echo "🎉 Установка зависимостей завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Компиляция GUI сканера: make"
echo "2. Запуск GUI сканера: make run"
echo "3. Или напрямую: ./fpv_scanner_gui"
echo ""
echo "🔧 Если есть ошибки компиляции:"
echo "1. Проверьте GTK3: pkg-config --cflags gtk+-3.0"
echo "2. Проверьте библиотеки: pkg-config --libs gtk+-3.0"
echo "3. Переустановите GTK3: sudo apt reinstall libgtk-3-dev"
