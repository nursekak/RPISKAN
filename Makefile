# Makefile для FPV Scanner
# Компиляция C версии сканера для Raspberry Pi 4 + RX5808

CC = gcc
CFLAGS = -Wall -Wextra -O2 -std=c99
LDFLAGS = -lwiringPi -lwiringPiDev

# Исходные файлы
SOURCES_BASIC = src/fpv_scanner.c
SOURCES_ADVANCED = src/fpv_scanner_advanced.c
SOURCES_NATIVE = src/fpv_scanner_native.c
SOURCES_SIMPLE = src/fpv_scanner_simple.c
SOURCES_MINIMAL = src/fpv_scanner_minimal.c
SOURCES_1MHZ = src/fpv_scanner_1mhz.c
TARGET_BASIC = fpv_scanner
TARGET_ADVANCED = fpv_scanner_advanced
TARGET_NATIVE = fpv_scanner_native
TARGET_SIMPLE = fpv_scanner_simple
TARGET_MINIMAL = fpv_scanner_minimal
TARGET_1MHZ = fpv_scanner_1mhz
INSTALL_DIR = /usr/local/bin

# Цели по умолчанию
all: $(TARGET_1MHZ)

# Компиляция сканера с шагом 1 МГц (рекомендуется)
$(TARGET_1MHZ): $(SOURCES_1MHZ)
	@echo "🔨 Компиляция FPV Scanner с шагом 1 МГц..."
	$(CC) $(CFLAGS) -o $(TARGET_1MHZ) $(SOURCES_1MHZ)
	@echo "✅ Сканер с шагом 1 МГц скомпилирован: $(TARGET_1MHZ)"

# Компиляция минимального сканера
$(TARGET_MINIMAL): $(SOURCES_MINIMAL)
	@echo "🔨 Компиляция минимального FPV Scanner..."
	$(CC) $(CFLAGS) -o $(TARGET_MINIMAL) $(SOURCES_MINIMAL)
	@echo "✅ Минимальный сканер скомпилирован: $(TARGET_MINIMAL)"

# Компиляция простого сканера
$(TARGET_SIMPLE): $(SOURCES_SIMPLE)
	@echo "🔨 Компиляция простого FPV Scanner..."
	$(CC) $(CFLAGS) -o $(TARGET_SIMPLE) $(SOURCES_SIMPLE)
	@echo "✅ Простой сканер скомпилирован: $(TARGET_SIMPLE)"

# Компиляция нативного сканера (без WiringPi)
$(TARGET_NATIVE): $(SOURCES_NATIVE)
	@echo "🔨 Компиляция нативного FPV Scanner..."
	$(CC) $(CFLAGS) -o $(TARGET_NATIVE) $(SOURCES_NATIVE)
	@echo "✅ Нативный сканер скомпилирован: $(TARGET_NATIVE)"

# Компиляция базового сканера
$(TARGET_BASIC): $(SOURCES_BASIC)
	@echo "🔨 Компиляция базового FPV Scanner..."
	$(CC) $(CFLAGS) -o $(TARGET_BASIC) $(SOURCES_BASIC) $(LDFLAGS)
	@echo "✅ Базовый сканер скомпилирован: $(TARGET_BASIC)"

# Компиляция продвинутого сканера
$(TARGET_ADVANCED): $(SOURCES_ADVANCED)
	@echo "🔨 Компиляция продвинутого FPV Scanner..."
	$(CC) $(CFLAGS) -o $(TARGET_ADVANCED) $(SOURCES_ADVANCED) $(LDFLAGS) -lpthread
	@echo "✅ Продвинутый сканер скомпилирован: $(TARGET_ADVANCED)"

# Установка
install: $(TARGET_1MHZ)
	@echo "📦 Установка FPV Scanner..."
	sudo cp $(TARGET_1MHZ) $(INSTALL_DIR)/
	sudo chmod +x $(INSTALL_DIR)/$(TARGET_1MHZ)
	@echo "✅ Установка завершена"

# Удаление
uninstall:
	@echo "🗑️  Удаление FPV Scanner..."
	sudo rm -f $(INSTALL_DIR)/$(TARGET_1MHZ)
	@echo "✅ Удаление завершено"

