# Makefile для FPV Scanner
# Компиляция C версии сканера для Raspberry Pi 4 + RX5808

CC = gcc
CFLAGS = -Wall -Wextra -O2 -std=c99
LDFLAGS = -lwiringPi -lwiringPiDev

# Исходные файлы
SOURCES_BASIC = src/fpv_scanner.c
SOURCES_ADVANCED = src/fpv_scanner_advanced.c
TARGET_BASIC = fpv_scanner
TARGET_ADVANCED = fpv_scanner_advanced
INSTALL_DIR = /usr/local/bin

# Цели по умолчанию
all: $(TARGET_BASIC) $(TARGET_ADVANCED)

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
install: $(TARGET_BASIC) $(TARGET_ADVANCED)
	@echo "📦 Установка FPV Scanner..."
	sudo cp $(TARGET_BASIC) $(INSTALL_DIR)/
	sudo cp $(TARGET_ADVANCED) $(INSTALL_DIR)/
	sudo chmod +x $(INSTALL_DIR)/$(TARGET_BASIC)
	sudo chmod +x $(INSTALL_DIR)/$(TARGET_ADVANCED)
	@echo "✅ Установка завершена"

# Удаление
uninstall:
	@echo "🗑️  Удаление FPV Scanner..."
	sudo rm -f $(INSTALL_DIR)/$(TARGET_BASIC)
	sudo rm -f $(INSTALL_DIR)/$(TARGET_ADVANCED)
	@echo "✅ Удаление завершено"

# Очистка
clean:
	@echo "🧹 Очистка..."
	rm -f $(TARGET_BASIC) $(TARGET_ADVANCED)
	@echo "✅ Очистка завершена"

# Запуск базового сканера
run: $(TARGET_BASIC)
	@echo "🚀 Запуск базового FPV Scanner..."
	sudo ./$(TARGET_BASIC)

# Запуск продвинутого сканера
run-advanced: $(TARGET_ADVANCED)
	@echo "🚀 Запуск продвинутого FPV Scanner..."
	sudo ./$(TARGET_ADVANCED)

# Тест базового сканера
test: $(TARGET_BASIC)
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
	@echo "  make              - Компиляция всех сканеров"
	@echo "  make install      - Установка в систему"
	@echo "  make run          - Запуск базового сканера"
	@echo "  make run-advanced - Запуск продвинутого сканера"
	@echo "  make test         - Тест базового сканера"
	@echo "  make test-advanced - Тест продвинутого сканера"
	@echo "  make clean        - Очистка"
	@echo "  make help         - Эта справка"
	@echo ""
	@echo "Требования:"
	@echo "  - wiringPi библиотека"
	@echo "  - SPI включен на Raspberry Pi"
	@echo "  - RX5808 подключен"

# Флаги для отладки
debug: CFLAGS += -g -DDEBUG
debug: $(TARGET)

# Флаги для оптимизации
optimize: CFLAGS += -O3 -march=native
optimize: $(TARGET)

.PHONY: all install uninstall clean run test help debug optimize
