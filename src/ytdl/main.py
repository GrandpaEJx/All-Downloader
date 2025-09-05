#!/usr/bin/env python3
"""
YTDL - All-in-One Video/Audio Downloader GUI Application
Main application entry point using Flet
"""

import flet as ft
from .gui.app import YTDLApp
from .utils.config import Config
from .utils.logger import setup_logger

def main():
    """Main application entry point"""
    try:
        # Setup logging
        logger = setup_logger()
        logger.info("Starting YTDL Flet Application")

        # Initialize configuration
        config = Config()

        # Create and run the Flet app
        def create_app(page: ft.Page):
            app = YTDLApp(page, config)
            app.build()

        # Run the Flet application
        ft.app(
            target=create_app,
            name="YTDL - All-in-One Downloader",
            assets_dir="assets"
        )

    except Exception as e:
        print(f"Failed to start YTDL application: {e}")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()
