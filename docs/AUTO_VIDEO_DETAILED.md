# 📺 Auto Video Functionality - Detailed Analysis

## 📋 Overview

Auto Video - это автоматическая система захвата видео, которая запускает видеозахват при обнаружении сильных сигналов. Система работает в реальном времени и автоматически переключается между каналами для получения лучшего качества видео.

## 🔧 Как работает Auto Video

### **1. Конфигурация Auto Video**

#### **В файле конфигурации:**
```json
// config/scanner_config.json
{
    "scanner": {
        "auto_video_capture": true,        // Включить/выключить Auto Video
        "strong_signal_threshold": 100,    // Порог RSSI для запуска видео
        "rssi_threshold": 50              // Минимальный порог для обнаружения сигнала
    }
}
```

#### **В коде сканера:**
```python
# src/advanced_scanner.py - строки 85-90
def setup_hardware_config(self):
    # ...
    self.auto_video_capture = scanner_config.get("auto_video_capture", True)
    self.strong_signal_threshold = scanner_config["strong_signal_threshold"]
    self.rssi_threshold = scanner_config["rssi_threshold"]
```

### **2. Логика обнаружения сильных сигналов**

#### **Основной цикл сканирования:**
```python
# src/advanced_scanner.py - строки 190-220
def scan_channels(self):
    while self.scanning:
        for channel, freq in self.channels.items():
            # Установка частоты
            self.set_frequency(freq)
            time.sleep(self.settling_time)
            
            # Чтение RSSI
            rssi = self.read_rssi()
            
            # Обновление обнаруженных сигналов
            if rssi > self.rssi_threshold:
                signal_info = {
                    'frequency': freq,
                    'rssi': rssi,
                    'strength': min(100, int(rssi * 100 / 255)),
                    'timestamp': time.time(),
                    'channel': channel
                }
                
                self.detected_signals[channel] = signal_info
                
                # 🔥 КЛЮЧЕВАЯ ЛОГИКА AUTO VIDEO
                if (rssi > self.strong_signal_threshold and 
                    self.auto_video_capture and 
                    not self.video_capturing):
                    self.start_video_capture(channel, freq)
```

### **3. Условия запуска Auto Video**

Auto Video запускается только при выполнении **ВСЕХ** условий:

1. **RSSI > strong_signal_threshold** (по умолчанию 100)
2. **auto_video_capture = True** (включено в настройках)
3. **not self.video_capturing** (видео еще не захватывается)

### **4. Процесс запуска видеозахвата**

#### **Функция start_video_capture:**
```python
# src/advanced_scanner.py - строки 240-260
def start_video_capture(self, channel, frequency):
    try:
        self.video_capturing = True
        self.current_channel = channel
        
        # Обновление статуса
        self.status_label.config(text=f"Capturing video from {channel} ({frequency} MHz)")
        
        # Запуск потока видеозахвата
        video_thread = threading.Thread(target=self.capture_video)
        video_thread.daemon = True
        video_thread.start()
        
        self.logger.info(f"Started video capture from {channel} ({frequency} MHz)")
        
    except Exception as e:
        self.logger.error(f"Video capture start error: {e}")
```

### **5. Процесс захвата видео**

#### **Функция capture_video:**
```python
# src/advanced_scanner.py - строки 262-300
def capture_video(self):
    try:
        # Инициализация видеозахвата
        self.video_cap = cv2.VideoCapture(self.video_device)
        self.video_cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_width)
        self.video_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_height)
        self.video_cap.set(cv2.CAP_PROP_FPS, self.video_fps)
        
        if not self.video_cap.isOpened():
            self.logger.error("Failed to open video device")
            return
        
        # Основной цикл видеозахвата
        while self.video_capturing:
            ret, frame = self.video_cap.read()
            if ret:
                # Добавление временной метки и информации о канале
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(frame, f"{timestamp} - Channel {self.current_channel}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Конвертация кадра для Tkinter
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_pil = Image.fromarray(frame_rgb)
                frame_tk = ImageTk.PhotoImage(frame_pil)
                
                # Обновление дисплея
                self.video_label.config(image=frame_tk)
                self.video_label.image = frame_tk
            
            time.sleep(1.0 / self.video_fps)
        
    except Exception as e:
        self.logger.error(f"Video capture error: {e}")
    finally:
        if self.video_cap:
            self.video_cap.release()
        self.video_capturing = False
```

## 🎮 Пользовательский интерфейс

### **1. Чекбокс Auto Video**

#### **Создание элемента управления:**
```python
# src/advanced_scanner.py - строки 350-370
def create_control_panel(self):
    # ...
    # Auto video capture checkbox
    self.auto_video_var = tk.BooleanVar(value=self.auto_video_capture)
    auto_video_check = ttk.Checkbutton(control_frame, text="Auto Video", 
                                      variable=self.auto_video_var)
    auto_video_check.pack(side="left", padx=5)
```

#### **Обработка изменений:**
```python
# Пользователь может включить/выключить Auto Video в реальном времени
# Изменения применяются немедленно при следующем сканировании
```

### **2. Кнопка остановки видео**

#### **Создание кнопки:**
```python
# src/advanced_scanner.py - строки 350-370
def create_control_panel(self):
    # ...
    # Video capture button
    self.video_button = ttk.Button(control_frame, text="Stop Video", 
                                  command=self.stop_video_capture)
    self.video_button.pack(side="left", padx=5)
```

