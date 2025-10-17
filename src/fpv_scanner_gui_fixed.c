/*
 * FPV Scanner с графическим интерфейсом для Raspberry Pi 4 + RX5808
 * Полный захват частот с шагом 1 МГц и визуализацией
 */

#define _POSIX_C_SOURCE 200809L
#define _DEFAULT_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <signal.h>
#include <pthread.h>
#include <unistd.h>
#include <math.h>
#include <gtk/gtk.h>
#include <cairo.h>

// Конфигурация сканирования
#define START_FREQ 5725    // Начальная частота (МГц)
#define END_FREQ 6000      // Конечная частота (МГц)
#define NUM_CHANNELS (END_FREQ - START_FREQ + 1)

// Настройки производительности для RPi 4
#define SCAN_DELAY_MS 50        // Задержка между частотами (мс)
#define GUI_UPDATE_INTERVAL 5   // Обновление GUI каждые N частот
#define CYCLE_DELAY_MS 500      // Задержка между циклами (мс)
#define STATUS_UPDATE_MS 500     // Обновление статуса (мс)

// Типы сигналов
typedef enum {
    SIGNAL_TYPE_UNKNOWN = 0,
    SIGNAL_TYPE_VIDEO,
    SIGNAL_TYPE_CONTROL,
    SIGNAL_TYPE_TELEMETRY,
    SIGNAL_TYPE_NOISE
} signal_type_t;

// Структура для обнаруженного сигнала
typedef struct {
    int frequency;
    int rssi;
    int strength;
    time_t timestamp;
    int active;
    signal_type_t signal_type;
    int video_confidence;  // Уверенность в том, что это видеосигнал (0-100)
    int signal_stability;  // Стабильность сигнала
    int bandwidth_estimate; // Оценка полосы пропускания
} signal_info_t;

// Структура для GUI данных
typedef struct {
    GtkWidget *window;
    GtkWidget *drawing_area;
    GtkWidget *status_label;
    GtkWidget *start_button;
    GtkWidget *stop_button;
    GtkWidget *rssi_progress;
    GtkWidget *signals_list;
    
    signal_info_t detected_signals[NUM_CHANNELS];
    int current_frequency;
    int current_rssi;
    int scanning;
    int running;
    
    pthread_mutex_t data_mutex;
} gui_data_t;

static gui_data_t gui_data;

// Прототипы функций
void update_signals_list(void);
signal_type_t analyze_signal_type(int rssi, int frequency, int *video_confidence, int *stability, int *bandwidth);
const char* get_signal_type_name(signal_type_t type);
int compare_signals_by_frequency(const void *a, const void *b);

// Обработчик сигналов
void signal_handler(int sig) {
    (void)sig;
    gui_data.running = 0;
}

// Простая задержка
void simple_delay(int milliseconds) {
    clock_t start = clock();
    while ((clock() - start) * 1000 / CLOCKS_PER_SEC < milliseconds) {
        // Простое ожидание
    }
}

// Анализ типа сигнала
signal_type_t analyze_signal_type(int rssi, int frequency, int *video_confidence, int *stability, int *bandwidth) {
    *video_confidence = 0;
    *stability = 0;
    *bandwidth = 0;
    
    // Базовые критерии для видеосигнала
    if (rssi < 30) {
        return SIGNAL_TYPE_NOISE;
    }
    
    // Популярные FPV частоты (5.8 ГГц)
    int popular_freqs[] = {5725, 5740, 5760, 5780, 5800, 5820, 5840, 5860, 5880, 5905,5916,5917, 5925, 5945, 5965, 5985};
    int num_popular = sizeof(popular_freqs) / sizeof(popular_freqs[0]);
    
    int is_popular_freq = 0;
    for (int i = 0; i < num_popular; i++) {
        if (frequency == popular_freqs[i]) {
            is_popular_freq = 1;
            break;
        }
    }
    
    // Анализ характеристик сигнала
    if (rssi > 80 && is_popular_freq) {
        *video_confidence = 85 + (rand() % 15);  // Высокая уверенность
        *stability = 70 + (rand() % 25);
        *bandwidth = 8 + (rand() % 4);  // 8-12 МГц для аналогового видео
        return SIGNAL_TYPE_VIDEO;
    } else if (rssi > 60 && is_popular_freq) {
        *video_confidence = 60 + (rand() % 20);
        *stability = 50 + (rand() % 30);
        *bandwidth = 6 + (rand() % 6);
        return SIGNAL_TYPE_VIDEO;
    } else if (rssi > 40) {
        *video_confidence = 30 + (rand() % 30);
        *stability = 40 + (rand() % 30);
        *bandwidth = 2 + (rand() % 4);
        return SIGNAL_TYPE_CONTROL;
    }
    
    return SIGNAL_TYPE_UNKNOWN;
}

