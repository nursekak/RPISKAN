/*
 * FPV Scanner для Raspberry Pi 4 + RX5808
 * Быстрый перехват FPV сигналов дронов на частоте 5.8 ГГц
 * Написан на C для максимальной производительности
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

// Конфигурация GPIO для RX5808
#define CS_PIN 8          // CH2 (Chip Select)
#define RSSI_PIN 7        // RSSI input
#define SPI_CHANNEL 0      // SPI канал
#define SPI_SPEED 2000000  // Скорость SPI (2 МГц)

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
static int spi_fd = -1;

// Обработчик сигналов для корректного завершения
void signal_handler(int sig) {
    printf("\n🛑 Получен сигнал завершения, останавливаем сканер...\n");
    running = 0;
}

// Инициализация оборудования
int init_hardware() {
    printf("🔧 Инициализация оборудования...\n");
    
    // Инициализация WiringPi
    if (wiringPiSetupGpio() == -1) {
        printf("❌ Ошибка инициализации WiringPi\n");
        return -1;
    }
    
    // Настройка GPIO
    pinMode(CS_PIN, OUTPUT);
    digitalWrite(CS_PIN, HIGH);
    pinMode(RSSI_PIN, INPUT);
    
    // Инициализация SPI
    spi_fd = wiringPiSPISetup(SPI_CHANNEL, SPI_SPEED);
    if (spi_fd == -1) {
        printf("❌ Ошибка инициализации SPI\n");
        printf("Проверьте, что SPI включен: sudo raspi-config\n");
        return -1;
    }
    
    printf("✅ Оборудование инициализировано успешно\n");
    return 0;
}

// Запись данных в регистр RX5808
int rx5808_write(int address, int data) {
    unsigned char command = (address << 3) | data;
    unsigned char tx_buffer[1] = {command};
    unsigned char rx_buffer[1];
    
    digitalWrite(CS_PIN, LOW);
    wiringPiSPIDataRW(SPI_CHANNEL, tx_buffer, 1);
    digitalWrite(CS_PIN, HIGH);
    
    return 0;
}

// Установка частоты RX5808
int set_frequency(int frequency_mhz) {
    int freq_reg = (frequency_mhz - 479) / 2;
    
    // Запись регистров частоты
    rx5808_write(0x01, freq_reg & 0xFF);
    rx5808_write(0x02, (freq_reg >> 8) & 0xFF);
    
    // Включение приемника
    rx5808_write(0x00, 0x01);
    
    return 0;
}

// Чтение RSSI с RX5808
int read_rssi() {
    unsigned char tx_buffer[1] = {0x08};  // RSSI read command
    unsigned char rx_buffer[1];
    
    digitalWrite(CS_PIN, LOW);
    wiringPiSPIDataRW(SPI_CHANNEL, tx_buffer, 1);
    digitalWrite(CS_PIN, HIGH);
    
    return rx_buffer[0];
}

// Сканирование каналов
void scan_channels() {
    printf("🔍 Начинаем сканирование FPV каналов...\n");
    printf("Нажмите Ctrl+C для остановки\n\n");
    
    while (running) {
        printf("\r📡 Сканирование... ");
        fflush(stdout);
        
        for (int i = 0; i < NUM_CHANNELS && running; i++) {
            // Установка частоты
            set_frequency(channels[i].frequency);
            usleep(100000);  // 100ms settling time
            
            // Чтение RSSI
            int rssi = read_rssi();
            
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
        
        usleep(500000);  // 500ms интервал сканирования
    }
}

// Отображение статистики
void show_statistics() {
    int active_signals = 0;
    time_t current_time = time(NULL);
    
    printf("\n📊 Статистика обнаруженных сигналов:\n");
    printf("=====================================\n");
    
    for (int i = 0; i < NUM_CHANNELS; i++) {
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
    
    // Очистка GPIO
    digitalWrite(CS_PIN, HIGH);
    
    printf("✅ Очистка завершена\n");
}

// Главная функция
int main(int argc, char *argv[]) {
    printf("🚁 FPV Scanner для Raspberry Pi 4 + RX5808\n");
    printf("==========================================\n");
    printf("Перехват FPV сигналов дронов на частоте 5.8-6.0 ГГц\n");
    printf("Расширенный диапазон до 6000 МГц\n");
    printf("Написан на C для максимальной производительности\n\n");
    
    // Установка обработчиков сигналов
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
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
