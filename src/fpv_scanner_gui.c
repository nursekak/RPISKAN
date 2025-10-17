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
#include <gtk/gtk.h>
#include <cairo.h>

// Конфигурация сканирования
#define START_FREQ 5725    // Начальная частота (МГц)
#define END_FREQ 6000      // Конечная частота (МГц)
#define NUM_CHANNELS (END_FREQ - START_FREQ + 1)
#define MAX_SIGNALS 100

// Структура для обнаруженного сигнала
typedef struct {
    int frequency;
    int rssi;
    int strength;
    time_t timestamp;
    int active;
} signal_info_t;

// Структура для GUI данных
typedef struct {
    GtkWidget *window;
    GtkWidget *drawing_area;
    GtkWidget *status_label;
    GtkWidget *start_button;
    GtkWidget *stop_button;
    GtkWidget *frequency_entry;
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

// Обертка для gtk_widget_queue_draw для использования с g_idle_add
gboolean queue_draw_wrapper(gpointer data) {
    gtk_widget_queue_draw(GTK_WIDGET(data));
    return FALSE;  // Не повторять
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

// Функция сканирования в отдельном потоке
void* scan_thread(void* arg) {
    (void)arg;
    
    while (gui_data.running && gui_data.scanning) {
        for (int freq = START_FREQ; freq <= END_FREQ && gui_data.running && gui_data.scanning; freq++) {
            // Установка частоты
            set_frequency(freq);
            
            // Чтение RSSI
            int rssi = read_rssi_simulated(freq);
            
            // Обновление данных
            pthread_mutex_lock(&gui_data.data_mutex);
            gui_data.current_frequency = freq;
            gui_data.current_rssi = rssi;
            
            int channel_index = freq - START_FREQ;
            if (rssi > 50) {
                gui_data.detected_signals[channel_index].frequency = freq;
                gui_data.detected_signals[channel_index].rssi = rssi;
                gui_data.detected_signals[channel_index].strength = (rssi * 100) / 255;
                gui_data.detected_signals[channel_index].timestamp = time(NULL);
                gui_data.detected_signals[channel_index].active = 1;
            } else {
                gui_data.detected_signals[channel_index].active = 0;
            }
            pthread_mutex_unlock(&gui_data.data_mutex);
            
            // Обновление GUI
            g_idle_add(queue_draw_wrapper, gui_data.drawing_area);
            
            // Небольшая задержка для GUI
            usleep(10000);  // 10ms
        }
        
        simple_delay(100);
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
    }
    
    // Горизонтальные линии (RSSI)
    for (int i = 0; i <= 5; i++) {
        int y = (height * i) / 5;
        cairo_move_to(cr, 0, y);
        cairo_line_to(cr, width, y);
        cairo_stroke(cr);
    }
    
    // Отрисовка спектра
    cairo_set_line_width(cr, 2);
    cairo_set_source_rgb(cr, 0.0, 1.0, 0.0);
    
    for (int i = 0; i < NUM_CHANNELS; i++) {
        if (gui_data.detected_signals[i].active) {
            int x = (width * i) / NUM_CHANNELS;
            int y = height - (height * gui_data.detected_signals[i].rssi) / 255;
            
            cairo_move_to(cr, x, height);
            cairo_line_to(cr, x, y);
            cairo_stroke(cr);
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
        
        // Запуск потока сканирования
        pthread_t scan_thread_id;
        pthread_create(&scan_thread_id, NULL, scan_thread, NULL);
        pthread_detach(scan_thread_id);
        
        // Таймер обновления GUI
        g_timeout_add(100, update_status, NULL);
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
    frame = gtk_frame_new("Обнаруженные сигналы");
    gtk_box_pack_start(GTK_BOX(vbox), frame, TRUE, TRUE, 5);
    
    scrolled_window = gtk_scrolled_window_new(NULL, NULL);
    gtk_container_add(GTK_CONTAINER(frame), scrolled_window);
    
    gui_data.signals_list = gtk_list_box_new();
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