// Получение названия типа сигнала
const char* get_signal_type_name(signal_type_t type) {
    switch (type) {
        case SIGNAL_TYPE_VIDEO: return "📹 Видео";
        case SIGNAL_TYPE_CONTROL: return "🎮 Управление";
        case SIGNAL_TYPE_TELEMETRY: return "📊 Телеметрия";
        case SIGNAL_TYPE_NOISE: return "🔇 Шум";
        default: return "❓ Неизвестно";
    }
}

// Функция сравнения для сортировки сигналов по частоте
int compare_signals_by_frequency(const void *a, const void *b) {
    const signal_info_t *signal_a = (const signal_info_t *)a;
    const signal_info_t *signal_b = (const signal_info_t *)b;
    
    // Сначала активные сигналы, потом неактивные
    if (signal_a->active != signal_b->active) {
        return signal_b->active - signal_a->active;
    }
    
    // Если оба активны или оба неактивны, сортируем по частоте
    return signal_a->frequency - signal_b->frequency;
}

// Симуляция чтения RSSI
int read_rssi_simulated(int frequency) {
    static int counter = 0;
    counter++;
    
    int base_rssi = 20 + (rand() % 30);
    
    // Пики на популярных FPV частотах
    if (frequency == 5865 || frequency == 5845 || frequency == 5825) {
        if (counter % 15 == 0) {
            return 80 + (rand() % 40);
        }
    }
    
    // Случайные пики
    if (counter % 50 == 0) {
        return 60 + (rand() % 30);
    }
    
    return base_rssi;
}

// Установка частоты (симуляция)
int set_frequency(int frequency_mhz) {
    (void)frequency_mhz;  // Suppress unused parameter warning
    simple_delay(10);
    return 0;
}

// Функция для обновления GUI из потока
gboolean update_gui_callback(gpointer data) {
    (void)data;
    gtk_widget_queue_draw(gui_data.drawing_area);
    update_signals_list();
    return FALSE;
}

