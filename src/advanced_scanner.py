#!/usr/bin/env python3
"""
Advanced Raspberry Pi 4 RX5808 5.8GHz Scanner
Enhanced version with configuration support and advanced features
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import cv2
import numpy as np
import RPi.GPIO as GPIO
import spidev
import subprocess
import os
import json
import logging
from datetime import datetime
from PIL import Image, ImageTk
import queue
import math

class AdvancedRPIScanner:
    def __init__(self, config_file="config/scanner_config.json"):
        # Load configuration
        self.config = self.load_config(config_file)
        
        # Setup logging
        self.setup_logging()
        
        # Initialize hardware configuration
        self.setup_hardware_config()
        
        # Scanner state
        self.scanning = False
        self.current_channel = 'A'
        self.detected_signals = {}
        self.video_capturing = False
        self.signal_history = []
        
        # Multi-video capture system
        self.video_streams = {}  # Dictionary to store multiple video streams
        self.video_caps = {}     # Dictionary to store video capture objects
        self.video_labels = {}   # Dictionary to store video display labels
        self.max_video_streams = 4  # Maximum number of simultaneous video streams
        
        # Initialize hardware
        self.setup_hardware()
        
        # Create GUI
        self.create_gui()
        
        # Start background tasks
        self.start_background_tasks()
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Config file {config_file} not found")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in config file: {e}")
            return self.get_default_config()
    
    def get_default_config(self):
        """Return default configuration"""
        return {
            "hardware": {
                "gpio": {"cs_pin": 8, "rssi_pin": 7, "spi_bus": 0, "spi_device": 0},
                "video": {"device": "/dev/video0", "width": 640, "height": 480, "fps": 30}
            },
            "frequencies": {
                "channels": {"A": 5865, "B": 5845, "C": 5825, "D": 5805, "E": 5785, "F": 5765, "G": 5745, "H": 5725}
            },
            "scanner": {"scan_interval": 0.5, "rssi_threshold": 50, "strong_signal_threshold": 100}
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config.get("logging", {})
        if log_config.get("enabled", True):
            logging.basicConfig(
                level=getattr(logging, log_config.get("level", "INFO")),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_config.get("file", "/var/log/rpi_scanner.log")),
                    logging.StreamHandler()
                ]
            )
        self.logger = logging.getLogger("RPIScanner")
    
    def setup_hardware_config(self):
        """Extract hardware configuration"""
        hw_config = self.config["hardware"]
        gpio_config = hw_config["gpio"]
        video_config = hw_config["video"]
        
        # GPIO Configuration
        self.CS_PIN = gpio_config["cs_pin"]
        self.RSSI_PIN = gpio_config["rssi_pin"]
        self.SPI_BUS = gpio_config["spi_bus"]
        self.SPI_DEVICE = gpio_config["spi_device"]
        self.SPI_SPEED = gpio_config.get("spi_speed", 2000000)
        
        # Video Configuration
        self.video_device = video_config["device"]
        self.video_width = video_config["width"]
        self.video_height = video_config["height"]
        self.video_fps = video_config["fps"]
        
        # Scanner Configuration
        scanner_config = self.config["scanner"]
        self.scan_interval = scanner_config["scan_interval"]
        self.settling_time = scanner_config.get("settling_time", 0.1)
        self.rssi_threshold = scanner_config["rssi_threshold"]
        self.strong_signal_threshold = scanner_config["strong_signal_threshold"]
        self.auto_video_capture = scanner_config.get("auto_video_capture", True)
        
        # Frequency Configuration
        self.channels = self.config["frequencies"]["channels"]
    
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
            self.spi.max_speed_hz = self.SPI_SPEED
            self.spi.mode = 0
            
            self.logger.info("Hardware initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Hardware initialization error: {e}")
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
            self.logger.error(f"RX5808 write error: {e}")
    
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
            
            self.logger.debug(f"Frequency set to {frequency_mhz} MHz")
            
        except Exception as e:
            self.logger.error(f"Frequency setting error: {e}")
    
    def read_rssi(self):
        """Read RSSI value from RX5808 with averaging"""
        try:
            # Read multiple samples for averaging
            samples = []
            for _ in range(self.config["performance"].get("rssi_averaging", 5)):
                GPIO.output(self.CS_PIN, GPIO.LOW)
                self.spi.writebytes([0x08])  # RSSI read command
                response = self.spi.readbytes(1)
                GPIO.output(self.CS_PIN, GPIO.HIGH)
                
                if response:
                    samples.append(response[0])
            
            # Return average
            return sum(samples) // len(samples) if samples else 0
            
        except Exception as e:
            self.logger.error(f"RSSI read error: {e}")
            return 0
    
    def scan_channels(self):
        """Scan all channels for signals"""
        while self.scanning:
            scan_start = time.time()
            
            for channel, freq in self.channels.items():
                if not self.scanning:
                    break
                    
                # Set frequency
                self.set_frequency(freq)
                time.sleep(self.settling_time)
                
                # Read RSSI
                rssi = self.read_rssi()
                
                # Update detected signals
                if rssi > self.rssi_threshold:
                    signal_info = {
                        'frequency': freq,
                        'rssi': rssi,
                        'strength': min(100, int(rssi * 100 / 255)),
                        'timestamp': time.time(),
                        'channel': channel
                    }
                    
                    self.detected_signals[channel] = signal_info
                    
                    # Add to history
                    self.signal_history.append(signal_info)
                    if len(self.signal_history) > 100:  # Keep last 100 signals
                        self.signal_history.pop(0)
                    
                    # Try to capture video if strong signal and not already capturing
                    if (rssi > self.strong_signal_threshold and 
                        self.auto_video_capture and 
                        channel not in self.video_streams and
                        len(self.video_streams) < self.max_video_streams):
                        self.start_video_capture(channel, freq)
                    
                    self.logger.info(f"Signal detected on {channel}: {freq}MHz, RSSI: {rssi}")
                
                # Update GUI
                self.update_signal_list()
            
            # Maintain scan interval
            elapsed = time.time() - scan_start
            if elapsed < self.scan_interval:
                time.sleep(self.scan_interval - elapsed)
    
    def start_video_capture(self, channel, frequency):
        """Start video capture from detected signal"""
        try:
            # Add to video streams
            self.video_streams[channel] = {
                'frequency': frequency,
                'start_time': time.time(),
                'rssi': self.detected_signals[channel]['rssi']
            }
            
            # Create video capture object
            video_cap = cv2.VideoCapture(self.video_device)
            video_cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_width)
            video_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_height)
            video_cap.set(cv2.CAP_PROP_FPS, self.video_fps)
            
            if video_cap.isOpened():
                self.video_caps[channel] = video_cap
                
                # Start video capture thread for this channel
                video_thread = threading.Thread(target=self.capture_video, args=(channel,))
                video_thread.daemon = True
                video_thread.start()
                
                self.logger.info(f"Started video capture from {channel} ({frequency} MHz)")
                
                # Update GUI layout
                self.update_video_layout()
            else:
                self.logger.error(f"Failed to open video device for {channel}")
                del self.video_streams[channel]
                
        except Exception as e:
            self.logger.error(f"Video capture start error: {e}")
            if channel in self.video_streams:
                del self.video_streams[channel]
    
    def capture_video(self, channel):
        """Capture and display video for specific channel"""
        try:
            video_cap = self.video_caps[channel]
            
            while channel in self.video_streams and self.video_streams[channel]:
                ret, frame = video_cap.read()
                if ret:
                    # Add timestamp and channel info to frame
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    rssi = self.video_streams[channel]['rssi']
                    
                    # Add overlay information
                    cv2.putText(frame, f"CH:{channel} {self.video_streams[channel]['frequency']}MHz", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"RSSI:{rssi} {timestamp}", 
                               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                    
                    # Convert frame for Tkinter
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_pil = Image.fromarray(frame_rgb)
                    
                    # Resize frame based on layout
                    display_width, display_height = self.get_video_display_size()
                    frame_pil = frame_pil.resize((display_width, display_height), Image.Resampling.LANCZOS)
                    
                    frame_tk = ImageTk.PhotoImage(frame_pil)
                    
                    # Update video display
                    if channel in self.video_labels:
                        self.video_labels[channel].config(image=frame_tk)
                        self.video_labels[channel].image = frame_tk
                
                time.sleep(1.0 / self.video_fps)
            
        except Exception as e:
            self.logger.error(f"Video capture error for {channel}: {e}")
        finally:
            if channel in self.video_caps:
                self.video_caps[channel].release()
                del self.video_caps[channel]
    
    def get_video_display_size(self):
        """Calculate video display size based on number of streams"""
        num_streams = len(self.video_streams)
        if num_streams == 0:
            return 640, 480
        
        # Calculate grid layout
        cols = math.ceil(math.sqrt(num_streams))
        rows = math.ceil(num_streams / cols)
        
        # Calculate individual video size
        display_width = min(640 // cols, 480)
        display_height = min(480 // rows, 360)
        
        return display_width, display_height
    
    def update_video_layout(self):
        """Update video display layout based on number of streams"""
        num_streams = len(self.video_streams)
        
        if num_streams == 0:
            # Show "No video signal" message
            self.video_label.config(text="No video signal", image="")
            return
        
        # Clear existing video labels
        for label in self.video_labels.values():
            label.destroy()
        self.video_labels.clear()
        
        # Calculate grid layout
        cols = math.ceil(math.sqrt(num_streams))
        rows = math.ceil(num_streams / cols)
        
        # Configure grid
        for i in range(rows):
            self.video_frame.grid_rowconfigure(i, weight=1)
        for j in range(cols):
            self.video_frame.grid_columnconfigure(j, weight=1)
        
        # Create video labels
        stream_index = 0
        for channel in self.video_streams.keys():
            row = stream_index // cols
            col = stream_index % cols
            
            # Create frame for this video stream
            stream_frame = ttk.Frame(self.video_frame)
            stream_frame.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
            
            # Create label for video display
            video_label = ttk.Label(stream_frame, text=f"Loading {channel}...", 
                                   background="black", foreground="white")
            video_label.pack(fill="both", expand=True)
            
            # Create info label
            info_label = ttk.Label(stream_frame, 
                                  text=f"Channel {channel} - {self.video_streams[channel]['frequency']} MHz",
                                  background="black", foreground="green")
            info_label.pack(fill="x")
            
            self.video_labels[channel] = video_label
            stream_index += 1
    
    def create_gui(self):
        """Create the main GUI window"""
        self.root = tk.Tk()
        self.root.title("Advanced Raspberry Pi RX5808 5.8GHz Scanner - Multi-Video")
        
        # Set window size from config
        window_size = self.config["display"].get("window_size", "1400x900")
        self.root.geometry(window_size)
        
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Create menu
        self.create_menu()
        
        # Control panel
        self.create_control_panel()
        
        # Video display (expanded to full width)
        self.create_video_display()
        
        # Signal list
        self.create_signal_list()
        
        # Status bar
        self.create_status_bar()
    
    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Signal Log", command=self.save_signal_log)
        file_menu.add_command(label="Load Configuration", command=self.load_configuration)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_application)
        
        # Video menu
        video_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Video", menu=video_menu)
        video_menu.add_command(label="Stop All Video", command=self.stop_all_video)
        video_menu.add_command(label="Video Settings", command=self.video_settings)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Calibrate RSSI", command=self.calibrate_rssi)
        tools_menu.add_command(label="Test Video", command=self.test_video)
        tools_menu.add_command(label="System Info", command=self.show_system_info)
    
    def create_control_panel(self):
        """Create control panel with buttons and settings"""
        control_frame = ttk.LabelFrame(self.root, text="Scanner Controls", padding="10")
        control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # Start/Stop button
        self.scan_button = ttk.Button(control_frame, text="Start Scanning", 
                                     command=self.toggle_scanning)
        self.scan_button.pack(side="left", padx=5)
        
        # Stop all video button
        self.stop_video_button = ttk.Button(control_frame, text="Stop All Video", 
                                           command=self.stop_all_video)
        self.stop_video_button.pack(side="left", padx=5)
        
        # Channel selection
        ttk.Label(control_frame, text="Channel:").pack(side="left", padx=5)
        self.channel_var = tk.StringVar(value="A")
        channel_combo = ttk.Combobox(control_frame, textvariable=self.channel_var, 
                                    values=list(self.channels.keys()), width=5)
        channel_combo.pack(side="left", padx=5)
        channel_combo.bind("<<ComboboxSelected>>", self.on_channel_select)
        
        # RSSI threshold
        ttk.Label(control_frame, text="RSSI Threshold:").pack(side="left", padx=5)
        self.threshold_var = tk.IntVar(value=self.rssi_threshold)
        threshold_scale = ttk.Scale(control_frame, from_=0, to=255, 
                                   variable=self.threshold_var, orient="horizontal")
        threshold_scale.pack(side="left", padx=5)
        threshold_scale.bind("<ButtonRelease-1>", self.on_threshold_change)
        
        # Auto video capture checkbox
        self.auto_video_var = tk.BooleanVar(value=self.auto_video_capture)
        auto_video_check = ttk.Checkbutton(control_frame, text="Auto Video", 
                                          variable=self.auto_video_var)
        auto_video_check.pack(side="left", padx=5)
        
        # Video streams count
        self.video_count_label = ttk.Label(control_frame, text="Video Streams: 0")
        self.video_count_label.pack(side="right", padx=5)
    
    def create_video_display(self):
        """Create expanded video display area"""
        video_frame = ttk.LabelFrame(self.root, text="Multi-Video Output", padding="10")
        video_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Configure video frame grid
        video_frame.grid_columnconfigure(0, weight=1)
        video_frame.grid_rowconfigure(0, weight=1)
        
        # Main video display area
        self.video_frame = ttk.Frame(video_frame)
        self.video_frame.grid(row=0, column=0, sticky="nsew")
        
        # Default "No video signal" label
        self.video_label = ttk.Label(self.video_frame, text="No video signal", 
                                    background="black", foreground="white")
        self.video_label.pack(fill="both", expand=True)
    
    def create_signal_list(self):
        """Create signal list display"""
        signal_frame = ttk.LabelFrame(self.root, text="Detected Signals", padding="10")
        signal_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        # Create treeview for signals
        columns = ("Channel", "Frequency", "RSSI", "Strength", "Time", "Video")
        self.signal_tree = ttk.Treeview(signal_frame, columns=columns, show="headings", height=4)
        
        # Configure columns
        for col in columns:
            self.signal_tree.heading(col, text=col)
            self.signal_tree.column(col, width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(signal_frame, orient="vertical", command=self.signal_tree.yview)
        self.signal_tree.configure(yscrollcommand=scrollbar.set)
        
        self.signal_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_status_bar(self):
        """Create status bar"""
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side="left")
        
        # Signal count
        self.signal_count_label = ttk.Label(status_frame, text="Signals: 0")
        self.signal_count_label.pack(side="right")
        
        # Video streams count
        self.status_video_count_label = ttk.Label(status_frame, text="Video Streams: 0")
        self.status_video_count_label.pack(side="right", padx=20)
    
    def update_signal_list(self):
        """Update signal list display"""
        # Clear existing items
        for item in self.signal_tree.get_children():
            self.signal_tree.delete(item)
        
        # Add current signals
        for channel, signal in self.detected_signals.items():
            timestamp = datetime.fromtimestamp(signal['timestamp']).strftime("%H:%M:%S")
            video_status = "Active" if channel in self.video_streams else "None"
            
            self.signal_tree.insert("", "end", values=(
                channel,
                f"{signal['frequency']} MHz",
                signal['rssi'],
                f"{signal['strength']}%",
                timestamp,
                video_status
            ))
        
        # Update counts
        signal_count = len(self.detected_signals)
        video_count = len(self.video_streams)
        self.signal_count_label.config(text=f"Signals: {signal_count}")
        self.video_count_label.config(text=f"Video Streams: {video_count}")
        self.status_video_count_label.config(text=f"Video Streams: {video_count}")
    
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
    
    def stop_all_video(self):
        """Stop all video streams"""
        for channel in list(self.video_streams.keys()):
            self.stop_video_stream(channel)
        self.update_video_layout()
        self.status_label.config(text="All video streams stopped")
    
    def stop_video_stream(self, channel):
        """Stop specific video stream"""
        if channel in self.video_streams:
            self.video_streams[channel] = None  # Signal thread to stop
            if channel in self.video_caps:
                self.video_caps[channel].release()
                del self.video_caps[channel]
            if channel in self.video_labels:
                self.video_labels[channel].destroy()
                del self.video_labels[channel]
            del self.video_streams[channel]
    
    def on_channel_select(self, event):
        """Handle channel selection"""
        channel = self.channel_var.get()
        if channel in self.channels:
            freq = self.channels[channel]
            self.set_frequency(freq)
            self.status_label.config(text=f"Tuned to {channel} ({freq} MHz)")
    
    def on_threshold_change(self, event):
        """Handle RSSI threshold change"""
        self.rssi_threshold = self.threshold_var.get()
        self.logger.info(f"RSSI threshold changed to {self.rssi_threshold}")
    
    def save_signal_log(self):
        """Save signal detection log to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.signal_history, f, indent=2)
                messagebox.showinfo("Success", f"Signal log saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save log: {e}")
    
    def load_configuration(self):
        """Load configuration from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    new_config = json.load(f)
                self.config.update(new_config)
                self.setup_hardware_config()
                messagebox.showinfo("Success", "Configuration loaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration: {e}")
    
    def calibrate_rssi(self):
        """Calibrate RSSI readings"""
        messagebox.showinfo("Calibration", "RSSI calibration feature coming soon!")
    
    def test_video(self):
        """Test video capture"""
        try:
            cap = cv2.VideoCapture(self.video_device)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                if ret:
                    messagebox.showinfo("Video Test", "Video device working correctly")
                else:
                    messagebox.showerror("Video Test", "No video signal detected")
            else:
                messagebox.showerror("Video Test", "Failed to open video device")
        except Exception as e:
            messagebox.showerror("Video Test", f"Video test error: {e}")
    
    def video_settings(self):
        """Open video settings dialog"""
        messagebox.showinfo("Video Settings", "Video settings dialog coming soon!")
    
    def show_system_info(self):
        """Show system information"""
        info = f"""
System Information:
- Raspberry Pi 4 Model B
- RX5808 5.8GHz Receiver
- USB Video DVR
- Python {subprocess.check_output(['python3', '--version']).decode().strip()}
- OpenCV {cv2.__version__}
- Detected Signals: {len(self.detected_signals)}
- Active Video Streams: {len(self.video_streams)}
- Max Video Streams: {self.max_video_streams}
        """
        messagebox.showinfo("System Info", info)
    
    def start_background_tasks(self):
        """Start background tasks"""
        # Update signal list periodically
        def update_signal_list():
            if self.scanning:
                self.update_signal_list()
            self.root.after(1000, update_signal_list)
        
        update_signal_list()
    
    def quit_application(self):
        """Quit the application"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.cleanup()
            self.root.quit()
    
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.logger.info("Shutting down...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        self.scanning = False
        
        # Stop all video streams
        for channel in list(self.video_streams.keys()):
            self.stop_video_stream(channel)
        
        try:
            GPIO.cleanup()
            if hasattr(self, 'spi'):
                self.spi.close()
        except:
            pass

if __name__ == "__main__":
    scanner = AdvancedRPIScanner()
    scanner.run() 