"""
Batch downloader module for YTDL application
"""

import threading
import time
from queue import Queue, Empty
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass
from enum import Enum
from ..utils.config import Config
from ..utils.logger import get_logger
from .video_downloader import VideoDownloader
from .audio_downloader import AudioDownloader

class DownloadType(Enum):
    VIDEO = "video"
    AUDIO = "audio"

class DownloadStatus(Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class DownloadItem:
    """Represents a single download item in the batch queue"""
    id: str
    url: str
    output_path: str
    download_type: DownloadType
    quality: str = 'best'
    format_ext: str = 'mp4'
    status: DownloadStatus = DownloadStatus.PENDING
    progress: float = 0.0
    error_message: str = ""
    filename: str = ""
    add_metadata: bool = True

class BatchDownloader:
    """Batch downloader with queue management"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger()
        
        # Initialize downloaders
        self.video_downloader = VideoDownloader(config)
        self.audio_downloader = AudioDownloader(config)
        
        # Queue management
        self.download_queue = Queue()
        self.active_downloads: Dict[str, DownloadItem] = {}
        self.completed_downloads: List[DownloadItem] = []
        self.failed_downloads: List[DownloadItem] = []
        
        # Threading
        self.worker_threads: List[threading.Thread] = []
        self.max_concurrent = config.get('concurrent_downloads', 3)
        self.is_running = False
        self.queue_lock = threading.Lock()
        
        # Callbacks
        self.progress_callback: Optional[Callable] = None
        self.status_callback: Optional[Callable] = None
        
    def set_callbacks(
        self, 
        progress_callback: Optional[Callable] = None,
        status_callback: Optional[Callable] = None
    ):
        """Set callbacks for progress and status updates"""
        self.progress_callback = progress_callback
        self.status_callback = status_callback
    
    def add_download(
        self,
        url: str,
        output_path: str,
        download_type: DownloadType,
        quality: str = 'best',
        format_ext: str = 'mp4',
        add_metadata: bool = True
    ) -> str:
        """Add a download to the queue"""
        
        # Generate unique ID
        download_id = f"{download_type.value}_{int(time.time() * 1000)}"
        
        item = DownloadItem(
            id=download_id,
            url=url,
            output_path=output_path,
            download_type=download_type,
            quality=quality,
            format_ext=format_ext,
            add_metadata=add_metadata
        )
        
        self.download_queue.put(item)
        self.logger.info(f"Added download to queue: {url}")
        
        # Notify status callback
        if self.status_callback:
            self.status_callback('item_added', item)
        
        return download_id
    
    def add_video_download(
        self,
        url: str,
        output_path: str,
        quality: str = 'best',
        format_ext: str = 'mp4'
    ) -> str:
        """Add a video download to the queue"""
        return self.add_download(
            url, output_path, DownloadType.VIDEO, quality, format_ext
        )
    
    def add_audio_download(
        self,
        url: str,
        output_path: str,
        quality: str = '192',
        format_ext: str = 'mp3',
        add_metadata: bool = True
    ) -> str:
        """Add an audio download to the queue"""
        return self.add_download(
            url, output_path, DownloadType.AUDIO, quality, format_ext, add_metadata
        )
    
    def add_bulk_downloads(self, urls: List[str], **kwargs) -> List[str]:
        """Add multiple downloads at once"""
        download_ids = []
        for url in urls:
            download_id = self.add_download(url, **kwargs)
            download_ids.append(download_id)
        return download_ids
    
    def start_batch(self):
        """Start the batch download process"""
        if self.is_running:
            self.logger.warning("Batch download is already running")
            return
        
        self.is_running = True
        self.logger.info(f"Starting batch download with {self.max_concurrent} concurrent downloads")
        
        # Start worker threads
        for i in range(self.max_concurrent):
            thread = threading.Thread(
                target=self._worker_thread,
                name=f"BatchWorker-{i+1}",
                daemon=True
            )
            thread.start()
            self.worker_threads.append(thread)
        
        # Notify status callback
        if self.status_callback:
            self.status_callback('batch_started', None)
    
    def stop_batch(self):
        """Stop the batch download process"""
        self.is_running = False
        self.logger.info("Stopping batch download")
        
        # Cancel active downloads
        with self.queue_lock:
            for item in self.active_downloads.values():
                item.status = DownloadStatus.CANCELLED
        
        # Clear queue
        while not self.download_queue.empty():
            try:
                item = self.download_queue.get_nowait()
                item.status = DownloadStatus.CANCELLED
                self.failed_downloads.append(item)
            except Empty:
                break
        
        # Wait for threads to finish
        for thread in self.worker_threads:
            if thread.is_alive():
                thread.join(timeout=5)
        
        self.worker_threads.clear()
        
        # Notify status callback
        if self.status_callback:
            self.status_callback('batch_stopped', None)
    
    def pause_batch(self):
        """Pause the batch download process"""
        self.is_running = False
        self.logger.info("Pausing batch download")
        
        if self.status_callback:
            self.status_callback('batch_paused', None)
    
    def resume_batch(self):
        """Resume the batch download process"""
        if not self.is_running and (not self.download_queue.empty() or self.active_downloads):
            self.start_batch()
    
    def remove_download(self, download_id: str) -> bool:
        """Remove a download from the queue"""
        with self.queue_lock:
            # Check if it's currently downloading
            if download_id in self.active_downloads:
                item = self.active_downloads[download_id]
                item.status = DownloadStatus.CANCELLED
                return True
        
        # TODO: Remove from queue (requires queue modification)
        return False
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        with self.queue_lock:
            return {
                'queue_size': self.download_queue.qsize(),
                'active_downloads': len(self.active_downloads),
                'completed_downloads': len(self.completed_downloads),
                'failed_downloads': len(self.failed_downloads),
                'is_running': self.is_running,
                'max_concurrent': self.max_concurrent
            }
    
    def get_all_downloads(self) -> Dict[str, List[DownloadItem]]:
        """Get all downloads organized by status"""
        with self.queue_lock:
            # Get pending downloads from queue
            pending = []
            temp_queue = Queue()
            
            while not self.download_queue.empty():
                try:
                    item = self.download_queue.get_nowait()
                    pending.append(item)
                    temp_queue.put(item)
                except Empty:
                    break
            
            # Restore queue
            while not temp_queue.empty():
                self.download_queue.put(temp_queue.get_nowait())
            
            return {
                'pending': pending,
                'active': list(self.active_downloads.values()),
                'completed': self.completed_downloads.copy(),
                'failed': self.failed_downloads.copy()
            }
    
    def _worker_thread(self):
        """Worker thread for processing downloads"""
        thread_name = threading.current_thread().name
        self.logger.info(f"Worker thread {thread_name} started")
        
        while self.is_running:
            try:
                # Get next download item
                item = self.download_queue.get(timeout=1)
                
                # Add to active downloads
                with self.queue_lock:
                    self.active_downloads[item.id] = item
                    item.status = DownloadStatus.DOWNLOADING
                
                self.logger.info(f"[{thread_name}] Starting download: {item.url}")
                
                # Notify status callback
                if self.status_callback:
                    self.status_callback('download_started', item)
                
                # Perform download
                success = self._perform_download(item)
                
                # Update status
                with self.queue_lock:
                    if item.id in self.active_downloads:
                        del self.active_downloads[item.id]
                    
                    if success and item.status != DownloadStatus.CANCELLED:
                        item.status = DownloadStatus.COMPLETED
                        self.completed_downloads.append(item)
                        self.logger.info(f"[{thread_name}] Download completed: {item.url}")
                    else:
                        if item.status != DownloadStatus.CANCELLED:
                            item.status = DownloadStatus.FAILED
                        self.failed_downloads.append(item)
                        self.logger.error(f"[{thread_name}] Download failed: {item.url}")
                
                # Notify status callback
                if self.status_callback:
                    self.status_callback('download_completed', item)
                
                # Mark task as done
                self.download_queue.task_done()
                
            except Empty:
                # No items in queue, continue
                continue
            except Exception as e:
                self.logger.error(f"Error in worker thread {thread_name}: {e}")
        
        self.logger.info(f"Worker thread {thread_name} stopped")
    
    def _perform_download(self, item: DownloadItem) -> bool:
        """Perform the actual download"""
        try:
            def progress_callback(progress_info):
                item.progress = progress_info.get('progress', 0)
                item.filename = progress_info.get('filename', '')
                
                if self.progress_callback:
                    self.progress_callback(item, progress_info)
            
            def completion_callback(success, message):
                if not success:
                    item.error_message = message
            
            if item.download_type == DownloadType.VIDEO:
                return self.video_downloader.download_video(
                    url=item.url,
                    output_path=item.output_path,
                    quality=item.quality,
                    format_ext=item.format_ext,
                    progress_callback=progress_callback,
                    completion_callback=completion_callback
                )
            elif item.download_type == DownloadType.AUDIO:
                return self.audio_downloader.download_audio(
                    url=item.url,
                    output_path=item.output_path,
                    quality=item.quality,
                    format_ext=item.format_ext,
                    add_metadata=item.add_metadata,
                    progress_callback=progress_callback,
                    completion_callback=completion_callback
                )
            
            return False
            
        except Exception as e:
            item.error_message = str(e)
            self.logger.error(f"Error downloading {item.url}: {e}")
            return False