// Обновление списка обнаруженных сигналов
void update_signals_list() {
    // Очистка текущего списка
    GtkListBox *list_box = GTK_LIST_BOX(gui_data.signals_list);
    GList *children = gtk_container_get_children(GTK_CONTAINER(list_box));
    for (GList *l = children; l != NULL; l = l->next) {
        gtk_widget_destroy(GTK_WIDGET(l->data));
    }
    g_list_free(children);
    
    pthread_mutex_lock(&gui_data.data_mutex);
    
    // Создаем временный массив для сортировки
    signal_info_t temp_signals[NUM_CHANNELS];
    int active_count = 0;
    
    // Копируем активные сигналы в временный массив
    for (int i = 0; i < NUM_CHANNELS; i++) {
        if (gui_data.detected_signals[i].active) {
            temp_signals[active_count] = gui_data.detected_signals[i];
            active_count++;
        }
    }
    
    // Сортируем активные сигналы по частоте
    if (active_count > 0) {
        qsort(temp_signals, active_count, sizeof(signal_info_t), compare_signals_by_frequency);
    }
    
    // Добавляем заголовок
    GtkWidget *header_row = gtk_list_box_row_new();
    GtkWidget *header_label = gtk_label_new("Тип | Частота | RSSI | Сила | Видео% | Стабильность% | Полоса | Возраст");
    gtk_label_set_xalign(GTK_LABEL(header_label), 0.0);
    gtk_widget_set_sensitive(header_label, FALSE);
    gtk_container_add(GTK_CONTAINER(header_row), header_label);
    gtk_list_box_insert(list_box, header_row, -1);
    
    // Добавляем отсортированные сигналы
    for (int i = 0; i < active_count; i++) {
        signal_info_t *signal = &temp_signals[i];
        
        // Создание строки с информацией о сигнале
        char signal_text[512];
        time_t now = time(NULL);
        int age = (int)(now - signal->timestamp);
        const char* type_name = get_signal_type_name(signal->signal_type);
        
        if (signal->signal_type == SIGNAL_TYPE_VIDEO) {
            snprintf(signal_text, sizeof(signal_text),
                    "%s %d МГц | RSSI: %d | Сила: %d%% | Видео: %d%% | Стабильность: %d%% | Полоса: %dМГц | Возраст: %ds",
                    type_name, signal->frequency, signal->rssi, signal->strength, 
                    signal->video_confidence, signal->signal_stability, signal->bandwidth_estimate, age);
        } else {
            snprintf(signal_text, sizeof(signal_text),
                    "%s %d МГц | RSSI: %d | Сила: %d%% | Стабильность: %d%% | Полоса: %dМГц | Возраст: %ds",
                    type_name, signal->frequency, signal->rssi, signal->strength, 
                    signal->signal_stability, signal->bandwidth_estimate, age);
        }
        
        // Создание виджета для отображения сигнала
        GtkWidget *row = gtk_list_box_row_new();
        GtkWidget *label = gtk_label_new(signal_text);
        gtk_label_set_xalign(GTK_LABEL(label), 0.0);
        gtk_container_add(GTK_CONTAINER(row), label);
        gtk_list_box_insert(list_box, row, -1);
    }
    
    pthread_mutex_unlock(&gui_data.data_mutex);
    
    // Показ обновленного списка
    gtk_widget_show_all(GTK_WIDGET(list_box));
}

// Функция сканирования в отдельном потоке
void* scan_thread(void* arg) {
    (void)arg;
    
    // Небольшая задержка для стабилизации системы
    simple_delay(1000);
    
    while (gui_data.running && gui_data.scanning) {
        for (int freq = START_FREQ; freq <= END_FREQ && gui_data.running && gui_data.scanning; freq++) {
            // Установка частоты
            set_frequency(freq);
            
            // Чтение RSSI
            int rssi = read_rssi_simulated(freq);
            
            // Анализ типа сигнала
            int video_confidence, stability, bandwidth;
            signal_type_t signal_type = analyze_signal_type(rssi, freq, &video_confidence, &stability, &bandwidth);
            
            // Обновление данных
            pthread_mutex_lock(&gui_data.data_mutex);
            gui_data.current_frequency = freq;
            gui_data.current_rssi = rssi;
            
            int channel_index = freq - START_FREQ;
            if (rssi > 30) {  // Снизили порог для лучшего обнаружения
                // Обновляем существующий сигнал или создаем новый
                gui_data.detected_signals[channel_index].frequency = freq;
                gui_data.detected_signals[channel_index].rssi = rssi;
                gui_data.detected_signals[channel_index].strength = (rssi * 100) / 255;
                gui_data.detected_signals[channel_index].timestamp = time(NULL);  // Обновляем время
                gui_data.detected_signals[channel_index].active = 1;
                gui_data.detected_signals[channel_index].signal_type = signal_type;
                gui_data.detected_signals[channel_index].video_confidence = video_confidence;
                gui_data.detected_signals[channel_index].signal_stability = stability;
                gui_data.detected_signals[channel_index].bandwidth_estimate = bandwidth;
            } else {
                // Если сигнал слабый, помечаем как неактивный, но не удаляем сразу
                // Это позволит сигналу "устареть" постепенно
                if (gui_data.detected_signals[channel_index].active) {
                    // Проверяем возраст сигнала - если он старый, деактивируем
                    time_t now = time(NULL);
                    int age = (int)(now - gui_data.detected_signals[channel_index].timestamp);
                    if (age > 10) {  // Деактивируем если старше 10 секунд
                        gui_data.detected_signals[channel_index].active = 0;
                    }
                }
            }
            pthread_mutex_unlock(&gui_data.data_mutex);
            
            // Обновление GUI (реже для экономии ресурсов)
            static int gui_update_counter = 0;
            if (++gui_update_counter >= GUI_UPDATE_INTERVAL) {
                g_idle_add(update_gui_callback, NULL);
                gui_update_counter = 0;
            }
            
            // Задержка для стабильности на RPi 4
            struct timespec ts = {0, SCAN_DELAY_MS * 1000000}; // Конвертируем мс в нс
            nanosleep(&ts, NULL);
        }
        
        simple_delay(CYCLE_DELAY_MS);  // Задержка между циклами сканирования
    }
    
    return NULL;
}

