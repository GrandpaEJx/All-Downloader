# YTDL - All-in-One Video/Audio Downloader

A modern, clean GUI application built with **Flet** for downloading videos and audio from 50+ platforms with format conversion capabilities and beautiful Material Design interface.

## Features

### ✅ **Modern Flet Implementation**
- **🎨 Beautiful Material Design UI**: Built with Flet for modern, responsive interface
- **🧹 Clean, Minimal Code**: 60% less code than previous versions - easy to understand and maintain
- **📱 Cross-Platform**: Works on Windows, macOS, Linux with native performance
- **⚡ Instant Theme Switching**: Dark, Light, and Kawaii themes without restart

### ✅ **Comprehensive Platform Support**
Download from **50+ platforms** including:
- **Video**: YouTube, Vimeo, Dailymotion, Instagram, TikTok, Facebook, Twitter/X, Twitch, Rumble, Kick
- **Audio**: SoundCloud, Bandcamp, Mixcloud, YouTube Music
- **Educational**: TED Talks, Coursera
- **International**: Bilibili, Niconico
- **Adult Content**: Pornhub, XVideos, xHamster (with automatic detection and filtering)
- **Generic**: Any yt-dlp supported site (1000+ platforms)

### ✅ **Advanced Features**
- **🎬 Video Downloads**: Quality selection (4K to 360p), multiple formats (MP4, WEBM, MKV, AVI)
- **🎵 Audio Downloads**: High-quality audio (MP3, WAV, FLAC, M4A) with metadata and album art
- **📦 Batch Processing**: Queue management with 1-5 concurrent downloads
- **🔄 Format Conversion**: FFmpeg-powered conversion with quality presets
- **🚫 Download Cancellation**: Real-time cancellation with proper cleanup
- **📊 Progress Tracking**: Visual progress bars with speed and ETA
- **🔍 Smart URL Detection**: Automatic platform detection and validation
- **⚙️ Persistent Settings**: Configuration saved across sessions

## Installation

### Prerequisites
- Python 3.12 or higher
- FFmpeg (for format conversion)

### Using uv (Recommended)
```bash
git clone https://github.com/GrandpaEJx/ytdl
cd ytdl
uv sync
```

### Using pip
```bash
git clone https://github.com/GrandpaEJx/ytdl
cd ytdl
pip install -e .
```

## Usage

### GUI Application
```bash
# Start the modern Flet application
uv run python main.py

# Or directly (if dependencies are installed)
python main.py
```

## 🎯 **Application Interface**

### 📱 **Modern Flet GUI**
- **Navigation Rail**: Clean sidebar with Material Design icons
- **5 Main Pages**: Video, Audio, Batch, Converter, Settings
- **Instant Theme Switching**: Dark, Light, Kawaii modes
- **Responsive Design**: Adapts to window size
- **Real-time Feedback**: URL validation, progress tracking

### 🎬 **Video Download Page**
- URL input with instant platform detection
- Quality selection (Best, 1080p, 720p, 480p, 360p, Audio Only)
- Format options (MP4, WEBM, MKV, MP3)
- Download/Cancel controls with progress tracking

### 🎵 **Audio Download Page**
- Audio-specific quality settings (96k-320k bitrate)
- Format selection (MP3, WAV, FLAC, M4A, OGG)
- Metadata embedding option (album art, artist info)
- Optimized for music downloads

### 📦 **Batch Download Page**
- Multi-line URL input
- Mixed video/audio processing
- Concurrent download settings (1-5 simultaneous)
- Queue status tracking

### 🔄 **Format Converter Page**
- File browser integration
- Video/Audio format conversion
- Quality presets (Low, Medium, High, Lossless)
- FFmpeg-powered processing

### ⚙️ **Settings Page**
- Theme switching (instant, no restart)
- Default download directory
- Quality preferences
- Application configuration

## Supported Platforms

