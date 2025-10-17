/*
 * FPV Scanner с шагом 1 МГц для Raspberry Pi 4 + RX5808
 * Оптимизированная версия для точного сканирования
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <signal.h>

// Конфигурация сканирования
#define START_FREQ 5725    // Начальная частота (МГц)
#define END_FREQ 6000      // Конечная частота (МГц)
#define NUM_CHANNELS (END_FREQ - START_FREQ + 1)

// Структура для обнаруженного сигнала
typedef struct {
    int frequency;
    int rssi;
    int strength;
    time_t timestamp;
    int active;
} signal_info_t;

// Глобальные переменные
static int running = 1;
static signal_info_t detected_signals[NUM_CHANNELS];

// Обработчик сигналов
void signal_handler(int sig __attribute__((unused))) {
    printf("\n🛑 Получен сигнал завершения, останавливаем сканер...\n");
    running = 0;
}

// Простая задержка
void simple_delay(int milliseconds) {
    clock_t start = clock();
    while ((clock() - start) * 1000 / CLOCKS_PER_SEC < milliseconds) {
        // Простое ожидание
    }
}

// Симуляция чтения RSSI с более реалистичными данными
int read_rssi_simulated(int frequency) {
    static int counter = 0;
    counter++;
    
    // Симулируем пики на определенных частотах
    int base_rssi = 20 + (rand() % 30);  // Базовый шум
    
    // Пики на популярных FPV частотах
    if (frequency == 5865 || frequency == 5845 || frequency == 5825) {
        if (counter % 15 == 0) {
            return 80 + (rand() % 40);  // Сильный сигнал
        }
    }
    
    // Случайные пики на других частотах
    if (counter % 50 == 0) {
        return 60 + (rand() % 30);  // Средний сигнал
    }
    
    return base_rssi;
}

// Установка частоты (симуляция)
int set_frequency(int frequency_mhz) {
    // В реальной версии здесь будет код для настройки RX5808
    simple_delay(10);  // 10ms settling time для быстрого сканирования
    return 0;
}

// Сканирование каналов
void scan_channels(void) {
    printf("🔍 Начинаем сканирование с шагом 1 МГц...\n");
    printf("Диапазон: %d-%d МГц (%d каналов)\n", START_FREQ, END_FREQ, NUM_CHANNELS);
    printf("Нажмите Ctrl+C для остановки\n\n");
    
    int scan_count = 0;
    
    while (running) {
        printf("\r📡 Сканирование... Проход %d", ++scan_count);
        fflush(stdout);
        
        for (int freq = START_FREQ; freq <= END_FREQ && running; freq++) {
            // Установка частоты
            set_frequency(freq);
            
            // Чтение RSSI (симуляция)
            int rssi = read_rssi_simulated(freq);
            
            // Обновление обнаруженных сигналов
            int channel_index = freq - START_FREQ;
            if (rssi > 50) {  // Порог обнаружения
                detected_signals[channel_index].frequency = freq;
                detected_signals[channel_index].rssi = rssi;
                detected_signals[channel_index].strength = (rssi * 100) / 255;
                detected_signals[channel_index].timestamp = time(NULL);
                detected_signals[channel_index].active = 1;
                
                printf("\n🚁 Сигнал: %d МГц, RSSI: %d, Сила: %d%%\n",
                       freq, rssi, detected_signals[channel_index].strength);
            } else {
                detected_signals[channel_index].active = 0;
            }
        }
        
        simple_delay(100);  // 100ms интервал между проходами
    }
}

// Отображение статистики
void show_statistics(void) {
    int active_signals = 0;
    
    printf("\n📊 Статистика обнаруженных сигналов:\n");
    printf("=====================================\n");
    
    for (int i = 0; i < NUM_CHANNELS; i++) {
        if (detected_signals[i].active) {
            active_signals++;
            printf("Частота %d МГц: RSSI %d, Сила %d%%, Время %s",
                   detected_signals[i].frequency,
                   detected_signals[i].rssi,
                   detected_signals[i].strength,
                   ctime(&detected_signals[i].timestamp));
        }
    }
    
    if (active_signals == 0) {
        printf("❌ Активных сигналов не обнаружено\n");
    } else {
        printf("✅ Обнаружено активных сигналов: %d\n", active_signals);
    }
}

// Главная функция
int main(void) {
    printf("🚁 FPV Scanner с шагом 1 МГц для Raspberry Pi 4 + RX5808\n");
    printf("=======================================================\n");
    printf("Точное сканирование FPV сигналов с шагом 1 МГц\n");
    printf("Диапазон: %d-%d МГц (%d каналов)\n", START_FREQ, END_FREQ, NUM_CHANNELS);
    printf("Оптимизированная версия для максимальной точности\n\n");
    
    // Установка обработчиков сигналов
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // Инициализация генератора случайных чисел
    srand((unsigned int)time(NULL));
    
    // Инициализация массива сигналов
    memset(detected_signals, 0, sizeof(detected_signals));
    
    printf("✅ Система инициализирована\n");
    printf("📡 SPI устройства: /dev/spi0.0 (симуляция)\n");
    printf("📊 Каналов для сканирования: %d\n", NUM_CHANNELS);
    printf("🎯 Начинаем сканирование...\n\n");
    
    // Запуск сканирования
    scan_channels();
    
    // Отображение статистики
    show_statistics();
    
    printf("👋 Сканер завершен\n");
    return 0;
}
