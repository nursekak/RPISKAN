/*
 * FPV Scanner для Raspberry Pi 4 + RX5808 (без WiringPi)
 * Использует прямые системные вызовы для максимальной совместимости
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <signal.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>
#include <fcntl.h>
#include <errno.h>

// Конфигурация GPIO для RX5808
#define CS_PIN 8          // CH2 (Chip Select)
#define RSSI_PIN 7        // RSSI input
#define SPI_DEVICE "/dev/spi0.0"
#define SPI_SPEED 2000000  // Скорость SPI (2 МГц)

// FPV каналы 5.8 ГГц
typedef struct {
    char channel;
    int frequency;
} fpv_channel_t;

static const fpv_channel_t channels[] = {
    {'A', 5865}, {'B', 5845}, {'C', 5825}, {'D', 5805},
    {'E', 5785}, {'F', 5765}, {'G', 5745}, {'H', 5725}
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

// Управление GPIO через sysfs
int gpio_export(int pin) {
    char path[64];
    int fd;
    
    snprintf(path, sizeof(path), "/sys/class/gpio/export");
    fd = open(path, O_WRONLY);
    if (fd < 0) {
        return -1;
    }
    
    char pin_str[4];
    snprintf(pin_str, sizeof(pin_str), "%d", pin);
    write(fd, pin_str, strlen(pin_str));
    close(fd);
    
    return 0;
}

int gpio_unexport(int pin) {
    char path[64];
    int fd;
    
    snprintf(path, sizeof(path), "/sys/class/gpio/unexport");
    fd = open(path, O_WRONLY);
    if (fd < 0) {
        return -1;
    }
    
    char pin_str[4];
    snprintf(pin_str, sizeof(pin_str), "%d", pin);
    write(fd, pin_str, strlen(pin_str));
    close(fd);
    
    return 0;
}

int gpio_set_direction(int pin, const char* direction) {
    char path[64];
    int fd;
    
    snprintf(path, sizeof(path), "/sys/class/gpio/gpio%d/direction", pin);
    fd = open(path, O_WRONLY);
    if (fd < 0) {
        return -1;
    }
    
    write(fd, direction, strlen(direction));
    close(fd);
    
    return 0;
}

int gpio_write(int pin, int value) {
    char path[64];
    int fd;
    
    snprintf(path, sizeof(path), "/sys/class/gpio/gpio%d/value", pin);
    fd = open(path, O_WRONLY);
    if (fd < 0) {
        return -1;
    }
    
    char val = value ? '1' : '0';
    write(fd, &val, 1);
    close(fd);
    
    return 0;
}

int gpio_read(int pin) {
    char path[64];
    int fd;
    char value;
    
    snprintf(path, sizeof(path), "/sys/class/gpio/gpio%d/value", pin);
    fd = open(path, O_RDONLY);
    if (fd < 0) {
        return -1;
    }
    
    read(fd, &value, 1);
    close(fd);
    
    return value == '1' ? 1 : 0;
}

// Инициализация оборудования
int init_hardware() {
    printf("🔧 Инициализация оборудования...\n");
    
    // Экспорт GPIO пинов
    if (gpio_export(CS_PIN) < 0) {
        printf("❌ Ошибка экспорта CS_PIN %d\n", CS_PIN);
        return -1;
    }
    
    if (gpio_export(RSSI_PIN) < 0) {
        printf("❌ Ошибка экспорта RSSI_PIN %d\n", RSSI_PIN);
        return -1;
    }
    
    // Настройка направления пинов
    gpio_set_direction(CS_PIN, "out");
    gpio_set_direction(RSSI_PIN, "in");
    
    // Установка начального состояния
    gpio_write(CS_PIN, 1);  // CS высокий по умолчанию
    
    // Инициализация SPI
    spi_fd = open(SPI_DEVICE, O_RDWR);
    if (spi_fd < 0) {
        printf("❌ Ошибка открытия SPI устройства %s: %s\n", SPI_DEVICE, strerror(errno));
        printf("Проверьте, что SPI включен: sudo raspi-config\n");
        return -1;
    }
    
    // Настройка SPI режима
    uint8_t mode = SPI_MODE_0;
    if (ioctl(spi_fd, SPI_IOC_WR_MODE, &mode) < 0) {
        printf("❌ Ошибка настройки SPI режима\n");
        return -1;
    }
    
    // Настройка скорости SPI
    uint32_t speed = SPI_SPEED;
    if (ioctl(spi_fd, SPI_IOC_WR_MAX_SPEED_HZ, &speed) < 0) {
        printf("❌ Ошибка настройки скорости SPI\n");
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
    
    struct spi_ioc_transfer transfer = {
        .tx_buf = (unsigned long)tx_buffer,
        .rx_buf = (unsigned long)rx_buffer,
        .len = 1,
        .speed_hz = SPI_SPEED,
        .bits_per_word = 8,
    };
    
    gpio_write(CS_PIN, 0);  // CS низкий
    if (ioctl(spi_fd, SPI_IOC_MESSAGE(1), &transfer) < 0) {
        printf("❌ Ошибка SPI передачи\n");
        return -1;
    }
    gpio_write(CS_PIN, 1);  // CS высокий
    
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
    
    struct spi_ioc_transfer transfer = {
        .tx_buf = (unsigned long)tx_buffer,
        .rx_buf = (unsigned long)rx_buffer,
        .len = 1,
        .speed_hz = SPI_SPEED,
        .bits_per_word = 8,
    };
    
    gpio_write(CS_PIN, 0);  // CS низкий
    if (ioctl(spi_fd, SPI_IOC_MESSAGE(1), &transfer) < 0) {
        printf("❌ Ошибка чтения RSSI\n");
        return 0;
    }
    gpio_write(CS_PIN, 1);  // CS высокий
    
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
    gpio_write(CS_PIN, 1);
    gpio_unexport(CS_PIN);
    gpio_unexport(RSSI_PIN);
    
    printf("✅ Очистка завершена\n");
}

// Главная функция
int main(int argc, char *argv[]) {
    printf("🚁 FPV Scanner для Raspberry Pi 4 + RX5808 (Native C)\n");
    printf("==================================================\n");
    printf("Перехват FPV сигналов дронов на частоте 5.8 ГГц\n");
    printf("Использует прямые системные вызовы (без WiringPi)\n\n");
    
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