| Platform | Video | Audio | Batch | Subtitles | Max Quality | Category |
|----------|-------|-------|-------|-----------|-------------|----------|
| YouTube | ✅ | ✅ | ✅ | ✅ | 4320p | Video |
| Vimeo | ✅ | ✅ | ✅ | ✅ | 1080p | Video |
| Dailymotion | ✅ | ✅ | ✅ | ✅ | 1080p | Video |
| Instagram | ✅ | ✅ | ✅ | ❌ | 1080p | Social |
| TikTok | ✅ | ✅ | ✅ | ❌ | 1080p | Social |
| Facebook | ✅ | ✅ | ✅ | ❌ | 1080p | Social |
| Twitter/X | ✅ | ✅ | ✅ | ❌ | 1080p | Social |
| Twitch | ✅ | ✅ | ✅ | ❌ | 1080p | Streaming |
| SoundCloud | ✅ | ✅ | ✅ | ❌ | N/A | Audio |
| Bandcamp | ✅ | ✅ | ✅ | ❌ | N/A | Audio |
| Mixcloud | ✅ | ✅ | ✅ | ❌ | N/A | Audio |
| TED Talks | ✅ | ✅ | ✅ | ✅ | 1080p | Educational |
| Coursera | ✅ | ✅ | ✅ | ✅ | 720p | Educational |
| Pornhub | ✅ | ✅ | ✅ | ❌ | 1080p | Adult* |
| XVideos | ✅ | ✅ | ✅ | ❌ | 1080p | Adult* |
| xHamster | ✅ | ✅ | ✅ | ❌ | 1080p | Adult* |
| Rumble | ✅ | ✅ | ✅ | ❌ | 1080p | Video |
| Kick | ✅ | ✅ | ✅ | ❌ | 1080p | Streaming |
| Bilibili | ✅ | ✅ | ✅ | ✅ | 1080p | International |
| Niconico | ✅ | ✅ | ✅ | ❌ | 720p | International |
| **50+ More** | ✅ | ✅ | ✅ | ✅ | Varies | Generic |

*Adult content platforms with automatic detection and filtering
Legend: ✅ Fully Supported | ❌ Not Supported

## 📁 **Clean Project Structure**

```
ytdl/
├── main.py                    # Application launcher
├── pyproject.toml            # Dependencies (Flet-based)
├── README.md                 # This file
└── src/ytdl/
    ├── main.py               # Flet app entry point
    ├── gui/                  # Modern Flet GUI (6 files total)
    │   ├── app.py           # Main application class
    │   └── pages/           # Clean, minimal pages
    │       ├── video_page.py     # Video downloads
    │       ├── audio_page.py     # Audio downloads
    │       ├── batch_page.py     # Batch processing
    │       ├── converter_page.py # Format conversion
    │       └── settings_page.py  # Settings & themes
    ├── downloaders/         # Core download functionality
    │   ├── video_downloader.py   # Video downloader
    │   ├── audio_downloader.py   # Audio downloader
    │   ├── batch_downloader.py   # Batch processing
    │   └── platform_manager.py  # 50+ platform support
    ├── converters/          # Format conversion
    │   └── format_converter.py  # FFmpeg integration
    └── utils/              # Configuration & logging
        ├── config.py        # Settings management
        └── logger.py        # Logging system
```

**Key Benefits:**
- ✅ **60% less GUI code** (1,200 lines vs 3,000+ before)
- ✅ **Clean, minimal structure** - Easy to understand
- ✅ **Well-commented code** - Every function documented
- ✅ **Modern architecture** - Built with Flet framework

## Configuration

The application stores configuration in `~/.ytdl/config.json`:

```json
{
  "appearance_mode": "dark",
  "color_theme": "blue",
  "download_directory": "~/Downloads/YTDL",
  "video_quality": "best",
  "audio_quality": "192",
  "concurrent_downloads": 3,
  "theme_mode": "dark"
}
```

## Development

### Running Tests
```bash
python test_downloader.py
```

### Adding New Platforms
1. Add platform configuration to `platform_manager.py`
2. Update URL patterns and domain matching
3. Test with platform-specific URLs

## 🔧 **Dependencies**

### Core Dependencies
- **flet[all]**: Modern cross-platform GUI framework
- **yt-dlp**: Video/audio extraction from 1000+ sites
- **ffmpeg-python**: Format conversion engine
- **requests**: HTTP requests
- **beautifulsoup4**: Web scraping
- **mutagen**: Audio metadata handling

### Why Flet?
- ✅ **Modern UI**: Material Design components
- ✅ **Cross-platform**: Windows, macOS, Linux
- ✅ **Python-native**: No HTML/CSS/JS required
- ✅ **Fast development**: Minimal, clean code
- ✅ **Responsive**: Automatic responsive design

## 🎉 **Why Choose YTDL?**

### **Modern & Clean**
- Beautiful Material Design interface
- Minimal, well-commented codebase
- Easy to understand and maintain
- Built with modern Flet framework

### **Comprehensive**
- 50+ platforms including adult content
- Video, audio, and batch downloads
- Format conversion with FFmpeg
- Real-time progress tracking

### **User-Friendly**
- Instant theme switching
- Smart URL validation
- Download cancellation
- Persistent settings

### **Developer-Friendly**
- Clean, minimal code structure
- Excellent documentation
- Easy to extend and modify
- Production-ready architecture

## ⚖️ **Disclaimer**

This tool is for educational and personal use only. Please respect the terms of service of the platforms you download from and ensure you have the right to download the content.

## 🚀 **Get Started**

```bash
# Clone and run
git clone https://github.com/GrandpaEJx/ytdl
cd ytdl
uv sync
uv run python main.py
```

**Enjoy downloading with style!** 🎉
