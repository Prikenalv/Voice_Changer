import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import customtkinter as ctk
from typing import Optional

class AudioVisualizer:
    def __init__(self, max_points: int = 1000):
        """
        Initialize the audio visualizer
        
        Args:
            max_points: Maximum number of points to display in the waveform
        """
        self.max_points = max_points
        self.fig = None
        self.ax = None
        self.canvas = None
        self.line = None
        self.animation = None
        
        # Data storage
        self.audio_data = None
        self.sample_rate = None
        self.time_axis = None
        
        # Setup the plot
        self._setup_plot()
    
    def _setup_plot(self):
        """Setup the matplotlib figure and axes"""
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(10, 4), facecolor='black')
        self.fig.patch.set_facecolor('black')
        self.ax.set_facecolor('black')
        self.ax.grid(True, alpha=0.3, color='gray')
        self.ax.set_xlabel('Time (s)', color='white')
        self.ax.set_ylabel('Amplitude', color='white')
        self.ax.set_title('Audio Waveform', color='white', fontsize=14, fontweight='bold')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.tick_params(colors='white')
        # Force green line
        self.line, = self.ax.plot([], [], color='lime', linewidth=2.0, alpha=0.9)
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(-1, 1)
        self.fig.tight_layout()
    
    def create_canvas(self, parent) -> ctk.CTkFrame:
        print("[Visualizer] Creating new canvas")
        # Create a frame to hold the canvas
        canvas_frame = ctk.CTkFrame(parent, fg_color="black")
        
        # Create the matplotlib canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_frame)
        self.canvas.draw()
        
        # Get the TK widget and configure it
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.config(bg="black", highlightthickness=0)
        canvas_widget.pack(fill="both", expand=True)
        
        # Set a reasonable size
        canvas_widget.configure(width=800, height=300)
        
        return canvas_frame  # Return the frame, not the widget
    
    def update_waveform(self, audio_data: np.ndarray, sample_rate: int):
        try:
            # Ensure audio data is in correct format
            audio_data = np.asarray(audio_data, dtype=np.float32)
            audio_data = np.ravel(audio_data)  # Flatten to 1D
            
            print(f"Updating waveform with {len(audio_data)} samples")
            
            # Store the data
            self.audio_data = audio_data
            self.sample_rate = sample_rate
            
            # Calculate duration and time axis
            duration = len(audio_data) / sample_rate
            self.time_axis = np.linspace(0, duration, len(audio_data))
            
            # Downsample if too many points
            if len(audio_data) > self.max_points:
                step = len(audio_data) // self.max_points
                audio_data = audio_data[::step]
                time_axis = self.time_axis[::step]
            else:
                time_axis = self.time_axis
            
            # Update the plot
            self.line.set_data(time_axis, audio_data)
            
            # Set axis limits with some padding
            x_padding = duration * 0.05
            y_padding = 0.1
            self.ax.set_xlim(0 - x_padding, duration + x_padding)
            
            if len(audio_data) > 0:
                y_min = min(-0.1, audio_data.min() - y_padding)
                y_max = max(0.1, audio_data.max() + y_padding)
                self.ax.set_ylim(y_min, y_max)
            
            # Redraw the canvas
            if self.canvas:
                self.canvas.draw_idle()
                print("Waveform updated successfully")
                
        except Exception as e:
            print(f"Error updating waveform: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def update_realtime(self, audio_chunk: np.ndarray, sample_rate: int):
        """
        Update the waveform in real-time during recording
        
        Args:
            audio_chunk: New audio chunk
            sample_rate: Sample rate of the audio
        """
        try:
            # Append new chunk to existing data
            if self.audio_data is None:
                self.audio_data = audio_chunk
            else:
                self.audio_data = np.concatenate([self.audio_data, audio_chunk])
            
            # Keep only the last N points for real-time display
            max_points = self.max_points
            if len(self.audio_data) > max_points:
                self.audio_data = self.audio_data[-max_points:]
            
            # Create time axis for the visible portion
            duration = len(self.audio_data) / sample_rate
            time_axis = np.linspace(0, duration, len(self.audio_data))
            
            # Update the plot
            self.line.set_data(time_axis, self.audio_data)  # type: ignore
            
            # Update axis limits
            self.ax.set_xlim(0, duration)  # type: ignore
            if len(self.audio_data) > 0:
                self.ax.set_ylim(self.audio_data.min() - 0.1, self.audio_data.max() + 0.1)  # type: ignore
            
            # Redraw the canvas
            if self.canvas:
                self.canvas.draw_idle()
                
        except Exception as e:
            print(f"Error updating real-time waveform: {e}")
    
    def clear_waveform(self):
        """Clear the waveform display"""
        try:
            self.audio_data = None
            self.sample_rate = None
            self.time_axis = None
            
            # Clear the line
            self.line.set_data([], [])  # type: ignore
            
            # Reset axis limits
            self.ax.set_xlim(0, 1)  # type: ignore
            self.ax.set_ylim(-1, 1)  # type: ignore
            
            # Redraw the canvas
            if self.canvas:
                self.canvas.draw_idle()
                
        except Exception as e:
            print(f"Error clearing waveform: {e}")
    
    def set_color(self, color: str):
        """
        Set the waveform color
        
        Args:
            color: Color string (e.g., 'green', 'red', 'blue')
        """
        try:
            self.line.set_color(color)  # type: ignore
            if self.canvas:
                self.canvas.draw_idle()
        except Exception as e:
            print(f"Error setting color: {e}")
    
    def set_line_width(self, width: float):
        """
        Set the waveform line width
        
        Args:
            width: Line width in points
        """
        try:
            self.line.set_linewidth(width)  # type: ignore
            if self.canvas:
                self.canvas.draw_idle()
        except Exception as e:
            print(f"Error setting line width: {e}")
    
    def set_max_points(self, max_points: int):
        """
        Set the maximum number of points to display
        
        Args:
            max_points: Maximum number of points
        """
        self.max_points = max_points
    
    def get_audio_data(self) -> Optional[np.ndarray]:
        """Get the current audio data"""
        return self.audio_data
    
    def get_sample_rate(self) -> Optional[int]:
        """Get the current sample rate"""
        return self.sample_rate
    
    def get_duration(self) -> Optional[float]:
        """Get the duration of the current audio in seconds"""
        if self.audio_data is not None and self.sample_rate is not None:
            return len(self.audio_data) / self.sample_rate
        return None
    
    def save_plot(self, filename: str):
        """
        Save the current plot as an image
        
        Args:
            filename: Output filename
        """
        try:
            self.fig.savefig(filename, facecolor='black', edgecolor='none', bbox_inches='tight', dpi=300)  # type: ignore
            print(f"Plot saved as {filename}")
        except Exception as e:
            print(f"Error saving plot: {e}")
    
    def create_spectrogram(self, audio_data: np.ndarray, sample_rate: int):
        """
        Create and display a spectrogram of the audio data
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio
        """
        try:
            # Clear current plot
            self.ax.clear()  # type: ignore
            
            # Create spectrogram
            self.ax.specgram(audio_data, Fs=sample_rate, cmap='viridis')  # type: ignore
            
            # Configure axes
            self.ax.set_xlabel('Time (s)', color='white')  # type: ignore
            self.ax.set_ylabel('Frequency (Hz)', color='white')  # type: ignore
            self.ax.set_title('Audio Spectrogram', color='white', fontsize=14, fontweight='bold')  # type: ignore
            
            # Set axis colors
            self.ax.spines['bottom'].set_color('white')  # type: ignore
            self.ax.spines['top'].set_color('white')  # type: ignore
            self.ax.spines['left'].set_color('white')  # type: ignore
            self.ax.spines['right'].set_color('white')  # type: ignore
            self.ax.tick_params(colors='white')  # type: ignore
            
            # Redraw the canvas
            if self.canvas:
                self.canvas.draw_idle()
                
        except Exception as e:
            print(f"Error creating spectrogram: {e}")
    
    def switch_to_waveform(self):
        """Switch back to waveform display"""
        try:
            # Clear current plot
            self.ax.clear()  # type: ignore
            
            # Recreate the waveform plot
            self._setup_plot()
            
            # Update with current data if available
            if self.audio_data is not None and self.sample_rate is not None:
                self.update_waveform(self.audio_data, self.sample_rate)
                
        except Exception as e:
            print(f"Error switching to waveform: {e}") 