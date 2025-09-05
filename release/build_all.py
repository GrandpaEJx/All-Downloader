#!/usr/bin/env python3
"""
Complete Release Builder for YTDL
Builds Android APK, Web App, and Desktop versions
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    # Check if flet is installed
    try:
        import flet
        print("✅ Flet is installed")
    except ImportError:
        print("❌ Flet is not installed. Run: uv add 'flet[all]'")
        return False
    
    return True

def clean_build_directory():
    """Clean previous builds"""
    print("🧹 Cleaning previous builds...")
    build_dir = Path("build")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(exist_ok=True)
    print("✅ Build directory cleaned")

def build_desktop():
    """Build desktop application"""
    print("🖥️ Building Desktop Application...")
    
    platforms = ["windows", "macos", "linux"]
    success_count = 0
    
    for platform in platforms:
        print(f"📦 Building for {platform}...")
        build_cmd = f'flet build {platform} --project "YTDL" --verbose'
        if run_command(build_cmd, f"Building {platform} version"):
            success_count += 1
    
    return success_count > 0

def build_android():
    """Build Android APK"""
    print("📱 Building Android APK...")
    build_cmd = 'flet build apk --project "YTDL" --org com.grandpaejx.ytdl --verbose'
    return run_command(build_cmd, "Building Android APK")

def build_web():
    """Build Web Application"""
    print("🌐 Building Web Application...")
    build_cmd = 'flet build web --project "YTDL" --web-renderer canvaskit --verbose'
    return run_command(build_cmd, "Building Web Application")

def create_release_package():
    """Create release package with all builds"""
    print("📦 Creating release package...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    release_dir = Path(f"release/ytdl_release_{timestamp}")
    release_dir.mkdir(parents=True, exist_ok=True)
    
    build_dir = Path("build")
    if not build_dir.exists():
        print("❌ No build directory found")
        return False
    
    # Copy builds to release directory
    for item in build_dir.iterdir():
        if item.is_dir():
            dest = release_dir / item.name
            shutil.copytree(item, dest)
            print(f"✅ Copied {item.name} to release package")
    
    # Create release notes
    release_notes = f"""
# YTDL Release {timestamp}

## 🎉 Complete Release Package

### 📱 Android APK
- Location: `apk/YTDL.apk`
- Install: `adb install YTDL.apk`
- Features: Full YTDL functionality on Android

### 🌐 Web Application
- Location: `web/`
- Deploy: Upload to any web server
- Features: Browser-based YTDL with modern UI

### 🖥️ Desktop Applications
- Windows: `windows/YTDL.exe`
- macOS: `macos/YTDL.app`
- Linux: `linux/YTDL`

## 🚀 Features
- 50+ platform support including adult content
- Video/Audio downloads with quality selection
- Batch processing with queue management
- Format conversion with FFmpeg
- Modern Material Design interface
- Instant theme switching (Dark/Light/Kawaii)
- Cross-platform compatibility

## 📋 Installation

### Android
```bash
adb install apk/YTDL.apk
```

### Web
Upload `web/` contents to your web server or static hosting.

### Desktop
Extract and run the appropriate executable for your platform.

## 🔧 Technical Details
- Built with Flet framework
- Python-based with native performance
- Material Design UI components
- Cross-platform compatibility
- Production-ready architecture

## 📞 Support
- GitHub: https://github.com/GrandpaEJx/All-Downloader
- Issues: Report bugs and feature requests on GitHub

---
Built on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    with open(release_dir / "README.md", "w") as f:
        f.write(release_notes)
    
    print(f"✅ Release package created: {release_dir}")
    return True

def main():
    """Main build process"""
    print("🚀 YTDL Complete Release Builder")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Clean build directory
    clean_build_directory()
    
    # Change to project root
    os.chdir(Path(__file__).parent.parent)
    
    # Track build results
    results = {
        "desktop": False,
        "android": False,
        "web": False
    }
    
    # Build all platforms
    print("\n📦 Building all platforms...")
    
    # Desktop builds
    results["desktop"] = build_desktop()
    
    # Android build
    results["android"] = build_android()
    
    # Web build
    results["web"] = build_web()
    
    # Create release package
    if any(results.values()):
        create_release_package()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Build Summary:")
    print(f"🖥️ Desktop: {'✅ Success' if results['desktop'] else '❌ Failed'}")
    print(f"📱 Android: {'✅ Success' if results['android'] else '❌ Failed'}")
    print(f"🌐 Web: {'✅ Success' if results['web'] else '❌ Failed'}")
    
    success_count = sum(results.values())
    if success_count > 0:
        print(f"\n🎉 {success_count}/3 builds completed successfully!")
        print("📦 Release package created in release/ directory")
    else:
        print("\n❌ All builds failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