#### **Функция остановки:**
```python
# src/advanced_scanner.py - строки 620-625
def stop_video_capture(self):
    """Stop video capture"""
    self.video_capturing = False
    self.video_label.config(text="No video signal")
    self.status_label.config(text="Video capture stopped")
```

## 🎯 Mockup версия Auto Video

### **1. Симуляция в макете интерфейса**

#### **Генерация тестовых сигналов:**
```python
# examples/interface_mockup.py - строки 460-480
def start_mock_data(self):
    def generate_mock_signals():
        while True:
            if self.scanning:
                active_channels = self.scan_modes[self.current_scan_mode]['channels']
                
                for channel in active_channels:
                    if random.random() < 0.2:  # 20% шанс сигнала
                        rssi = random.randint(30, 180)
                        strength = min(100, int(rssi * 100 / 255))
                        
                        self.detected_signals[channel] = {
                            'frequency': self.channels[channel],
                            'rssi': rssi,
                            'strength': strength,
                            'timestamp': time.time()
                        }
                        
                        # 🔥 AUTO VIDEO ЛОГИКА В MOCKUP
                        if rssi > 100 and self.auto_video_var.get() and not self.video_capturing:
                            self.start_mock_video(channel)
```

### **2. Mockup видеозахват**

#### **Функция start_mock_video:**
```python
# examples/interface_mockup.py - строки 510-515
def start_mock_video(self, channel):
    """Start mock video capture"""
    self.video_capturing = True
    self.current_channel = channel
    self.video_status.config(text=f"Capturing video from {channel}")
    self.status_label.config(text=f"Video capture started - Channel {channel}")
```

## 🔄 Многопоточность

### **1. Основной поток сканирования**
- **Функция**: `scan_channels()`
- **Задача**: Сканирование частот и обнаружение сигналов
- **Приоритет**: Высокий

### **2. Поток видеозахвата**
- **Функция**: `capture_video()`
- **Задача**: Захват и отображение видео
- **Приоритет**: Средний
- **Daemon**: True (завершается при остановке программы)

### **3. Поток GUI**
- **Функция**: `mainloop()`
- **Задача**: Обновление интерфейса
- **Приоритет**: Низкий

## 📊 Настройки производительности

### **1. Конфигурация видео**
```json
// config/scanner_config.json
{
    "hardware": {
        "video": {
            "device": "/dev/video0",
            "width": 640,
            "height": 480,
            "fps": 30,
            "codec": "MJPG"
        }
    }
}
```

### **2. Оптимизация сканирования**
```json
// config/scanner_config.json
{
    "performance": {
        "scan_optimization": {
            "skip_weak_signals": true,
            "focus_on_strong_signals": true,
            "adaptive_scan_interval": true
        }
    }
}
```

## 🚨 Обработка ошибок

### **1. Ошибки видеозахвата**
```python
# src/advanced_scanner.py - строки 262-300
try:
    # Инициализация видеозахвата
    self.video_cap = cv2.VideoCapture(self.video_device)
    if not self.video_cap.isOpened():
        self.logger.error("Failed to open video device")
        return
except Exception as e:
    self.logger.error(f"Video capture error: {e}")
finally:
    if self.video_cap:
        self.video_cap.release()
    self.video_capturing = False
```

### **2. Логирование событий**
```python
# Логирование запуска Auto Video
self.logger.info(f"Started video capture from {channel} ({frequency} MHz)")

# Логирование ошибок
self.logger.error(f"Video capture start error: {e}")
self.logger.error(f"Video capture error: {e}")
```

## 🎯 Алгоритм работы Auto Video

### **Пошаговый алгоритм:**

1. **Сканирование каналов**
   - Установка частоты на RX5808
   - Чтение RSSI значения
   - Проверка порога обнаружения

2. **Оценка сигнала**
   - RSSI > rssi_threshold (50) → Сигнал обнаружен
   - RSSI > strong_signal_threshold (100) → Сильный сигнал

3. **Проверка условий Auto Video**
   - auto_video_capture = True
   - not self.video_capturing
   - RSSI > strong_signal_threshold

4. **Запуск видеозахвата**
   - Установка флага video_capturing = True
   - Создание потока capture_video()
   - Обновление статуса GUI

5. **Захват видео**
   - Инициализация OpenCV VideoCapture
   - Чтение кадров в цикле
   - Добавление временных меток
   - Отображение в GUI

6. **Остановка видео**
   - Установка video_capturing = False
   - Освобождение ресурсов
   - Обновление статуса

## 🔧 Настройка порогов

### **Рекомендуемые значения:**

| **Настройка** | **Значение** | **Описание** |
|---------------|--------------|--------------|
| `rssi_threshold` | 30-50 | Минимальный RSSI для обнаружения |
| `strong_signal_threshold` | 80-120 | RSSI для запуска Auto Video |
| `auto_video_capture` | true/false | Включение/выключение функции |

### **Настройка для разных условий:**

#### **Чувствительный режим:**
```json
{
    "rssi_threshold": 30,
    "strong_signal_threshold": 60,
    "auto_video_capture": true
}
```

#### **Стабильный режим:**
```json
{
    "rssi_threshold": 50,
    "strong_signal_threshold": 100,
    "auto_video_capture": true
}
```

#### **Только сильные сигналы:**
```json
{
    "rssi_threshold": 70,
    "strong_signal_threshold": 120,
    "auto_video_capture": true
}
```

---

**🎯 Auto Video обеспечивает автоматический захват видео при обнаружении сильных FPV сигналов, работая в реальном времени с минимальной задержкой.** 