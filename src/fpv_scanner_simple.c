/*
 * Простой FPV Scanner для Raspberry Pi 4 + RX5808
 * Минимальная версия без сложных системных вызовов
 */

#define _POSIX_C_SOURCE 200809L
#define _DEFAULT_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <signal.h>
#include <fcntl.h>
#include <errno.h>
#include <stdint.h>

// Конфигурация
#define SPI_DEVICE "/dev/spi0.0"
#define SPI_SPEED 2000000

// FPV каналы 5.8-6.0 ГГц (шаг 1 МГц)
typedef struct {
    char channel;
    int frequency;
} fpv_channel_t;

// Генерация каналов с шагом 1 МГц от 5725 до 6000 МГц
#define START_FREQ 5725
#define END_FREQ 6000
#define NUM_CHANNELS (END_FREQ - START_FREQ + 1)

static fpv_channel_t channels[NUM_CHANNELS];

// Инициализация каналов
void init_channels(void) {
    for (int i = 0; i < NUM_CHANNELS; i++) {
        channels[i].channel = 'A' + (i % 26);  // A-Z, затем повтор
        channels[i].frequency = START_FREQ + i;
    }
}

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
static int spi_fd = -1;

// Обработчик сигналов
void signal_handler(int sig __attribute__((unused))) {
    printf("\n🛑 Получен сигнал завершения, останавливаем сканер...\n");
    running = 0;
}

// Инициализация оборудования
int init_hardware() {
    printf("🔧 Инициализация оборудования...\n");
    
    // Проверка SPI устройства
    spi_fd = open(SPI_DEVICE, O_RDWR);
    if (spi_fd < 0) {
        printf("❌ Ошибка открытия SPI устройства %s: %s\n", SPI_DEVICE, strerror(errno));
        printf("Проверьте, что SPI включен: sudo raspi-config\n");
        return -1;
    }
    
    printf("✅ Оборудование инициализировано успешно\n");
    return 0;
}

// Симуляция чтения RSSI (для тестирования)
int read_rssi_simulated() {
    // Генерируем случайные значения RSSI для демонстрации
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
    // В реальной версии здесь будет код для настройки RX5808
    printf("📡 Установка частоты: %d МГц\n", frequency_mhz);
    // Задержка 100ms
    struct timespec ts = {0, 100000000};  // 100ms в наносекундах
    nanosleep(&ts, NULL);
    return 0;
}

// Сканирование каналов
void scan_channels() {
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
        
        // Задержка 500ms
        struct timespec ts = {0, 500000000};  // 500ms в наносекундах
        nanosleep(&ts, NULL);
    }
}

// Отображение статистики
void show_statistics() {
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

// Очистка ресурсов
void cleanup() {
    printf("\n🧹 Очистка ресурсов...\n");
    
    if (spi_fd != -1) {
        close(spi_fd);
    }
    
    printf("✅ Очистка завершена\n");
}

// Главная функция
int main(int argc __attribute__((unused)), char *argv[] __attribute__((unused))) {
    printf("🚁 Простой FPV Scanner для Raspberry Pi 4 + RX5808\n");
    printf("==================================================\n");
    printf("Перехват FPV сигналов дронов на частоте 5.8-6.0 ГГц\n");
    printf("Сканирование с шагом 1 МГц (5725-6000 МГц)\n");
    printf("Упрощенная версия для тестирования\n\n");
    
    // Установка обработчиков сигналов
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // Инициализация генератора случайных чисел
    srand(time(NULL));
    
    // Инициализация каналов
    init_channels();
    
    // Инициализация оборудования
    if (init_hardware() != 0) {
        printf("❌ Не удалось инициализировать оборудование\n");
        printf("Проверьте подключение RX5808 и настройки SPI\n");
        return 1;
    }
    
    // Инициализация массива сигналов
    memset(detected_signals, 0, sizeof(detected_signals));
    
    // Запуск сканирования
    scan_channels();
    
    // Отображение статистики
    show_statistics();
    
    // Очистка ресурсов
    cleanup();
    
    printf("👋 Сканер завершен\n");
    return 0;
}
