# 📦 Installation Guide - Raspberry Pi RX5808 Scanner

## 🎯 Quick Start

### **Prerequisites**
- Raspberry Pi 4 Model B (4GB RAM recommended)
- MicroSD card (32GB+ recommended)
- Power supply (5V, 3A minimum)
- Internet connection

### **Hardware Components**
- RX5808 5.8GHz Receiver Module
- USB Video DVR
- 5.8GHz Antenna (circular polarized)
- Breadboard and jumper wires
- Optional: ADC module for better RSSI reading

## 🔧 Step-by-Step Installation

### **Step 1: Prepare Raspberry Pi**

#### **1.1 Install Raspberry Pi OS**
```bash
# Download Raspberry Pi Imager
# https://www.raspberrypi.org/software/

# Flash Raspberry Pi OS Lite (recommended) or Desktop
# Enable SSH and set hostname during setup
```

#### **1.2 Initial Setup**
```bash
# Connect to Raspberry Pi via SSH or terminal
ssh pi@raspberrypi.local

# Update system
sudo apt update && sudo apt upgrade -y

# Set timezone and locale
sudo raspi-config
# Navigate to: Localisation Options > Change Timezone
# Navigate to: Localisation Options > Change Locale
```

### **Step 2: Enable Required Interfaces**

#### **2.1 Enable SPI**
```bash
# Open config file
sudo nano /boot/config.txt

# Add these lines at the end:
dtparam=spi=on
dtoverlay=spi0-2cs

# Save and exit (Ctrl+X, Y, Enter)
sudo reboot
```

#### **2.2 Enable I2C (if using ADC)**
```bash
sudo raspi-config
# Navigate to: Interface Options > I2C > Enable
```

### **Step 3: Install System Dependencies**

#### **3.1 Install Python and Development Tools**
```bash
# Install Python 3 and pip
sudo apt install python3 python3-pip python3-dev -y

# Install development tools
sudo apt install build-essential cmake pkg-config -y
```

#### **3.2 Install OpenCV and Image Processing**
```bash
# Install OpenCV dependencies
sudo apt install libjpeg-dev libtiff5-dev libjasper-dev libpng-dev -y
sudo apt install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev -y
sudo apt install libxvidcore-dev libx264-dev -y
sudo apt install libgtk-3-dev -y
sudo apt install libatlas-base-dev gfortran -y

# Install OpenCV
sudo apt install python3-opencv -y

# Install PIL/Pillow
sudo apt install python3-pil python3-pil.imagetk -y
```

#### **3.3 Install GPIO and SPI Libraries**
```bash
# Install RPi.GPIO
sudo apt install python3-rpi.gpio -y

# Install spidev
sudo apt install python3-spidev -y

# Install additional Python packages
pip3 install numpy pillow
```

### **Step 4: Clone and Setup Project**

#### **4.1 Clone Repository**
```bash
# Navigate to home directory
cd ~

# Clone project (replace with actual repository URL)
git clone <repository-url> RPISKAN
cd RPISKAN

# Make scripts executable
chmod +x src/*.py
chmod +x examples/*.py
```

#### **4.2 Create Log Directory**
```bash
# Create log directory
sudo mkdir -p /var/log
sudo touch /var/log/rpi_scanner.log
sudo chown pi:pi /var/log/rpi_scanner.log
```

### **Step 5: Hardware Assembly**

#### **5.1 Connect RX5808 Module**
```
RX5808 Module          Raspberry Pi 4
─────────────────      ──────────────────
VCC (3.3V)      ────── 3.3V (Pin 1)
GND             ────── GND (Pin 6)
CS (Chip Select)────── GPIO 8 (Pin 24)
MOSI            ────── GPIO 10 (Pin 19)
MISO            ────── GPIO 9 (Pin 21)
SCK             ────── GPIO 11 (Pin 23)
RSSI            ────── GPIO 7 (Pin 26)
```

#### **5.2 Connect USB Video DVR**
```bash
# Insert USB Video DVR into any USB port
# Connect RX5808 video output to DVR video input
# Connect RX5808 audio output to DVR audio input (optional)
```

#### **5.3 Connect Antenna**
```bash
# Connect 5.8GHz antenna to RX5808 antenna port
# Use appropriate connector (SMA/RP-SMA)
```

### **Step 6: Test Hardware**

#### **6.1 Run Hardware Test**
```bash
# Navigate to project directory
cd ~/RPISKAN

# Run hardware test
python3 examples/test_hardware.py
```

#### **6.2 Verify Test Results**
```
Expected output:
✅ GPIO Setup
✅ SPI Communication  
✅ RX5808 Communication
✅ RSSI Reading
✅ Video Device
✅ System Resources

Overall: 6/6 tests passed
🎉 All tests passed! Hardware is ready for scanning.
```

### **Step 7: Configure Scanner**

#### **7.1 Edit Configuration**
```bash
# Open configuration file
nano config/scanner_config.json

# Modify settings as needed:
# - GPIO pin assignments
# - Video device path
# - Frequency channels
# - RSSI thresholds
```

