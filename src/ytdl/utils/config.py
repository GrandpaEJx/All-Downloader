"""
Configuration management for YTDL application
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

class Config:
    """Configuration manager for YTDL application"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.ytdl'
        self.config_file = self.config_dir / 'config.json'
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Return default configuration
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'appearance_mode': 'dark',
            'color_theme': 'blue',
            'download_directory': str(Path.home() / 'Downloads' / 'YTDL'),
            'video_quality': 'best',
            'audio_quality': '192',
            'concurrent_downloads': 3,
            'enable_notifications': True,
            'auto_convert': False,
            'keep_original': True,
            'subtitle_languages': ['en'],
            'window_geometry': '1200x800',
            'theme_mode': 'dark',  # 'dark', 'light', 'kawaii'
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self._config[key] = value
        self._save_config()
    
    def _save_config(self) -> None:
        """Save configuration to file"""
        try:
            self.config_dir.mkdir(exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save configuration: {e}")
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self._config = self._get_default_config()
        self._save_config()
    
    def get_download_directory(self) -> Path:
        """Get download directory as Path object"""
        return Path(self.get('download_directory'))
    
    def ensure_download_directory(self) -> None:
        """Ensure download directory exists"""
        download_dir = self.get_download_directory()
        download_dir.mkdir(parents=True, exist_ok=True)
