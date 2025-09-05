"""
Batch Download Page - Clean and minimal Flet implementation
"""

import flet as ft
from ...utils.config import Config
from ...utils.logger import get_logger
from ...downloaders.batch_downloader import BatchDownloader, DownloadType

class BatchPage:
    """Batch download page with clean UI"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger()
        self.batch_downloader = BatchDownloader(config)
        
        # Set up callbacks
        self.batch_downloader.set_callbacks(
            progress_callback=self.on_progress,
            status_callback=self.on_status_change
        )
        
        # UI components
        self.url_textbox = None
        self.type_dropdown = None
        self.quality_dropdown = None
        self.format_dropdown = None
        self.concurrent_dropdown = None
        self.add_button = None
        self.start_button = None
        self.stop_button = None
        self.status_text = None
        
    def build(self) -> ft.Control:
        """Build the batch page UI"""
        
        # URL input section
        self.url_textbox = ft.TextField(
            label="URLs (one per line)",
            multiline=True,
            min_lines=5,
            max_lines=10,
            hint_text="Enter URLs here, one per line...\nhttps://www.youtube.com/watch?v=...\nhttps://soundcloud.com/...",
            expand=True
        )
        
        # Options section
        self.type_dropdown = ft.Dropdown(
            label="Type",
            value="Video",
            options=[
                ft.dropdown.Option("Video"),
                ft.dropdown.Option("Audio"),
            ],
            width=120
        )
        
        self.quality_dropdown = ft.Dropdown(
            label="Quality",
            value="Best",
            options=[
                ft.dropdown.Option("Best"),
                ft.dropdown.Option("1080p"),
                ft.dropdown.Option("720p"),
                ft.dropdown.Option("480p"),
                ft.dropdown.Option("360p"),
                ft.dropdown.Option("192"),
                ft.dropdown.Option("128"),
            ],
            width=120
        )
        
        self.format_dropdown = ft.Dropdown(
            label="Format",
            value="MP4",
            options=[
                ft.dropdown.Option("MP4"),
                ft.dropdown.Option("MP3"),
                ft.dropdown.Option("WEBM"),
                ft.dropdown.Option("MKV"),
            ],
            width=120
        )
        
        self.concurrent_dropdown = ft.Dropdown(
            label="Concurrent",
            value="3",
            options=[
                ft.dropdown.Option("1"),
                ft.dropdown.Option("2"),
                ft.dropdown.Option("3"),
                ft.dropdown.Option("4"),
                ft.dropdown.Option("5"),
            ],
            width=120
        )
        
        # Control buttons
        self.add_button = ft.ElevatedButton(
            text="Add to Queue",
            icon=ft.Icons.ADD,
            on_click=self.add_to_queue,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE
            )
        )
        
        self.start_button = ft.ElevatedButton(
            text="Start Batch",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self.start_batch,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN
            )
        )
        
        self.stop_button = ft.ElevatedButton(
            text="Stop",
            icon=ft.Icons.STOP,
            on_click=self.stop_batch,
            disabled=True,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.RED
            )
        )
        
        # Status section
        self.status_text = ft.Text(
            value="Queue: 0 pending, 0 active, 0 completed, 0 failed",
            size=14
        )
        
        # Layout
        return ft.Column([
            # Title
            ft.Text("Batch Download", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            # URL input
            ft.Container(
                content=self.url_textbox,
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=8
            ),
            
            # Options
            ft.Container(
                content=ft.Row([
                    self.type_dropdown,
                    self.quality_dropdown,
                    self.format_dropdown,
                    self.concurrent_dropdown
                ]),
                padding=10
            ),
            
            # Control buttons
            ft.Row([
                self.add_button,
                self.start_button,
                self.stop_button
            ]),
            
            # Status
            ft.Container(
                content=ft.Column([
                    ft.Text("Queue Status", size=16, weight=ft.FontWeight.BOLD),
                    self.status_text
                ]),
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=8
            )
        ])
    
    def add_to_queue(self, e):
        """Add URLs to the download queue"""
        urls_text = self.url_textbox.value.strip()
        
        if not urls_text:
            self.show_error("Please enter some URLs")
            return
        
        # Parse URLs
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        if not urls:
            self.show_error("No valid URLs found")
            return
        
        # Get options
        download_type = DownloadType.VIDEO if self.type_dropdown.value == "Video" else DownloadType.AUDIO
        quality = self.quality_dropdown.value.lower()
        format_ext = self.format_dropdown.value.lower()
        output_path = str(self.config.get_download_directory())
        
        # Update concurrent downloads
        concurrent = int(self.concurrent_dropdown.value)
        self.batch_downloader.max_concurrent = concurrent
        
        # Add downloads to queue
        added_count = 0
        for url in urls:
            try:
                self.batch_downloader.add_download(
                    url=url,
                    output_path=output_path,
                    download_type=download_type,
                    quality=quality,
                    format_ext=format_ext
                )
                added_count += 1
            except Exception as ex:
                self.logger.error(f"Error adding URL {url}: {ex}")
        
        # Clear textbox and show success
        self.url_textbox.value = ""
        self.show_success(f"Added {added_count} downloads to queue")
        self.update_status()
        e.page.update()
    
    def start_batch(self, e):
        """Start the batch download process"""
        try:
            self.batch_downloader.start_batch()
            self.start_button.disabled = True
            self.stop_button.disabled = False
            e.page.update()
        except Exception as ex:
            self.show_error(f"Failed to start batch: {str(ex)}")
    
    def stop_batch(self, e):
        """Stop the batch download process"""
        try:
            self.batch_downloader.stop_batch()
            self.start_button.disabled = False
            self.stop_button.disabled = True
            e.page.update()
        except Exception as ex:
            self.show_error(f"Failed to stop batch: {str(ex)}")
    
    def on_progress(self, item, progress_info):
        """Handle individual download progress"""
        # Update status when progress changes
        self.update_status()
    
    def on_status_change(self, event_type: str, item):
        """Handle batch status changes"""
        if event_type in ['batch_started', 'batch_stopped', 'download_completed']:
            self.update_status()
    
    def update_status(self):
        """Update the status display"""
        try:
            status = self.batch_downloader.get_queue_status()
            
            self.status_text.value = (
                f"Queue: {status['queue_size']} pending, "
                f"{status['active_downloads']} active, "
                f"{status['completed_downloads']} completed, "
                f"{status['failed_downloads']} failed"
            )
            
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")
    
    def show_error(self, message: str):
        """Show error message"""
        print(f"Error: {message}")
        
    def show_success(self, message: str):
        """Show success message"""
        print(f"Success: {message}")
