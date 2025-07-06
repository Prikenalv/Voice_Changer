import customtkinter as ctk
import threading
import queue
from recording import AudioRecorder
from visualizer import AudioVisualizer
from dsp import DSPProcessor
from presets import PresetManager
from fileops import FileOperations
import os
from tkinter import filedialog, messagebox
import numpy as np

class VoiceChangerApp:
    def __init__(self):
        # Configure customtkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize main window
        self.root = ctk.CTk()
        self.root.title("Voice Changer DSP Tool")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # --- Add scrollable canvas for main_frame ---
        self.canvas = ctk.CTkCanvas(self.root, borderwidth=0, highlightthickness=0, bg="#222222")
        self.v_scrollbar = ctk.CTkScrollbar(self.root, orientation="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set)
        self.v_scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.main_frame = ctk.CTkFrame(self.canvas)
        self.main_frame_id = self.canvas.create_window((10, 10), window=self.main_frame, anchor="nw")
        self.main_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # --- End scrollable setup ---
        
        # Initialize components
        self.audio_queue = queue.Queue()
        self.recorder = AudioRecorder(self.audio_queue)
        self.visualizer = AudioVisualizer()
        self.dsp = DSPProcessor()
        self.presets = PresetManager()
        self.fileops = FileOperations()
        
        # Audio state
        self.is_recording = False
        self.is_playing = False
        self.current_audio = None
        self.processed_audio = None
        self.sample_rate = 44100  # Default sample rate
        
        # Create GUI
        self.create_widgets()
        
        # Start audio processing thread
        self.audio_thread = threading.Thread(target=self.audio_processing_loop, daemon=True)
        self.audio_thread.start()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        #self.main_frame.configure(padx=10, pady=10)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="🎤 Voice Changer DSP Tool", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(0, 20))

        # Visualizer section
        self.visualizer_frame = ctk.CTkFrame(self.main_frame, fg_color="black")
        self.visualizer_frame.pack(fill="both", expand=True, pady=(0, 10))
        

        self.visualizer_label = ctk.CTkLabel(
            self.visualizer_frame, 
            text="Audio Visualizer", 
            font=ctk.CTkFont(size=16),
            text_color="white"
        )
        self.visualizer_label.pack(pady=(10, 5))

        self.visualizer_canvas = None
        self.create_visualizer_canvas()
        
        # Control panels container
        control_panels = ctk.CTkFrame(self.main_frame)
        control_panels.pack(fill="both", expand=True, pady=(0, 10))
        
        # Left panel - Recording and Effects
        left_panel = ctk.CTkFrame(control_panels)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Recording controls - simplified
        self.recording_frame = ctk.CTkFrame(left_panel)
        self.recording_frame.pack(fill="x", pady=(0, 10))
        
        self.recording_label = ctk.CTkLabel(self.recording_frame, text="Audio Controls", font=ctk.CTkFont(size=16))
        self.recording_label.pack(pady=(0, 10))
        
        record_buttons_frame = ctk.CTkFrame(self.recording_frame)
        record_buttons_frame.pack(pady=5)
        
        self.record_button = ctk.CTkButton(
            record_buttons_frame, 
            text="🎤 Record", 
            command=self.toggle_recording,
            fg_color="red",
            hover_color="darkred",
            width=100
        )
        self.record_button.pack(side="left", padx=5)
        
        self.play_button = ctk.CTkButton(
            record_buttons_frame, 
            text="▶️ Play", 
            command=self.play_audio,
            state="disabled",
            width=100
        )
        self.play_button.pack(side="left", padx=5)
        
        # Add Pause and Resume buttons to record_buttons_frame
        self.pause_button = ctk.CTkButton(
            record_buttons_frame,
            text="⏸️ Pause",
            command=self.pause_action,
            state="disabled",
            width=100
        )
        self.pause_button.pack(side="left", padx=5)
        self.resume_button = ctk.CTkButton(
            record_buttons_frame,
            text="▶️ Resume",
            command=self.resume_action,
            state="disabled",
            width=100
        )
        self.resume_button.pack(side="left", padx=5)
        
        file_buttons_frame = ctk.CTkFrame(self.recording_frame)
        file_buttons_frame.pack(pady=5)
        
        self.import_button = ctk.CTkButton(
            file_buttons_frame, 
            text="📁 Import", 
            command=self.import_audio,
            width=100
        )
        self.import_button.pack(side="left", padx=5)
        
        self.export_button = ctk.CTkButton(
            file_buttons_frame, 
            text="💾 Export", 
            command=self.export_audio,
            state="disabled",
            width=100
        )
        self.export_button.pack(side="left", padx=5)


        # Device IO


        self.device_frame = ctk.CTkFrame(left_panel)
        self.device_frame.pack(fill="both", expand=True, pady=(0, 10))

        self.device_label = ctk.CTkLabel(self.device_frame, text="Devices", font=ctk.CTkFont(size=16))
        self.device_label.pack(pady=(0, 10))

        

        input_frame = ctk.CTkFrame(self.device_frame, fg_color='transparent')
        input_frame.pack(fill='x')

        self.input_label = ctk.CTkLabel(input_frame, text="Input: ", font=ctk.CTkFont(size=16))
        self.input_label.pack(side='left',padx=(0,5))
        # idk happening but it works :D
        input_device, output_device = self.recorder.get_devices()
        input_text = [i[1] for i in input_device]
        output_text = [i[1] for i in output_device]
        # ---------------

        input_current = next((name for i, name in input_device if i == self.recorder.input_device), "None")
        self.input_device_variable = ctk.StringVar(value=input_current)
        self.input_device_menu = ctk.CTkOptionMenu(
            input_frame,
            values= input_text,
            variable=self.input_device_variable,
            command=self.update_device
        )

        self.input_device_menu.pack(fill='x',side='left',expand=True)

        output_frame = ctk.CTkFrame(self.device_frame, fg_color='transparent')
        output_frame.pack(fill='x')

        self.output_label = ctk.CTkLabel(output_frame, text="Output: ", font=ctk.CTkFont(size=16))
        self.output_label.pack(side='left', padx=(0,5))

        output_current = next((name for i, name in output_device if i == self.recorder.output_device), "None")
        self.output_device_variable = ctk.StringVar(value=output_current)
        self.output_device_menu = ctk.CTkOptionMenu(
            output_frame,
            values= output_text,
            variable=self.output_device_variable,
            command=self.update_device
        )

        self.output_device_menu.pack(fill='x',side='left',expand=True)


        
        # Effects
        self.effects_frame = ctk.CTkFrame(left_panel)
        self.effects_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.effects_label = ctk.CTkLabel(self.effects_frame, text="DSP Effects", font=ctk.CTkFont(size=16))
        self.effects_label.pack(pady=(0, 10))
        
        # Gain control
        gain_frame = ctk.CTkFrame(self.effects_frame)
        gain_frame.pack(fill="x", padx=10, pady=5)
        
        self.gain_label = ctk.CTkLabel(gain_frame, text="Gain:")
        self.gain_label.pack(side="left", padx=(10, 5))
        
        self.gain_slider = ctk.CTkSlider(
            gain_frame, 
            from_=1, 
            to=30, 
            number_of_steps=29,
            command=lambda v: self.update_gain(v/10)
        )
        self.gain_slider.pack(side="left", fill="x", expand=True, padx=5)
        self.gain_slider.set(10)  # Default to 1.0
        
        self.gain_value = ctk.CTkLabel(gain_frame, text="1.0x")
        self.gain_value.pack(side="right", padx=(5, 10))
        
        # Echo control
        echo_frame = ctk.CTkFrame(self.effects_frame)
        echo_frame.pack(fill="x", padx=10, pady=5)
        
        self.echo_label = ctk.CTkLabel(echo_frame, text="Echo:")
        self.echo_label.pack(side="left", padx=(10, 5))
        
        self.echo_slider = ctk.CTkSlider(
            echo_frame, 
            from_=0, 
            to=8, 
            number_of_steps=8,
            command=lambda v: self.update_echo(v/10)
        )
        self.echo_slider.pack(side="left", fill="x", expand=True, padx=5)
        
        self.echo_value = ctk.CTkLabel(echo_frame, text="0.0")
        self.echo_value.pack(side="right", padx=(5, 10))
        
        # Pitch shift
        pitch_frame = ctk.CTkFrame(self.effects_frame)
        pitch_frame.pack(fill="x", padx=10, pady=5)
        
        self.pitch_label = ctk.CTkLabel(pitch_frame, text="Pitch Shift:")
        self.pitch_label.pack(side="left", padx=(10, 5))
        
        self.pitch_slider = ctk.CTkSlider(
            pitch_frame,
            from_=5,
            to=20,
            number_of_steps=15,
            command=lambda v: self.update_pitch(v/10)
        )
        self.pitch_slider.pack(side="left", fill="x", expand=True, padx=5)
        self.pitch_slider.set(10)  # Default to 1.0
        
        self.pitch_value = ctk.CTkLabel(pitch_frame, text="1.0x")
        self.pitch_value.pack(side="right", padx=(5, 10))
        
        # Distortion control
        distortion_frame = ctk.CTkFrame(self.effects_frame)
        distortion_frame.pack(fill="x", padx=10, pady=5)
        
        self.distortion_label = ctk.CTkLabel(distortion_frame, text="Distortion:")
        self.distortion_label.pack(side="left", padx=(10, 5))
        
        self.distortion_slider = ctk.CTkSlider(
            distortion_frame,
            from_=0,
            to=10,
            number_of_steps=10,
            command=lambda v: self.update_distortion(v/10)
        )
        self.distortion_slider.pack(side="left", fill="x", expand=True, padx=5)
        
        self.distortion_value = ctk.CTkLabel(distortion_frame, text="0.0")
        self.distortion_value.pack(side="right", padx=(5, 10))
        
        # Right panel - Presets and Filters
        right_panel = ctk.CTkFrame(control_panels)
        right_panel.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        # Presets
        self.presets_frame = ctk.CTkFrame(right_panel)
        self.presets_frame.pack(fill="x", pady=(0, 10))
        
        self.presets_label = ctk.CTkLabel(self.presets_frame, text="Presets", font=ctk.CTkFont(size=16))
        self.presets_label.pack(pady=(0, 10))
        
        # Get all preset names from PresetManager
        preset_names = ["None"] + self.presets.get_preset_names()
        
        self.preset_var = ctk.StringVar(value="None")
        self.preset_menu = ctk.CTkOptionMenu(
            self.presets_frame,
            values=preset_names,
            variable=self.preset_var,
            command=self.apply_preset
        )
        self.preset_menu.pack(fill="x", padx=10, pady=5)
        
        # Filter controls - moved below presets
        self.filter_frame = ctk.CTkFrame(right_panel)
        self.filter_frame.pack(fill="x", pady=(0, 10))
        
        self.filter_label = ctk.CTkLabel(self.filter_frame, text="Filters:", font=ctk.CTkFont(size=16))
        self.filter_label.pack(pady=(0, 10))
        
        filter_checks_frame = ctk.CTkFrame(self.filter_frame)
        filter_checks_frame.pack(pady=5)
        
        self.lowpass_var = ctk.BooleanVar()
        self.lowpass_check = ctk.CTkCheckBox(
            filter_checks_frame, 
            text="Low-Pass", 
            variable=self.lowpass_var,
            command=self.update_filters
        )
        self.lowpass_check.pack(side="left", padx=10)
        
        self.highpass_var = ctk.BooleanVar()
        self.highpass_check = ctk.CTkCheckBox(
            filter_checks_frame, 
            text="High-Pass", 
            variable=self.highpass_var,
            command=self.update_filters
        )
        self.highpass_check.pack(side="left", padx=10)
        
        self.robot_var = ctk.BooleanVar()
        self.robot_check = ctk.CTkCheckBox(
            filter_checks_frame, 
            text="Robot Voice", 
            variable=self.robot_var,
            command=self.update_filters
        )
        self.robot_check.pack(side="left", padx=10)
        
        self.reverb_var = ctk.BooleanVar()
        self.reverb_check = ctk.CTkCheckBox(
            filter_checks_frame, 
            text="Reverb", 
            variable=self.reverb_var,
            command=self.update_filters
        )
        self.reverb_check.pack(side="left", padx=10)
        
        self.chorus_var = ctk.BooleanVar()
        self.chorus_check = ctk.CTkCheckBox(
            filter_checks_frame,
            text="Chorus",
            variable=self.chorus_var,
            command=self.update_filters
        )
        self.chorus_check.pack(side="left", padx=10)
    
    def create_visualizer_canvas(self):
        # Clear existing canvas if it exists
        if hasattr(self, 'visualizer_canvas') and self.visualizer_canvas is not None:
            self.visualizer_canvas.destroy()
        
        # Create new canvas
        self.visualizer_canvas = self.visualizer.create_canvas(self.visualizer_frame)
        self.visualizer_canvas.pack(fill="both", expand=True, padx=10, pady=10)

    def update_visualizer(self, audio, sample_rate):
        if audio is not None and sample_rate is not None:
            # Ensure audio is in correct format
            audio = np.asarray(audio, dtype=np.float32)
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)  # Convert to mono if stereo
                
            self.create_visualizer_canvas()
            self.visualizer.update_waveform(audio, sample_rate)

    def set_button_states(self, *, recording=False, playing=False, paused=False, can_play=False):
        # Default: only record enabled
        if recording:
            self.record_button.configure(text="⏹️ Stop", state="normal", fg_color="gray", hover_color="darkgray")
            self.pause_button.configure(state="normal")
            self.resume_button.configure(state="disabled")
            self.play_button.configure(state="disabled", text="▶️ Play")
        elif playing:
            self.record_button.configure(state="disabled", text="🎤 Record", fg_color="red", hover_color="darkred")
            self.pause_button.configure(state="normal")
            self.resume_button.configure(state="disabled")
            self.play_button.configure(text="⏹️ Stop", state="normal")
        elif paused:
            self.pause_button.configure(state="disabled")
            self.resume_button.configure(state="normal")
        else:
            self.record_button.configure(state="normal", text="🎤 Record", fg_color="red", hover_color="darkred")
            self.pause_button.configure(state="disabled")
            self.resume_button.configure(state="disabled")
            if can_play:
                self.play_button.configure(state="normal", text="▶️ Play")
            else:
                self.play_button.configure(state="disabled", text="▶️ Play")
        # Effects and presets only enabled if not recording or playing
        effect_state = "normal" if not (recording or playing) else "disabled"
        for w in [self.gain_slider, self.echo_slider, self.pitch_slider, self.distortion_slider,
                  self.lowpass_check, self.highpass_check, self.robot_check, self.reverb_check, self.chorus_check,
                  self.preset_menu]:
            w.configure(state=effect_state)

    def toggle_recording(self):
        if not getattr(self, 'is_recording', False):
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        # If audio exists, clear it
        self.current_audio = None
        self.processed_audio = None
        self.sample_rate = None
        self.visualizer.clear_waveform()
        self.recorder.start_recording()
        self.is_recording = True
        self.is_playing = False
        self.set_button_states(recording=True)
    
    def stop_recording(self):
        self.recorder.stop_recording()
        self.is_recording = False
        self.set_button_states(can_play=self.processed_audio is not None)
        if self.processed_audio is not None and self.sample_rate is not None:
            self.update_visualizer(self.processed_audio, self.sample_rate)
        
    def check_playback_status(self):
        if not self.recorder.is_playing and self.is_playing:
            self.is_playing = False
            self.set_button_states(can_play=self.processed_audio is not None)
        elif self.is_playing:
            self.root.after(100, self.check_playback_status)

    def play_audio(self):
        if self.processed_audio is not None:
            if not self.is_playing:
                self.recorder.play_audio(self.processed_audio)
                self.is_playing = True
                self.is_recording = False
                self.set_button_states(playing=True)
                self.root.after(100, self.check_playback_status)
            else:
                self.stop_audio()
    
    def stop_audio(self):
        self.recorder.stop_playback()
        self.is_playing = False
        self.set_button_states(can_play=self.processed_audio is not None)
        self.play_button.configure(command=self.play_audio)
    
    def poll_playback_end(self):
        if not self.recorder.get_playback_status():
            self.is_playing = False
            self.set_button_states(can_play=self.processed_audio is not None)
            self.play_button.configure(command=self.play_audio)
        else:
            self.root.after(100, self.poll_playback_end)
    
    def pause_action(self):
        if self.is_recording:
            self.recorder.pause_recording()
            self.set_button_states(paused=True)
        elif self.is_playing:
            self.recorder.pause_playback()
            self.set_button_states(paused=True)

    def resume_action(self):
        if self.is_recording:
            self.recorder.resume_recording()
            self.set_button_states(recording=True)
        elif self.is_playing:
            self.recorder.resume_playback()
            self.set_button_states(playing=True)
    
    def import_audio(self):
        try:
            import os
            from tkinter import filedialog, messagebox
            file_path = filedialog.askopenfilename(
                title="Import Audio File",
                filetypes=[
                    ("MP3 files", "*.mp3"),
                    ("WAV files", "*.wav"),
                    ("All files", "*.*")
                ]
            )
            if not file_path:
                return
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.mp3':
                try:
                    import librosa
                    audio_data, sample_rate = librosa.load(file_path, sr=None, mono=True)
                    sample_rate = int(sample_rate)
                except Exception as e:
                    messagebox.showerror("MP3 Import Error", f"Failed to import MP3 file.\nMake sure librosa and ffmpeg are installed.\nError: {str(e)}")
                    return
            else:
                try:
                    import soundfile as sf
                    audio_data, sample_rate = sf.read(file_path)
                    if len(audio_data.shape) > 1:
                        audio_data = audio_data.mean(axis=1)
                    if audio_data.dtype != float:
                        audio_data = audio_data.astype('float32')
                except Exception as e:
                    messagebox.showerror("Import Error", f"Failed to import audio file.\nError: {str(e)}")
                    return
            self.current_audio = audio_data
            self.sample_rate = sample_rate
            self.process_audio()
            self.update_visualizer(self.processed_audio, self.sample_rate)
            self.set_button_states(can_play=True)
        except Exception as e:
            print(f"Import error: {str(e)}")
    
    def export_audio(self):
        """Export processed audio to file"""
        if self.processed_audio is not None:
            try:
                import os
                from tkinter import filedialog, messagebox
                file_path = filedialog.asksaveasfilename(
                    title="Export Audio File",
                    defaultextension=".mp3",
                    filetypes=[
                        ("MP3 files", "*.mp3"),
                        ("WAV files", "*.wav"),
                        ("All files", "*.*")
                    ]
                )
                if not file_path:
                    return
                ext = os.path.splitext(file_path)[1].lower()
                export_format = "MP3" if ext == ".mp3" else "WAV"
                sample_rate = self.sample_rate if self.sample_rate is not None else 44100
                try:
                    self.fileops.export_audio(self.processed_audio, sample_rate, filename=file_path, format=export_format)
                except Exception as e:
                    messagebox.showerror("Export Error", f"Failed to export audio file.\nIf exporting as MP3, make sure pydub and ffmpeg are installed.\nError: {str(e)}")
            except Exception as e:
                print(f"Export error: {str(e)}")
    
    def update_gain(self, value):
        self.gain_value.configure(text=f"{value:.1f}x")
        self.save_current_effects_state()
        self.process_audio()

    def update_echo(self, value):
        self.echo_value.configure(text=f"{value:.1f}")
        self.save_current_effects_state()
        self.process_audio()

    def update_pitch(self, value):
        self.pitch_value.configure(text=f"{value:.1f}x")
        self.save_current_effects_state()
        self.process_audio()

    def update_distortion(self, value):
        self.distortion_value.configure(text=f"{value:.1f}")
        self.save_current_effects_state()
        self.process_audio()

    def update_filters(self):
        self.save_current_effects_state()
        self.process_audio()
    
    def apply_preset(self, preset_name=None):
        """Apply a preset configuration"""
        if preset_name is None:
            preset_name = self.preset_var.get()
        if preset_name != "None":
            preset_config = self.presets.get_preset(preset_name)
            if preset_config:
                # Apply preset settings to UI
                self.gain_slider.set(preset_config.get('gain', 1.0) * 10)
                self.echo_slider.set(preset_config.get('echo', 0.0) * 10)
                self.pitch_slider.set(preset_config.get('pitch_shift', 1.0) * 10)
                self.distortion_slider.set(preset_config.get('distortion', 0.0) * 10)
                self.lowpass_var.set(preset_config.get('lowpass', False))
                self.highpass_var.set(preset_config.get('highpass', False))
                self.robot_var.set(preset_config.get('robot', False))
                self.reverb_var.set(preset_config.get('reverb', False))
                self.chorus_var.set(preset_config.get('chorus', False))
                # Update display values
                self.gain_value.configure(text=f"{preset_config.get('gain', 1.0):.1f}x")
                self.echo_value.configure(text=f"{preset_config.get('echo', 0.0):.1f}")
                self.pitch_value.configure(text=f"{preset_config.get('pitch_shift', 1.0):.1f}x")
                self.distortion_value.configure(text=f"{preset_config.get('distortion', 0.0):.1f}")
                # Save the current effect/filter state for export
                self.save_current_effects_state()
                self.process_audio()

    def update_device(self, _=None):
        I,O = self.recorder.get_devices()

        current_input = self.input_device_menu.get()
        current_output = self.output_device_menu.get()

        getInputID = next((i for i, name in I if name == current_input),None)
        getOutputID = next((i for i, name in O if name == current_output),None)

        self.recorder.update_IO_device(getInputID,getOutputID)

    def save_current_effects_state(self):
        # Save the current slider and filter values to internal state
        self.current_effects_state = {
            'gain': self.gain_slider.get() / 10,
            'echo': self.echo_slider.get() / 10,
            'pitch_shift': self.pitch_slider.get() / 10,
            'distortion': self.distortion_slider.get() / 10,
            'lowpass': self.lowpass_var.get(),
            'highpass': self.highpass_var.get(),
            'robot': self.robot_var.get(),
            'reverb': self.reverb_var.get(),
            'chorus': self.chorus_var.get(),
        }

    def process_audio(self):
        
        if self.current_audio is None:
            return
        try:
            gain = self.gain_slider.get() / 10
            echo = self.echo_slider.get() / 10
            lowpass = self.lowpass_var.get()
            highpass = self.highpass_var.get()
            robot = self.robot_var.get()
            reverb = self.reverb_var.get()
            pitch = self.pitch_slider.get() / 10
            chorus = self.chorus_var.get()
            distortion = self.distortion_slider.get() / 10
            self.processed_audio = self.dsp.process_audio(
                self.current_audio,
                gain=gain,
                echo=echo,
                lowpass=lowpass,
                highpass=highpass,
                robot=robot,
                reverb=reverb,
                pitch=pitch,
                chorus=chorus,
                distortion=distortion
            )
            if self.processed_audio is not None and self.sample_rate is not None:
                self.update_visualizer(self.processed_audio, self.sample_rate)
            self.processed_audio = np.clip(self.processed_audio, -1.0, 1.0)
            return self.processed_audio.astype(np.float32)
        except Exception as e:
            print(f"Processing error: {str(e)}")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def audio_processing_loop(self):
        """Background thread for processing audio data"""
        while True:
            try:
                # Get audio data from queue
                audio_data = self.audio_queue.get(timeout=0.1)
                if audio_data is not None:
                    self.current_audio = audio_data
                    self.sample_rate = self.recorder.sample_rate
                    self.process_audio()
                    self.update_visualizer(audio_data, self.sample_rate)
                    self.play_button.configure(state="normal")
                    self.export_button.configure(state="normal")
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Audio processing error: {e}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = VoiceChangerApp()
    app.run()