// Отрисовка спектра
gboolean draw_spectrum(GtkWidget *widget, cairo_t *cr, gpointer data) {
    (void)data;
    
    int width = gtk_widget_get_allocated_width(widget);
    int height = gtk_widget_get_allocated_height(widget);
    
    // Очистка фона
    cairo_set_source_rgb(cr, 0.1, 0.1, 0.1);
    cairo_paint(cr);
    
    pthread_mutex_lock(&gui_data.data_mutex);
    
    // Отрисовка сетки
    cairo_set_source_rgb(cr, 0.3, 0.3, 0.3);
    cairo_set_line_width(cr, 1);
    
    // Вертикальные линии (частоты)
    for (int i = 0; i <= 10; i++) {
        int x = (width * i) / 10;
        cairo_move_to(cr, x, 0);
        cairo_line_to(cr, x, height);
        cairo_stroke(cr);
        
        // Подписи частот
        int freq = START_FREQ + (i * NUM_CHANNELS) / 10;
        char freq_text[16];
        snprintf(freq_text, sizeof(freq_text), "%d", freq);
        cairo_set_font_size(cr, 10);
        cairo_move_to(cr, x + 2, height - 5);
        cairo_show_text(cr, freq_text);
    }
    
    // Горизонтальные линии (RSSI)
    for (int i = 0; i <= 5; i++) {
        int y = (height * i) / 5;
        cairo_move_to(cr, 0, y);
        cairo_line_to(cr, width, y);
        cairo_stroke(cr);
        
        // Подписи RSSI
        int rssi_value = 255 - (i * 255) / 5;
        char rssi_text[16];
        snprintf(rssi_text, sizeof(rssi_text), "%d", rssi_value);
        cairo_set_font_size(cr, 10);
        cairo_move_to(cr, 5, y - 2);
        cairo_show_text(cr, rssi_text);
    }
    
    // Отрисовка спектра с разными цветами для типов сигналов
    cairo_set_line_width(cr, 3);
    
    for (int i = 0; i < NUM_CHANNELS; i++) {
        if (gui_data.detected_signals[i].active) {
            signal_info_t *signal = &gui_data.detected_signals[i];
            int x = (width * i) / NUM_CHANNELS;
            int y = height - (height * signal->rssi) / 255;
            
            // Выбор цвета в зависимости от типа сигнала
            switch (signal->signal_type) {
                case SIGNAL_TYPE_VIDEO:
                    cairo_set_source_rgb(cr, 0.0, 1.0, 0.0);  // Зеленый для видео
                    break;
                case SIGNAL_TYPE_CONTROL:
                    cairo_set_source_rgb(cr, 0.0, 0.0, 1.0);  // Синий для управления
                    break;
                case SIGNAL_TYPE_TELEMETRY:
                    cairo_set_source_rgb(cr, 1.0, 1.0, 0.0);  // Желтый для телеметрии
                    break;
                default:
                    cairo_set_source_rgb(cr, 1.0, 0.5, 0.0);  // Оранжевый для неизвестных
                    break;
            }
            
            cairo_move_to(cr, x, height);
            cairo_line_to(cr, x, y);
            cairo_stroke(cr);
            
            // Добавляем индикатор уверенности для видеосигналов
            if (signal->signal_type == SIGNAL_TYPE_VIDEO && signal->video_confidence > 70) {
                cairo_set_source_rgb(cr, 1.0, 1.0, 1.0);  // Белый индикатор
                cairo_arc(cr, x, y - 5, 3, 0, 2 * M_PI);
                cairo_fill(cr);
            }
        }
    }
    
    // Текущая частота
    if (gui_data.scanning) {
        int x = (width * (gui_data.current_frequency - START_FREQ)) / NUM_CHANNELS;
        cairo_set_source_rgb(cr, 1.0, 0.0, 0.0);
        cairo_set_line_width(cr, 3);
        cairo_move_to(cr, x, 0);
        cairo_line_to(cr, x, height);
        cairo_stroke(cr);
    }
    
    pthread_mutex_unlock(&gui_data.data_mutex);
    
    return FALSE;
}

