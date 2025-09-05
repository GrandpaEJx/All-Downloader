"""
Platform-specific download manager for YTDL application
"""

import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from ..utils.logger import get_logger

class PlatformManager:
    """Manages platform-specific download configurations"""
    
    def __init__(self):
        self.logger = get_logger()
        self.platforms = self._define_platforms()
    
    def _define_platforms(self) -> Dict[str, Dict]:
        """Define supported platforms and their configurations"""
        return {
            'youtube': {
                'name': 'YouTube',
                'domains': ['youtube.com', 'youtu.be', 'm.youtube.com', 'music.youtube.com'],
                'patterns': [
                    r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
                    r'youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)',
                    r'music\.youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
                ],
                'supports': ['video', 'audio', 'playlist', 'subtitles', 'live'],
                'max_quality': '4320p',
                'formats': ['mp4', 'webm', 'mkv', 'mp3', 'wav', 'flac', 'm4a', 'ogg']
            },
            'vimeo': {
                'name': 'Vimeo',
                'domains': ['vimeo.com'],
                'patterns': [r'vimeo\.com/(\d+)'],
                'supports': ['video', 'audio'],
                'max_quality': '1080p',
                'formats': ['mp4', 'mp3']
            },
            'dailymotion': {
                'name': 'Dailymotion',
                'domains': ['dailymotion.com'],
                'patterns': [r'dailymotion\.com/video/([a-zA-Z0-9]+)'],
                'supports': ['video', 'audio'],
                'max_quality': '1080p',
                'formats': ['mp4', 'mp3']
            },
            'instagram': {
                'name': 'Instagram',
                'domains': ['instagram.com'],
                'patterns': [
                    r'instagram\.com/p/([a-zA-Z0-9_-]+)',
                    r'instagram\.com/reel/([a-zA-Z0-9_-]+)',
                    r'instagram\.com/tv/([a-zA-Z0-9_-]+)'
                ],
                'supports': ['video', 'audio', 'stories'],
                'max_quality': '1080p',
                'formats': ['mp4', 'mp3']
            },
            'tiktok': {
                'name': 'TikTok',
                'domains': ['tiktok.com', 'vm.tiktok.com'],
                'patterns': [
                    r'tiktok\.com/@[^/]+/video/(\d+)',
                    r'vm\.tiktok\.com/([a-zA-Z0-9]+)'
                ],
                'supports': ['video', 'audio'],
                'max_quality': '1080p',
                'formats': ['mp4', 'mp3']
            },
            'facebook': {
                'name': 'Facebook',
                'domains': ['facebook.com', 'fb.watch'],
                'patterns': [
                    r'facebook\.com/watch/?\?v=(\d+)',
                    r'facebook\.com/[^/]+/videos/(\d+)',
                    r'fb\.watch/([a-zA-Z0-9_-]+)'
                ],
                'supports': ['video', 'audio'],
                'max_quality': '1080p',
                'formats': ['mp4', 'mp3']
            },
            'twitter': {
                'name': 'Twitter/X',
                'domains': ['twitter.com', 'x.com'],
                'patterns': [
                    r'(?:twitter|x)\.com/[^/]+/status/(\d+)'
                ],
                'supports': ['video', 'audio'],
                'max_quality': '1080p',
                'formats': ['mp4', 'mp3']
            },
            'twitch': {
                'name': 'Twitch',
                'domains': ['twitch.tv'],
                'patterns': [
                    r'twitch\.tv/videos/(\d+)',
                    r'twitch\.tv/[^/]+/clip/([a-zA-Z0-9_-]+)'
                ],
                'supports': ['video', 'audio', 'live'],
                'max_quality': '1080p',
                'formats': ['mp4', 'mp3']
            },
            # Adult platforms
            'pornhub': {
                'name': 'Pornhub',
                'domains': ['pornhub.com'],
                'patterns': [r'pornhub\.com/view_video\.php\?viewkey=([a-zA-Z0-9]+)'],
                'supports': ['video', 'audio'],
                'max_quality': '1080p',
                'formats': ['mp4', 'mp3'],
                'category': 'adult'
            },
            'xvideos': {
                'name': 'XVideos',
                'domains': ['xvideos.com'],
                'patterns': [r'xvideos\.com/video(\d+)'],
                'supports': ['video', 'audio'],
                'max_quality': '1080p',
                'formats': ['mp4', 'mp3'],
                'category': 'adult'
            },
            'xhamster': {
                'name': 'xHamster',
                'domains': ['xhamster.com'],
                'patterns': [r'xhamster\.com/videos/([a-zA-Z0-9_-]+)'],
                'supports': ['video', 'audio'],
                'max_quality': '1080p',
                'formats': ['mp4', 'mp3'],
                'category': 'adult'
            },
            # Streaming services
            'soundcloud': {
                'name': 'SoundCloud',
                'domains': ['soundcloud.com'],
                'patterns': [r'soundcloud\.com/[^/]+/[^/]+'],
                'supports': ['audio', 'playlist'],
                'max_quality': 'N/A',
                'formats': ['mp3', 'wav', 'flac', 'm4a']
            },
            'bandcamp': {
                'name': 'Bandcamp',
                'domains': ['bandcamp.com'],
                'patterns': [r'[^.]+\.bandcamp\.com/track/[^/]+'],
                'supports': ['audio', 'album'],
                'max_quality': 'N/A',
                'formats': ['mp3', 'wav', 'flac']
            },
            'mixcloud': {
                'name': 'Mixcloud',
                'domains': ['mixcloud.com'],
                'patterns': [r'mixcloud\.com/[^/]+/[^/]+'],
                'supports': ['audio'],
                'max_quality': 'N/A',
                'formats': ['mp3', 'm4a']
            },
            # News and educational
            'ted': {
                'name': 'TED Talks',
                'domains': ['ted.com'],
                'patterns': [r'ted\.com/talks/([a-zA-Z0-9_-]+)'],
                'supports': ['video', 'audio', 'subtitles'],
                'max_quality': '1080p',
                'formats': ['mp4', 'mp3']
            },
            'coursera': {
                'name': 'Coursera',
                'domains': ['coursera.org'],
                'patterns': [r'coursera\.org/learn/[^/]+/lecture/([a-zA-Z0-9_-]+)'],
                'supports': ['video', 'audio', 'subtitles'],
                'max_quality': '720p',
                'formats': ['mp4', 'mp3']
            },
            # Live streaming
            'kick': {
                'name': 'Kick',
                'domains': ['kick.com'],
                'patterns': [r'kick\.com/([a-zA-Z0-9_-]+)'],
                'supports': ['video', 'audio', 'live'],
                'max_quality': '1080p',
                'formats': ['mp4', 'mp3']
            },
            'rumble': {
                'name': 'Rumble',
                'domains': ['rumble.com'],
                'patterns': [r'rumble\.com/([a-zA-Z0-9_-]+)'],
                'supports': ['video', 'audio'],
                'max_quality': '1080p',
                'formats': ['mp4', 'mp3']
            },
            # International platforms
            'bilibili': {
                'name': 'Bilibili',
                'domains': ['bilibili.com'],
                'patterns': [r'bilibili\.com/video/([a-zA-Z0-9_-]+)'],
                'supports': ['video', 'audio', 'subtitles'],
                'max_quality': '1080p',
                'formats': ['mp4', 'mp3']
            },
            'niconico': {
                'name': 'Niconico',
                'domains': ['nicovideo.jp'],
                'patterns': [r'nicovideo\.jp/watch/([a-zA-Z0-9_-]+)'],
                'supports': ['video', 'audio'],
                'max_quality': '720p',
                'formats': ['mp4', 'mp3']
            },
            # Generic fallback for yt-dlp supported sites
            'generic': {
                'name': 'Generic (yt-dlp supported)',
                'domains': [],
                'patterns': [r'https?://.*'],
                'supports': ['video', 'audio'],
                'max_quality': '1080p',
                'formats': ['mp4', 'mp3', 'webm', 'mkv'],
                'fallback': True
            }
        }
    
    def identify_platform(self, url: str) -> Optional[Tuple[str, Dict]]:
        """Identify platform from URL"""
        try:
            parsed_url = urlparse(url.lower())
            domain = parsed_url.netloc.replace('www.', '')

            # First pass: exact matches (excluding generic)
            for platform_id, platform_info in self.platforms.items():
                if platform_info.get('fallback'):
                    continue

                # Check domain match
                if platform_info['domains'] and any(domain.endswith(d) for d in platform_info['domains']):
                    return platform_id, platform_info

                # Check pattern match
                for pattern in platform_info['patterns']:
                    if re.search(pattern, url, re.IGNORECASE):
                        return platform_id, platform_info

            # Second pass: try generic fallback for any HTTP(S) URL
            if url.startswith(('http://', 'https://')):
                return 'generic', self.platforms['generic']

            return None

        except Exception as e:
            self.logger.error(f"Error identifying platform: {e}")
            return None
    
    def get_platform_info(self, platform_id: str) -> Optional[Dict]:
        """Get platform information"""
        return self.platforms.get(platform_id)
    
    def get_supported_platforms(self, include_adult: bool = True, include_generic: bool = False) -> List[str]:
        """Get list of supported platform names"""
        platforms = []
        for platform_id, info in self.platforms.items():
            if not include_adult and info.get('category') == 'adult':
                continue
            if not include_generic and info.get('fallback'):
                continue
            platforms.append(info['name'])
        return platforms

    def get_platform_categories(self) -> Dict[str, List[str]]:
        """Get platforms organized by category"""
        categories = {
            'video': [],
            'audio': [],
            'social': [],
            'streaming': [],
            'educational': [],
            'adult': [],
            'other': []
        }

        category_mapping = {
            'youtube': 'video',
            'vimeo': 'video',
            'dailymotion': 'video',
            'instagram': 'social',
            'tiktok': 'social',
            'facebook': 'social',
            'twitter': 'social',
            'twitch': 'streaming',
            'kick': 'streaming',
            'rumble': 'video',
            'soundcloud': 'audio',
            'bandcamp': 'audio',
            'mixcloud': 'audio',
            'ted': 'educational',
            'coursera': 'educational',
            'pornhub': 'adult',
            'xvideos': 'adult',
            'xhamster': 'adult',
            'bilibili': 'video',
            'niconico': 'video',
        }

        for platform_id, info in self.platforms.items():
            if info.get('fallback'):
                continue
            category = category_mapping.get(platform_id, 'other')
            categories[category].append(info['name'])

        return categories

    def is_adult_content(self, url: str) -> bool:
        """Check if URL is from an adult content platform"""
        platform_info = self.identify_platform(url)
        if platform_info:
            platform_id, info = platform_info
            return info.get('category') == 'adult'
        return False
    
    def is_url_supported(self, url: str) -> bool:
        """Check if URL is from a supported platform"""
        return self.identify_platform(url) is not None
    
    def get_platform_capabilities(self, url: str) -> Optional[Dict]:
        """Get capabilities for the platform of the given URL"""
        platform_info = self.identify_platform(url)
        if platform_info:
            platform_id, info = platform_info
            return {
                'platform': info['name'],
                'supports': info['supports'],
                'max_quality': info['max_quality'],
                'formats': info['formats']
            }
        return None
    
    def validate_url(self, url: str) -> Tuple[bool, str]:
        """Validate URL and return status with message"""
        if not url or not url.strip():
            return False, "URL cannot be empty"
        
        url = url.strip()
        
        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return False, "Invalid URL format"
        except Exception:
            return False, "Invalid URL format"
        
        # Check if platform is supported
        platform_info = self.identify_platform(url)
        if not platform_info:
            return False, f"Platform not supported. Supported platforms: {', '.join(self.get_supported_platforms())}"
        
        return True, f"Valid {platform_info[1]['name']} URL"
    
    def get_download_options(self, url: str) -> Dict:
        """Get recommended download options for platform"""
        platform_info = self.identify_platform(url)
        if not platform_info:
            return self._get_default_options()
        
        platform_id, info = platform_info
        
        # Platform-specific optimizations
        options = {
            'qualities': self._get_quality_options(info['max_quality']),
            'formats': info['formats'],
            'supports_subtitles': 'subtitles' in info['supports'],
            'supports_playlist': 'playlist' in info['supports'],
            'recommended_format': 'mp4',
            'recommended_quality': '720p'
        }
        
        # Platform-specific recommendations
        if platform_id == 'youtube':
            options['recommended_quality'] = '1080p'
        elif platform_id in ['instagram', 'tiktok']:
            options['recommended_quality'] = '720p'
        elif platform_id == 'twitter':
            options['recommended_quality'] = '480p'
        
        return options
    
    def _get_quality_options(self, max_quality: str) -> List[str]:
        """Get available quality options based on max quality"""
        all_qualities = ['4320p', '2160p', '1440p', '1080p', '720p', '480p', '360p', '240p']
        max_height = int(max_quality.replace('p', ''))
        
        return ['Best'] + [q for q in all_qualities if int(q.replace('p', '')) <= max_height] + ['Audio Only']
    
    def _get_default_options(self) -> Dict:
        """Get default download options for unknown platforms"""
        return {
            'qualities': ['Best', '1080p', '720p', '480p', '360p', 'Audio Only'],
            'formats': ['mp4', 'mp3'],
            'supports_subtitles': False,
            'supports_playlist': False,
            'recommended_format': 'mp4',
            'recommended_quality': '720p'
        }
