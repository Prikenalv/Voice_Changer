import numpy as np
from scipy import signal
from scipy.signal import butter, filtfilt
from typing import Optional

class DSPProcessor:
    def __init__(self):
        """Initialize the DSP processor"""
        pass
    
    def process_audio(self, audio_data: np.ndarray, gain: float = 1.0, echo: float = 0.0,
                     lowpass: bool = False, highpass: bool = False, 
                     robot: bool = False, reverb: bool = False,
                     pitch: float = 1.0, chorus: bool = False, distortion: float = 0.0) -> np.ndarray:
        """
        Process audio with multiple effects
        
        Args:
            audio_data: Input audio data
            gain: Gain multiplier (0.1 to 3.0)
            echo: Echo intensity (0.0 to 0.8)
            lowpass: Apply low-pass filter
            highpass: Apply high-pass filter
            robot: Apply robot voice effect
            reverb: Apply reverb effect
            pitch: Pitch shift factor (0.5 = octave down, 2.0 = octave up)
            chorus: Apply chorus effect
            distortion: Distortion amount (0.0 to 1.0)
            
        Returns:
            Processed audio data
        """
        # Flatten to 1D
        audio_data = np.ravel(audio_data)
        processed_audio = audio_data.copy()
        
        # Apply effects in order
        if gain != 1.0:
            processed_audio = self.apply_gain(processed_audio, gain)
        
        if echo > 0.0:
            processed_audio = self.apply_echo(processed_audio, echo)
        
        if lowpass:
            processed_audio = self.apply_lowpass_filter(processed_audio)
        
        if highpass:
            processed_audio = self.apply_highpass_filter(processed_audio)
        
        if robot:
            processed_audio = self.apply_robot_voice(processed_audio)
        
        if reverb:
            processed_audio = self.apply_reverb(processed_audio)
        
        if pitch != 1.0:
            processed_audio = self.apply_pitch_shift(processed_audio, pitch)
        
        if chorus:
            processed_audio = self.apply_chorus(processed_audio)
        
        if distortion > 0.0:
            processed_audio = self.apply_distortion(processed_audio, distortion)
        
        # Ensure audio doesn't clip
        processed_audio = np.clip(processed_audio, -1.0, 1.0)
        
        return processed_audio.astype(np.float32)
    
    def apply_gain(self, audio_data: np.ndarray, gain: float) -> np.ndarray:
        """
        Apply gain (volume) control
        
        Args:
            audio_data: Input audio data
            gain: Gain multiplier
            
        Returns:
            Audio data with applied gain
        """
        return audio_data * gain
    
    def apply_echo(self, audio_data: np.ndarray, echo_intensity: float, 
                  delay_samples: int = 8000, decay: float = 0.5) -> np.ndarray:
        """
        Apply echo effect
        
        Args:
            audio_data: Input audio data
            echo_intensity: Echo intensity (0.0 to 1.0)
            delay_samples: Delay in samples (default: ~0.18s at 44.1kHz)
            decay: Echo decay factor
            
        Returns:
            Audio data with echo effect
        """
        if echo_intensity == 0.0:
            return audio_data
        
        # Create delayed version
        delayed = np.zeros_like(audio_data)
        delayed[delay_samples:] = audio_data[:-delay_samples] * decay
        
        # Mix original and delayed audio
        result = audio_data + delayed * echo_intensity
        
        return result
    
    def apply_lowpass_filter(self, audio_data: np.ndarray, 
                           cutoff_freq: float = 1000.0, sample_rate: int = 44100) -> np.ndarray:
        """
        Apply low-pass filter (muffle effect)
        
        Args:
            audio_data: Input audio data
            cutoff_freq: Cutoff frequency in Hz
            sample_rate: Audio sample rate
            
        Returns:
            Filtered audio data
        """
        # Design Butterworth low-pass filter
        nyquist = sample_rate / 2
        normal_cutoff = cutoff_freq / nyquist
        b, a= butter(4, normal_cutoff, btype='low', analog=False)
        
        
        # Apply filter
        filtered = filtfilt(b, a, audio_data)
        
        return filtered.astype(np.float32)
    
    def apply_highpass_filter(self, audio_data: np.ndarray, 
                            cutoff_freq: float = 300.0, sample_rate: int = 44100) -> np.ndarray:
        """
        Apply high-pass filter (tinny/radio effect)
        
        Args:
            audio_data: Input audio data
            cutoff_freq: Cutoff frequency in Hz
            sample_rate: Audio sample rate
            
        Returns:
            Filtered audio data
        """
        # Design Butterworth high-pass filter
        nyquist = sample_rate / 2
        normal_cutoff = cutoff_freq / nyquist
        b, a = butter(4, normal_cutoff, btype='high', analog=False)
        
        # Apply filter
        filtered = filtfilt(b, a, audio_data)
        
        return filtered.astype(np.float32)
    
    def apply_robot_voice(self, audio_data: np.ndarray, 
                         sample_rate: int = 44100) -> np.ndarray:
        """
        Apply robot voice effect (rectification + filtering)
        
        Args:
            audio_data: Input audio data
            sample_rate: Audio sample rate
            
        Returns:
            Audio data with robot effect
        """
        # Full-wave rectification
        rectified = np.abs(audio_data)
        
        # Apply low-pass filter to smooth the rectified signal
        nyquist = sample_rate / 2
        normal_cutoff = 800.0 / nyquist  # 800 Hz cutoff
        b, a = butter(4, normal_cutoff, btype='low', analog=False)
        
        smoothed = filtfilt(b, a, rectified)
        
        # Add some harmonics for robotic sound
        harmonics = np.sin(2 * np.pi * 50 * np.arange(len(smoothed)) / sample_rate)
        result = smoothed + 0.3 * harmonics * smoothed
        
        return result.astype(np.float32)
    
    def apply_reverb(self, audio_data: np.ndarray, 
                    room_size: float = 0.8, damping: float = 0.5) -> np.ndarray:
        """
        Apply reverb effect (chain of fading echoes)
        
        Args:
            audio_data: Input audio data
            room_size: Room size (0.0 to 1.0)
            damping: Damping factor (0.0 to 1.0)
            
        Returns:
            Audio data with reverb effect
        """
        if room_size == 0.0:
            return audio_data
        
        # Create multiple delayed echoes
        delays = [int(8000 * room_size), int(12000 * room_size), int(16000 * room_size)]
        decays = [0.6 * damping, 0.4 * damping, 0.2 * damping]
        
        result = audio_data.copy()
        
        for delay, decay in zip(delays, decays):
            if delay < len(audio_data):
                delayed = np.zeros_like(audio_data)
                delayed[delay:] = audio_data[:-delay] * decay
                result += delayed
        
        return result
    
    def apply_pitch_shift(self, audio_data: np.ndarray, 
                         pitch_factor: float, sample_rate: int = 44100) -> np.ndarray:
        """
        Apply pitch shifting effect
        
        Args:
            audio_data: Input audio data
            pitch_factor: Pitch shift factor (0.5 = octave down, 2.0 = octave up)
            sample_rate: Audio sample rate
            
        Returns:
            Pitch-shifted audio data
        """
        # Flatten to 1D
        audio_data = np.ravel(audio_data)
        
        # Resample the audio
        new_length = int(len(audio_data) / pitch_factor)
        indices = np.linspace(0, len(audio_data) - 1, new_length)
        
        # Linear interpolation
        result = np.interp(indices, np.arange(len(audio_data)), audio_data)
        return result.astype(np.float32)
    
    def apply_chorus(self, audio_data: np.ndarray, 
                    depth: float = 0.002, rate: float = 1.5, 
                    sample_rate: int = 44100) -> np.ndarray:
        """
        Apply chorus effect
        
        Args:
            audio_data: Input audio data
            depth: Chorus depth in seconds
            rate: Chorus rate in Hz
            sample_rate: Audio sample rate
            
        Returns:
            Audio data with chorus effect
        """
        # Create modulation signal
        t = np.arange(len(audio_data)) / sample_rate
        modulation = depth * np.sin(2 * np.pi * rate * t)
        
        # Create delayed version with modulation
        max_delay = int(depth * sample_rate)
        result = np.zeros_like(audio_data)
        
        for i in range(len(audio_data)):
            delay = int(modulation[i] * sample_rate)
            if i + delay < len(audio_data):
                result[i] = audio_data[i] + 0.5 * audio_data[i + delay]
        
        return result
    
    def apply_distortion(self, audio_data: np.ndarray, 
                        amount: float = 0.5) -> np.ndarray:
        """
        Apply distortion effect
        
        Args:
            audio_data: Input audio data
            amount: Distortion amount (0.0 to 1.0)
            
        Returns:
            Distorted audio data
        """
        if amount == 0.0:
            return audio_data
        
        # Apply soft clipping
        threshold = 1.0 - amount
        result = np.where(
            np.abs(audio_data) > threshold,
            np.sign(audio_data) * (threshold + (1.0 - threshold) * 
                                 np.tanh((np.abs(audio_data) - threshold) / (1.0 - threshold))),
            audio_data
        )
        
        return result
    
    def apply_compression(self, audio_data: np.ndarray, 
                         threshold: float = 0.5, ratio: float = 4.0) -> np.ndarray:
        """
        Apply dynamic range compression
        
        Args:
            audio_data: Input audio data
            threshold: Compression threshold
            ratio: Compression ratio
            
        Returns:
            Compressed audio data
        """
        # Calculate compression
        result = np.where(
            np.abs(audio_data) > threshold,
            np.sign(audio_data) * (threshold + (np.abs(audio_data) - threshold) / ratio),
            audio_data
        )
        
        return result
    
    def normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Normalize audio to prevent clipping
        
        Args:
            audio_data: Input audio data
            
        Returns:
            Normalized audio data
        """
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            return audio_data / max_val
        return audio_data
    
    def get_audio_stats(self, audio_data: np.ndarray) -> dict:
        """
        Get statistics about the audio data
        
        Args:
            audio_data: Input audio data
            
        Returns:
            Dictionary with audio statistics
        """
        return {
            'length': len(audio_data),
            'duration': len(audio_data) / 44100,  # Assuming 44.1kHz
            'max_amplitude': np.max(np.abs(audio_data)),
            'rms': np.sqrt(np.mean(audio_data**2)),
            'mean': np.mean(audio_data),
            'std': np.std(audio_data)
        } 