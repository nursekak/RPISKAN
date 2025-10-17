# 🚁 FPV Scanner для Raspberry Pi 4 + RX5808

Простая система для перехвата FPV видеосигналов дронов на частоте 5.8 ГГц.

## 🚀 Быстрый старт

### **1. Установка:**
```bash
chmod +x install.sh
./install.sh
```

### **2. Включите SPI на Raspberry Pi:**
```bash
# Быстрое включение SPI
chmod +x enable_spi_simple.sh
./enable_spi_simple.sh

# Или через raspi-config
sudo raspi-config
# Выберите: 3 Interface Options → P4 SPI → Yes → Finish

# Перезагрузите Raspberry Pi
sudo reboot
```

### **3. Подключение RX5808:**
```
RX5808 Pin    →    Raspberry Pi 4    →    Функция
─────────────────────────────────────────────────
GND           →    Pin 6 (GND)       →    Земля
+5V           →    Pin 2 (5V)        →    Питание
RSSI          →    Pin 26 (GPIO 7)   →    Сила сигнала
VIDEO         →    USB Video DVR     →    Видео
A6.5M         →    Pin 19 (GPIO 10)  →    SPI MOSI
CH1           →    Pin 23 (GPIO 11)  →    SPI SCK
CH2           →    Pin 24 (GPIO 8)   →    SPI CS
ANT           →    Антенна 5.8 ГГц  →    Антенна
```

### **4. Запуск:**
```bash
python3 quick_start.py
# Выберите опцию 2 (Простой сканер)
```

## 📊 FPV каналы 5.8 ГГц

```
Канал    Частота    Тип дрона
─────────────────────────────
A        5865 МГц   Racing
B        5845 МГц   Freestyle  
C        5825 МГц   Long Range
D        5805 МГц   Cinematic
E        5785 МГц   Acro
F        5765 МГц   Beginner
G        5745 МГц   Pro
H        5725 МГц   Competition
```

## 🎯 Возможности

- ✅ Сканирование 8 FPV каналов в реальном времени
- ✅ Автоматическое обнаружение сигналов дронов
- ✅ Захват видео при обнаружении сильных сигналов
- ✅ Простой интерфейс с визуализацией спектра
- ✅ Автоматическое определение USB Video DVR

## 📚 Документация

- **README_RU.md** - Полная документация на русском
- **docs/RPI_WIRING.md** - Подробная схема подключения
- **docs/QUICK_WIRING.md** - Быстрая схема подключения

## 🔧 Команды

```bash
# Меню выбора
python3 quick_start.py

# Простой сканер
python3 src/simple_scanner.py

# Тест оборудования
python3 examples/test_hardware.py
```

**Готово к перехвату дронов! 🚁📡**
