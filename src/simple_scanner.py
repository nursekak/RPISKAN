#!/usr/bin/env python3
"""
Простой сканер FPV сигналов для Raspberry Pi 4 + RX5808
Упрощенный интерфейс для быстрого перехвата дронов на частоте 5.8 ГГц
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import cv2
import numpy as np
import RPi.GPIO as GPIO
import spidev
import subprocess
import os
from PIL import Image, ImageTk
import json

class SimpleFPVScanner:
    def __init__(self):
        # GPIO конфигурация для RX5808
        self.CS_PIN = 8          # CH2 (Chip Select)
        self.RSSI_PIN = 7       # RSSI input
        self.SPI_BUS = 0
        self.SPI_DEVICE = 0
        
        # Видео конфигурация
        self.video_device = self.find_video_device()
        self.video_width = 640
        self.video_height = 480
        self.video_fps = 30
        
        # FPV каналы 5.8 ГГц
        self.channels = {
            'A': 5865, 'B': 5845, 'C': 5825, 'D': 5805,
            'E': 5785, 'F': 5765, 'G': 5745, 'H': 5725
        }
        
        # Состояние сканера
        self.scanning = False
        self.current_channel = 'A'
        self.detected_signals = {}
        self.video_capturing = False
        
        # Инициализация оборудования
        if not self.setup_hardware():
            print("❌ Не удалось инициализировать оборудование")
            return
        
        # Создание GUI
        self.create_gui()
        
    def find_video_device(self):
        """Автоматическое определение USB Video DVR"""
        try:
            result = subprocess.run(['ls', '/dev/video*'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                devices = result.stdout.strip().split('\n')
                for device in devices:
                    if device.strip():
                        return device.strip()
            return "/dev/video0"
        except:
            return "/dev/video0"
    
    def setup_hardware(self):
        """Инициализация GPIO и SPI для RX5808"""
        try:
            # Проверка SPI устройств
            import os
            if not os.path.exists('/dev/spi0.0'):
                print("❌ SPI не включен! Включите SPI в настройках Raspberry Pi:")
                print("1. sudo nano /boot/firmware/config.txt")
                print("2. Добавьте строку: dtparam=spi=on")
                print("3. sudo reboot")
                messagebox.showerror("SPI не включен", 
                    "SPI не включен на Raspberry Pi!\n\n"
                    "Включите SPI:\n"
                    "1. sudo nano /boot/firmware/config.txt\n"
                    "2. Добавьте: dtparam=spi=on\n"
                    "3. sudo reboot")
                return False
            
            # Настройка GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.CS_PIN, GPIO.OUT)
            GPIO.output(self.CS_PIN, GPIO.HIGH)
            
            # Настройка SPI
            self.spi = spidev.SpiDev()
            self.spi.open(self.SPI_BUS, self.SPI_DEVICE)
            self.spi.max_speed_hz = 2000000
            self.spi.mode = 0
            
            print("✅ Оборудование инициализировано успешно")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка инициализации оборудования: {e}")
            messagebox.showerror("Ошибка оборудования", 
                f"Не удалось инициализировать оборудование: {e}\n\n"
                "Возможные причины:\n"
                "1. SPI не включен\n"
                "2. Неправильное подключение RX5808\n"
                "3. Недостаточно прав доступа")
            return False
    
    def rx5808_write(self, address, data):
        """Запись данных в регистр RX5808"""
        try:
            command = (address << 3) | data
            GPIO.output(self.CS_PIN, GPIO.LOW)
            self.spi.writebytes([command])
            GPIO.output(self.CS_PIN, GPIO.HIGH)
        except Exception as e:
            print(f"Ошибка записи RX5808: {e}")
    
    def set_frequency(self, frequency_mhz):
        """Установка частоты RX5808 в МГц"""
        try:
            freq_reg = int((frequency_mhz - 479) / 2)
            self.rx5808_write(0x01, freq_reg & 0xFF)
            self.rx5808_write(0x02, (freq_reg >> 8) & 0xFF)
            self.rx5808_write(0x00, 0x01)
            print(f"Частота установлена: {frequency_mhz} МГц")
        except Exception as e:
            print(f"Ошибка установки частоты: {e}")
    
    def read_rssi(self):
        """Чтение значения RSSI с RX5808"""
        try:
            GPIO.output(self.CS_PIN, GPIO.LOW)
            self.spi.writebytes([0x08])
            response = self.spi.readbytes(1)
            GPIO.output(self.CS_PIN, GPIO.HIGH)
            return response[0] if response else 0
        except Exception as e:
            print(f"Ошибка чтения RSSI: {e}")
            return 0
    
    def scan_channels(self):
        """Сканирование всех каналов на наличие сигналов"""
        while self.scanning:
            for channel, freq in self.channels.items():
                if not self.scanning:
                    break
                    
                # Установка частоты
                self.set_frequency(freq)
                time.sleep(0.1)
                
                # Чтение RSSI
                rssi = self.read_rssi()
                
                # Обновление обнаруженных сигналов
                if rssi > 50:
                    self.detected_signals[channel] = {
                        'frequency': freq,
                        'rssi': rssi,
                        'strength': min(100, int(rssi * 100 / 255)),
                        'timestamp': time.time()
                    }
                    
                    # Захват видео при сильном сигнале
                    if rssi > 100 and not self.video_capturing:
                        self.start_video_capture(channel, freq)
                
                # Обновление GUI
                self.update_display()
                
            time.sleep(0.5)
    
    def start_video_capture(self, channel, frequency):
        """Запуск захвата видео с обнаруженного сигнала"""
        try:
            self.video_capturing = True
            self.current_channel = channel
            
            self.status_label.config(text=f"🎥 Захват видео с канала {channel} ({frequency} МГц)")
            
            # Запуск потока захвата видео
            video_thread = threading.Thread(target=self.capture_video)
            video_thread.daemon = True
            video_thread.start()
            
        except Exception as e:
            print(f"Ошибка запуска захвата видео: {e}")
    
    def capture_video(self):
        """Захват и отображение видео с USB Video DVR"""
        try:
            cap = cv2.VideoCapture(self.video_device)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_height)
            cap.set(cv2.CAP_PROP_FPS, self.video_fps)
            
            if not cap.isOpened():
                print("Не удалось открыть видеоустройство")
                return
            
            while self.video_capturing:
                ret, frame = cap.read()
                if ret:
                    # Добавление информации о канале
                    cv2.putText(frame, f"Канал: {self.current_channel}", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Частота: {self.channels[self.current_channel]} МГц", 
                               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                    
                    # Конвертация для Tkinter
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_pil = Image.fromarray(frame_rgb)
                    frame_tk = ImageTk.PhotoImage(frame_pil)
                    
                    # Обновление отображения видео
                    self.video_label.config(image=frame_tk)
                    self.video_label.image = frame_tk
                
                time.sleep(1.0 / self.video_fps)
            
            cap.release()
            
        except Exception as e:
            print(f"Ошибка захвата видео: {e}")
        finally:
            self.video_capturing = False
    
    def create_gui(self):
        """Создание главного окна GUI"""
        self.root = tk.Tk()
        self.root.title("🚁 Простой FPV Сканер - Raspberry Pi 4 + RX5808")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2b2b2b')
        
        # Настройка сетки
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Панель управления
        self.create_control_panel()
        
        # Отображение спектра
        self.create_spectrum_display()
        
        # Отображение видео
        self.create_video_display()
        
        # Строка состояния
        self.create_status_bar()
    
    def create_control_panel(self):
        """Создание панели управления"""
        control_frame = ttk.LabelFrame(self.root, text="🎛️ Управление сканером", padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Кнопка старт/стоп
        self.scan_button = ttk.Button(control_frame, text="▶️ Начать сканирование", 
                                     command=self.toggle_scanning)
        self.scan_button.pack(side="left", padx=5)
        
        # Кнопка остановки видео
        self.video_button = ttk.Button(control_frame, text="⏹️ Остановить видео", 
                                      command=self.stop_video_capture)
        self.video_button.pack(side="left", padx=5)
        
        # Выбор канала
        ttk.Label(control_frame, text="Канал:").pack(side="left", padx=5)
        self.channel_var = tk.StringVar(value="A")
        channel_combo = ttk.Combobox(control_frame, textvariable=self.channel_var, 
                                    values=list(self.channels.keys()), width=5)
        channel_combo.pack(side="left", padx=5)
        channel_combo.bind("<<ComboboxSelected>>", self.on_channel_select)
        
        # Порог RSSI
        ttk.Label(control_frame, text="Порог RSSI:").pack(side="left", padx=5)
        self.threshold_var = tk.IntVar(value=50)
        threshold_scale = ttk.Scale(control_frame, from_=0, to=255, 
                                   variable=self.threshold_var, orient="horizontal")
        threshold_scale.pack(side="left", padx=5)
    
    def create_spectrum_display(self):
        """Создание отображения частотного спектра"""
        spectrum_frame = ttk.LabelFrame(self.root, text="📊 Частотный спектр", padding="10")
        spectrum_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Canvas для визуализации спектра
        self.spectrum_canvas = tk.Canvas(spectrum_frame, width=400, height=300, 
                                        bg="black", highlightthickness=0)
        self.spectrum_canvas.pack(fill="both", expand=True)
        
        # Отрисовка шкалы частот
        self.draw_frequency_scale()
    
    def create_video_display(self):
        """Создание области отображения видео"""
        video_frame = ttk.LabelFrame(self.root, text="📺 Видео выход", padding="10")
        video_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)
        
        # Метка отображения видео
        self.video_label = ttk.Label(video_frame, text="Нет видеосигнала", 
                                    background="black", foreground="white")
        self.video_label.pack(fill="both", expand=True)
    
    def create_status_bar(self):
        """Создание строки состояния"""
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Готов к работе")
        self.status_label.pack(side="left")
        
        # Счетчик сигналов
        self.signal_count_label = ttk.Label(status_frame, text="Сигналов: 0")
        self.signal_count_label.pack(side="right")
    
    def draw_frequency_scale(self):
        """Отрисовка шкалы частот на canvas спектра"""
        canvas = self.spectrum_canvas
        canvas.delete("all")
        
        # Заголовок
        canvas.create_text(200, 20, text="5.8 ГГц FPV Частотный спектр", 
                          fill="white", font=("Arial", 12, "bold"))
        
        # Маркеры частот
        x_start = 50
        x_end = 350
        y_base = 250
        
        for i, (channel, freq) in enumerate(self.channels.items()):
            x = x_start + (i * (x_end - x_start) / (len(self.channels) - 1))
            
            # Метка частоты
            canvas.create_text(x, y_base + 20, text=f"{freq}", 
                              fill="white", font=("Arial", 8))
            canvas.create_text(x, y_base + 35, text=channel, 
                              fill="yellow", font=("Arial", 10, "bold"))
            
            # Полоса силы сигнала
            if channel in self.detected_signals:
                signal = self.detected_signals[channel]
                strength = signal['strength']
                bar_height = int((strength / 100) * 150)
                
                # Цвет в зависимости от силы
                if strength > 80:
                    color = "red"
                elif strength > 60:
                    color = "orange"
                elif strength > 40:
                    color = "yellow"
                else:
                    color = "green"
                
                canvas.create_rectangle(x-10, y_base - bar_height, x+10, y_base, 
                                      fill=color, outline="white")
                
                # Значение RSSI
                canvas.create_text(x, y_base - bar_height - 10, 
                                  text=f"{signal['rssi']}", 
                                  fill="white", font=("Arial", 8))
    
    def update_display(self):
        """Обновление отображения с текущими данными сигнала"""
        self.draw_frequency_scale()
        
        # Обновление счетчика сигналов
        signal_count = len(self.detected_signals)
        self.signal_count_label.config(text=f"Сигналов: {signal_count}")
        
        # Планирование следующего обновления
        if self.scanning:
            self.root.after(100, self.update_display)
    
    def toggle_scanning(self):
        """Переключение сканирования вкл/выкл"""
        if not self.scanning:
            self.scanning = True
            self.scan_button.config(text="⏹️ Остановить сканирование")
            self.status_label.config(text="Сканирование...")
            
            # Запуск потока сканирования
            scan_thread = threading.Thread(target=self.scan_channels)
            scan_thread.daemon = True
            scan_thread.start()
        else:
            self.scanning = False
            self.scan_button.config(text="▶️ Начать сканирование")
            self.status_label.config(text="Сканирование остановлено")
    
    def stop_video_capture(self):
        """Остановка захвата видео"""
        self.video_capturing = False
        self.video_label.config(text="Нет видеосигнала")
        self.status_label.config(text="Захват видео остановлен")
    
    def on_channel_select(self, event):
        """Обработка выбора канала"""
        channel = self.channel_var.get()
        if channel in self.channels:
            freq = self.channels[channel]
            self.set_frequency(freq)
            self.status_label.config(text=f"Настроен на канал {channel} ({freq} МГц)")
    
    def run(self):
        """Запуск приложения"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Завершение работы...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.scanning = False
        self.video_capturing = False
        
        try:
            GPIO.cleanup()
            if hasattr(self, 'spi'):
                self.spi.close()
        except:
            pass

if __name__ == "__main__":
    scanner = SimpleFPVScanner()
    scanner.run()