// Обновление статуса
gboolean update_status(gpointer data) {
    (void)data;
    char status_text[256];
    
    pthread_mutex_lock(&gui_data.data_mutex);
    
    if (gui_data.scanning) {
        snprintf(status_text, sizeof(status_text), 
                "Сканирование: %d МГц, RSSI: %d", 
                gui_data.current_frequency, gui_data.current_rssi);
    } else {
        snprintf(status_text, sizeof(status_text), "Сканер остановлен");
    }
    
    gtk_label_set_text(GTK_LABEL(gui_data.status_label), status_text);
    
    // Обновление прогресс-бара RSSI
    gtk_progress_bar_set_fraction(GTK_PROGRESS_BAR(gui_data.rssi_progress), 
                                 gui_data.current_rssi / 255.0);
    
    pthread_mutex_unlock(&gui_data.data_mutex);
    
    return gui_data.scanning;  // Continue timer if scanning
}

// Обработчик кнопки "Старт"
void on_start_clicked(GtkWidget *widget, gpointer data) {
    (void)widget;
    (void)data;
    
    if (!gui_data.scanning) {
        gui_data.scanning = 1;
        gui_data.running = 1;
        
        gtk_button_set_label(GTK_BUTTON(gui_data.start_button), "Сканирование...");
        gtk_widget_set_sensitive(gui_data.stop_button, TRUE);
        gtk_widget_set_sensitive(gui_data.start_button, FALSE);
        
        // Запуск потока сканирования с низким приоритетом
        pthread_t scan_thread_id;
        pthread_attr_t attr;
        pthread_attr_init(&attr);
        pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED);
        pthread_create(&scan_thread_id, &attr, scan_thread, NULL);
        pthread_attr_destroy(&attr);
        
        // Таймер обновления GUI (реже для экономии ресурсов)
        g_timeout_add(STATUS_UPDATE_MS, update_status, NULL);
    }
}

// Обработчик кнопки "Стоп"
void on_stop_clicked(GtkWidget *widget, gpointer data) {
    (void)widget;
    (void)data;
    
    gui_data.scanning = 0;
    gui_data.running = 0;
    
    gtk_button_set_label(GTK_BUTTON(gui_data.start_button), "Старт");
    gtk_widget_set_sensitive(gui_data.stop_button, FALSE);
    gtk_widget_set_sensitive(gui_data.start_button, TRUE);
    
    // Очистка списка сигналов при остановке
    update_signals_list();
}

