# 🚁 Raspberry Pi 4 RX5808 5.8GHz Scanner

## 📋 Overview

Advanced frequency scanner for Raspberry Pi 4 with RX5808 5.8GHz receiver module. This project provides real-time frequency scanning, signal detection, and video capture capabilities for FPV drone monitoring.

## ✨ Features

### **🎯 Core Functionality**
- **Real-time frequency scanning** across 8 FPV channels (A-H)
- **Signal strength visualization** with color-coded spectrum display
- **Automatic video capture** when strong signals are detected
- **USB Video DVR integration** for live video display
- **Configurable RSSI thresholds** for signal detection
- **Signal history logging** and export capabilities

### **🖥️ User Interface**
- **Modern GUI** built with Tkinter
- **Real-time spectrum analyzer** with frequency visualization
- **Live video display** with timestamp overlay
- **Signal detection list** with detailed information
- **Control panel** for manual channel selection
- **Status monitoring** and system information

### **⚙️ Advanced Features**
- **JSON configuration** for easy customization
- **Logging system** with file rotation
- **Multi-threading** for smooth operation
- **Hardware abstraction** for easy portability
- **Performance optimization** with configurable parameters

## 🛠️ Hardware Requirements

### **Essential Components**
- **Raspberry Pi 4 Model B** (4GB RAM recommended)
- **RX5808 5.8GHz Receiver Module**
- **USB Video DVR** (for video capture)
- **5.8GHz Antenna** (circular polarized recommended)
- **Breadboard** and jumper wires
- **Power supply** (5V, 3A minimum)

### **Optional Components**
- **ADC Module** (MCP3008) for better RSSI reading
- **Video amplifier** for signal boosting
- **Heat sink** for RX5808 module
- **Case/enclosure** for protection

## 🔌 Pin Connections

### **RX5808 Pinout (Actual):**
```
RX5808 Module Pinout:
┌─────────────────────────────────────┐
│ GND  ANT  GND                       │
│ GND  VIDEO  A  6.5M  RSSI  +5V  GND │
│ CH3  CH2   CH1                      │
└─────────────────────────────────────┘
```

### **RX5808 to Raspberry Pi 4:**
```
RX5808 Pin           Function          Raspberry Pi 4
─────────────────    ──────────        ──────────────────
GND                  Ground            GND (Pin 6)
+5V                  Power             5V (Pin 2) or 3.3V (Pin 1)
RSSI                 Signal Strength   GPIO 7 (Pin 26)
VIDEO                Video Output      USB Video DVR Input
A                    SPI MOSI          GPIO 10 (Pin 19)
6.5M                 SPI MISO          GPIO 9 (Pin 21)
CH1                  SPI SCK           GPIO 11 (Pin 23)
CH2                  SPI CS            GPIO 8 (Pin 24)
CH3                  Not Used          -
ANT                  Antenna           Antenna Connector
```

### **USB Video DVR:**
```
USB Video DVR          Raspberry Pi 4
─────────────────      ──────────────────
USB Connector    ────── USB Port (any)
Video Input      ────── RX5808 VIDEO Pin
Audio Input      ────── (Not available on RX5808)
```

## 📦 Installation

### **1. System Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade

# Enable SPI
sudo nano /boot/config.txt
# Add: dtparam=spi=on
sudo reboot
```

### **2. Install Dependencies**
```bash
# Install Python packages
sudo apt install python3-pip python3-dev
sudo apt install python3-opencv python3-pil python3-pil.imagetk

# Install GPIO and SPI libraries
sudo apt install python3-rpi.gpio python3-spidev