#### **7.2 Test Configuration**
```bash
# Test basic scanner
python3 src/rpi_scanner.py

# Test advanced scanner
python3 src/advanced_scanner.py
```

## 🚀 Running the Scanner

### **Basic Operation**
```bash
# Start basic scanner
python3 src/rpi_scanner.py

# Start advanced scanner with configuration
python3 src/advanced_scanner.py
```

### **GUI Controls**
- **Start/Stop Scanning**: Toggle frequency scanning
- **Channel Selection**: Manual channel tuning
- **RSSI Threshold**: Adjust signal detection sensitivity
- **Auto Video**: Enable/disable automatic video capture
- **Signal List**: View detected signals with details

### **Command Line Options**
```bash
# Run with specific configuration
python3 src/advanced_scanner.py --config custom_config.json

# Run in headless mode (future feature)
python3 src/advanced_scanner.py --headless

# Run with debug logging
python3 src/advanced_scanner.py --debug
```

## 🔧 Advanced Configuration

### **Performance Tuning**

#### **Overclock Raspberry Pi**
```bash
# Edit config file
sudo nano /boot/config.txt

# Add overclock settings
over_voltage=2
arm_freq=1750
gpu_freq=600

# Reboot
sudo reboot
```

#### **Optimize Video Settings**
```json
{
    "hardware": {
        "video": {
            "width": 640,
            "height": 480,
            "fps": 30,
            "codec": "MJPG"
        }
    }
}
```

### **Network Configuration**

#### **Enable SSH**
```bash
# Enable SSH
sudo systemctl enable ssh
sudo systemctl start ssh
```

#### **Configure WiFi (if needed)**
```bash
# Edit WiFi configuration
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf

# Add network configuration
network={
    ssid="YourWiFiName"
    psk="YourWiFiPassword"
}
```

## 🔍 Troubleshooting

### **Common Issues**

#### **1. SPI Not Working**
```bash
# Check SPI status
ls /dev/spi*

# If empty, check config
cat /boot/config.txt | grep spi

# Reboot if needed
sudo reboot
```

#### **2. Video Device Not Found**
```bash
# Check USB devices
lsusb

# Check video devices
ls /dev/video*

# Check device permissions
ls -la /dev/video*
```

#### **3. GPIO Permission Errors**
```bash
# Add user to gpio group
sudo usermod -a -G gpio pi

# Logout and login again
logout
# Reconnect via SSH
```

#### **4. High CPU Usage**
```bash
# Monitor system resources
htop

# Check running processes
ps aux | grep python

# Optimize video settings in config
```

### **Debug Commands**
```bash
# Check system information
cat /proc/cpuinfo
cat /proc/meminfo

# Check GPIO status
gpio readall

# Check SPI devices
ls /dev/spi*

# Check video devices
ls /dev/video*

# Monitor system resources
htop

# Check logs
tail -f /var/log/rpi_scanner.log
```

## 📊 Performance Monitoring

### **System Monitoring**
```bash
# Install monitoring tools
sudo apt install htop iotop -y

# Monitor CPU and memory
htop

# Monitor disk I/O
iotop

# Monitor network
iftop
```

### **Log Analysis**
```bash
# View recent logs
tail -f /var/log/rpi_scanner.log

# Search for errors
grep ERROR /var/log/rpi_scanner.log

# Search for signal detections
grep "Signal detected" /var/log/rpi_scanner.log
```

## 🔒 Security Considerations

### **System Security**
```bash
# Change default password
passwd

# Update regularly
sudo apt update && sudo apt upgrade

# Configure firewall (optional)
sudo ufw enable
sudo ufw allow ssh
```

### **Data Protection**
```bash
# Secure log files
sudo chmod 640 /var/log/rpi_scanner.log
sudo chown root:adm /var/log/rpi_scanner.log

# Regular log rotation
sudo nano /etc/logrotate.d/rpi_scanner
```

## 📈 Optimization Tips

### **Performance Optimization**
1. **Use SSD** instead of SD card for logging
2. **Overclock Raspberry Pi** for better performance
3. **Optimize video settings** for your use case
4. **Adjust scan intervals** based on requirements
5. **Use efficient video codecs** (MJPG)

### **Memory Management**
1. **Limit signal history** to prevent memory overflow
2. **Use video buffering** for smooth display
3. **Implement garbage collection** for long-running sessions
4. **Monitor memory usage** with htop

### **Power Management**
1. **Use adequate power supply** (5V, 3A minimum)
2. **Monitor temperature** during operation
3. **Add heat sinks** if running continuously
4. **Consider UPS** for critical applications

---

**🎉 Installation Complete!**

Your Raspberry Pi RX5808 Scanner is now ready to scan the skies and capture FPV video feeds. 

**Next Steps:**
1. Run hardware test: `python3 examples/test_hardware.py`
2. Start scanner: `python3 src/advanced_scanner.py`
3. Configure settings in `config/scanner_config.json`
4. Monitor logs: `tail -f /var/log/rpi_scanner.log`

**Happy Scanning! 🚁📡** 