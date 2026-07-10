"""
Services for API calls and downloads
"""
import os
import requests
import threading
import queue
from typing import List, Optional, Callable, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class PexelsService:
    """Service for Pexels API (Video and Image search)"""
    
    def __init__(self):
        self.api_key = os.getenv("PEXELS_API_KEY", "")
        self.base_url = "https://api.pexels.com/v1"
        self.headers = {"Authorization": self.api_key} if self.api_key else {}
    
    def search_videos(self, query: str, per_page: int = 12) -> List[Dict[str, Any]]:
        """Search for videos on Pexels"""
        if not self.api_key:
            return self._get_mock_videos(query, per_page)
        
        try:
            response = requests.get(
                f"{self.base_url}/videos",
                params={"query": query, "per_page": per_page},
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for video in data.get("videos", []):
                video_files = video.get("video_files", [])
                best_file = max(video_files, key=lambda x: x.get("width", 0)) if video_files else {}
                
                results.append({
                    "id": video.get("id"),
                    "title": video.get("title", "Untitled Video"),
                    "thumbnail_url": video.get("image", ""),
                    "download_url": best_file.get("link", ""),
                    "provider": "Pexels",
                    "asset_type": "video",
                    "width": best_file.get("width", 1920),
                    "height": best_file.get("height", 1080),
                    "duration": str(video.get("duration", 0))
                })
            return results
        except Exception as e:
            print(f"Pexels video search error: {e}")
            return self._get_mock_videos(query, per_page)
    
    def search_images(self, query: str, per_page: int = 12) -> List[Dict[str, Any]]:
        """Search for images on Pexels"""
        if not self.api_key:
            return self._get_mock_images(query, per_page)
        
        try:
            response = requests.get(
                f"{self.base_url}/search",
                params={"query": query, "per_page": per_page},
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for photo in data.get("photos", []):
                results.append({
                    "id": photo.get("id"),
                    "title": photo.get("alt", "Untitled Image"),
                    "thumbnail_url": photo.get("src", {}).get("medium", ""),
                    "download_url": photo.get("src", {}).get("original", ""),
                    "provider": "Pexels",
                    "asset_type": "image",
                    "width": photo.get("width", 3840),
                    "height": photo.get("height", 2160),
                    "duration": ""
                })
            return results
        except Exception as e:
            print(f"Pexels image search error: {e}")
            return self._get_mock_images(query, per_page)
    
    def _get_mock_videos(self, query: str, count: int) -> List[Dict[str, Any]]:
        """Return mock video results when API unavailable"""
        return [
            {
                "id": 1000 + i,
                "title": f"{query.title()} Stock Video {i+1}",
                "thumbnail_url": "",
                "download_url": f"https://example.com/video{i}.mp4",
                "provider": "Mock",
                "asset_type": "video",
                "width": 1920,
                "height": 1080,
                "duration": "0:15"
            }
            for i in range(count)
        ]
    
    def _get_mock_images(self, query: str, count: int) -> List[Dict[str, Any]]:
        """Return mock image results when API unavailable"""
        return [
            {
                "id": 2000 + i,
                "title": f"{query.title()} Stock Image {i+1}",
                "thumbnail_url": "",
                "download_url": f"https://example.com/image{i}.jpg",
                "provider": "Mock",
                "asset_type": "image",
                "width": 3840,
                "height": 2160,
                "duration": ""
            }
            for i in range(count)
        ]


class LogoService:
    """Service for logo search using Logo.dev or Clearbit"""
    
    def __init__(self):
        self.logo_dev_key = os.getenv("LOGO_API_KEY", "")
    
    def search_logo(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Search for a company logo"""
        # Try Logo.dev first
        if self.logo_dev_key:
            logo_url = f"https://logo.clearbit.com/{company_name.lower().replace(' ', '')}.com"
            return {
                "id": hash(company_name),
                "title": f"{company_name} Logo",
                "thumbnail_url": logo_url,
                "download_url": logo_url,
                "provider": "Clearbit",
                "asset_type": "logo",
                "width": 128,
                "height": 128,
                "duration": ""
            }
        
        # Return mock result
        return {
            "id": 3000,
            "title": f"{company_name} Logo",
            "thumbnail_url": "",
            "download_url": "",
            "provider": "Local",
            "asset_type": "logo",
            "width": 128,
            "height": 128,
            "duration": ""
        }


class ScreenshotService:
    """Service for capturing website screenshots"""
    
    def capture_screenshot(self, url: str, output_path: Path) -> bool:
        """Capture a screenshot of a website"""
        try:
            # Use a simple approach - in production would use selenium or similar
            # For now, create a placeholder
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create a simple text file as placeholder
            with open(output_path.with_suffix('.txt'), 'w') as f:
                f.write(f"Screenshot of: {url}\n")
                f.write("In production, this would be an actual screenshot.\n")
            
            return True
        except Exception as e:
            print(f"Screenshot capture error: {e}")
            return False


class DownloadService:
    """Service for downloading assets"""
    
    def __init__(self, assets_dir: Path):
        self.assets_dir = assets_dir
        self.download_callbacks: List[Callable] = []
    
    def download_asset(self, url: str, filename: str, asset_type: str, 
                       callback: Optional[Callable[[bool, str], None]] = None) -> str:
        """Download an asset to the appropriate folder"""
        # Map asset types to folders
        type_folders = {
            "video": "videos",
            "image": "images",
            "logo": "logos",
            "screenshot": "screenshots",
            "icon": "icons",
            "font": "fonts",
            "sfx": "sfx"
        }
        
        folder = type_folders.get(asset_type, "assets")
        dest_folder = self.assets_dir / folder
        dest_folder.mkdir(parents=True, exist_ok=True)
        
        dest_path = dest_folder / filename
        
        try:
            if not url or url.startswith("https://example.com"):
                # Mock download
                dest_path.touch()
                if callback:
                    callback(True, str(dest_path))
                return str(dest_path)
            
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            if callback:
                callback(True, str(dest_path))
            return str(dest_path)
        except Exception as e:
            print(f"Download error: {e}")
            if callback:
                callback(False, str(e))
            return ""
    
    def download_in_background(self, url: str, filename: str, asset_type: str,
                               callback: Optional[Callable[[bool, str], None]] = None):
        """Download asset in background thread"""
        thread = threading.Thread(
            target=self.download_asset,
            args=(url, filename, asset_type, callback)
        )
        thread.daemon = True
        thread.start()
        return thread


class SearchManager:
    """Manages all search operations across providers"""
    
    def __init__(self, assets_dir: Path):
        self.pexels = PexelsService()
        self.logo_service = LogoService()
        self.screenshot_service = ScreenshotService()
        self.download_service = DownloadService(assets_dir)
        self.search_queue = queue.Queue()
        self.results_cache: Dict[str, List[Dict[str, Any]]] = {}
    
    def search(self, asset_type: str, query: str, 
               callback: Optional[Callable[[List[Dict[str, Any]]], None]] = None) -> List[Dict[str, Any]]:
        """Search for assets based on type"""
        cache_key = f"{asset_type}:{query}"
        
        if cache_key in self.results_cache:
            if callback:
                callback(self.results_cache[cache_key])
            return self.results_cache[cache_key]
        
        results = []
        
        if asset_type.lower() == "video":
            results = self.pexels.search_videos(query)
        elif asset_type.lower() == "image":
            results = self.pexels.search_images(query)
        elif asset_type.lower() == "logo":
            result = self.logo_service.search_logo(query)
            results = [result] if result else []
        elif asset_type.lower() in ["website screenshot", "icon", "font", "sfx"]:
            results = self._get_local_results(asset_type, query)
        
        self.results_cache[cache_key] = results
        
        if callback:
            callback(results)
        
        return results
    
    def search_async(self, asset_type: str, query: str,
                     callback: Optional[Callable[[List[Dict[str, Any]]], None]] = None):
        """Search asynchronously"""
        def do_search():
            results = self.search(asset_type, query, callback)
        
        thread = threading.Thread(target=do_search)
        thread.daemon = True
        thread.start()
        return thread
    
    def _get_local_results(self, asset_type: str, query: str) -> List[Dict[str, Any]]:
        """Get mock results for local asset types"""
        return [
            {
                "id": 4000 + i,
                "title": f"{query.title()} {asset_type} {i+1}",
                "thumbnail_url": "",
                "download_url": "",
                "provider": "Local",
                "asset_type": asset_type.lower().replace(" ", "_"),
                "width": 0,
                "height": 0,
                "duration": ""
            }
            for i in range(6)
        ]