# Очистка
clean:
	@echo "🧹 Очистка..."
	rm -f $(TARGET_BASIC) $(TARGET_ADVANCED) $(TARGET_NATIVE) $(TARGET_SIMPLE) $(TARGET_MINIMAL) $(TARGET_1MHZ)
	@echo "✅ Очистка завершена"

# Запуск сканера с шагом 1 МГц
run: $(TARGET_1MHZ)
	@echo "🚀 Запуск FPV Scanner с шагом 1 МГц..."
	sudo ./$(TARGET_1MHZ)

# Запуск минимального сканера
run-minimal: $(TARGET_MINIMAL)
	@echo "🚀 Запуск минимального FPV Scanner..."
	sudo ./$(TARGET_MINIMAL)

# Запуск простого сканера
run-simple: $(TARGET_SIMPLE)
	@echo "🚀 Запуск простого FPV Scanner..."
	sudo ./$(TARGET_SIMPLE)

# Запуск нативного сканера
run-native: $(TARGET_NATIVE)
	@echo "🚀 Запуск нативного FPV Scanner..."
	sudo ./$(TARGET_NATIVE)

# Запуск базового сканера
run-basic: $(TARGET_BASIC)
	@echo "🚀 Запуск базового FPV Scanner..."
	sudo ./$(TARGET_BASIC)

# Запуск продвинутого сканера
run-advanced: $(TARGET_ADVANCED)
	@echo "🚀 Запуск продвинутого FPV Scanner..."
	sudo ./$(TARGET_ADVANCED)

# Тест сканера с шагом 1 МГц
test: $(TARGET_1MHZ)
	@echo "🧪 Тестирование FPV Scanner с шагом 1 МГц..."
	sudo ./$(TARGET_1MHZ)

# Тест минимального сканера
test-minimal: $(TARGET_MINIMAL)
	@echo "🧪 Тестирование минимального FPV Scanner..."
	sudo ./$(TARGET_MINIMAL)

# Тест простого сканера
test-simple: $(TARGET_SIMPLE)
	@echo "🧪 Тестирование простого FPV Scanner..."
	sudo ./$(TARGET_SIMPLE)

# Тест нативного сканера
test-native: $(TARGET_NATIVE)
	@echo "🧪 Тестирование нативного FPV Scanner..."
	sudo ./$(TARGET_NATIVE)

# Тест базового сканера
test-basic: $(TARGET_BASIC)
	@echo "🧪 Тестирование базового FPV Scanner..."
	sudo ./$(TARGET_BASIC)

# Тест продвинутого сканера
test-advanced: $(TARGET_ADVANCED)
	@echo "🧪 Тестирование продвинутого FPV Scanner..."
	sudo ./$(TARGET_ADVANCED) -v

# Помощь
help:
	@echo "🚁 FPV Scanner - Makefile"
	@echo "========================="
	@echo "Доступные команды:"
	@echo "  make              - Компиляция сканера с шагом 1 МГц (рекомендуется)"
	@echo "  make install      - Установка в систему"
	@echo "  make run          - Запуск сканера с шагом 1 МГц"
	@echo "  make run-minimal  - Запуск минимального сканера"
	@echo "  make run-simple    - Запуск простого сканера"
	@echo "  make run-native    - Запуск нативного сканера"
	@echo "  make run-basic     - Запуск базового сканера (требует WiringPi)"
	@echo "  make run-advanced  - Запуск продвинутого сканера (требует WiringPi)"
	@echo "  make test          - Тест сканера с шагом 1 МГц"
	@echo "  make test-minimal  - Тест минимального сканера"
	@echo "  make test-simple   - Тест простого сканера"
	@echo "  make test-native   - Тест нативного сканера"
	@echo "  make test-basic    - Тест базового сканера"
	@echo "  make test-advanced - Тест продвинутого сканера"
	@echo "  make clean         - Очистка"
	@echo "  make help          - Эта справка"
	@echo ""
	@echo "Требования:"
	@echo "  - SPI включен на Raspberry Pi"
	@echo "  - RX5808 подключен"
	@echo "  - Нативный сканер не требует дополнительных библиотек"

# Флаги для отладки
debug: CFLAGS += -g -DDEBUG
debug: $(TARGET)

# Флаги для оптимизации
optimize: CFLAGS += -O3 -march=native
optimize: $(TARGET)

.PHONY: all install uninstall clean run test help debug optimize
