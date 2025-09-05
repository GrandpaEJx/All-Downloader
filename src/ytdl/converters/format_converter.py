"""
Format converter module for YTDL application using FFmpeg
"""

import ffmpeg
import os
import threading
import subprocess
from pathlib import Path
from typing import Dict, Any, Callable, Optional, List, Tuple
from ..utils.config import Config
from ..utils.logger import get_logger

class FormatConverter:
    """Format converter using FFmpeg"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger()
        self.current_conversion = None
        self.conversion_cancelled = False
        self.ffmpeg_process = None
        self.conversion_lock = threading.Lock()
        
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get supported input and output formats"""
        return {
            'video_input': ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm', '3gp', 'm4v'],
            'video_output': ['mp4', 'avi', 'mkv', 'mov', 'webm', 'ogv'],
            'audio_input': ['mp3', 'wav', 'flac', 'm4a', 'aac', 'ogg', 'wma'],
            'audio_output': ['mp3', 'wav', 'flac', 'm4a', 'aac', 'ogg']
        }
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get information about a media file"""
        try:
            probe = ffmpeg.probe(file_path)
            
            info = {
                'duration': float(probe['format'].get('duration', 0)),
                'size': int(probe['format'].get('size', 0)),
                'bitrate': int(probe['format'].get('bit_rate', 0)),
                'format': probe['format'].get('format_name', ''),
                'streams': []
            }
            
            for stream in probe['streams']:
                stream_info = {
                    'type': stream.get('codec_type', ''),
                    'codec': stream.get('codec_name', ''),
                    'bitrate': int(stream.get('bit_rate', 0)) if stream.get('bit_rate') else 0,
                }
                
                if stream['codec_type'] == 'video':
                    stream_info.update({
                        'width': stream.get('width', 0),
                        'height': stream.get('height', 0),
                        'fps': eval(stream.get('r_frame_rate', '0/1')) if stream.get('r_frame_rate') else 0
                    })
                elif stream['codec_type'] == 'audio':
                    stream_info.update({
                        'sample_rate': int(stream.get('sample_rate', 0)) if stream.get('sample_rate') else 0,
                        'channels': stream.get('channels', 0)
                    })
                
                info['streams'].append(stream_info)
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting file info: {e}")
            raise Exception(f"Failed to get file information: {str(e)}")
    
    def convert_file(
        self,
        input_path: str,
        output_path: str,
        output_format: str,
        quality: str = 'medium',
        custom_options: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable] = None,
        completion_callback: Optional[Callable] = None
    ) -> bool:
        """Convert file to specified format"""
        
        try:
            with self.conversion_lock:
                self.conversion_cancelled = False
            
            # Ensure input file exists
            if not Path(input_path).exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Get file info for progress tracking
            file_info = self.get_file_info(input_path)
            total_duration = file_info.get('duration', 0)
            
            # Build FFmpeg command
            input_stream = ffmpeg.input(input_path)
            
            # Apply conversion options based on format and quality
            output_options = self._get_conversion_options(output_format, quality, custom_options)
            
            output_stream = ffmpeg.output(input_stream, output_path, **output_options)
            
            # Run conversion with progress tracking
            cmd = ffmpeg.compile(output_stream, overwrite_output=True)
            
            self.logger.info(f"Starting conversion: {input_path} -> {output_path}")
            self.logger.debug(f"FFmpeg command: {' '.join(cmd)}")
            
            # Start FFmpeg process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            self.ffmpeg_process = process
            
            # Monitor progress
            if progress_callback:
                self._monitor_progress(process, total_duration, progress_callback)
            
            # Wait for completion
            stdout, stderr = process.communicate()
            
            # Check if cancelled
            if self.conversion_cancelled:
                if completion_callback:
                    completion_callback(False, "Conversion cancelled by user")
                return False
            
            # Check for errors
            if process.returncode != 0:
                error_msg = f"FFmpeg error: {stderr}"
                self.logger.error(error_msg)
                if completion_callback:
                    completion_callback(False, error_msg)
                return False
            
            self.logger.info(f"Conversion completed: {output_path}")
            if completion_callback:
                completion_callback(True, "Conversion completed successfully")
            
            return True
            
        except Exception as e:
            error_msg = f"Conversion failed: {str(e)}"
            self.logger.error(error_msg)
            
            if completion_callback:
                completion_callback(False, error_msg)
            
            return False
        
        finally:
            self.ffmpeg_process = None
    
    def _get_conversion_options(
        self, 
        output_format: str, 
        quality: str, 
        custom_options: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get FFmpeg options for conversion"""
        
        options = {}
        
        # Quality presets
        quality_presets = {
            'low': {'crf': 28, 'preset': 'fast'},
            'medium': {'crf': 23, 'preset': 'medium'},
            'high': {'crf': 18, 'preset': 'slow'},
            'lossless': {'crf': 0, 'preset': 'veryslow'}
        }
        
        # Format-specific options
        if output_format.lower() in ['mp4', 'mkv', 'avi', 'mov', 'webm']:
            # Video formats
            preset = quality_presets.get(quality, quality_presets['medium'])
            options.update({
                'vcodec': 'libx264',
                'crf': preset['crf'],
                'preset': preset['preset'],
                'acodec': 'aac',
                'audio_bitrate': '128k'
            })
            
        elif output_format.lower() in ['mp3', 'wav', 'flac', 'm4a', 'aac', 'ogg']:
            # Audio formats
            if output_format.lower() == 'mp3':
                bitrate_map = {
                    'low': '128k',
                    'medium': '192k',
                    'high': '320k',
                    'lossless': '320k'
                }
                options.update({
                    'acodec': 'libmp3lame',
                    'audio_bitrate': bitrate_map.get(quality, '192k')
                })
            elif output_format.lower() == 'wav':
                options.update({'acodec': 'pcm_s16le'})
            elif output_format.lower() == 'flac':
                options.update({'acodec': 'flac'})
            elif output_format.lower() == 'm4a':
                options.update({'acodec': 'aac'})
            elif output_format.lower() == 'ogg':
                options.update({'acodec': 'libvorbis'})
        
        # Apply custom options
        if custom_options:
            options.update(custom_options)
        
        return options
    
    def _monitor_progress(self, process, total_duration: float, progress_callback: Callable):
        """Monitor FFmpeg progress"""
        try:
            while process.poll() is None:
                if self.conversion_cancelled:
                    process.terminate()
                    break
                
                # Read stderr for progress info
                line = process.stderr.readline()
                if line:
                    # Parse time from FFmpeg output
                    if 'time=' in line:
                        try:
                            time_str = line.split('time=')[1].split()[0]
                            current_time = self._parse_time(time_str)
                            
                            if total_duration > 0:
                                progress = min(current_time / total_duration, 1.0)
                                progress_callback({
                                    'progress': progress,
                                    'current_time': current_time,
                                    'total_time': total_duration,
                                    'status': 'converting'
                                })
                        except Exception:
                            pass
                            
        except Exception as e:
            self.logger.error(f"Error monitoring progress: {e}")
    
    def _parse_time(self, time_str: str) -> float:
        """Parse time string (HH:MM:SS.mmm) to seconds"""
        try:
            parts = time_str.split(':')
            if len(parts) == 3:
                hours = float(parts[0])
                minutes = float(parts[1])
                seconds = float(parts[2])
                return hours * 3600 + minutes * 60 + seconds
        except Exception:
            pass
        return 0.0
    
    def convert_file_async(
        self,
        input_path: str,
        output_path: str,
        output_format: str,
        quality: str = 'medium',
        custom_options: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable] = None,
        completion_callback: Optional[Callable] = None
    ) -> threading.Thread:
        """Convert file asynchronously"""
        
        def conversion_thread():
            self.convert_file(
                input_path, output_path, output_format, quality,
                custom_options, progress_callback, completion_callback
            )
        
        thread = threading.Thread(target=conversion_thread, daemon=True)
        thread.start()
        self.current_conversion = thread
        
        return thread
    
    def cancel_conversion(self):
        """Cancel current conversion"""
        try:
            with self.conversion_lock:
                self.conversion_cancelled = True
            
            self.logger.info("Conversion cancellation requested")
            
            if self.ffmpeg_process:
                try:
                    self.ffmpeg_process.terminate()
                    self.logger.info("FFmpeg process terminated")
                except Exception as e:
                    self.logger.error(f"Error terminating FFmpeg: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error cancelling conversion: {e}")
            return False
    
    def is_conversion_active(self) -> bool:
        """Check if a conversion is currently active"""
        return (self.current_conversion and 
                self.current_conversion.is_alive() and 
                not self.conversion_cancelled)
    
    def get_conversion_status(self) -> Dict[str, Any]:
        """Get current conversion status"""
        return {
            'active': self.is_conversion_active(),
            'cancelled': self.conversion_cancelled,
            'thread_alive': self.current_conversion.is_alive() if self.current_conversion else False
        }
