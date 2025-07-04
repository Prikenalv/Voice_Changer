import soundfile as sf
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional, Tuple
import os
import librosa

class FileOperations:
    def __init__(self):
        """Initialize the file operations handler"""
        self.supported_formats = {
            'WAV': '*.wav',
            'FLAC': '*.flac',
            'OGG': '*.ogg',
            'AIFF': '*.aiff',
            'MP3': '*.mp3',
            'All Audio Files': '*.wav;*.flac;*.ogg;*.aiff;*.mp3'
        }
        
        # Create root window for file dialogs (hidden)
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the root window
    
    def import_audio(self) -> Tuple[Optional[np.ndarray], Optional[int]]:
        """
        Import audio file using file dialog
        
        Returns:
            Tuple of (audio_data, sample_rate) or (None, None) if cancelled
        """
        try:
            # Create file dialog
            file_path = filedialog.askopenfilename(
                title="Import Audio File",
                filetypes=[
                    ("WAV files", "*.wav"),
                    ("FLAC files", "*.flac"),
                    ("OGG files", "*.ogg"),
                    ("AIFF files", "*.aiff"),
                    ("MP3 files", "*.mp3"),
                    ("All supported files", "*.wav;*.flac;*.ogg;*.aiff;*.mp3"),
                    ("All files", "*.*")
                ]
            )
            
            if not file_path:
                return None, None
            
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.mp3':
                # Use librosa to load mp3
                audio_data, sample_rate = librosa.load(file_path, sr=None, mono=True)
                sample_rate = int(sample_rate)
            else:
                # Use soundfile for other formats
                audio_data, sample_rate = sf.read(file_path)
                
                # Convert to mono if stereo
                if len(audio_data.shape) > 1:
                    audio_data = np.mean(audio_data, axis=1)
                
                # Normalize to float32 range (-1.0 to 1.0)
                if audio_data.dtype != np.float32:
                    if audio_data.dtype == np.int16:
                        audio_data = audio_data.astype(np.float32) / 32768.0
                    elif audio_data.dtype == np.int32:
                        audio_data = audio_data.astype(np.float32) / 2147483648.0
                    else:
                        audio_data = audio_data.astype(np.float32)
            
            print(f"Imported: {os.path.basename(file_path)}")
            print(f"Sample rate: {sample_rate} Hz")
            print(f"Duration: {len(audio_data) / sample_rate:.2f} seconds")
            
            return audio_data, sample_rate
            
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import audio file:\n{str(e)}")
            return None, None
    
    def export_audio(self, audio_data: np.ndarray, sample_rate: int, 
                    filename: Optional[str] = None, format: str = "WAV") -> bool:
        """
        Export audio data to file
        
        Args:
            audio_data: Audio data to export
            sample_rate: Sample rate of the audio
            filename: Optional filename, if None shows file dialog
            format: Export format ("WAV", "MP3", "FLAC", "OGG", "AIFF")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if filename is None:
                # Set default extension based on format
                format_extensions = {
                    "WAV": ".wav",
                    "MP3": ".mp3",
                    "FLAC": ".flac",
                    "OGG": ".ogg",
                    "AIFF": ".aiff"
                }
                
                # Set filetypes based on format
                if format == "MP3":
                    filetypes = [
                        ("MP3 files", "*.mp3"),
                        ("All files", "*.*")
                    ]
                    default_ext = ".mp3"
                else:
                    filetypes = [
                        ("WAV files", "*.wav"),
                        ("FLAC files", "*.flac"),
                        ("OGG files", "*.ogg"),
                        ("AIFF files", "*.aiff"),
                        ("All files", "*.*")
                    ]
                    default_ext = format_extensions.get(format, ".wav")
                
                # Create file dialog for export
                filename = filedialog.asksaveasfilename(
                    title=f"Export Audio File as {format}",
                    defaultextension=default_ext,
                    filetypes=filetypes
                )
            
            if not filename:
                return False
            
            # Ensure audio data is in the correct format
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Clip audio to prevent distortion
            audio_data = np.clip(audio_data, -1.0, 1.0)
            
            # Get file extension
            ext = os.path.splitext(filename)[1].lower()
            
            # Export based on format
            if format.upper() == "MP3" or ext == ".mp3":
                # For MP3 export, we need to use a different approach
                # since soundfile doesn't support MP3 writing
                self._export_mp3(audio_data, sample_rate, filename)
            else:
                # Use soundfile for other formats
                sf.write(filename, audio_data, sample_rate)
            
            print(f"Exported: {os.path.basename(filename)}")
            print(f"Sample rate: {sample_rate} Hz")
            print(f"Duration: {len(audio_data) / sample_rate:.2f} seconds")
            
            messagebox.showinfo("Export Success", f"Audio exported successfully to:\n{filename}")
            return True
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export audio file:\n{str(e)}")
            return False
    
    def _export_mp3(self, audio_data: np.ndarray, sample_rate: int, filename: str):
        """
        Export audio data as MP3 file
        
        Args:
            audio_data: Audio data to export
            sample_rate: Sample rate of the audio
            filename: Output filename
        """
        try:
            # Try using pydub for MP3 export
            try:
                from pydub import AudioSegment
                from pydub.utils import make_chunks
                
                # Convert numpy array to AudioSegment
                # First convert to int16 format for pydub
                audio_int16 = (audio_data * 32767).astype(np.int16)
                
                # Create AudioSegment
                audio_segment = AudioSegment(
                    audio_int16.tobytes(),
                    frame_rate=sample_rate,
                    sample_width=2,  # 16-bit
                    channels=1  # mono
                )
                
                # Export as MP3
                audio_segment.export(filename, format="mp3", bitrate="192k")
                return
                
            except ImportError:
                # Fallback: Try using librosa
                try:
                    import librosa
                    
                    # Use librosa to save as MP3 (requires ffmpeg)
                    # First save as temporary WAV, then convert
                    temp_wav = filename.replace('.mp3', '_temp.wav')
                    sf.write(temp_wav, audio_data, sample_rate)
                    
                    # Use librosa to convert to MP3
                    # This requires ffmpeg to be installed
                    import subprocess
                    
                    # Use ffmpeg to convert WAV to MP3
                    cmd = [
                        'ffmpeg', '-i', temp_wav, '-acodec', 'mp3', 
                        '-ab', '192k', '-y', filename
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    # Clean up temporary file
                    if os.path.exists(temp_wav):
                        os.remove(temp_wav)
                    
                    if result.returncode != 0:
                        raise Exception(f"FFmpeg conversion failed: {result.stderr}")
                    
                    return
                    
                except (ImportError, FileNotFoundError, Exception):
                    # Final fallback: Save as WAV with MP3 extension and warn user
                    sf.write(filename, audio_data, sample_rate)
                    messagebox.showwarning(
                        "MP3 Export Warning",
                        "MP3 export libraries not available. "
                        "File saved as WAV format with .mp3 extension.\n\n"
                        "To enable proper MP3 export, install:\n"
                        "- pydub: pip install pydub\n"
                        "- ffmpeg: Download from https://ffmpeg.org/"
                    )
                    return
                    
        except Exception as e:
            # If all else fails, save as WAV
            sf.write(filename.replace('.mp3', '.wav'), audio_data, sample_rate)
            raise Exception(f"MP3 export failed, saved as WAV instead. Error: {str(e)}")
    
    def get_audio_info(self, file_path: str) -> Optional[dict]:
        """
        Get information about an audio file
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dictionary with audio file information or None if error
        """
        try:
            # Get file info without loading the entire file
            info = sf.info(file_path)
            
            return {
                'filename': os.path.basename(file_path),
                'filepath': file_path,
                'sample_rate': info.samplerate,
                'duration': info.duration,
                'channels': info.channels,
                'format': info.format,
                'subtype': info.subtype,
                'frames': info.frames
            }
            
        except Exception as e:
            print(f"Error getting audio info: {e}")
            return None
    
    def batch_import(self, directory: str) -> list:
        """
        Import all supported audio files from a directory
        
        Args:
            directory: Directory path to scan
            
        Returns:
            List of tuples (file_path, audio_data, sample_rate)
        """
        imported_files = []
        
        try:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                
                # Check if file is supported
                if any(filename.lower().endswith(ext.replace('*', '')) 
                      for ext in self.supported_formats.values()):
                    
                    try:
                        audio_data, sample_rate = sf.read(file_path)
                        
                        # Convert to mono if stereo
                        if len(audio_data.shape) > 1:
                            audio_data = np.mean(audio_data, axis=1)
                        
                        # Normalize
                        if audio_data.dtype != np.float32:
                            audio_data = audio_data.astype(np.float32)
                        
                        imported_files.append((file_path, audio_data, sample_rate))
                        print(f"Batch imported: {filename}")
                        
                    except Exception as e:
                        print(f"Failed to import {filename}: {e}")
            
            print(f"Batch import completed: {len(imported_files)} files imported")
            return imported_files
            
        except Exception as e:
            print(f"Batch import error: {e}")
            return []
    
    def save_preset(self, preset_name: str, preset_config: dict, 
                   filename: Optional[str] = None) -> bool:
        """
        Save a preset configuration to file
        
        Args:
            preset_name: Name of the preset
            preset_config: Preset configuration dictionary
            filename: Optional filename, if None uses preset name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if filename is None:
                filename = f"{preset_name.lower().replace(' ', '_')}.json"
            
            import json
            
            # Add metadata
            preset_data = {
                'name': preset_name,
                'config': preset_config,
                'created': str(np.datetime64('now')),
                'version': '1.0'
            }
            
            with open(filename, 'w') as f:
                json.dump(preset_data, f, indent=2)
            
            print(f"Preset saved: {filename}")
            return True
            
        except Exception as e:
            print(f"Error saving preset: {e}")
            return False
    
    def load_preset(self, filename: str) -> Optional[dict]:
        """
        Load a preset configuration from file
        
        Args:
            filename: Path to the preset file
            
        Returns:
            Preset configuration dictionary or None if error
        """
        try:
            import json
            
            with open(filename, 'r') as f:
                preset_data = json.load(f)
            
            print(f"Preset loaded: {filename}")
            return preset_data.get('config', {})
            
        except Exception as e:
            print(f"Error loading preset: {e}")
            return None
    
    def create_audio_preview(self, audio_data: np.ndarray, sample_rate: int, 
                           duration: float = 5.0) -> np.ndarray:
        """
        Create a preview of audio data (first N seconds)
        
        Args:
            audio_data: Full audio data
            sample_rate: Sample rate
            duration: Preview duration in seconds
            
        Returns:
            Preview audio data
        """
        preview_samples = int(duration * sample_rate)
        return audio_data[:preview_samples]
    
    def normalize_audio_file(self, input_path: str, output_path: str) -> bool:
        """
        Normalize an audio file (adjust volume to prevent clipping)
        
        Args:
            input_path: Input audio file path
            output_path: Output audio file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read audio file
            audio_data, sample_rate = sf.read(input_path)
            
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Normalize
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val
            
            # Write normalized file
            sf.write(output_path, audio_data, sample_rate)
            
            print(f"Normalized: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
            return True
            
        except Exception as e:
            print(f"Error normalizing audio: {e}")
            return False
    
    def get_supported_formats(self) -> dict:
        """
        Get list of supported audio formats
        
        Returns:
            Dictionary of supported formats
        """
        return self.supported_formats.copy()
    
    def cleanup(self):
        """Clean up resources"""
        try:
            self.root.destroy()
        except:
            pass