"""
Utility functions for Blueprint Asset Builder
"""
import hashlib
from pathlib import Path
from typing import Optional


def sanitize_filename(name: str) -> str:
    """Sanitize a string for use as filename"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name.strip()


def get_file_extension(url: str) -> str:
    """Get file extension from URL"""
    ext_map = {
        'mp4': '.mp4',
        'mov': '.mov',
        'avi': '.avi',
        'jpg': '.jpg',
        'jpeg': '.jpg',
        'png': '.png',
        'gif': '.gif',
        'svg': '.svg',
        'wav': '.wav',
        'mp3': '.mp3',
        'ttf': '.ttf',
        'otf': '.otf'
    }
    
    url_lower = url.lower()
    for ext, full_ext in ext_map.items():
        if url_lower.endswith(ext):
            return full_ext
    
    # Default based on common patterns
    if 'video' in url_lower:
        return '.mp4'
    elif 'image' in url_lower or 'photo' in url_lower:
        return '.jpg'
    elif 'audio' in url_lower or 'sfx' in url_lower:
        return '.wav'
    elif 'font' in url_lower:
        return '.ttf'
    
    return '.dat'


def generate_cache_key(asset_type: str, query: str) -> str:
    """Generate a cache key for search results"""
    key_string = f"{asset_type}:{query}"
    return hashlib.md5(key_string.encode()).hexdigest()


def format_duration(seconds: int) -> str:
    """Format duration in MM:SS format"""
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins}:{secs:02d}"


def get_asset_folder_name(asset_type: str) -> str:
    """Get folder name for asset type"""
    mapping = {
        'video': 'videos',
        'image': 'images',
        'logo': 'logos',
        'website_screenshot': 'screenshots',
        'icon': 'icons',
        'font': 'fonts',
        'sfx': 'sfx'
    }
    return mapping.get(asset_type.lower(), 'assets')


def ensure_path_exists(path: Path) -> bool:
    """Ensure a path exists, creating directories if needed"""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def is_valid_json_file(path: Path) -> bool:
    """Check if a file is a valid JSON file"""
    import json
    try:
        with open(path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True
    except Exception:
        return False


def get_thumbnail_placeholder(asset_type: str) -> str:
    """Get placeholder text for asset thumbnails"""
    placeholders = {
        'video': 'VIDEO',
        'image': 'IMAGE',
        'logo': 'LOGO',
        'website_screenshot': 'SCREENSHOT',
        'icon': 'ICON',
        'font': 'FONT',
        'sfx': 'SFX'
    }
    return placeholders.get(asset_type.lower(), 'ASSET')