# Install additional packages
pip3 install numpy pillow
```

### **3. Clone Project**
```bash
git clone <repository-url>
cd RPISKAN
chmod +x src/*.py
```

### **4. Configure Hardware**
- Connect RX5808 module according to pin diagram
- Connect USB Video DVR
- Connect 5.8GHz antenna
- Power up Raspberry Pi

## 🚀 Usage

### **Basic Operation**
```bash
# Run basic scanner
python3 src/rpi_scanner.py

# Run advanced scanner with configuration
python3 src/advanced_scanner.py
```

### **Configuration**
Edit `config/scanner_config.json` to customize:
- GPIO pin assignments
- Video settings
- Frequency channels
- Scanner parameters
- Display options

### **GUI Controls**
- **Start/Stop Scanning**: Toggle frequency scanning
- **Channel Selection**: Manual channel tuning
- **RSSI Threshold**: Adjust signal detection sensitivity
- **Auto Video**: Enable/disable automatic video capture
- **Signal List**: View detected signals with details

## 📊 Frequency Channels

### **5.8GHz FPV Channels:**
```
Channel    Frequency    Use
─────────────────────────────────
A          5865 MHz     FPV Racing
B          5845 MHz     FPV Freestyle
C          5825 MHz     FPV Long Range
D          5805 MHz     FPV Cinematic
E          5785 MHz     FPV Acro
F          5765 MHz     FPV Beginner
G          5745 MHz     FPV Pro
H          5725 MHz     FPV Competition
```

## 🔧 Configuration

### **Hardware Configuration**
```json
{
    "hardware": {
        "gpio": {
            "cs_pin": 8,
            "rssi_pin": 7,
            "spi_bus": 0,
            "spi_device": 0
        },
        "video": {
            "device": "/dev/video0",
            "width": 640,
            "height": 480,
            "fps": 30
        }
    }
}
```

### **Scanner Configuration**
```json
{
    "scanner": {
        "scan_interval": 0.5,
        "rssi_threshold": 50,
        "strong_signal_threshold": 100,
        "auto_video_capture": true
    }
}
```

## 📁 Project Structure

```
RPISKAN/
├── src/                    # Source code
│   ├── rpi_scanner.py     # Basic scanner
│   └── advanced_scanner.py # Advanced scanner with config
├── config/                 # Configuration files
│   └── scanner_config.json # Main configuration
├── docs/                   # Documentation
│   └── RPI_WIRING.md      # Wiring diagrams
├── examples/               # Example scripts
└── README.md              # This file
```

## 🎯 Use Cases

### **FPV Drone Monitoring**
- Monitor FPV drone frequencies
- Detect unauthorized drone activity
- Analyze signal strength and quality
- Capture video feeds for analysis

### **Frequency Analysis**
- Scan for active FPV channels
- Measure signal strength across bands
- Log frequency usage patterns
- Identify interference sources

### **Security Applications**
- Drone detection and monitoring
- Frequency surveillance
- Signal intelligence gathering
- Video evidence collection

## 🔍 Troubleshooting

### **Common Issues**

1. **SPI Communication Errors**
   - Check `/boot/config.txt` SPI settings
   - Verify pin connections (CH2=CS, A=MOSI, 6.5M=MISO, CH1=SCK)
   - Test with `ls /dev/spi*`

2. **Video Capture Issues**
   - Check USB Video DVR connection
   - Verify device permissions
   - Test with `lsusb` command

3. **Poor Signal Reception**
   - Check antenna connection to ANT pin
   - Verify antenna type and frequency
   - Test antenna positioning

4. **High CPU Usage**
   - Reduce video frame rate
   - Lower scan frequency
   - Optimize display update rate

### **Debug Commands**
```bash
# Check SPI devices
ls /dev/spi*

# Check USB devices
lsusb

# Check video devices
ls /dev/video*

# Monitor system resources
htop

# Check GPIO
gpio readall

# Test hardware
python3 examples/test_hardware.py
```

## 📈 Performance Optimization

### **System Tuning**
- **Overclock Raspberry Pi** for better performance
- **Use SSD** instead of SD card for logging
- **Optimize video settings** for your use case
- **Adjust scan intervals** based on requirements

### **Memory Management**
- **Limit signal history** to prevent memory overflow
- **Use video buffering** for smooth display
- **Implement garbage collection** for long-running sessions

## 🔒 Security Considerations

### **Legal Compliance**
- **Check local regulations** for frequency monitoring
- **Respect privacy** when capturing video
- **Follow drone detection laws** in your area
- **Obtain necessary permits** for frequency scanning

### **Data Protection**
- **Secure log files** with proper permissions
- **Encrypt sensitive data** if required
- **Implement access controls** for video feeds
- **Regular data cleanup** to prevent storage issues

## 🤝 Contributing

### **Development Setup**
1. Fork the repository
2. Create feature branch
3. Make changes with proper testing
4. Submit pull request

### **Testing Guidelines**
- Test on actual Raspberry Pi 4 hardware
- Verify GPIO connections
- Test video capture functionality
- Validate configuration options

## 📄 License

This project is licensed under the **MIT License**. See LICENSE file for details.

## 🙏 Acknowledgments

- **Raspberry Pi Foundation** for the amazing platform
- **OpenCV community** for video processing capabilities
- **FPV community** for frequency information
- **Open source contributors** for libraries and tools

## 📞 Support

### **Getting Help**
1. Check documentation in `docs/` folder
2. Review troubleshooting section
3. Search existing issues
4. Create new issue with detailed information

### **Community**
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Share experiences and tips
- **Wiki**: Community-maintained documentation

---

**🎯 Ready to scan the skies with your Raspberry Pi 4 RX5808 Scanner!**

**Key Pin Connections:**
- **CH2 (CS)**: GPIO 8 (Pin 24)
- **A (MOSI)**: GPIO 10 (Pin 19)
- **6.5M (MISO)**: GPIO 9 (Pin 21)
- **CH1 (SCK)**: GPIO 11 (Pin 23)
- **RSSI**: GPIO 7 (Pin 26)
- **VIDEO**: To USB Video DVR
- **ANT**: To antenna
- **+5V**: 5V or 3.3V power
- **GND**: Ground

**Next Steps:**
1. Follow installation guide
2. Connect hardware according to wiring diagram
3. Configure settings in `scanner_config.json`
4. Run the scanner and start monitoring!

**Happy Scanning! 🚁📡** 