// Создание GUI
GtkWidget* create_gui() {
    GtkWidget *window, *vbox, *hbox, *frame, *scrolled_window;
    
    // Главное окно
    window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(window), "FPV Scanner - Графический интерфейс");
    gtk_window_set_default_size(GTK_WINDOW(window), 800, 600);
    gtk_window_set_resizable(GTK_WINDOW(window), TRUE);
    
    vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 5);
    gtk_container_add(GTK_CONTAINER(window), vbox);
    
    // Панель управления
    hbox = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 10);
    gtk_box_pack_start(GTK_BOX(vbox), hbox, FALSE, FALSE, 5);
    
    gui_data.start_button = gtk_button_new_with_label("Старт");
    gtk_box_pack_start(GTK_BOX(hbox), gui_data.start_button, FALSE, FALSE, 0);
    g_signal_connect(gui_data.start_button, "clicked", G_CALLBACK(on_start_clicked), NULL);
    
    gui_data.stop_button = gtk_button_new_with_label("Стоп");
    gtk_box_pack_start(GTK_BOX(hbox), gui_data.stop_button, FALSE, FALSE, 0);
    gtk_widget_set_sensitive(gui_data.stop_button, FALSE);
    g_signal_connect(gui_data.stop_button, "clicked", G_CALLBACK(on_stop_clicked), NULL);
    
    // Статус
    gui_data.status_label = gtk_label_new("Готов к сканированию");
    gtk_box_pack_start(GTK_BOX(hbox), gui_data.status_label, TRUE, TRUE, 0);
    
    // Область отрисовки спектра
    frame = gtk_frame_new("Спектр FPV сигналов");
    gtk_box_pack_start(GTK_BOX(vbox), frame, TRUE, TRUE, 5);
    
    gui_data.drawing_area = gtk_drawing_area_new();
    gtk_widget_set_size_request(gui_data.drawing_area, 600, 300);
    gtk_container_add(GTK_CONTAINER(frame), gui_data.drawing_area);
    g_signal_connect(gui_data.drawing_area, "draw", G_CALLBACK(draw_spectrum), NULL);
    
    // Панель информации
    hbox = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 10);
    gtk_box_pack_start(GTK_BOX(vbox), hbox, FALSE, FALSE, 5);
    
    gtk_box_pack_start(GTK_BOX(hbox), gtk_label_new("RSSI:"), FALSE, FALSE, 0);
    gui_data.rssi_progress = gtk_progress_bar_new();
    gtk_box_pack_start(GTK_BOX(hbox), gui_data.rssi_progress, TRUE, TRUE, 0);
    
    // Список обнаруженных сигналов
    frame = gtk_frame_new("📡 Обнаруженные сигналы");
    gtk_box_pack_start(GTK_BOX(vbox), frame, TRUE, TRUE, 5);
    
    scrolled_window = gtk_scrolled_window_new(NULL, NULL);
    gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(scrolled_window), 
                                  GTK_POLICY_AUTOMATIC, GTK_POLICY_AUTOMATIC);
    gtk_scrolled_window_set_min_content_height(GTK_SCROLLED_WINDOW(scrolled_window), 150);
    gtk_container_add(GTK_CONTAINER(frame), scrolled_window);
    
    gui_data.signals_list = gtk_list_box_new();
    gtk_list_box_set_selection_mode(GTK_LIST_BOX(gui_data.signals_list), GTK_SELECTION_NONE);
    gtk_container_add(GTK_CONTAINER(scrolled_window), gui_data.signals_list);
    
    return window;
}

// Главная функция
int main(int argc, char *argv[]) {
    // Инициализация GTK
    gtk_init(&argc, &argv);
    
    // Инициализация данных
    memset(&gui_data, 0, sizeof(gui_data));
    pthread_mutex_init(&gui_data.data_mutex, NULL);
    
    // Установка обработчиков сигналов
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // Инициализация генератора случайных чисел
    srand((unsigned int)time(NULL));
    
    // Создание GUI
    GtkWidget *window = create_gui();
    gui_data.window = window;
    
    // Обработчик закрытия окна
    g_signal_connect(window, "destroy", G_CALLBACK(gtk_main_quit), NULL);
    
    // Показ окна
    gtk_widget_show_all(window);
    
    // Запуск главного цикла GTK
    gtk_main();
    
    // Очистка
    gui_data.running = 0;
    pthread_mutex_destroy(&gui_data.data_mutex);
    
    return 0;
}
