/*
 * Продвинутый FPV Scanner для Raspberry Pi 4 + RX5808
 * Высокопроизводительный перехват FPV сигналов с детекцией и анализом
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <signal.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>
#include <wiringPi.h>
#include <wiringPiSPI.h>
#include <pthread.h>
#include <math.h>

// Конфигурация
#define CS_PIN 8
#define RSSI_PIN 7
#define SPI_CHANNEL 0
#define SPI_SPEED 2000000
#define MAX_SIGNALS 32
#define SCAN_INTERVAL 100000  // 100ms в микросекундах
#define SETTLING_TIME 100000  // 100ms settling time

// FPV каналы 5.8-6.0 ГГц (расширенный диапазон)
typedef struct {
    char channel;
    int frequency;
    int rssi_threshold;
} fpv_channel_t;

static const fpv_channel_t channels[] = {
    // Стандартные FPV каналы 5.8 ГГц
    {'A', 5865, 50}, {'B', 5845, 50}, {'C', 5825, 50}, {'D', 5805, 50},
    {'E', 5785, 50}, {'F', 5765, 50}, {'G', 5745, 50}, {'H', 5725, 50},
    // Расширенные каналы до 6.0 ГГц
    {'I', 5905, 50}, {'J', 5925, 50}, {'K', 5945, 50}, {'L', 5965, 50},
    {'M', 5985, 50}, {'N', 6000, 50}, {'O', 6020, 50}, {'P', 6040, 50}
};

#define NUM_CHANNELS (sizeof(channels) / sizeof(channels[0]))

// Структура сигнала
typedef struct {
    char channel;
    int frequency;
    int rssi;
    int strength;
    time_t timestamp;
    int active;
    int duration;
    int peak_rssi;
    int samples;
} signal_info_t;

// Глобальные переменные
static int running = 1;
static signal_info_t signals[MAX_SIGNALS];
static int signal_count = 0;
static int spi_fd = -1;
static pthread_mutex_t signal_mutex = PTHREAD_MUTEX_INITIALIZER;
static int verbose_mode = 0;
static int continuous_mode = 0;

// Обработчик сигналов
void signal_handler(int sig) {
    printf("\n🛑 Получен сигнал завершения...\n");
    running = 0;
}

// Инициализация оборудования
int init_hardware() {
    printf("🔧 Инициализация оборудования...\n");
    
    if (wiringPiSetupGpio() == -1) {
        printf("❌ Ошибка инициализации WiringPi\n");
        return -1;
    }
    
    pinMode(CS_PIN, OUTPUT);
    digitalWrite(CS_PIN, HIGH);
    pinMode(RSSI_PIN, INPUT);
    
    spi_fd = wiringPiSPISetup(SPI_CHANNEL, SPI_SPEED);
    if (spi_fd == -1) {
        printf("❌ Ошибка инициализации SPI\n");
        return -1;
    }
    
    printf("✅ Оборудование инициализировано\n");
    return 0;
}

// Запись в RX5808
int rx5808_write(int address, int data) {
    unsigned char command = (address << 3) | data;
    unsigned char tx_buffer[1] = {command};
    
    digitalWrite(CS_PIN, LOW);
    wiringPiSPIDataRW(SPI_CHANNEL, tx_buffer, 1);
    digitalWrite(CS_PIN, HIGH);
    
    return 0;
}

// Установка частоты
int set_frequency(int frequency_mhz) {
    int freq_reg = (frequency_mhz - 479) / 2;
    
    rx5808_write(0x01, freq_reg & 0xFF);
    rx5808_write(0x02, (freq_reg >> 8) & 0xFF);
    rx5808_write(0x00, 0x01);
    
    return 0;
}

// Чтение RSSI с усреднением
int read_rssi_averaged(int samples) {
    int total = 0;
    unsigned char tx_buffer[1] = {0x08};
    
    for (int i = 0; i < samples; i++) {
        digitalWrite(CS_PIN, LOW);
        wiringPiSPIDataRW(SPI_CHANNEL, tx_buffer, 1);
        digitalWrite(CS_PIN, HIGH);
        total += tx_buffer[0];
        usleep(1000);  // 1ms между измерениями
    }
    
    return total / samples;
}

// Поиск сигнала по каналу
signal_info_t* find_signal_by_channel(char channel) {
    for (int i = 0; i < signal_count; i++) {
        if (signals[i].channel == channel && signals[i].active) {
            return &signals[i];
        }
    }
    return NULL;
}

// Добавление нового сигнала
void add_signal(char channel, int frequency, int rssi) {
    pthread_mutex_lock(&signal_mutex);
    
    signal_info_t* existing = find_signal_by_channel(channel);
    if (existing) {
        // Обновление существующего сигнала
        existing->rssi = rssi;
        existing->strength = (rssi * 100) / 255;
        existing->timestamp = time(NULL);
        existing->duration++;
        existing->samples++;
        if (rssi > existing->peak_rssi) {
            existing->peak_rssi = rssi;
        }
    } else if (signal_count < MAX_SIGNALS) {
        // Добавление нового сигнала
        signals[signal_count].channel = channel;
        signals[signal_count].frequency = frequency;
        signals[signal_count].rssi = rssi;
        signals[signal_count].strength = (rssi * 100) / 255;
        signals[signal_count].timestamp = time(NULL);
        signals[signal_count].active = 1;
        signals[signal_count].duration = 1;
        signals[signal_count].peak_rssi = rssi;
        signals[signal_count].samples = 1;
        signal_count++;
        
        if (verbose_mode) {
            printf("🚁 НОВЫЙ СИГНАЛ: Канал %c, %d МГц, RSSI: %d, Сила: %d%%\n",
                   channel, frequency, rssi, signals[signal_count-1].strength);
        }
    }
    
    pthread_mutex_unlock(&signal_mutex);
}

// Удаление неактивных сигналов
void cleanup_inactive_signals() {
    pthread_mutex_lock(&signal_mutex);
    
    time_t current_time = time(NULL);
    for (int i = 0; i < signal_count; i++) {
        if (signals[i].active && (current_time - signals[i].timestamp) > 10) {
            signals[i].active = 0;
            if (verbose_mode) {
                printf("⏰ Сигнал на канале %c стал неактивным\n", signals[i].channel);
            }
        }
    }
    
    pthread_mutex_unlock(&signal_mutex);
}

// Сканирование одного канала
void scan_channel(int channel_index) {
    const fpv_channel_t* ch = &channels[channel_index];
    
    set_frequency(ch->frequency);
    usleep(SETTLING_TIME);
    
    int rssi = read_rssi_averaged(3);  // 3 измерения для усреднения
    
    if (rssi > ch->rssi_threshold) {
        add_signal(ch->channel, ch->frequency, rssi);
    }
}

// Основной цикл сканирования
void* scan_loop(void* arg) {
    printf("🔍 Начинаем сканирование...\n");
    
    while (running) {
        for (int i = 0; i < NUM_CHANNELS && running; i++) {
            scan_channel(i);
            usleep(SCAN_INTERVAL / NUM_CHANNELS);
        }
        
        cleanup_inactive_signals();
        usleep(SCAN_INTERVAL);
    }
    
    return NULL;
}

// Отображение активных сигналов
void display_signals() {
    pthread_mutex_lock(&signal_mutex);
    
    printf("\r📡 Активных сигналов: %d", signal_count);
    fflush(stdout);
    
    if (verbose_mode) {
        printf("\n");
        for (int i = 0; i < signal_count; i++) {
            if (signals[i].active) {
                printf("  Канал %c: %d МГц, RSSI: %d, Сила: %d%%, Длительность: %ds\n",
                       signals[i].channel, signals[i].frequency, signals[i].rssi,
                       signals[i].strength, signals[i].duration);
            }
        }
    }
    
    pthread_mutex_unlock(&signal_mutex);
}

// Статистика
void show_statistics() {
    pthread_mutex_lock(&signal_mutex);
    
    printf("\n\n📊 Статистика обнаруженных сигналов:\n");
    printf("=====================================\n");
    
    int active_count = 0;
    int total_samples = 0;
    int max_rssi = 0;
    
    for (int i = 0; i < signal_count; i++) {
        if (signals[i].active) {
            active_count++;
            total_samples += signals[i].samples;
            if (signals[i].peak_rssi > max_rssi) {
                max_rssi = signals[i].peak_rssi;
            }
        }
    }
    
    if (active_count > 0) {
        printf("✅ Активных сигналов: %d\n", active_count);
        printf("📈 Всего измерений: %d\n", total_samples);
        printf("🔥 Максимальный RSSI: %d\n", max_rssi);
        
        printf("\nДетали сигналов:\n");
        for (int i = 0; i < signal_count; i++) {
            if (signals[i].active) {
                printf("  %c: %d МГц, RSSI: %d, Пик: %d, Образцов: %d\n",
                       signals[i].channel, signals[i].frequency, signals[i].rssi,
                       signals[i].peak_rssi, signals[i].samples);
            }
        }
    } else {
        printf("❌ Активных сигналов не обнаружено\n");
    }
    
    pthread_mutex_unlock(&signal_mutex);
}

// Очистка ресурсов
void cleanup() {
    printf("\n🧹 Очистка ресурсов...\n");
    
    if (spi_fd != -1) {
        close(spi_fd);
    }
    
    digitalWrite(CS_PIN, HIGH);
    pthread_mutex_destroy(&signal_mutex);
    
    printf("✅ Очистка завершена\n");
}

// Показать справку
void show_help() {
    printf("🚁 Продвинутый FPV Scanner для Raspberry Pi 4 + RX5808\n");
    printf("====================================================\n");
    printf("Использование: %s [опции]\n", "fpv_scanner_advanced");
    printf("\nОпции:\n");
    printf("  -v, --verbose    Подробный вывод\n");
    printf("  -c, --continuous Непрерывное сканирование\n");
    printf("  -h, --help       Показать эту справку\n");
    printf("\nПримеры:\n");
    printf("  %s -v          # Подробный режим\n", "fpv_scanner_advanced");
    printf("  %s -c          # Непрерывное сканирование\n", "fpv_scanner_advanced");
    printf("\nНажмите Ctrl+C для остановки\n");
}

// Главная функция
int main(int argc, char *argv[]) {
    // Обработка аргументов командной строки
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-v") == 0 || strcmp(argv[i], "--verbose") == 0) {
            verbose_mode = 1;
        } else if (strcmp(argv[i], "-c") == 0 || strcmp(argv[i], "--continuous") == 0) {
            continuous_mode = 1;
        } else if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0) {
            show_help();
            return 0;
        }
    }
    
    printf("🚁 Продвинутый FPV Scanner для Raspberry Pi 4 + RX5808\n");
    printf("====================================================\n");
    printf("Высокопроизводительный перехват FPV сигналов 5.8-6.0 ГГц\n");
    printf("Расширенный диапазон до 6000 МГц с детекцией и анализом\n");
    printf("Написан на C для максимальной скорости\n\n");
    
    // Установка обработчиков сигналов
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // Инициализация оборудования
    if (init_hardware() != 0) {
        printf("❌ Не удалось инициализировать оборудование\n");
        return 1;
    }
    
    // Инициализация массива сигналов
    memset(signals, 0, sizeof(signals));
    
    // Запуск сканирования в отдельном потоке
    pthread_t scan_thread;
    if (pthread_create(&scan_thread, NULL, scan_loop, NULL) != 0) {
        printf("❌ Ошибка создания потока сканирования\n");
        return 1;
    }
    
    // Основной цикл отображения
    while (running) {
        display_signals();
        usleep(1000000);  // Обновление каждую секунду
    }
    
    // Ожидание завершения потока сканирования
    pthread_join(scan_thread, NULL);
    
    // Отображение финальной статистики
    show_statistics();
    
    // Очистка ресурсов
    cleanup();
    
    printf("👋 Сканер завершен\n");
    return 0;
}
