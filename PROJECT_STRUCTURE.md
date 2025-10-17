# 📁 Project Structure - Raspberry Pi RX5808 Scanner

## 🎯 Overview

This document describes the complete structure of the Raspberry Pi RX5808 5.8GHz Scanner project, including all files, their purposes, and relationships.

## 📂 Directory Structure

```
RPISKAN/
├── src/                          # Source code files
│   ├── rpi_scanner.py           # Basic scanner implementation
│   └── advanced_scanner.py      # Advanced scanner with configuration
├── config/                       # Configuration files
│   └── scanner_config.json      # Main configuration file
├── docs/                         # Documentation
│   └── RPI_WIRING.md           # Hardware wiring diagrams
├── examples/                     # Example scripts and tests
│   └── test_hardware.py         # Hardware testing script
├── README.md                     # Main project documentation
├── INSTALLATION.md              # Installation guide
└── PROJECT_STRUCTURE.md         # This file
```

## 📄 File Descriptions

### **Source Code (`src/`)**

#### **`rpi_scanner.py`**
- **Purpose**: Basic scanner implementation
- **Features**:
  - Simple GUI with Tkinter
  - Real-time frequency scanning
  - Basic signal detection
  - Video capture from USB DVR
  - RSSI monitoring
- **Dependencies**: RPi.GPIO, spidev, OpenCV, PIL
- **Usage**: `python3 src/rpi_scanner.py`

#### **`advanced_scanner.py`**
- **Purpose**: Advanced scanner with full configuration support
- **Features**:
  - JSON configuration loading
  - Advanced GUI with menus
  - Signal history logging
  - Performance optimization
  - Multi-threading support
  - Comprehensive error handling
- **Dependencies**: All basic dependencies + json, logging, queue
- **Usage**: `python3 src/advanced_scanner.py`

### **Configuration (`config/`)**

#### **`scanner_config.json`**
- **Purpose**: Main configuration file
- **Sections**:
  - **hardware**: GPIO pins, SPI settings, video configuration
  - **frequencies**: Channel definitions and frequency ranges
  - **scanner**: Scan intervals, thresholds, auto-capture settings
  - **display**: GUI settings, colors, window sizes
  - **logging**: Log file settings and rotation
  - **performance**: Threading, buffering, memory limits
- **Format**: JSON
- **Usage**: Automatically loaded by advanced scanner

### **Documentation (`docs/`)**

#### **`RPI_WIRING.md`**
- **Purpose**: Complete hardware wiring guide
- **Contents**:
  - Pin connection diagrams
  - Hardware requirements
  - Alternative connection methods
  - Testing procedures
  - Troubleshooting guide
- **Format**: Markdown
- **Usage**: Reference for hardware assembly

### **Examples (`examples/`)**

#### **`test_hardware.py`**
- **Purpose**: Comprehensive hardware testing
- **Tests**:
  - GPIO setup and functionality
  - SPI communication
  - RX5808 module communication
  - RSSI reading accuracy
  - Video device detection
  - System resource verification
- **Usage**: `python3 examples/test_hardware.py`
- **Output**: Pass/fail status for each component

### **Documentation Files**

#### **`README.md`**
- **Purpose**: Main project overview and quick start
- **Contents**:
  - Project description and features
  - Hardware requirements
  - Quick installation guide
  - Basic usage instructions
  - Troubleshooting tips
- **Format**: Markdown
- **Usage**: First point of reference for users

#### **`INSTALLATION.md`**
- **Purpose**: Detailed installation and setup guide
- **Contents**:
  - Step-by-step installation process
  - System requirements and dependencies
  - Hardware assembly instructions
  - Configuration options
  - Performance optimization tips
- **Format**: Markdown
- **Usage**: Complete setup reference

#### **`PROJECT_STRUCTURE.md`**
- **Purpose**: This file - project structure documentation
- **Contents**:
  - File and directory descriptions
  - Dependencies and relationships
  - Usage instructions for each component
- **Format**: Markdown
- **Usage**: Developer reference

## 🔗 Dependencies and Relationships

### **Core Dependencies**
```
Python 3.7+           # Base runtime
RPi.GPIO              # GPIO control
spidev                # SPI communication
OpenCV (cv2)          # Video processing
PIL/Pillow            # Image processing
tkinter               # GUI framework
```

