/*
 * Минимальный FPV Scanner для Raspberry Pi 4 + RX5808
 * Максимально простая версия без проблемных функций
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <signal.h>

// FPV каналы 5.8-6.0 ГГц (расширенный диапазон)
typedef struct {
    char channel;
    int frequency;
} fpv_channel_t;

static const fpv_channel_t channels[] = {
    // Стандартные FPV каналы 5.8 ГГц
    {'A', 5865}, {'B', 5845}, {'C', 5825}, {'D', 5805},
    {'E', 5785}, {'F', 5765}, {'G', 5745}, {'H', 5725},
    // Расширенные каналы до 6.0 ГГц
    {'I', 5905}, {'J', 5925}, {'K', 5945}, {'L', 5965},
    {'M', 5985}, {'N', 6000}, {'O', 6020}, {'P', 6040}
};

#define NUM_CHANNELS (sizeof(channels) / sizeof(channels[0]))

// Структура для обнаруженного сигнала
typedef struct {
    char channel;
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

// Симуляция чтения RSSI
int read_rssi_simulated(void) {
    static int counter = 0;
    counter++;
    
    // Симулируем обнаружение сигнала на канале A каждые 10 циклов
    if (counter % 10 == 0) {
        return 80 + (rand() % 40);  // RSSI 80-120
    }
    
    return 20 + (rand() % 30);  // RSSI 20-50 (слабый сигнал)
}

// Установка частоты (симуляция)
int set_frequency(int frequency_mhz) {
    printf("📡 Установка частоты: %d МГц\n", frequency_mhz);
    simple_delay(100);  // 100ms settling time
    return 0;
}

// Сканирование каналов
void scan_channels(void) {
    printf("🔍 Начинаем сканирование FPV каналов...\n");
    printf("Нажмите Ctrl+C для остановки\n\n");
    
    while (running) {
        printf("\r📡 Сканирование... ");
        fflush(stdout);
        
        for (size_t i = 0; i < NUM_CHANNELS && running; i++) {
            // Установка частоты
            set_frequency(channels[i].frequency);
            
            // Чтение RSSI (симуляция)
            int rssi = read_rssi_simulated();
            
            // Обновление обнаруженных сигналов
            if (rssi > 50) {  // Порог обнаружения
                detected_signals[i].channel = channels[i].channel;
                detected_signals[i].frequency = channels[i].frequency;
                detected_signals[i].rssi = rssi;
                detected_signals[i].strength = (rssi * 100) / 255;
                detected_signals[i].timestamp = time(NULL);
                detected_signals[i].active = 1;
                
                printf("\n🚁 Сигнал обнаружен на канале %c: %d МГц, RSSI: %d, Сила: %d%%\n",
                       channels[i].channel, channels[i].frequency, rssi, detected_signals[i].strength);
            } else {
                detected_signals[i].active = 0;
            }
        }
        
        simple_delay(500);  // 500ms интервал сканирования
    }
}

// Отображение статистики
void show_statistics(void) {
    int active_signals = 0;
    
    printf("\n📊 Статистика обнаруженных сигналов:\n");
    printf("=====================================\n");
    
    for (size_t i = 0; i < NUM_CHANNELS; i++) {
        if (detected_signals[i].active) {
            active_signals++;
            printf("Канал %c: %d МГц, RSSI: %d, Сила: %d%%, Время: %s",
                   detected_signals[i].channel,
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
    printf("🚁 Минимальный FPV Scanner для Raspberry Pi 4 + RX5808\n");
    printf("====================================================\n");
    printf("Перехват FPV сигналов дронов на частоте 5.8-6.0 ГГц\n");
    printf("Расширенный диапазон до 6000 МГц\n");
    printf("Максимально простая версия для тестирования\n\n");
    
    // Установка обработчиков сигналов
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // Инициализация генератора случайных чисел
    srand((unsigned int)time(NULL));
    
    // Инициализация массива сигналов
    memset(detected_signals, 0, sizeof(detected_signals));
    
    printf("✅ Система инициализирована\n");
    printf("📡 SPI устройства: /dev/spi0.0 (симуляция)\n");
    printf("🎯 Начинаем сканирование...\n\n");
    
    // Запуск сканирования
    scan_channels();
    
    // Отображение статистики
    show_statistics();
    
    printf("👋 Сканер завершен\n");
    return 0;
}
