#!/usr/bin/env python3
"""
Raspberry Pi 4 RX5808 5.8GHz Scanner
Real-time frequency scanner with video capture and display
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

class RPIScanner:
    def __init__(self):
        # GPIO Configuration for RX5808
        self.CS_PIN = 8          # Chip Select
        self.RSSI_PIN = 7        # RSSI input (ADC)
        self.SPI_BUS = 0
        self.SPI_DEVICE = 0
        
        # Video Configuration
        self.video_device = "/dev/video0"  # USB Video DVR device
        self.video_width = 640
        self.video_height = 480
        self.video_fps = 30
        
        # Frequency Configuration (5.8GHz FPV channels)
        self.channels = {
            'A': 5865, 'B': 5845, 'C': 5825, 'D': 5805,
            'E': 5785, 'F': 5765, 'G': 5745, 'H': 5725
        }
        
        # Scanner state
        self.scanning = False
        self.current_channel = 'A'
        self.detected_signals = {}
        self.video_capturing = False
        
        # Initialize GPIO and SPI
        self.setup_hardware()
        
        # Create GUI
        self.create_gui()
        
    def setup_hardware(self):
        """Initialize GPIO and SPI for RX5808 communication"""
        try:
            # Setup GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.CS_PIN, GPIO.OUT)
            GPIO.output(self.CS_PIN, GPIO.HIGH)
            
            # Setup SPI
            self.spi = spidev.SpiDev()
            self.spi.open(self.SPI_BUS, self.SPI_DEVICE)
            self.spi.max_speed_hz = 2000000
            self.spi.mode = 0
            
            print("Hardware initialized successfully")
            
        except Exception as e:
            print(f"Hardware initialization error: {e}")
            messagebox.showerror("Hardware Error", f"Failed to initialize hardware: {e}")
    
    def rx5808_write(self, address, data):
        """Write data to RX5808 register"""
        try:
            # Prepare command (address + data)
            command = (address << 3) | data
            
            # Send via SPI
            GPIO.output(self.CS_PIN, GPIO.LOW)
            self.spi.writebytes([command])
            GPIO.output(self.CS_PIN, GPIO.HIGH)
            
        except Exception as e:
            print(f"RX5808 write error: {e}")
    
    def set_frequency(self, frequency_mhz):
        """Set RX5808 frequency in MHz"""
        try:
            # Convert frequency to RX5808 format
            freq_reg = int((frequency_mhz - 479) / 2)
            
            # Write frequency registers
            self.rx5808_write(0x01, freq_reg & 0xFF)
            self.rx5808_write(0x02, (freq_reg >> 8) & 0xFF)
            
            # Enable receiver
            self.rx5808_write(0x00, 0x01)
            
            print(f"Frequency set to {frequency_mhz} MHz")
            
        except Exception as e:
            print(f"Frequency setting error: {e}")
    
    def read_rssi(self):
        """Read RSSI value from RX5808"""
        try:
            # Read RSSI register
            GPIO.output(self.CS_PIN, GPIO.LOW)
            self.spi.writebytes([0x08])  # RSSI read command
            response = self.spi.readbytes(1)
            GPIO.output(self.CS_PIN, GPIO.HIGH)
            
            return response[0] if response else 0
            
        except Exception as e:
            print(f"RSSI read error: {e}")
            return 0
    
    def scan_channels(self):
        """Scan all channels for signals"""
        while self.scanning:
            for channel, freq in self.channels.items():
                if not self.scanning:
                    break
                    
                # Set frequency
                self.set_frequency(freq)
                time.sleep(0.1)  # Settling time
                
                # Read RSSI
                rssi = self.read_rssi()
                
                # Update detected signals
                if rssi > 50:  # Threshold for signal detection
                    self.detected_signals[channel] = {
                        'frequency': freq,
                        'rssi': rssi,
                        'strength': min(100, int(rssi * 100 / 255)),
                        'timestamp': time.time()
                    }
                    
                    # Try to capture video if strong signal
                    if rssi > 100 and not self.video_capturing:
                        self.start_video_capture(channel, freq)
                
                # Update GUI
                self.update_spectrum_display()
                
            time.sleep(0.5)  # Scan interval
    
    def start_video_capture(self, channel, frequency):
        """Start video capture from detected signal"""
        try:
            self.video_capturing = True
            self.current_channel = channel
            
            # Update status
            self.status_label.config(text=f"Capturing video from {channel} ({frequency} MHz)")
            
            # Start video capture thread
            video_thread = threading.Thread(target=self.capture_video)
            video_thread.daemon = True
            video_thread.start()
            
        except Exception as e:
            print(f"Video capture start error: {e}")
    
    def capture_video(self):
        """Capture and display video from USB Video DVR"""
        try:
            # Initialize video capture
            cap = cv2.VideoCapture(self.video_device)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_height)
            cap.set(cv2.CAP_PROP_FPS, self.video_fps)
            
            if not cap.isOpened():
                print("Failed to open video device")
                return
            
            while self.video_capturing:
                ret, frame = cap.read()
                if ret:
                    # Convert frame for Tkinter
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_pil = Image.fromarray(frame_rgb)
                    frame_tk = ImageTk.PhotoImage(frame_pil)
                    
                    # Update video display
                    self.video_label.config(image=frame_tk)
                    self.video_label.image = frame_tk
                
                time.sleep(1.0 / self.video_fps)
            
            cap.release()
            
        except Exception as e:
            print(f"Video capture error: {e}")
        finally:
            self.video_capturing = False
    
    def create_gui(self):
        """Create the main GUI window"""
        self.root = tk.Tk()
        self.root.title("Raspberry Pi RX5808 5.8GHz Scanner")
        self.root.geometry("1200x800")
        
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Control panel
        self.create_control_panel()
        
        # Spectrum display
        self.create_spectrum_display()
        
        # Video display
        self.create_video_display()
        
        # Status bar
        self.create_status_bar()
    
    def create_control_panel(self):
        """Create control panel with buttons and settings"""
        control_frame = ttk.LabelFrame(self.root, text="Scanner Controls", padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Start/Stop button
        self.scan_button = ttk.Button(control_frame, text="Start Scanning", 
                                     command=self.toggle_scanning)
        self.scan_button.pack(side="left", padx=5)
        
        # Video capture button
        self.video_button = ttk.Button(control_frame, text="Stop Video", 
                                      command=self.stop_video_capture)
        self.video_button.pack(side="left", padx=5)
        
        # Channel selection
        ttk.Label(control_frame, text="Channel:").pack(side="left", padx=5)
        self.channel_var = tk.StringVar(value="A")
        channel_combo = ttk.Combobox(control_frame, textvariable=self.channel_var, 
                                    values=list(self.channels.keys()), width=5)
        channel_combo.pack(side="left", padx=5)
        channel_combo.bind("<<ComboboxSelected>>", self.on_channel_select)
        
        # RSSI threshold
        ttk.Label(control_frame, text="RSSI Threshold:").pack(side="left", padx=5)
        self.threshold_var = tk.IntVar(value=50)
        threshold_scale = ttk.Scale(control_frame, from_=0, to=255, 
                                   variable=self.threshold_var, orient="horizontal")
        threshold_scale.pack(side="left", padx=5)
    
    def create_spectrum_display(self):
        """Create frequency spectrum display"""
        spectrum_frame = ttk.LabelFrame(self.root, text="Frequency Spectrum", padding="10")
        spectrum_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Canvas for spectrum visualization
        self.spectrum_canvas = tk.Canvas(spectrum_frame, width=400, height=300, 
                                        bg="black", highlightthickness=0)
        self.spectrum_canvas.pack(fill="both", expand=True)
        
        # Draw frequency scale
        self.draw_frequency_scale()
    
    def create_video_display(self):
        """Create video display area"""
        video_frame = ttk.LabelFrame(self.root, text="Video Output", padding="10")
        video_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)
        
        # Video display label
        self.video_label = ttk.Label(video_frame, text="No video signal", 
                                    background="black", foreground="white")
        self.video_label.pack(fill="both", expand=True)
    
    def create_status_bar(self):
        """Create status bar"""
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side="left")
        
        # Signal count
        self.signal_count_label = ttk.Label(status_frame, text="Signals: 0")
        self.signal_count_label.pack(side="right")
    
    def draw_frequency_scale(self):
        """Draw frequency scale on spectrum canvas"""
        canvas = self.spectrum_canvas
        canvas.delete("all")
        
        # Draw frequency range
        canvas.create_text(200, 20, text="5.8GHz FPV Frequency Spectrum", 
                          fill="white", font=("Arial", 12, "bold"))
        
        # Draw frequency markers
        x_start = 50
        x_end = 350
        y_base = 250
        
        for i, (channel, freq) in enumerate(self.channels.items()):
            x = x_start + (i * (x_end - x_start) / (len(self.channels) - 1))
            
            # Frequency label
            canvas.create_text(x, y_base + 20, text=f"{freq}", 
                              fill="white", font=("Arial", 8))
            canvas.create_text(x, y_base + 35, text=channel, 
                              fill="yellow", font=("Arial", 10, "bold"))
            
            # Signal strength bar
            if channel in self.detected_signals:
                signal = self.detected_signals[channel]
                strength = signal['strength']
                bar_height = int((strength / 100) * 150)
                
                # Color based on strength
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
                
                # RSSI value
                canvas.create_text(x, y_base - bar_height - 10, 
                                  text=f"{signal['rssi']}", 
                                  fill="white", font=("Arial", 8))
    
    def update_spectrum_display(self):
        """Update spectrum display with current signal data"""
        self.draw_frequency_scale()
        
        # Update signal count
        signal_count = len(self.detected_signals)
        self.signal_count_label.config(text=f"Signals: {signal_count}")
        
        # Schedule next update
        if self.scanning:
            self.root.after(100, self.update_spectrum_display)
    
    def toggle_scanning(self):
        """Toggle scanning on/off"""
        if not self.scanning:
            self.scanning = True
            self.scan_button.config(text="Stop Scanning")
            self.status_label.config(text="Scanning...")
            
            # Start scanning thread
            scan_thread = threading.Thread(target=self.scan_channels)
            scan_thread.daemon = True
            scan_thread.start()
        else:
            self.scanning = False
            self.scan_button.config(text="Start Scanning")
            self.status_label.config(text="Scanning stopped")
    
    def stop_video_capture(self):
        """Stop video capture"""
        self.video_capturing = False
        self.video_label.config(text="No video signal")
        self.status_label.config(text="Video capture stopped")
    
    def on_channel_select(self, event):
        """Handle channel selection"""
        channel = self.channel_var.get()
        if channel in self.channels:
            freq = self.channels[channel]
            self.set_frequency(freq)
            self.status_label.config(text=f"Tuned to {channel} ({freq} MHz)")
    
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        self.scanning = False
        self.video_capturing = False
        
        try:
            GPIO.cleanup()
            if hasattr(self, 'spi'):
                self.spi.close()
        except:
            pass

if __name__ == "__main__":
    scanner = RPIScanner()
    scanner.run() 