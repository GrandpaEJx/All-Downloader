"""
Audio downloader module for YTDL application
"""

import yt_dlp
import os
import threading
from pathlib import Path
from typing import Dict, Any, Callable, Optional, List
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, APIC
import requests
from ..utils.config import Config
from ..utils.logger import get_logger

class AudioDownloader:
    """Audio downloader using yt-dlp with metadata support"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger()
        self.current_download = None
        self.download_cancelled = False
        self.ydl_process = None
        self.download_lock = threading.Lock()
        
    def get_audio_info(self, url: str) -> Dict[str, Any]:
        """Get audio information without downloading"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'artist': info.get('uploader', info.get('artist', 'Unknown')),
                    'album': info.get('album', ''),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'thumbnail': info.get('thumbnail'),
                    'description': info.get('description', ''),
                    'upload_date': info.get('upload_date'),
                    'formats': self._extract_audio_formats(info.get('formats', [])),
                    'genre': info.get('genre', ''),
                    'release_year': info.get('release_year', ''),
                }
                
        except Exception as e:
            self.logger.error(f"Error getting audio info: {e}")
            raise Exception(f"Failed to get audio information: {str(e)}")
    
    def _extract_audio_formats(self, formats: List[Dict]) -> List[Dict[str, Any]]:
        """Extract and organize available audio formats"""
        audio_formats = []
        
        for fmt in formats:
            if fmt.get('acodec') != 'none':
                audio_formats.append({
                    'format_id': fmt.get('format_id'),
                    'ext': fmt.get('ext'),
                    'abr': fmt.get('abr', 0),
                    'asr': fmt.get('asr', 0),
                    'filesize': fmt.get('filesize'),
                    'quality': fmt.get('quality', 0)
                })
        
        return sorted(audio_formats, key=lambda x: x.get('abr', 0), reverse=True)
    
    def download_audio(
        self,
        url: str,
        output_path: str,
        quality: str = '192',
        format_ext: str = 'mp3',
        add_metadata: bool = True,
        progress_callback: Optional[Callable] = None,
        completion_callback: Optional[Callable] = None
    ) -> bool:
        """Download audio with specified options"""
        
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
            
            # Configure yt-dlp options for audio
            ydl_opts = {
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [progress_hook],
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': format_ext.lower(),
                    'preferredquality': quality,
                }],
                'writeinfojson': add_metadata,
                'writethumbnail': add_metadata,
                'embedthumbnail': add_metadata and format_ext.lower() == 'mp3',
                'ignoreerrors': False,
                'no_warnings': False,
            }
            
            # Get audio info for metadata
            audio_info = None
            if add_metadata:
                try:
                    audio_info = self.get_audio_info(url)
                except Exception as e:
                    self.logger.warning(f"Could not get audio info for metadata: {e}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.ydl_process = ydl
                ydl.download([url])
            
            # Add metadata if requested and format is MP3
            if add_metadata and format_ext.lower() == 'mp3' and audio_info:
                self._add_mp3_metadata(output_path, audio_info)
            
            # Check if cancelled during download
            if self.download_cancelled:
                if completion_callback:
                    completion_callback(False, "Download cancelled by user")
                return False
            
            if completion_callback:
                completion_callback(True, "Audio download completed successfully")
            
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
    
    def _add_mp3_metadata(self, output_path: str, audio_info: Dict[str, Any]):
        """Add metadata to MP3 files"""
        try:
            # Find the downloaded MP3 file
            mp3_files = list(Path(output_path).glob("*.mp3"))
            if not mp3_files:
                return
            
            mp3_file = mp3_files[-1]  # Get the most recent file
            
            # Load the MP3 file
            audio = MP3(str(mp3_file), ID3=ID3)
            
            # Add ID3 tags if they don't exist
            if audio.tags is None:
                audio.add_tags()
            
            # Set metadata
            audio.tags.add(TIT2(encoding=3, text=audio_info.get('title', '')))
            audio.tags.add(TPE1(encoding=3, text=audio_info.get('artist', '')))
            audio.tags.add(TALB(encoding=3, text=audio_info.get('album', '')))
            
            if audio_info.get('release_year'):
                audio.tags.add(TDRC(encoding=3, text=str(audio_info['release_year'])))
            
            # Add thumbnail as album art
            if audio_info.get('thumbnail'):
                try:
                    response = requests.get(audio_info['thumbnail'], timeout=10)
                    if response.status_code == 200:
                        audio.tags.add(APIC(
                            encoding=3,
                            mime='image/jpeg',
                            type=3,  # Cover (front)
                            desc='Cover',
                            data=response.content
                        ))
                except Exception as e:
                    self.logger.warning(f"Could not add album art: {e}")
            
            # Save the file
            audio.save()
            self.logger.info(f"Added metadata to {mp3_file}")
            
        except Exception as e:
            self.logger.error(f"Error adding MP3 metadata: {e}")
    
    def download_audio_async(
        self,
        url: str,
        output_path: str,
        quality: str = '192',
        format_ext: str = 'mp3',
        add_metadata: bool = True,
        progress_callback: Optional[Callable] = None,
        completion_callback: Optional[Callable] = None
    ) -> threading.Thread:
        """Download audio asynchronously"""
        
        def download_thread():
            self.download_audio(
                url, output_path, quality, format_ext, add_metadata,
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
            
            self.logger.info("Audio download cancellation requested")
            
            if self.ydl_process:
                try:
                    self.logger.info("Interrupting yt-dlp process")
                except Exception as e:
                    self.logger.error(f"Error interrupting yt-dlp: {e}")
            
            if self.current_download and self.current_download.is_alive():
                self.logger.info("Waiting for download thread to stop...")
                
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
