"""
Format Converter Page - Clean and minimal Flet implementation
"""

import flet as ft
from pathlib import Path
from ...utils.config import Config
from ...utils.logger import get_logger
from ...converters.format_converter import FormatConverter

class ConverterPage:
    """Format converter page with clean UI"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger()
        self.converter = FormatConverter(config)
        
        # UI components
        self.input_field = None
        self.file_info_text = None
        self.format_dropdown = None
        self.quality_dropdown = None
        self.convert_button = None
        self.cancel_button = None
        self.progress_bar = None
        self.progress_text = None
        
        # Conversion state
        self.current_conversion = None
        
    def build(self) -> ft.Control:
        """Build the converter page UI"""
        
        # Input file section
        self.input_field = ft.TextField(
            label="Input File",
            hint_text="Select input file to convert",
            expand=True,
            read_only=True
        )
        
        browse_button = ft.ElevatedButton(
            text="Browse",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=self.browse_file
        )
        
        self.file_info_text = ft.Text(
            value="",
            size=12,
            color=ft.Colors.GREY_600
        )
        
        # Options section
        self.format_dropdown = ft.Dropdown(
            label="Output Format",
            value="MP4",
            options=[
                ft.dropdown.Option("MP4"),
                ft.dropdown.Option("AVI"),
                ft.dropdown.Option("MKV"),
                ft.dropdown.Option("MOV"),
                ft.dropdown.Option("WEBM"),
                ft.dropdown.Option("MP3"),
                ft.dropdown.Option("WAV"),
                ft.dropdown.Option("FLAC"),
                ft.dropdown.Option("M4A"),
                ft.dropdown.Option("AAC"),
                ft.dropdown.Option("OGG"),
            ],
            width=150,
            on_change=self.on_format_change
        )
        
        self.quality_dropdown = ft.Dropdown(
            label="Quality",
            value="Medium",
            options=[
                ft.dropdown.Option("Low"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("High"),
                ft.dropdown.Option("Lossless"),
            ],
            width=150
        )
        
        # Convert buttons
        self.convert_button = ft.ElevatedButton(
            text="Convert File",
            icon=ft.Icons.TRANSFORM,
            on_click=self.start_conversion,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.PURPLE
            )
        )
        
        self.cancel_button = ft.ElevatedButton(
            text="Cancel",
            icon=ft.Icons.CANCEL,
            on_click=self.cancel_conversion,
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
            ft.Text("Format Converter", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            # Input file
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        self.input_field,
                        browse_button
                    ]),
                    self.file_info_text
                ]),
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=8
            ),
            
            # Options
            ft.Container(
                content=ft.Row([
                    self.format_dropdown,
                    self.quality_dropdown
                ]),
                padding=10
            ),
            
            # Buttons
            ft.Row([
                self.convert_button,
                self.cancel_button
            ]),
            
            # Progress
            ft.Column([
                self.progress_bar,
                self.progress_text
            ])
        ])
    
    def browse_file(self, e):
        """Browse for input file"""
        # In a real implementation, this would open a file picker
        # For now, we'll simulate it
        print("File picker would open here")
        
        # Simulate file selection
        file_path = "/path/to/example.mp4"
        self.input_field.value = file_path
        self.update_file_info(file_path)
        e.page.update()
    
    def update_file_info(self, file_path: str):
        """Update file information display"""
        try:
            if Path(file_path).exists():
                info = self.converter.get_file_info(file_path)
                
                # Format duration
                duration = info.get('duration', 0)
                duration_str = f"{int(duration//60):02d}:{int(duration%60):02d}"
                
                # Format file size
                size = info.get('size', 0)
                size_mb = size / (1024 * 1024)
                
                self.file_info_text.value = f"Duration: {duration_str}, Size: {size_mb:.1f}MB"
                self.file_info_text.color = ft.Colors.GREEN
            else:
                self.file_info_text.value = "File not found"
                self.file_info_text.color = ft.Colors.RED
                
        except Exception as e:
            self.file_info_text.value = f"Error reading file: {str(e)}"
            self.file_info_text.color = ft.Colors.RED
    
    def on_format_change(self, e):
        """Handle format selection change"""
        format_name = e.control.value.lower()
        
        if format_name in ['mp3', 'wav', 'flac', 'm4a', 'aac', 'ogg']:
            # Audio format - different quality options
            self.quality_dropdown.options = [
                ft.dropdown.Option("96k"),
                ft.dropdown.Option("128k"),
                ft.dropdown.Option("192k"),
                ft.dropdown.Option("256k"),
                ft.dropdown.Option("320k"),
            ]
            self.quality_dropdown.value = "192k"
        else:
            # Video format - standard quality options
            self.quality_dropdown.options = [
                ft.dropdown.Option("Low"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("High"),
                ft.dropdown.Option("Lossless"),
            ]
            self.quality_dropdown.value = "Medium"
        
        e.page.update()
    
    def start_conversion(self, e):
        """Start file conversion"""
        input_path = self.input_field.value.strip()
        
        if not input_path:
            self.show_error("Please select an input file")
            return
        
        if not Path(input_path).exists():
            self.show_error("Input file does not exist")
            return
        
        # Check if conversion is active
        if self.current_conversion and self.current_conversion.is_alive():
            self.show_error("A conversion is already in progress")
            return
        
        # Get options
        output_format = self.format_dropdown.value.lower()
        quality = self.quality_dropdown.value.lower()
        output_dir = str(self.config.get_download_directory())
        
        # Generate output filename
        input_file = Path(input_path)
        output_filename = f"{input_file.stem}.{output_format}"
        output_path = Path(output_dir) / output_filename
        
        # Show progress
        self.show_progress()
        
        # Start conversion in thread
        self.current_conversion = self.converter.convert_file_async(
            input_path=input_path,
            output_path=str(output_path),
            output_format=output_format,
            quality=quality,
            progress_callback=self.on_progress,
            completion_callback=self.on_complete
        )
    
    def cancel_conversion(self, e):
        """Cancel current conversion"""
        if self.current_conversion and self.current_conversion.is_alive():
            self.converter.cancel_conversion()
            self.progress_text.value = "Cancelling..."
            e.page.update()
    
    def show_progress(self):
        """Show progress UI"""
        self.convert_button.disabled = True
        self.cancel_button.visible = True
        self.progress_bar.visible = True
        self.progress_text.visible = True
        self.progress_text.value = "Starting conversion..."
        
    def hide_progress(self):
        """Hide progress UI"""
        self.convert_button.disabled = False
        self.cancel_button.visible = False
        self.progress_bar.visible = False
        self.progress_text.visible = False
        self.progress_bar.value = 0
        
    def on_progress(self, progress_info):
        """Handle conversion progress"""
        try:
            progress = progress_info.get('progress', 0)
            current_time = progress_info.get('current_time', 0)
            total_time = progress_info.get('total_time', 0)
            
            # Update progress bar
            self.progress_bar.value = progress
            
            # Update progress text
            if total_time > 0:
                current_str = f"{int(current_time//60):02d}:{int(current_time%60):02d}"
                total_str = f"{int(total_time//60):02d}:{int(total_time%60):02d}"
                self.progress_text.value = f"Converting: {current_str} / {total_str} ({progress*100:.1f}%)"
            else:
                self.progress_text.value = "Converting..."
                
        except Exception as e:
            self.logger.error(f"Error updating progress: {e}")
    
    def on_complete(self, success: bool, message: str):
        """Handle conversion completion"""
        try:
            self.hide_progress()
            
            if success:
                self.show_success("File converted successfully!")
            else:
                if "cancelled" in message.lower():
                    self.show_info("Conversion was cancelled")
                else:
                    self.show_error(f"Conversion failed: {message}")
                    
        except Exception as e:
            self.logger.error(f"Error in completion handler: {e}")
    
    def show_error(self, message: str):
        """Show error message"""
        print(f"Error: {message}")
        
    def show_success(self, message: str):
        """Show success message"""
        print(f"Success: {message}")
        
    def show_info(self, message: str):
        """Show info message"""
        print(f"Info: {message}")
