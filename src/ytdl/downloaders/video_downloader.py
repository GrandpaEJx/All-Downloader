"""
Video downloader module for YTDL application
"""

import yt_dlp
import os
import threading
import time
import signal
import subprocess
from pathlib import Path
from typing import Dict, Any, Callable, Optional, List
from ..utils.config import Config
from ..utils.logger import get_logger

class VideoDownloader:
    """Video downloader using yt-dlp"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger()
        self.current_download = None
        self.download_cancelled = False
        self.ydl_process = None
        self.download_lock = threading.Lock()
        
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Get video information without downloading"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'formats': self._extract_formats(info.get('formats', [])),
                    'thumbnail': info.get('thumbnail'),
                    'description': info.get('description', ''),
                    'upload_date': info.get('upload_date'),
                }
                
        except Exception as e:
            self.logger.error(f"Error getting video info: {e}")
            raise Exception(f"Failed to get video information: {str(e)}")
    
    def _extract_formats(self, formats: List[Dict]) -> List[Dict[str, Any]]:
        """Extract and organize available formats"""
        video_formats = []
        audio_formats = []
        
        for fmt in formats:
            if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                # Video with audio
                video_formats.append({
                    'format_id': fmt.get('format_id'),
                    'ext': fmt.get('ext'),
                    'quality': fmt.get('height', 0),
                    'fps': fmt.get('fps'),
                    'filesize': fmt.get('filesize'),
                    'type': 'video+audio'
                })
            elif fmt.get('vcodec') != 'none':
                # Video only
                video_formats.append({
                    'format_id': fmt.get('format_id'),
                    'ext': fmt.get('ext'),
                    'quality': fmt.get('height', 0),
                    'fps': fmt.get('fps'),
                    'filesize': fmt.get('filesize'),
                    'type': 'video'
                })
            elif fmt.get('acodec') != 'none':
                # Audio only
                audio_formats.append({
                    'format_id': fmt.get('format_id'),
                    'ext': fmt.get('ext'),
                    'abr': fmt.get('abr'),
                    'filesize': fmt.get('filesize'),
                    'type': 'audio'
                })
        
        return {
            'video': sorted(video_formats, key=lambda x: x.get('quality', 0), reverse=True),
            'audio': sorted(audio_formats, key=lambda x: x.get('abr', 0), reverse=True)
        }
    
    def download_video(
        self,
        url: str,
        output_path: str,
        quality: str = 'best',
        format_ext: str = 'mp4',
        progress_callback: Optional[Callable] = None,
        completion_callback: Optional[Callable] = None
    ) -> bool:
        """Download video with specified options"""

        def progress_hook(d):
            # Check for cancellation
            if self.download_cancelled:
                raise yt_dlp.DownloadError("Download cancelled by user")

            if progress_callback and d['status'] == 'downloading':
                try:
                    if 'total_bytes' in d:
                        progress = d['downloaded_bytes'] / d['total_bytes']
                    elif 'total_bytes_estimate' in d:
                        progress = d['downloaded_bytes'] / d['total_bytes_estimate']
                    else:
                        progress = 0

                    progress_callback({
                        'progress': progress,
                        'downloaded': d.get('downloaded_bytes', 0),
                        'total': d.get('total_bytes', d.get('total_bytes_estimate', 0)),
                        'speed': d.get('speed', 0),
                        'eta': d.get('eta', 0),
                        'filename': d.get('filename', ''),
                        'status': d.get('status', 'downloading')
                    })
                except Exception as e:
                    self.logger.error(f"Error in progress callback: {e}")

        try:
            with self.download_lock:
                self.download_cancelled = False

            # Ensure output directory exists
            Path(output_path).mkdir(parents=True, exist_ok=True)

            # Configure yt-dlp options
            ydl_opts = {
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [progress_hook],
                'format': self._get_format_selector(quality, format_ext),
                'writesubtitles': self.config.get('download_subtitles', False),
                'writeautomaticsub': self.config.get('download_auto_subtitles', False),
                'subtitleslangs': self.config.get('subtitle_languages', ['en']),
                'ignoreerrors': False,
                'no_warnings': False,
            }

            # Add post-processor for format conversion if needed
            if format_ext.lower() in ['mp4', 'mkv', 'avi']:
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': format_ext.lower(),
                }]
            elif format_ext.lower() == 'mp3':
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': self.config.get('audio_quality', '192'),
                }]
            elif format_ext.lower() in ['wav', 'flac', 'm4a', 'ogg']:
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': format_ext.lower(),
                }]

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.ydl_process = ydl
                ydl.download([url])

            # Check if cancelled during download
            if self.download_cancelled:
                if completion_callback:
                    completion_callback(False, "Download cancelled by user")
                return False

            if completion_callback:
                completion_callback(True, "Download completed successfully")

            return True

        except yt_dlp.DownloadError as e:
            if "cancelled" in str(e).lower():
                error_msg = "Download cancelled by user"
                self.logger.info(error_msg)
            else:
                error_msg = f"Download failed: {str(e)}"
                self.logger.error(error_msg)

            if completion_callback:
                completion_callback(False, error_msg)

            return False

        except Exception as e:
            error_msg = f"Download failed: {str(e)}"
            self.logger.error(error_msg)

            if completion_callback:
                completion_callback(False, error_msg)

            return False

        finally:
            self.ydl_process = None
    
    def _get_format_selector(self, quality: str, format_ext: str) -> str:
        """Get yt-dlp format selector string"""
        if quality.lower() == 'best':
            if format_ext.lower() == 'mp3':
                return 'bestaudio/best'
            return 'best'
        elif quality.lower() == 'audio only':
            return 'bestaudio/best'
        else:
            # Extract height from quality (e.g., '1080p' -> '1080')
            height = ''.join(filter(str.isdigit, quality))
            if height:
                if format_ext.lower() == 'mp3':
                    return 'bestaudio/best'
                return f'best[height<={height}]'
            return 'best'
    
    def download_video_async(
        self,
        url: str,
        output_path: str,
        quality: str = 'best',
        format_ext: str = 'mp4',
        progress_callback: Optional[Callable] = None,
        completion_callback: Optional[Callable] = None
    ) -> threading.Thread:
        """Download video asynchronously"""
        
        def download_thread():
            self.download_video(
                url, output_path, quality, format_ext,
                progress_callback, completion_callback
            )
        
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
        self.current_download = thread
        
        return thread
    
    def cancel_download(self):
        """Cancel current download"""
        try:
            with self.download_lock:
                self.download_cancelled = True

            self.logger.info("Download cancellation requested")

            # If there's an active yt-dlp process, try to interrupt it
            if self.ydl_process:
                try:
                    # This will cause the progress hook to raise an exception
                    self.logger.info("Interrupting yt-dlp process")
                except Exception as e:
                    self.logger.error(f"Error interrupting yt-dlp: {e}")

            # If there's a download thread, it will check the cancelled flag
            if self.current_download and self.current_download.is_alive():
                self.logger.info("Waiting for download thread to stop...")
                # The thread will stop when it checks the cancelled flag

            return True

        except Exception as e:
            self.logger.error(f"Error cancelling download: {e}")
            return False

    def is_download_active(self) -> bool:
        """Check if a download is currently active"""
        return (self.current_download and
                self.current_download.is_alive() and
                not self.download_cancelled)

    def get_download_status(self) -> Dict[str, Any]:
        """Get current download status"""
        return {
            'active': self.is_download_active(),
            'cancelled': self.download_cancelled,
            'thread_alive': self.current_download.is_alive() if self.current_download else False
        }
