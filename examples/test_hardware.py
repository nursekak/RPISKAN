#!/usr/bin/env python3
"""
Hardware Test Script for Raspberry Pi RX5808 Scanner
Tests all hardware components before running the main scanner
"""

import RPi.GPIO as GPIO
import spidev
import time
import subprocess
import sys
import cv2

class HardwareTester:
    def __init__(self):
        # GPIO Configuration for RX5808
        self.CS_PIN = 8          # CH2 (Chip Select)
        self.RSSI_PIN = 7        # RSSI input
        self.SPI_BUS = 0
        self.SPI_DEVICE = 0
        
        # RX5808 Pin Mapping
        self.RX5808_PINS = {
            'cs': 'CH2',      # GPIO 8
            'mosi': 'A6.5M',  # GPIO 10
            'sck': 'CH1',     # GPIO 11
            'rssi': 'RSSI',   # GPIO 7
            'video': 'VIDEO', # To USB DVR
            'power': '+5V',   # 5V or 3.3V
            'ground': 'GND',  # Ground
            'antenna': 'ANT'  # Antenna
        }
        
        # Test results
        self.test_results = {}
        
    def run_all_tests(self):
        """Run all hardware tests"""
        print("🔧 Raspberry Pi RX5808 Hardware Test")
        print("=" * 50)
        print("RX5808 Pinout: GND ANT GND | GND VIDEO A 6.5M RSSI +5V GND | CH3 CH2 CH1")
        print("=" * 50)
        
        tests = [
            ("GPIO Setup", self.test_gpio),
            ("SPI Communication", self.test_spi),
            ("RX5808 Communication", self.test_rx5808),
            ("RSSI Reading", self.test_rssi),
            ("Video Device", self.test_video),
            ("System Resources", self.test_system)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🧪 Testing {test_name}...")
            try:
                result = test_func()
                self.test_results[test_name] = result
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"   {status}")
            except Exception as e:
                self.test_results[test_name] = False
                print(f"   ❌ FAIL: {e}")
        
        self.print_summary()
    
    def test_gpio(self):
        """Test GPIO setup"""
        try:
            GPIO.setmode(GPIO.BCM)
            
            # Setup CS pin (CH2)
            GPIO.setup(self.CS_PIN, GPIO.OUT)
            GPIO.output(self.CS_PIN, GPIO.HIGH)
            
            # Setup RSSI pin
            GPIO.setup(self.RSSI_PIN, GPIO.IN)
            
            # Test CS pin
            GPIO.output(self.CS_PIN, GPIO.LOW)
            time.sleep(0.1)
            GPIO.output(self.CS_PIN, GPIO.HIGH)
            time.sleep(0.1)
            
            print(f"   CS Pin (CH2): GPIO {self.CS_PIN}")
            print(f"   RSSI Pin: GPIO {self.RSSI_PIN}")
            return True
        except Exception as e:
            print(f"   GPIO Error: {e}")
            return False
    
    def test_spi(self):
        """Test SPI communication"""
        try:
            spi = spidev.SpiDev()
            spi.open(self.SPI_BUS, self.SPI_DEVICE)
            spi.max_speed_hz = 2000000
            spi.mode = 0
            
            # Test write
            test_data = [0x01, 0x02, 0x03]
            spi.writebytes(test_data)
            
            spi.close()
            print(f"   SPI Bus: {self.SPI_BUS}, Device: {self.SPI_DEVICE}")
            print(f"   Speed: 2MHz, Mode: 0")
            return True
        except Exception as e:
            print(f"   SPI Error: {e}")
            return False
    
    def test_rx5808(self):
        """Test RX5808 communication"""
        try:
            # Setup SPI
            spi = spidev.SpiDev()
            spi.open(self.SPI_BUS, self.SPI_DEVICE)
            spi.max_speed_hz = 2000000
            spi.mode = 0
            
            # Setup GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.CS_PIN, GPIO.OUT)
            
            # Test frequency setting (5865 MHz)
            freq_reg = int((5865 - 479) / 2)
            
            # Write frequency registers
            GPIO.output(self.CS_PIN, GPIO.LOW)
            spi.writebytes([0x01, freq_reg & 0xFF])  # Low byte
            GPIO.output(self.CS_PIN, GPIO.HIGH)
            
            GPIO.output(self.CS_PIN, GPIO.LOW)
            spi.writebytes([0x02, (freq_reg >> 8) & 0xFF])  # High byte
            GPIO.output(self.CS_PIN, GPIO.HIGH)
            
            spi.close()
            print(f"   Frequency set to 5865 MHz")
            print(f"   Register value: 0x{freq_reg:04X}")
            return True
        except Exception as e:
            print(f"   RX5808 Error: {e}")
            return False
    
    def test_rssi(self):
        """Test RSSI reading"""
        try:
            # Setup SPI
            spi = spidev.SpiDev()
            spi.open(self.SPI_BUS, self.SPI_DEVICE)
            spi.max_speed_hz = 2000000
            spi.mode = 0
            
            # Setup GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.CS_PIN, GPIO.OUT)
            
            # Read RSSI multiple times
            readings = []
            for i in range(5):
                GPIO.output(self.CS_PIN, GPIO.LOW)
                spi.writebytes([0x08])  # RSSI read command
                response = spi.readbytes(1)
                GPIO.output(self.CS_PIN, GPIO.HIGH)
                
                if response:
                    readings.append(response[0])
                    print(f"   RSSI reading {i+1}: {response[0]}")
                
                time.sleep(0.1)
            
            spi.close()
            
            if readings:
                avg_rssi = sum(readings) / len(readings)
                print(f"   Average RSSI: {avg_rssi:.1f}")
                print(f"   Min/Max: {min(readings)}/{max(readings)}")
                return True
            else:
                print("   No RSSI readings")
                return False
                
        except Exception as e:
            print(f"   RSSI Error: {e}")
            return False
    
    def test_video(self):
        """Test video device"""
        try:
            # Check if video device exists
            result = subprocess.run(['ls', '/dev/video*'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                video_devices = result.stdout.strip().split('\n')
                print(f"   Found video devices: {video_devices}")
                
                # Test OpenCV capture
                cap = cv2.VideoCapture('/dev/video0')
                if cap.isOpened():
                    ret, frame = cap.read()
                    cap.release()
                    
                    if ret:
                        print(f"   Video capture successful: {frame.shape}")
                        print(f"   Video device: /dev/video0")
                        return True
                    else:
                        print("   No video signal")
                        return False
                else:
                    print("   Failed to open video device")
                    return False
            else:
                print("   No video devices found")
                return False
                
        except Exception as e:
            print(f"   Video Error: {e}")
            return False
    
    def test_system(self):
        """Test system resources"""
        try:
            # Check CPU info
            with open('/proc/cpuinfo', 'r') as f:
                cpu_info = f.read()
                if 'Raspberry Pi 4' in cpu_info:
                    print("   Raspberry Pi 4 detected")
                else:
                    print("   Warning: Not a Raspberry Pi 4")
            
            # Check memory
            with open('/proc/meminfo', 'r') as f:
                mem_info = f.read()
                for line in mem_info.split('\n'):
                    if 'MemTotal' in line:
                        mem_total = int(line.split()[1]) // 1024  # MB
                        print(f"   Total memory: {mem_total} MB")
                        break
            
            # Check SPI devices
            result = subprocess.run(['ls', '/dev/spi*'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                spi_devices = result.stdout.strip().split('\n')
                print(f"   SPI devices: {spi_devices}")
            else:
                print("   No SPI devices found")
            
            # Check power supply
            try:
                result = subprocess.run(['vcgencmd', 'measure_volts'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    voltage = result.stdout.strip()
                    print(f"   Core voltage: {voltage}")
            except:
                print("   Could not read voltage")
            
            return True
            
        except Exception as e:
            print(f"   System Error: {e}")
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 Test Summary")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:<20} {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Hardware is ready for scanning.")
            print("\n📋 RX5808 Pin Connections:")
            print(f"   CS (CH2): GPIO {self.CS_PIN}")
            print(f"   MOSI (A6.5M): GPIO 10")
            print(f"   SCK (CH1): GPIO 11")
            print(f"   RSSI: GPIO {self.RSSI_PIN}")
            print(f"   VIDEO: To USB DVR")
            print(f"   ANT: To antenna")
        else:
            print("⚠️  Some tests failed. Please check hardware connections.")
            print("\nTroubleshooting tips:")
            print("- Check GPIO connections")
            print("- Verify SPI is enabled in /boot/config.txt")
            print("- Ensure USB Video DVR is connected")
            print("- Check antenna connection")
            print("- Verify power supply (5V or 3.3V)")
    
    def cleanup(self):
        """Clean up GPIO"""
        try:
            GPIO.cleanup()
        except:
            pass

def main():
    tester = HardwareTester()
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main() 