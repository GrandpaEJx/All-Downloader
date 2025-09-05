"""
Settings Page - Clean and minimal Flet implementation
"""

import flet as ft
from typing import Callable
from ...utils.config import Config
from ...utils.logger import get_logger

class SettingsPage:
    """Settings page with clean UI"""
    
    def __init__(self, config: Config, theme_callback: Callable[[str], None]):
        self.config = config
        self.logger = get_logger()
        self.theme_callback = theme_callback
        
        # UI components
        self.theme_dropdown = None
        self.download_dir_field = None
        self.video_quality_dropdown = None
        self.audio_quality_dropdown = None
        self.concurrent_dropdown = None
        self.save_button = None
        
    def build(self) -> ft.Control:
        """Build the settings page UI"""
        
        # Theme selection
        self.theme_dropdown = ft.Dropdown(
            label="Theme",
            value=self.config.get('theme_mode', 'dark').title(),
            options=[
                ft.dropdown.Option("Dark"),
                ft.dropdown.Option("Light"),
                ft.dropdown.Option("Kawaii"),
            ],
            width=150,
            on_change=self.on_theme_change
        )
        
        # Download directory
        self.download_dir_field = ft.TextField(
            label="Default Download Directory",
            value=str(self.config.get_download_directory()),
            expand=True
        )
        
        browse_button = ft.ElevatedButton(
            text="Browse",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=self.browse_directory
        )
        
        # Video quality
        self.video_quality_dropdown = ft.Dropdown(
            label="Default Video Quality",
            value=self.config.get('video_quality', 'best'),
            options=[
                ft.dropdown.Option("best"),
                ft.dropdown.Option("1080p"),
                ft.dropdown.Option("720p"),
                ft.dropdown.Option("480p"),
                ft.dropdown.Option("360p"),
            ],
            width=150
        )
        
        # Audio quality
        self.audio_quality_dropdown = ft.Dropdown(
            label="Default Audio Quality",
            value=self.config.get('audio_quality', '192'),
            options=[
                ft.dropdown.Option("320"),
                ft.dropdown.Option("256"),
                ft.dropdown.Option("192"),
                ft.dropdown.Option("128"),
                ft.dropdown.Option("96"),
            ],
            width=150
        )
        
        # Concurrent downloads
        self.concurrent_dropdown = ft.Dropdown(
            label="Concurrent Downloads",
            value=str(self.config.get('concurrent_downloads', 3)),
            options=[
                ft.dropdown.Option("1"),
                ft.dropdown.Option("2"),
                ft.dropdown.Option("3"),
                ft.dropdown.Option("4"),
                ft.dropdown.Option("5"),
            ],
            width=150
        )
        
        # Save button
        self.save_button = ft.ElevatedButton(
            text="Save Settings",
            icon=ft.Icons.SAVE,
            on_click=self.save_settings,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN
            )
        )
        
        # Layout
        return ft.Column([
            # Title
            ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            # Appearance section
            ft.Container(
                content=ft.Column([
                    ft.Text("Appearance", size=18, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.Text("Theme:", width=150),
                        self.theme_dropdown
                    ])
                ]),
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=8
            ),
            
            # Download settings section
            ft.Container(
                content=ft.Column([
                    ft.Text("Download Settings", size=18, weight=ft.FontWeight.BOLD),
                    
                    # Download directory
                    ft.Row([
                        ft.Text("Directory:", width=150),
                        self.download_dir_field,
                        browse_button
                    ]),
                    
                    # Quality settings
                    ft.Row([
                        ft.Text("Video Quality:", width=150),
                        self.video_quality_dropdown
                    ]),
                    
                    ft.Row([
                        ft.Text("Audio Quality:", width=150),
                        self.audio_quality_dropdown
                    ]),
                    
                    ft.Row([
                        ft.Text("Concurrent Downloads:", width=150),
                        self.concurrent_dropdown
                    ])
                ]),
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=8
            ),
            
            # Save button
            self.save_button,
            
            # Info section
            ft.Container(
                content=ft.Column([
                    ft.Text("About YTDL", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Version: 0.1.0"),
                    ft.Text("All-in-One Video/Audio Downloader"),
                    ft.Text("Supports 50+ platforms including adult content"),
                    ft.Text("Built with Flet for modern UI/UX")
                ]),
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=8
            )
        ])
    
    def on_theme_change(self, e):
        """Handle theme change"""
        theme_name = e.control.value.lower()
        
        # Apply theme immediately
        self.theme_callback(theme_name)
        
        self.logger.info(f"Theme changed to: {theme_name}")
    
    def browse_directory(self, e):
        """Browse for download directory"""
        # In a real implementation, this would open a directory picker
        # For now, we'll simulate it
        print("Directory picker would open here")
        
        # Simulate directory selection
        directory = "/path/to/downloads"
        self.download_dir_field.value = directory
        e.page.update()
    
    def save_settings(self, e):
        """Save all settings"""
        try:
            # Save all settings to config
            self.config.set('download_directory', self.download_dir_field.value)
            self.config.set('video_quality', self.video_quality_dropdown.value)
            self.config.set('audio_quality', self.audio_quality_dropdown.value)
            self.config.set('concurrent_downloads', int(self.concurrent_dropdown.value))
            
            # Show success message
            self.show_success("Settings saved successfully!")
            
            self.logger.info("Settings saved")
            
        except Exception as ex:
            self.show_error(f"Failed to save settings: {str(ex)}")
    
    def show_error(self, message: str):
        """Show error message"""
        print(f"Error: {message}")
        
    def show_success(self, message: str):
        """Show success message"""
        print(f"Success: {message}")
