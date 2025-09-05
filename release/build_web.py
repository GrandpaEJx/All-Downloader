#!/usr/bin/env python3
"""
Web Build Script for YTDL
Uses Flet's built-in web packaging
"""

import subprocess
import sys
import os
import shutil
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
    
    return True

def build_web_app():
    """Build web app using Flet"""
    print("🌐 Building Web Application...")
    
    # Ensure we're in the project root
    os.chdir(Path(__file__).parent.parent)
    
    # Flet build command for web
    build_cmd = 'flet build web --project "YTDL" --description "All-in-One Video/Audio Downloader" --base-url "/" --web-renderer canvaskit --route-url-strategy hash --verbose'
    return run_command(build_cmd, "Building Web Application")

def create_deployment_files():
    """Create additional deployment files"""
    print("📄 Creating deployment files...")
    
    # Create .htaccess for Apache
    htaccess_content = """
# YTDL Web App - Apache Configuration
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.html [QSA,L]

# Enable compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/plain
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/xml
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE application/xml
    AddOutputFilterByType DEFLATE application/xhtml+xml
    AddOutputFilterByType DEFLATE application/rss+xml
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/x-javascript
</IfModule>

# Cache static assets
<IfModule mod_expires.c>
    ExpiresActive on
    ExpiresByType text/css "access plus 1 year"
    ExpiresByType application/javascript "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
</IfModule>
"""
    
    # Create nginx.conf for Nginx
    nginx_content = """
# YTDL Web App - Nginx Configuration
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/ytdl/build/web;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Cache static assets
    location ~* \\.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Handle client-side routing
    location / {
        try_files $uri $uri/ /index.html;
    }
}
"""
    
    # Create deployment README
    deploy_readme = """
# YTDL Web Deployment

## Files Generated
- `build/web/` - Complete web application
- `.htaccess` - Apache configuration
- `nginx.conf` - Nginx configuration

## Deployment Options

### 1. Static Hosting (GitHub Pages, Netlify, Vercel)
Simply upload the contents of `build/web/` to your static hosting provider.

### 2. Apache Server
1. Upload `build/web/` contents to your web root
2. Copy `.htaccess` to the web root
3. Ensure mod_rewrite is enabled

### 3. Nginx Server
1. Upload `build/web/` contents to your web root
2. Add the nginx configuration to your server block
3. Reload nginx configuration

### 4. Local Testing
```bash
cd build/web
python -m http.server 8000
# Visit http://localhost:8000
```

## Features Available in Web Version
✅ Video downloads (browser limitations apply)
✅ Audio downloads 
✅ Format conversion (client-side)
✅ Batch processing
✅ All themes and UI features
⚠️ File system access limited by browser security

## Browser Compatibility
- Chrome/Chromium 88+
- Firefox 85+
- Safari 14+
- Edge 88+
"""
    
    # Write files
    build_dir = Path("build/web")
    if build_dir.exists():
        with open(build_dir / ".htaccess", "w") as f:
            f.write(htaccess_content)
        
        with open(build_dir.parent / "nginx.conf", "w") as f:
            f.write(nginx_content)
        
        with open(build_dir.parent / "DEPLOYMENT.md", "w") as f:
            f.write(deploy_readme)
        
        print("✅ Deployment files created")
        return True
    else:
        print("❌ Build directory not found")
        return False

def main():
    """Main build process"""
    print("🌐 YTDL Web App Builder")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Build web app
    if build_web_app():
        print("✅ Web build completed!")
        
        # Create deployment files
        if create_deployment_files():
            print("\n🎉 Web deployment package ready!")
            print("🌐 Web files: build/web/")
            print("📋 Deployment guide: build/DEPLOYMENT.md")
            print("🚀 Test locally: cd build/web && python -m http.server 8000")
        else:
            print("⚠️ Web build completed but deployment files failed")
    else:
        print("\n❌ Web build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
