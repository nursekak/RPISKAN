#!/usr/bin/env python3
"""
Interface Mockup for Raspberry Pi RX5808 Scanner
Demonstrates the GUI appearance and functionality with multi-video display
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random
from datetime import datetime
import json
import math

class ScannerInterfaceMockup:
    def __init__(self):
        # Expanded frequency range for 5.8GHz
        self.channels = {
            # Racing Band (Original)
            'A': 5865, 'B': 5845, 'C': 5825, 'D': 5805,
            'E': 5785, 'F': 5765, 'G': 5745, 'H': 5725,
            # Long Range Band
            'I': 5885, 'J': 5905, 'K': 5925, 'L': 5945,
            'M': 5705, 'N': 5685, 'O': 5665, 'P': 5645,
            # Low Band
            'Q': 5625, 'R': 5605, 'S': 5585, 'T': 5565,
            'U': 5545, 'V': 5525, 'W': 5505, 'X': 5485,
            # Ultra Low Band
            'Y': 5465, 'Z': 5445, '1': 5425, '2': 5405,
            '3': 5385, '4': 5365, '5': 5345, '6': 5325,
            # Extended Range
            '7': 5305, '8': 5285, '9': 5265, '0': 5245
        }
        
        # Frequency bands for organization
        self.frequency_bands = {
            'racing': {
                'name': 'FPV Racing',
                'channels': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
                'range': {'min': 5725, 'max': 5865},
                'color': '#00ff00'
            },
            'long_range': {
                'name': 'Long Range',
                'channels': ['I', 'J', 'K', 'L', 'M', 'N', 'O', 'P'],
                'range': {'min': 5645, 'max': 5945},
                'color': '#0088ff'
            },
            'low_band': {
                'name': 'Low Band',
                'channels': ['Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X'],
                'range': {'min': 5485, 'max': 5625},
                'color': '#ff8800'
            },
            'ultra_low': {
                'name': 'Ultra Low',
                'channels': ['Y', 'Z', '1', '2', '3', '4', '5', '6'],
                'range': {'min': 5325, 'max': 5465},
                'color': '#ff0088'
            },
            'extended': {
                'name': 'Extended Range',
                'channels': ['7', '8', '9', '0'],
                'range': {'min': 5245, 'max': 5305},
                'color': '#8800ff'
            }
        }
        
        # Scan modes
        self.scan_modes = {
            'full_range': {
                'name': 'Full Range Scan',
                'description': 'Scan entire 5.8GHz range (5245-5945 MHz)',
                'channels': list(self.channels.keys())
            },
            'racing_only': {
                'name': 'Racing Band Only',
                'description': 'Scan only FPV racing channels (5725-5865 MHz)',
                'channels': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
            },
            'long_range_only': {
                'name': 'Long Range Only',
                'description': 'Scan long range channels (5645-5945 MHz)',
                'channels': ['I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
            }
        }
        
        # Mock scanner state
        self.scanning = False
        self.current_channel = 'A'
        self.current_scan_mode = 'full_range'
        self.detected_signals = {}
        self.video_streams = {}  # Dictionary to store multiple video streams
        self.video_labels = {}   # Dictionary to store video display labels
        self.max_video_streams = 4  # Maximum number of simultaneous video streams
        self.signal_history = []
        
        # Create GUI
        self.create_gui()
        
        # Start mock data generation
        self.start_mock_data()
        
    def create_gui(self):
        """Create the main GUI window"""
        self.root = tk.Tk()
        self.root.title("Raspberry Pi RX5808 5.8GHz Scanner - Multi-Video Mockup")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#2b2b2b')
        
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
        
        # Add some style
        self.apply_styles()
    
    def apply_styles(self):
        """Apply custom styles to the interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', 
                       background='#2b2b2b', 
                       foreground='#00ff00', 
                       font=('Arial', 14, 'bold'))
        
        style.configure('Status.TLabel', 
                       background='#2b2b2b', 
                       foreground='#ffffff', 
                       font=('Arial', 10))
        
        style.configure('Signal.TLabel', 
                       background='#2b2b2b', 
                       foreground='#ffff00', 
                       font=('Arial', 9, 'bold'))
    
    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Signal Log", command=self.save_mock_log)
        file_menu.add_command(label="Load Configuration", command=self.load_mock_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Scan menu
        scan_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Scan", menu=scan_menu)
        for mode_key, mode_info in self.scan_modes.items():
            scan_menu.add_command(label=mode_info['name'], 
                                command=lambda m=mode_key: self.set_scan_mode(m))
        
        # Video menu
        video_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Video", menu=video_menu)
        video_menu.add_command(label="Stop All Video", command=self.stop_all_mock_video)
        video_menu.add_command(label="Video Settings", command=self.video_settings)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Calibrate RSSI", command=self.calibrate_mock)
        tools_menu.add_command(label="Test Video", command=self.test_mock_video)
        tools_menu.add_command(label="System Info", command=self.show_mock_system_info)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_control_panel(self):
        """Create control panel with buttons and settings"""
        control_frame = ttk.LabelFrame(self.root, text="Scanner Controls", padding="10")
        control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        control_frame.configure(style='Title.TLabel')
        
        # Start/Stop button
        self.scan_button = ttk.Button(control_frame, text="Start Scanning", 
                                     command=self.toggle_mock_scanning,
                                     style='Accent.TButton')
        self.scan_button.pack(side="left", padx=5)
        
        # Stop all video button
        self.stop_video_button = ttk.Button(control_frame, text="Stop All Video", 
                                           command=self.stop_all_mock_video)
        self.stop_video_button.pack(side="left", padx=5)
        
        # Scan mode selection
        ttk.Label(control_frame, text="Scan Mode:", style='Status.TLabel').pack(side="left", padx=5)
        self.scan_mode_var = tk.StringVar(value="Full Range")
        scan_mode_combo = ttk.Combobox(control_frame, textvariable=self.scan_mode_var, 
                                      values=[mode['name'] for mode in self.scan_modes.values()], width=15)
        scan_mode_combo.pack(side="left", padx=5)
        scan_mode_combo.bind("<<ComboboxSelected>>", self.on_scan_mode_select)
        
        # Channel selection
        ttk.Label(control_frame, text="Channel:", style='Status.TLabel').pack(side="left", padx=5)
        self.channel_var = tk.StringVar(value="A")
        channel_combo = ttk.Combobox(control_frame, textvariable=self.channel_var, 
                                    values=list(self.channels.keys()), width=5)
        channel_combo.pack(side="left", padx=5)
        channel_combo.bind("<<ComboboxSelected>>", self.on_channel_select)
        
        # RSSI threshold
        ttk.Label(control_frame, text="RSSI Threshold:", style='Status.TLabel').pack(side="left", padx=5)
        self.threshold_var = tk.IntVar(value=50)
        threshold_scale = ttk.Scale(control_frame, from_=0, to=255, 
                                   variable=self.threshold_var, orient="horizontal")
        threshold_scale.pack(side="left", padx=5)
        
        # Auto video capture checkbox
        self.auto_video_var = tk.BooleanVar(value=True)
        auto_video_check = ttk.Checkbutton(control_frame, text="Auto Video", 
                                          variable=self.auto_video_var)
        auto_video_check.pack(side="left", padx=5)
        
        # Video streams count
        self.video_count_label = ttk.Label(control_frame, text="Video Streams: 0", 
                                          style='Signal.TLabel')
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
        columns = ("Channel", "Frequency", "Band", "RSSI", "Strength", "Time", "Video")
        self.signal_tree = ttk.Treeview(signal_frame, columns=columns, show="headings", height=4)
        
        # Configure columns
        for col in columns:
            self.signal_tree.heading(col, text=col)
            self.signal_tree.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(signal_frame, orient="vertical", command=self.signal_tree.yview)
        self.signal_tree.configure(yscrollcommand=scrollbar.set)
        
        self.signal_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add some mock signals
        self.add_mock_signals()
    
    def create_status_bar(self):
        """Create status bar"""
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Ready - Multi-Video Mockup", 
                                     style='Status.TLabel')
        self.status_label.pack(side="left")
        
        # Scan mode display
        self.scan_mode_label = ttk.Label(status_frame, text="Mode: Full Range", 
                                        style='Status.TLabel')
        self.scan_mode_label.pack(side="left", padx=20)
        
        # Signal count
        self.signal_count_label = ttk.Label(status_frame, text="Signals: 0", 
                                           style='Status.TLabel')
        self.signal_count_label.pack(side="right")
        
        # Video streams count
        self.status_video_count_label = ttk.Label(status_frame, text="Video Streams: 0", 
                                                 style='Status.TLabel')
        self.status_video_count_label.pack(side="right", padx=20)
        
        # Time display
        self.time_label = ttk.Label(status_frame, text="", style='Status.TLabel')
        self.time_label.pack(side="right", padx=20)
        
        # Update time
        self.update_time()
    
    def draw_mock_video(self, channel):
        """Draw mock video frame for specific channel"""
        canvas = tk.Canvas(self.video_labels[channel], width=300, height=200, 
                          bg="black", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        # Draw mock video content
        canvas.create_text(150, 80, text="FPV VIDEO FEED", 
                          fill="#00ff00", font=("Arial", 16, "bold"))
        canvas.create_text(150, 110, text=f"Channel: {channel}", 
                          fill="white", font=("Arial", 12))
        canvas.create_text(150, 130, text=f"Frequency: {self.channels[channel]} MHz", 
                          fill="white", font=("Arial", 12))
        
        # Draw timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        canvas.create_text(150, 170, text=timestamp, 
                          fill="#00ff00", font=("Arial", 10))
        
        # Draw some mock video artifacts
        for i in range(3):
            x = random.randint(20, 280)
            y = random.randint(20, 180)
            canvas.create_rectangle(x, y, x+2, y+2, fill="#00ff00")
    
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
                                  text=f"Channel {channel} - {self.channels[channel]} MHz",
                                  background="black", foreground="green")
            info_label.pack(fill="x")
            
            self.video_labels[channel] = video_label
            
            # Draw mock video
            self.draw_mock_video(channel)
            
            stream_index += 1
    
    def add_mock_signals(self):
        """Add mock signals to the signal list"""
        mock_signals = [
            ("A", "5865 MHz", "Racing", 145, "85%", "14:32:15", "Active"),
            ("C", "5825 MHz", "Racing", 98, "62%", "14:32:12", "None"),
            ("I", "5885 MHz", "Long Range", 123, "72%", "14:32:10", "Active"),
            ("K", "5925 MHz", "Long Range", 156, "91%", "14:32:08", "Active"),
            ("Q", "5625 MHz", "Low Band", 67, "45%", "14:32:05", "None"),
            ("Y", "5465 MHz", "Ultra Low", 89, "55%", "14:32:02", "Active"),
            ("7", "5305 MHz", "Extended", 134, "78%", "14:31:58", "None")
        ]
        
        for signal in mock_signals:
            self.signal_tree.insert("", "end", values=signal)
    
    def start_mock_data(self):
        """Start generating mock data"""
        def generate_mock_signals():
            while True:
                if self.scanning:
                    # Generate random signals based on current scan mode
                    active_channels = self.scan_modes[self.current_scan_mode]['channels']
                    
                    for channel in active_channels:
                        if random.random() < 0.2:  # 20% chance of signal
                            rssi = random.randint(30, 180)
                            strength = min(100, int(rssi * 100 / 255))
                            
                            self.detected_signals[channel] = {
                                'frequency': self.channels[channel],
                                'rssi': rssi,
                                'strength': strength,
                                'timestamp': time.time()
                            }
                            
                            # Auto-start video for strong signals
                            if (rssi > 100 and 
                                self.auto_video_var.get() and 
                                channel not in self.video_streams and
                                len(self.video_streams) < self.max_video_streams):
                                self.start_mock_video(channel)
                
                time.sleep(2)  # Update every 2 seconds
        
        # Start mock data thread
        mock_thread = threading.Thread(target=generate_mock_signals, daemon=True)
        mock_thread.start()
    
    def set_scan_mode(self, mode_key):
        """Set scan mode"""
        self.current_scan_mode = mode_key
        mode_info = self.scan_modes[mode_key]
        self.scan_mode_var.set(mode_info['name'])
        self.scan_mode_label.config(text=f"Mode: {mode_info['name']}")
        self.status_label.config(text=f"Scan mode changed to {mode_info['name']}")
    
    def on_scan_mode_select(self, event):
        """Handle scan mode selection"""
        selected_name = self.scan_mode_var.get()
        for mode_key, mode_info in self.scan_modes.items():
            if mode_info['name'] == selected_name:
                self.set_scan_mode(mode_key)
                break
    
    def toggle_mock_scanning(self):
        """Toggle mock scanning"""
        if not self.scanning:
            self.scanning = True
            self.scan_button.config(text="Stop Scanning")
            mode_info = self.scan_modes[self.current_scan_mode]
            self.status_label.config(text=f"Scanning... {mode_info['name']} - Mockup Mode")
        else:
            self.scanning = False
            self.scan_button.config(text="Start Scanning")
            self.status_label.config(text="Scanning stopped - Mockup Mode")
    
    def start_mock_video(self, channel):
        """Start mock video capture"""
        self.video_streams[channel] = {
            'frequency': self.channels[channel],
            'start_time': time.time(),
            'rssi': self.detected_signals[channel]['rssi']
        }
        
        # Update video layout
        self.update_video_layout()
        
        # Update counts
        video_count = len(self.video_streams)
        self.video_count_label.config(text=f"Video Streams: {video_count}")
        self.status_video_count_label.config(text=f"Video Streams: {video_count}")
        
        self.status_label.config(text=f"Video capture started - Channel {channel}")
    
    def stop_all_mock_video(self):
        """Stop all mock video streams"""
        self.video_streams.clear()
        self.update_video_layout()
        
        # Update counts
        self.video_count_label.config(text="Video Streams: 0")
        self.status_video_count_label.config(text="Video Streams: 0")
        
        self.status_label.config(text="All video streams stopped")
    
    def on_channel_select(self, event):
        """Handle channel selection"""
        channel = self.channel_var.get()
        if channel in self.channels:
            freq = self.channels[channel]
            self.status_label.config(text=f"Tuned to {channel} ({freq} MHz)")
    
    def update_time(self):
        """Update time display"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def save_mock_log(self):
        """Save mock signal log"""
        messagebox.showinfo("Mock Function", "Save Signal Log - Multi-Video Mockup\nThis would save signal data to a file.")
    
    def load_mock_config(self):
        """Load mock configuration"""
        messagebox.showinfo("Mock Function", "Load Configuration - Multi-Video Mockup\nThis would load settings from a file.")
    
    def calibrate_mock(self):
        """Mock RSSI calibration"""
        messagebox.showinfo("Mock Function", "RSSI Calibration - Multi-Video Mockup\nThis would calibrate RSSI readings.")
    
    def test_mock_video(self):
        """Mock video test"""
        messagebox.showinfo("Mock Function", "Video Test - Multi-Video Mockup\nThis would test video capture functionality.")
    
    def video_settings(self):
        """Open video settings dialog"""
        messagebox.showinfo("Video Settings", "Video settings dialog coming soon!")
    
    def show_mock_system_info(self):
        """Show mock system information"""
        info = f"""
