"""
Main YTDL Flet Application
Clean, minimal, and well-commented implementation
"""

import flet as ft
from ..utils.config import Config
from ..utils.logger import get_logger
from .pages.video_page import VideoPage
from .pages.audio_page import AudioPage
from .pages.batch_page import BatchPage
from .pages.converter_page import ConverterPage
from .pages.settings_page import SettingsPage

class YTDLApp:
    """Main YTDL Application using Flet"""
    
    def __init__(self, page: ft.Page, config: Config):
        self.page = page
        self.config = config
        self.logger = get_logger()
        
        # Current page reference
        self.current_page = None
        
        # Initialize pages
        self.pages = {
            "video": VideoPage(self.config),
            "audio": AudioPage(self.config),
            "batch": BatchPage(self.config),
            "converter": ConverterPage(self.config),
            "settings": SettingsPage(self.config, self.on_theme_change)
        }
        
    def build(self):
        """Build the application UI"""
        # Configure page
        self.page.title = "YTDL - All-in-One Downloader"
        self.page.window.width = 1200
        self.page.window.height = 800
        self.page.window.min_width = 800
        self.page.window.min_height = 600
        self.page.padding = 20
        
        # Apply theme
        self.apply_theme()
        
        # Create navigation rail
        nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.VIDEO_LIBRARY,
                    selected_icon=ft.Icons.VIDEO_LIBRARY,
                    label="Video"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.AUDIOTRACK,
                    selected_icon=ft.Icons.AUDIOTRACK,
                    label="Audio"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.QUEUE,
                    selected_icon=ft.Icons.QUEUE,
                    label="Batch"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.TRANSFORM,
                    selected_icon=ft.Icons.TRANSFORM,
                    label="Convert"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS,
                    selected_icon=ft.Icons.SETTINGS,
                    label="Settings"
                ),
            ],
            on_change=self.on_nav_change,
        )
        
        # Create main content area
        self.content_area = ft.Container(
            content=self.pages["video"].build(),
            expand=True,
            padding=20
        )
        
        # Create main layout
        main_layout = ft.Row(
            [
                nav_rail,
                ft.VerticalDivider(width=1),
                self.content_area
            ],
            expand=True
        )
        
        # Add to page
        self.page.add(main_layout)
        self.current_page = "video"
        
        # Update page
        self.page.update()
        
    def on_nav_change(self, e):
        """Handle navigation change"""
        # Map index to page name
        page_names = ["video", "audio", "batch", "converter", "settings"]
        selected_page = page_names[e.control.selected_index]
        
        if selected_page != self.current_page:
            # Update content area
            self.content_area.content = self.pages[selected_page].build()
            self.current_page = selected_page
            
            # Update page
            self.page.update()
            
            self.logger.info(f"Switched to {selected_page} page")
    
    def on_theme_change(self, theme_mode: str):
        """Handle theme change from settings"""
        self.config.set('theme_mode', theme_mode)
        self.apply_theme()
        self.page.update()
        
    def apply_theme(self):
        """Apply theme to the page"""
        theme_mode = self.config.get('theme_mode', 'dark')
        
        if theme_mode == 'dark':
            self.page.theme_mode = ft.ThemeMode.DARK
        elif theme_mode == 'light':
            self.page.theme_mode = ft.ThemeMode.LIGHT
        else:  # kawaii
            self.page.theme_mode = ft.ThemeMode.LIGHT
            # Custom kawaii colors
            self.page.theme = ft.Theme(
                color_scheme_seed=ft.Colors.PINK
            )
