import sounddevice as sd
import numpy as np
import threading
import queue
from typing import Optional, Tuple

class AudioRecorder:
    def __init__(self, audio_queue: queue.Queue, sample_rate: int = 44100, channels: int = 1):
        self.audio_queue = audio_queue
        self.sample_rate = sample_rate
        self.channels = channels
        
        # Recording state
        self.is_recording = False
        self.recording_thread = None
        self.audio_buffer = []
        self.stream = None
        
        # Playback state
        self.is_playing = False
        self.playback_thread = None
        
        # Audio device settings
        self.input_device = None
        self.output_device = None
        
        # Initialize audio devices
        self._setup_audio_devices()
    
    def _setup_audio_devices(self):
        """Setup audio input and output devices"""
        try:
            devices = sd.query_devices()
            default_input = sd.default.device[0]
            default_output = sd.default.device[1]
            
            self.input_device = default_input
            self.output_device = default_output
            print(f"Using input device: {devices[default_input]['name']}")
            print(f"Using output device: {devices[default_output]['name']}")
            
        except Exception as e:
            print(f"Error setting up audio devices: {e}")
    
    def start_recording(self):
        """Start recording audio from microphone"""
        if self.is_recording:
            return
            
        self.is_recording = True
        self.audio_buffer = []
        self.recording_thread = threading.Thread(target=self._record_audio, daemon=True)
        self.recording_thread.start()
    
    def stop_recording(self):
        """Stop recording audio"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        
        if self.recording_thread:
            self.recording_thread.join(timeout=1.0)
        
        if self.stream:
            self.stream.close()
            self.stream = None
        
        # Combine all recorded audio chunks
        if self.audio_buffer:
            recorded_audio = np.concatenate(self.audio_buffer)
            self.audio_queue.put(recorded_audio)
    
    def _record_audio(self):
        try:
            def callback(indata, frames, time, status):
                if self.is_recording:
                    self.audio_buffer.append(indata.copy())
            
            self.stream = sd.InputStream(
                device=self.input_device,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=callback,
                dtype=np.float32
            )
            
            with self.stream:
                print("Recording started...")
                while self.is_recording:
                    sd.sleep(100)
                print("Recording stopped.")
                
        except Exception as e:
            print(f"Recording error: {e}")
            self.is_recording = False
    
    def play_audio(self, audio_data: np.ndarray):
        """Play audio data through speakers"""
        if self.is_playing:
            return
            
        self.is_playing = True
        
        # Start playback thread
        self.playback_thread = threading.Thread(
            target=self._play_audio, 
            args=(audio_data,), 
            daemon=True
        )
        self.playback_thread.start()
    
    def stop_playback(self):
        """Stop audio playback"""
        if not self.is_playing:
            return
            
        self.is_playing = False
        
        if self.playback_thread:
            self.playback_thread.join(timeout=1.0)
    
    def _play_audio(self, audio_data: np.ndarray):
        try:
            if len(audio_data.shape) == 1:
                audio_data = audio_data.reshape(-1, 1)
                
            with sd.OutputStream(
                device=self.output_device,
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32
            ) as stream:
                stream.write(audio_data)
                
            self.is_playing = False
        except Exception as e:
            print(f"Playback error: {e}")
            self.is_playing = False
    
    # ... (rest of the methods remain the same)
    
    def get_audio_devices(self) -> Tuple[list, list]:
        """Get available input and output devices"""
        try:
            devices = sd.query_devices()
            input_devices = []
            output_devices = []
            
            for i, device in enumerate(devices):
                if isinstance(device, dict) and device.get('max_inputs', 0) > 0:
                    input_devices.append((i, device['name']))
                if isinstance(device, dict) and device.get('max_outputs', 0) > 0:
                    output_devices.append((i, device['name']))
            
            return input_devices, output_devices
            
        except Exception as e:
            print(f"Error getting audio devices: {e}")
            return [], []
    
    def set_input_device(self, device_index: int):
        """Set the input device for recording"""
        try:
            devices = sd.query_devices()
            if 0 <= device_index < len(devices):
                device = devices[device_index]
                if isinstance(device, dict) and device.get('max_inputs', 0) > 0:
                    self.input_device = device_index
                    print(f"Input device set to: {device['name']}")
                else:
                    print("Selected device does not support input")
            else:
                print("Invalid device index")
        except Exception as e:
            print(f"Error setting input device: {e}")
    
    def set_output_device(self, device_index: int):
        """Set the output device for playback"""
        try:
            devices = sd.query_devices()
            if 0 <= device_index < len(devices):
                device = devices[device_index]
                if isinstance(device, dict) and device.get('max_outputs', 0) > 0:
                    self.output_device = device_index
                    print(f"Output device set to: {device['name']}")
                else:
                    print("Selected device does not support output")
            else:
                print("Invalid device index")
        except Exception as e:
            print(f"Error setting output device: {e}")
    
    def get_recording_status(self) -> bool:
        """Get current recording status"""
        return self.is_recording
    
    def get_playback_status(self) -> bool:
        """Get current playback status"""
        return self.is_playing
    
    def get_sample_rate(self) -> int:
        """Get current sample rate"""
        return self.sample_rate
    
    def set_sample_rate(self, sample_rate: int):
        """Set the sample rate for recording and playback"""
        if sample_rate > 0:
            self.sample_rate = sample_rate
            print(f"Sample rate set to: {sample_rate} Hz")
        else:
            print("Invalid sample rate")
    
    def pause_recording(self):
        self.is_paused = True

    def resume_recording(self):
        self.is_paused = False

    def pause_playback(self):
        self.is_playback_paused = True

    def resume_playback(self):
        self.is_playback_paused = False