System Information - Multi-Video Mockup:
- Raspberry Pi 4 Model B (Simulated)
- RX5808 5.8GHz Receiver (Simulated)
- USB Video DVR (Simulated)
- Python 3.8.5
- OpenCV 4.5.1
- Frequency Range: 5245-5945 MHz (700 MHz)
- Total Channels: {len(self.channels)}
- Current Scan Mode: {self.scan_modes[self.current_scan_mode]['name']}
- Detected Signals: {len(self.detected_signals)} (Mock)
- Active Video Streams: {len(self.video_streams)}
- Max Video Streams: {self.max_video_streams}
        """
        messagebox.showinfo("System Info", info)
    
    def show_about(self):
        """Show about dialog"""
        about_text = f"""
Raspberry Pi RX5808 5.8GHz Scanner
Multi-Video Interface Mockup v3.0

This is a demonstration of the scanner interface with multi-video support.
All data shown is simulated for preview purposes.

Features demonstrated:
- Extended 5.8GHz frequency range (5245-5945 MHz)
- {len(self.channels)} total channels across 5 frequency bands
- Multi-video display system (up to {self.max_video_streams} streams)
- Dynamic video layout based on number of streams
- Signal detection and display with band identification
- Video capture simulation with overlay information
- Multiple scan modes (Full Range, Racing Only, Long Range Only)
- Configuration management
- Signal logging

Video Layout:
- 1 stream: Full screen
- 2 streams: Side by side
- 3-4 streams: 2x2 grid
- Each stream shows channel info and timestamp

Frequency Bands:
- Racing: 5725-5865 MHz (8 channels)
- Long Range: 5645-5945 MHz (8 channels)
- Low Band: 5485-5625 MHz (8 channels)
- Ultra Low: 5325-5465 MHz (8 channels)
- Extended: 5245-5305 MHz (4 channels)

For actual use, connect real hardware and run the main scanner.
        """
        messagebox.showinfo("About", about_text)
    
    def run(self):
        """Start the mockup application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Mockup stopped by user")

def main():
    print("🚁 Starting Raspberry Pi RX5808 Scanner Multi-Video Interface Mockup")
    print("=" * 70)
    print("This is a demonstration of the scanner interface with multi-video support.")
    print("All data shown is simulated for preview purposes.")
    print("Frequency Range: 5245-5945 MHz (700 MHz bandwidth)")
    print("Total Channels: 36")
    print("Max Video Streams: 4")
    print("=" * 70)
    
    mockup = ScannerInterfaceMockup()
    mockup.run()

if __name__ == "__main__":
    main() 