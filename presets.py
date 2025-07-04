from typing import Dict, Any

class PresetManager:
    def __init__(self):
        """Initialize the preset manager with predefined voice effect presets"""
        self.presets = self._create_presets()
    
    def _create_presets(self) -> Dict[str, Dict[str, Any]]:
        """Create the predefined presets"""
        return {
            "Demon": {
                "name": "Demon",
                "description": "Deep, dark, demonic voice effect",
                "gain": 1.2,
                "echo": 0.3,
                "lowpass": True,
                "highpass": False,
                "robot": False,
                "reverb": True,
                "pitch_shift": 0.7,  # Lower pitch
                "distortion": 0.4,
                "compression": True,
                "compression_threshold": 0.3,
                "compression_ratio": 6.0
            },
            
            "Robot": {
                "name": "Robot",
                "description": "Mechanical, robotic voice effect",
                "gain": 1.0,
                "echo": 0.1,
                "lowpass": False,
                "highpass": True,
                "robot": True,
                "reverb": False,
                "pitch_shift": 1.0,  # No pitch shift
                "distortion": 0.2,
                "compression": True,
                "compression_threshold": 0.4,
                "compression_ratio": 4.0
            },
            
            "Underwater": {
                "name": "Underwater",
                "description": "Muffled, underwater voice effect",
                "gain": 0.8,
                "echo": 0.2,
                "lowpass": True,
                "highpass": False,
                "robot": False,
                "reverb": True,
                "pitch_shift": 0.9,  # Slightly lower pitch
                "distortion": 0.0,
                "compression": False,
                "chorus": True,
                "chorus_depth": 0.003,
                "chorus_rate": 0.8
            },
            
            "Walkie Talkie": {
                "name": "Walkie Talkie",
                "description": "Radio communication voice effect",
                "gain": 1.1,
                "echo": 0.0,
                "lowpass": False,
                "highpass": True,
                "robot": False,
                "reverb": False,
                "pitch_shift": 1.0,
                "distortion": 0.3,
                "compression": True,
                "compression_threshold": 0.5,
                "compression_ratio": 3.0,
                "noise": True,
                "noise_level": 0.05
            },
            
            "Alien": {
                "name": "Alien",
                "description": "Otherworldly, alien voice effect",
                "gain": 1.3,
                "echo": 0.4,
                "lowpass": False,
                "highpass": True,
                "robot": False,
                "reverb": True,
                "pitch_shift": 1.4,  # Higher pitch
                "distortion": 0.6,
                "compression": True,
                "compression_threshold": 0.2,
                "compression_ratio": 8.0,
                "chorus": True,
                "chorus_depth": 0.005,
                "chorus_rate": 2.0
            },
            
            "Helium": {
                "name": "Helium",
                "description": "High-pitched helium voice effect",
                "gain": 0.9,
                "echo": 0.0,
                "lowpass": False,
                "highpass": True,
                "robot": False,
                "reverb": False,
                "pitch_shift": 2.0,  # Much higher pitch
                "distortion": 0.0,
                "compression": False
            },
            
            "Deep Voice": {
                "name": "Deep Voice",
                "description": "Deep, bass-boosted voice effect",
                "gain": 1.1,
                "echo": 0.1,
                "lowpass": True,
                "highpass": False,
                "robot": False,
                "reverb": False,
                "pitch_shift": 0.6,  # Lower pitch
                "distortion": 0.0,
                "compression": True,
                "compression_threshold": 0.6,
                "compression_ratio": 2.0
            },
            
            "Echo Chamber": {
                "name": "Echo Chamber",
                "description": "Heavy echo and reverb effect",
                "gain": 0.8,
                "echo": 0.7,
                "lowpass": False,
                "highpass": False,
                "robot": False,
                "reverb": True,
                "pitch_shift": 1.0,
                "distortion": 0.0,
                "compression": False
            },
            
            "Telephone": {
                "name": "Telephone",
                "description": "Classic telephone voice effect",
                "gain": 1.0,
                "echo": 0.0,
                "lowpass": True,
                "highpass": True,
                "robot": False,
                "reverb": False,
                "pitch_shift": 1.0,
                "distortion": 0.1,
                "compression": True,
                "compression_threshold": 0.7,
                "compression_ratio": 2.5
            },
            
            "Megaphone": {
                "name": "Megaphone",
                "description": "Megaphone/PA system voice effect",
                "gain": 1.4,
                "echo": 0.0,
                "lowpass": False,
                "highpass": True,
                "robot": False,
                "reverb": False,
                "pitch_shift": 1.0,
                "distortion": 0.5,
                "compression": True,
                "compression_threshold": 0.3,
                "compression_ratio": 5.0
            }
        }
    
    def get_preset(self, preset_name: str) -> Dict[str, Any]:
        """
        Get a specific preset by name
        
        Args:
            preset_name: Name of the preset
            
        Returns:
            Preset configuration dictionary
        """
        return self.presets.get(preset_name, {})
    
    def get_all_presets(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all available presets
        
        Returns:
            Dictionary of all presets
        """
        return self.presets.copy()
    
    def get_preset_names(self) -> list:
        """
        Get list of all preset names
        
        Returns:
            List of preset names
        """
        return list(self.presets.keys())
    
    def get_preset_description(self, preset_name: str) -> str:
        """
        Get description of a specific preset
        
        Args:
            preset_name: Name of the preset
            
        Returns:
            Preset description
        """
        preset = self.presets.get(preset_name, {})
        return preset.get('description', 'No description available')
    
    def add_custom_preset(self, name: str, config: Dict[str, Any]):
        """
        Add a custom preset
        
        Args:
            name: Name of the custom preset
            config: Preset configuration dictionary
        """
        if name and config:
            self.presets[name] = config.copy()
            print(f"Custom preset '{name}' added successfully")
        else:
            print("Invalid preset name or configuration")
    
    def remove_preset(self, preset_name: str) -> bool:
        """
        Remove a preset (only custom presets can be removed)
        
        Args:
            preset_name: Name of the preset to remove
            
        Returns:
            True if removed, False if not found or is built-in
        """
        # Don't allow removal of built-in presets
        built_in_presets = ["Demon", "Robot", "Underwater", "Walkie Talkie", 
                           "Alien", "Helium", "Deep Voice", "Echo Chamber", 
                           "Telephone", "Megaphone"]
        
        if preset_name in built_in_presets:
            print(f"Cannot remove built-in preset '{preset_name}'")
            return False
        
        if preset_name in self.presets:
            del self.presets[preset_name]
            print(f"Preset '{preset_name}' removed successfully")
            return True
        else:
            print(f"Preset '{preset_name}' not found")
            return False
    
    def modify_preset(self, preset_name: str, new_config: Dict[str, Any]) -> bool:
        """
        Modify an existing preset
        
        Args:
            preset_name: Name of the preset to modify
            new_config: New configuration dictionary
            
        Returns:
            True if modified, False if not found
        """
        if preset_name in self.presets:
            # Preserve the original name and description
            original_preset = self.presets[preset_name]
            new_config['name'] = original_preset.get('name', preset_name)
            new_config['description'] = original_preset.get('description', 'Modified preset')
            
            self.presets[preset_name] = new_config
            print(f"Preset '{preset_name}' modified successfully")
            return True
        else:
            print(f"Preset '{preset_name}' not found")
            return False
    
    def get_preset_summary(self) -> str:
        """
        Get a summary of all available presets
        
        Returns:
            Formatted string with preset information
        """
        summary = "Available Presets:\n"
        summary += "=" * 50 + "\n"
        
        for name, config in self.presets.items():
            description = config.get('description', 'No description')
            summary += f"{name}: {description}\n"
        
        return summary
    
    def validate_preset_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate a preset configuration
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['name', 'description']
        optional_fields = ['gain', 'echo', 'lowpass', 'highpass', 'robot', 'reverb']
        
        # Check required fields
        for field in required_fields:
            if field not in config:
                print(f"Missing required field: {field}")
                return False
        
        # Check field types and ranges
        if 'gain' in config and not (0.1 <= config['gain'] <= 3.0):
            print("Gain must be between 0.1 and 3.0")
            return False
        
        if 'echo' in config and not (0.0 <= config['echo'] <= 1.0):
            print("Echo must be between 0.0 and 1.0")
            return False
        
        return True 