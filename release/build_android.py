#!/usr/bin/env python3
"""
Android APK Build Script for YTDL
Uses Flet's built-in Android packaging
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
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
    
    # Check if Android SDK is available (optional - Flet can handle this)
    android_home = os.environ.get('ANDROID_HOME')
    if android_home:
        print(f"✅ Android SDK found at: {android_home}")
    else:
        print("⚠️ ANDROID_HOME not set. Flet will use its own Android SDK.")
    
    return True

def build_android_apk():
    """Build Android APK using Flet"""
    print("📱 Building Android APK...")
    
    # Ensure we're in the project root
    os.chdir(Path(__file__).parent.parent)
    
    # Flet build command for Android
    build_cmd = 'flet build apk --project "YTDL" --description "All-in-One Video/Audio Downloader" --org com.grandpaejx.ytdl --template adaptive --build-number 1 --build-version 1.0.0 --verbose'
    return run_command(build_cmd, "Building Android APK")

def main():
    """Main build process"""
    print("🚀 YTDL Android APK Builder")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Build APK
    if build_android_apk():
        print("\n🎉 Android APK build completed!")
        print("📱 APK location: build/apk/")
        print("📋 Install with: adb install build/apk/YTDL.apk")
    else:
        print("\n❌ Android APK build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