### **Optional Dependencies**
```
numpy                 # Numerical operations
json                  # Configuration parsing
logging               # Log management
queue                 # Thread communication
threading             # Multi-threading
subprocess            # System commands
```

### **File Relationships**
```
advanced_scanner.py
├── scanner_config.json (loads configuration)
├── test_hardware.py (validates hardware)
└── RPI_WIRING.md (hardware reference)

rpi_scanner.py
├── RPI_WIRING.md (hardware reference)
└── test_hardware.py (hardware validation)

test_hardware.py
└── RPI_WIRING.md (connection reference)
```

## 🚀 Usage Workflow

### **1. Initial Setup**
```bash
# Clone project
git clone <repository> RPISKAN
cd RPISKAN

# Follow installation guide
# Reference: INSTALLATION.md
```

### **2. Hardware Assembly**
```bash
# Follow wiring guide
# Reference: docs/RPI_WIRING.md

# Test hardware
python3 examples/test_hardware.py
```

### **3. Configuration**
```bash
# Edit configuration
nano config/scanner_config.json

# Test basic scanner
python3 src/rpi_scanner.py
```

### **4. Advanced Usage**
```bash
# Run advanced scanner
python3 src/advanced_scanner.py

# Monitor logs
tail -f /var/log/rpi_scanner.log
```

## 🔧 Development Workflow

### **Adding New Features**
1. **Create feature branch**
2. **Modify source files** in `src/`
3. **Update configuration** in `config/` if needed
4. **Add tests** in `examples/`
5. **Update documentation** in `docs/`
6. **Test thoroughly** on actual hardware

### **Configuration Changes**
1. **Edit** `config/scanner_config.json`
2. **Test** with `examples/test_hardware.py`
3. **Validate** with both scanner versions
4. **Update** documentation if needed

### **Hardware Modifications**
1. **Update** `docs/RPI_WIRING.md`
2. **Modify** pin assignments in config
3. **Test** with hardware test script
4. **Update** source code if needed

## 📊 File Statistics

### **Lines of Code**
- **`rpi_scanner.py`**: ~300 lines
- **`advanced_scanner.py`**: ~500 lines
- **`test_hardware.py`**: ~200 lines
- **Configuration**: ~100 lines
- **Documentation**: ~1000 lines

### **File Types**
- **Python**: 3 files
- **JSON**: 1 file
- **Markdown**: 4 files

### **Total Project Size**
- **Source Code**: ~1000 lines
- **Documentation**: ~1000 lines
- **Configuration**: ~100 lines
- **Total**: ~2100 lines

## 🎯 Key Features by File

### **Core Functionality**
- **Frequency Scanning**: `rpi_scanner.py`, `advanced_scanner.py`
- **Signal Detection**: `rpi_scanner.py`, `advanced_scanner.py`
- **Video Capture**: `rpi_scanner.py`, `advanced_scanner.py`
- **Hardware Control**: All Python files

### **User Interface**
- **Basic GUI**: `rpi_scanner.py`
- **Advanced GUI**: `advanced_scanner.py`
- **Configuration**: `scanner_config.json`
- **Hardware Testing**: `test_hardware.py`

### **Documentation**
- **Quick Start**: `README.md`
- **Installation**: `INSTALLATION.md`
- **Hardware Setup**: `docs/RPI_WIRING.md`
- **Project Structure**: `PROJECT_STRUCTURE.md`

## 🔍 Maintenance

### **Regular Tasks**
1. **Update dependencies** when new versions available
2. **Test hardware compatibility** with new components
3. **Review and update documentation** as needed
4. **Monitor log files** for issues
5. **Backup configuration** files

### **Version Control**
- **Source code**: Version controlled
- **Configuration**: Template version controlled
- **Documentation**: Version controlled
- **Logs**: Not version controlled (runtime data)

### **Backup Strategy**
- **Configuration**: Backup `config/` directory
- **Logs**: Rotate and archive log files
- **Custom scripts**: Version control in separate repository

---

**📁 This structure provides a complete, well-organized Raspberry Pi RX5808 Scanner project with comprehensive documentation and testing capabilities.** 