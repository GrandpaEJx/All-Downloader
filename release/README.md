# YTDL Release Scripts

Complete release automation for YTDL across all platforms using Flet's built-in packaging.

## 🚀 Quick Start

### Build Everything
```bash
# Build all platforms (Android, Web, Desktop)
python release/build_all.py
```

### Individual Builds
```bash
# Android APK only
python release/build_android.py

# Web app only
python release/build_web.py
```

## 📱 Android APK Release

### Features
- ✅ Native Android app with full YTDL functionality
- ✅ Material Design interface optimized for mobile
- ✅ 50+ platform support including adult content detection
- ✅ Video/Audio downloads with quality selection
- ✅ Batch processing and format conversion
- ✅ Offline functionality once downloaded

### Build Process
```bash
python release/build_android.py
```

**Output**: `build/apk/YTDL.apk`

### Installation
```bash
# Install via ADB
adb install build/apk/YTDL.apk

# Or transfer APK to device and install manually
```

### Requirements
- Flet with Android support: `uv add 'flet[all]'`
- Android SDK (optional - Flet can handle this automatically)

## 🌐 Web Release

### Features
- ✅ Progressive Web App (PWA) capabilities
- ✅ Works on any modern browser
- ✅ Responsive design for mobile and desktop
- ✅ All YTDL features (with browser limitations)
- ✅ Offline caching for better performance

### Build Process
```bash
python release/build_web.py
```

**Output**: `build/web/` directory with complete web app

### Deployment Options

#### 1. Static Hosting (Recommended)
- **GitHub Pages**: Upload to `gh-pages` branch
- **Netlify**: Drag and drop `build/web` folder
- **Vercel**: Connect GitHub repo and deploy
- **Firebase Hosting**: `firebase deploy`

#### 2. Traditional Web Server
- **Apache**: Use included `.htaccess` file
- **Nginx**: Use included `nginx.conf` configuration
- **Any HTTP server**: Serve static files from `build/web/`

#### 3. Local Testing
```bash
cd build/web
python -m http.server 8000
# Visit http://localhost:8000
```

### Browser Compatibility
- Chrome/Chromium 88+
- Firefox 85+
- Safari 14+
- Edge 88+

## 🖥️ Desktop Releases

Desktop builds are included in `build_all.py`:
- **Windows**: `build/windows/YTDL.exe`
- **macOS**: `build/macos/YTDL.app`
- **Linux**: `build/linux/YTDL`

## 📦 Release Package Structure

After running `build_all.py`, you'll get:

```
release/ytdl_release_YYYYMMDD_HHMMSS/
├── README.md                 # Release notes
├── apk/
│   └── YTDL.apk             # Android APK
├── web/
│   ├── index.html           # Web app entry point
│   ├── main.dart.js         # Compiled Dart/Flutter code
│   ├── assets/              # App assets
│   └── .htaccess           # Apache configuration
├── windows/
│   └── YTDL.exe            # Windows executable
├── macos/
│   └── YTDL.app            # macOS application
└── linux/
    └── YTDL                # Linux executable
```

## 🔧 Build Configuration

### Android Configuration
- **Package**: `com.grandpaejx.ytdl`
- **App Name**: YTDL
- **Version**: 1.0.0
- **Build Number**: Auto-incremented
- **Template**: Adaptive (Material Design)

### Web Configuration
- **Renderer**: CanvasKit (better performance)
- **URL Strategy**: Hash-based routing
- **Base URL**: Configurable for subdirectory deployment
- **PWA**: Enabled with offline caching

### Desktop Configuration
- **Packaging**: Native executables for each platform
- **Dependencies**: Bundled (no Python installation required)
- **Size**: Optimized with tree-shaking

## 🚀 Deployment Examples

### GitHub Pages
```bash
# Build web app
python release/build_web.py

# Deploy to GitHub Pages
git checkout gh-pages
cp -r build/web/* .
git add .
git commit -m "Deploy YTDL web app"
git push origin gh-pages
```

### Netlify
1. Build: `python release/build_web.py`
2. Drag `build/web/` folder to Netlify dashboard
3. Done! Auto-deployed with CDN

### Android Play Store
1. Build: `python release/build_android.py`
2. Sign APK with your keystore
3. Upload to Google Play Console
4. Follow Play Store review process

## 🔍 Troubleshooting

### Android Build Issues
- Ensure Java 11+ is installed
- Check Android SDK path in environment
- Try: `flet doctor` to check setup

### Web Build Issues
- Clear browser cache after deployment
- Check console for JavaScript errors
- Ensure HTTPS for PWA features

### Desktop Build Issues
- Check platform-specific dependencies
- Ensure sufficient disk space
- Try building individual platforms

## 📋 Release Checklist

Before releasing:
- [ ] Test all builds locally
- [ ] Verify core functionality works
- [ ] Check theme switching
- [ ] Test download functionality
- [ ] Validate platform detection
- [ ] Update version numbers
- [ ] Create release notes
- [ ] Tag Git release

## 🎯 Next Steps

After building:
1. **Test thoroughly** on target platforms
2. **Create GitHub release** with binaries
3. **Update documentation** with download links
4. **Announce release** on relevant platforms
5. **Monitor feedback** and issues

## 📞 Support

- **Issues**: Report on GitHub
- **Documentation**: Check main README.md
- **Flet Docs**: https://flet.dev/docs/
- **Build Help**: `flet build --help`
