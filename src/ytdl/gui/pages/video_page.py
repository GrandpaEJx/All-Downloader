"""
Video Download Page - Clean and minimal Flet implementation
"""

import flet as ft
import threading
from ...utils.config import Config
from ...utils.logger import get_logger
from ...downloaders.video_downloader import VideoDownloader
from ...downloaders.platform_manager import PlatformManager

class VideoPage:
    """Video download page with clean UI"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger()
        self.downloader = VideoDownloader(config)
        self.platform_manager = PlatformManager()
        
        # UI components
        self.url_field = None
        self.status_text = None
        self.quality_dropdown = None
        self.format_dropdown = None
        self.download_button = None
        self.cancel_button = None
        self.progress_bar = None
        self.progress_text = None
        
        # Download state
        self.current_download = None
        
    def build(self) -> ft.Control:
        """Build the video page UI"""
        
        # URL input section
        self.url_field = ft.TextField(
            label="Video URL",
            hint_text="Enter video URL (YouTube, Instagram, TikTok, etc.)",
            expand=True,
            on_change=self.on_url_change
        )
        
        self.status_text = ft.Text(
            value="",
            size=12,
            color=ft.Colors.GREY_600
        )
        
        # Options section
        self.quality_dropdown = ft.Dropdown(
            label="Quality",
            value="Best",
            options=[
                ft.dropdown.Option("Best"),
                ft.dropdown.Option("1080p"),
                ft.dropdown.Option("720p"),
                ft.dropdown.Option("480p"),
                ft.dropdown.Option("360p"),
                ft.dropdown.Option("Audio Only"),
            ],
            width=150
        )
        
        self.format_dropdown = ft.Dropdown(
            label="Format",
            value="MP4",
            options=[
                ft.dropdown.Option("MP4"),
                ft.dropdown.Option("WEBM"),
                ft.dropdown.Option("MKV"),
                ft.dropdown.Option("MP3"),
            ],
            width=150
        )
        
        # Download buttons
        self.download_button = ft.ElevatedButton(
            text="Download Video",
            icon=ft.Icons.DOWNLOAD,
            on_click=self.start_download,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE
            )
        )
        
        self.cancel_button = ft.ElevatedButton(
            text="Cancel",
            icon=ft.Icons.CANCEL,
            on_click=self.cancel_download,
            visible=False,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.RED
            )
        )
        
        # Progress section
        self.progress_bar = ft.ProgressBar(
            width=400,
            visible=False
        )
        
        self.progress_text = ft.Text(
            value="",
            size=12,
            visible=False
        )
        
        # Layout
        return ft.Column([
            # Title
            ft.Text("Video Download", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            # URL input
            ft.Container(
                content=ft.Column([
                    self.url_field,
                    self.status_text
                ]),
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=8
            ),
            
            # Options
            ft.Container(
                content=ft.Row([
                    self.quality_dropdown,
                    self.format_dropdown
                ]),
                padding=10
            ),
            
            # Buttons
            ft.Row([
                self.download_button,
                self.cancel_button
            ]),
            
            # Progress
            ft.Column([
                self.progress_bar,
                self.progress_text
            ])
        ])
    
    def on_url_change(self, e):
        """Handle URL input changes"""
        url = e.control.value.strip()
        
        if not url:
            self.status_text.value = ""
            self.status_text.color = ft.Colors.GREY_600
        else:
            # Validate URL
            is_valid, message = self.platform_manager.validate_url(url)
            
            if is_valid:
                self.status_text.value = f"✓ {message}"
                self.status_text.color = ft.Colors.GREEN
            else:
                self.status_text.value = f"✗ {message}"
                self.status_text.color = ft.Colors.RED
        
        # Update UI
        e.page.update()
    
    def start_download(self, e):
        """Start video download"""
        url = self.url_field.value.strip()
        
        if not url:
            self.show_error("Please enter a video URL")
            return
        
        # Validate URL
        is_valid, message = self.platform_manager.validate_url(url)
        if not is_valid:
            self.show_error(message)
            return
        
        # Check if download is active
        if self.current_download and self.current_download.is_alive():
            self.show_error("A download is already in progress")
            return
        
        # Get options
        quality = self.quality_dropdown.value.lower()
        format_ext = self.format_dropdown.value.lower()
        output_path = str(self.config.get_download_directory())
        
        # Show progress
        self.show_progress()
        
        # Start download in thread
        self.current_download = self.downloader.download_video_async(
            url=url,
            output_path=output_path,
            quality=quality,
            format_ext=format_ext,
            progress_callback=self.on_progress,
            completion_callback=self.on_complete
        )
    
    def cancel_download(self, e):
        """Cancel current download"""
        if self.current_download and self.current_download.is_alive():
            self.downloader.cancel_download()
            self.progress_text.value = "Cancelling..."
            e.page.update()
    
    def show_progress(self):
        """Show progress UI"""
        self.download_button.disabled = True
        self.cancel_button.visible = True
        self.progress_bar.visible = True
        self.progress_text.visible = True
        self.progress_text.value = "Starting download..."
        
    def hide_progress(self):
        """Hide progress UI"""
        self.download_button.disabled = False
        self.cancel_button.visible = False
        self.progress_bar.visible = False
        self.progress_text.visible = False
        self.progress_bar.value = 0
        
    def on_progress(self, progress_info):
        """Handle download progress"""
        try:
            progress = progress_info.get('progress', 0)
            downloaded = progress_info.get('downloaded', 0)
            total = progress_info.get('total', 0)
            speed = progress_info.get('speed', 0)
            
            # Update progress bar
            self.progress_bar.value = progress
            
            # Update progress text
            if total > 0:
                downloaded_mb = downloaded / (1024 * 1024)
                total_mb = total / (1024 * 1024)
                speed_mb = speed / (1024 * 1024) if speed else 0
                
                self.progress_text.value = (
                    f"Downloaded: {downloaded_mb:.1f}MB / {total_mb:.1f}MB "
                    f"({speed_mb:.1f}MB/s)"
                )
            else:
                self.progress_text.value = "Downloading..."
                
        except Exception as e:
            self.logger.error(f"Error updating progress: {e}")
    
    def on_complete(self, success: bool, message: str):
        """Handle download completion"""
        try:
            self.hide_progress()
            
            if success:
                self.show_success("Video downloaded successfully!")
            else:
                if "cancelled" in message.lower():
                    self.show_info("Download was cancelled")
                else:
                    self.show_error(f"Download failed: {message}")
                    
        except Exception as e:
            self.logger.error(f"Error in completion handler: {e}")
    
    def show_error(self, message: str):
        """Show error message"""
        # This would show a snackbar or dialog in a real implementation
        print(f"Error: {message}")
        
    def show_success(self, message: str):
        """Show success message"""
        print(f"Success: {message}")
        
    def show_info(self, message: str):
        """Show info message"""
        print(f"Info: {message}")
