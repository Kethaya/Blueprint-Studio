"""
Core application logic and state management
"""
import json
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from models import Project, Scene, SceneSelection, AssetSelection, AppState


class BlueprintManager:
    """Manages blueprint.json loading and parsing"""
    
    def __init__(self):
        self.project: Optional[Project] = None
        self.scenes: List[Scene] = []
        self.blueprint_path: Optional[Path] = None
    
    def load_blueprint(self, path: Path) -> bool:
        """Load blueprint from JSON file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            project_data = data.get("project", {})
            self.project = Project(
                title=project_data.get("title", "Untitled Project"),
                description=project_data.get("description", ""),
                language=project_data.get("language", "English"),
                default_font=project_data.get("default_font", "Bebas Neue")
            )
            
            self.scenes = []
            for scene_data in data.get("scenes", []):
                scene = Scene.from_blueprint(scene_data)
                self.scenes.append(scene)
            
            self.blueprint_path = path
            return True
        except Exception as e:
            print(f"Error loading blueprint: {e}")
            return False
    
    def get_scene(self, index: int) -> Optional[Scene]:
        """Get scene by index"""
        if 0 <= index < len(self.scenes):
            return self.scenes[index]
        return None
    
    def get_scene_count(self) -> int:
        """Get total number of scenes"""
        return len(self.scenes)


class SelectionManager:
    """Manages selection.json reading and writing"""
    
    def __init__(self, assets_dir: Path):
        self.selection_path: Optional[Path] = None
        self.scene_selections: Dict[int, SceneSelection] = {}
        self.project_title: str = ""
        self.assets_dir = assets_dir
        self._lock = threading.Lock()
        self._save_callbacks: List[Callable] = []
    
    def initialize(self, blueprint_path: Path) -> bool:
        """Initialize selection.json based on blueprint"""
        try:
            # Determine selection.json path (same directory as blueprint)
            self.selection_path = blueprint_path.parent / "selection.json"
            
            # Load existing or create new
            if self.selection_path.exists():
                self._load_selection()
            else:
                self._create_default_selection(blueprint_path)
            
            return True
        except Exception as e:
            print(f"Error initializing selection: {e}")
            return False
    
    def _load_selection(self):
        """Load existing selection.json"""
        try:
            with open(self.selection_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.project_title = data.get("project", {}).get("title", "")
            
            for scene_data in data.get("scenes", []):
                scene_id = scene_data.get("scene_id", 0)
                self.scene_selections[scene_id] = SceneSelection.from_dict(scene_data)
        except Exception as e:
            print(f"Error loading selection: {e}")
    
    def _create_default_selection(self, blueprint_path: Path):
        """Create default selection.json from blueprint"""
        try:
            with open(blueprint_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.project_title = data.get("project", {}).get("title", "")
            
            for scene_data in data.get("scenes", []):
                scene_id = scene_data.get("scene_id", 0)
                selection = SceneSelection(scene_id=scene_id)
                
                # Pre-populate website from blueprint search
                websites = scene_data.get("search", {}).get("website", [])
                if websites:
                    selection.website = {"url": websites[0]}
                
                # Pre-populate text from blueprint
                text_data = scene_data.get("text", {})
                if text_data.get("enabled", False):
                    selection.text = {
                        "content": text_data.get("content", ""),
                        "font": text_data.get("font", "")
                    }
                
                self.scene_selections[scene_id] = selection
            
            self._auto_save()
        except Exception as e:
            print(f"Error creating default selection: {e}")
    
    def get_selection(self, scene_id: int) -> SceneSelection:
        """Get selection for a scene"""
        if scene_id not in self.scene_selections:
            self.scene_selections[scene_id] = SceneSelection(scene_id=scene_id)
        return self.scene_selections[scene_id]
    
    def set_video_selection(self, scene_id: int, selection: AssetSelection):
        """Set video selection for a scene"""
        with self._lock:
            sel = self.get_selection(scene_id)
            sel.video = selection
            self._auto_save()
    
    def set_image_selection(self, scene_id: int, selection: AssetSelection):
        """Set image selection for a scene"""
        with self._lock:
            sel = self.get_selection(scene_id)
            sel.image = selection
            self._auto_save()
    
    def set_logo_selection(self, scene_id: int, selection: AssetSelection):
        """Set logo selection for a scene"""
        with self._lock:
            sel = self.get_selection(scene_id)
            sel.logo = selection
            self._auto_save()
    
    def set_icon_selection(self, scene_id: int, selection: AssetSelection):
        """Set icon selection for a scene"""
        with self._lock:
            sel = self.get_selection(scene_id)
            sel.icon = selection
            self._auto_save()
    
    def set_sfx_selection(self, scene_id: int, selection: AssetSelection):
        """Set SFX selection for a scene"""
        with self._lock:
            sel = self.get_selection(scene_id)
            sel.sfx = selection
            self._auto_save()
    
    def set_website(self, scene_id: int, url: str):
        """Set website URL for a scene"""
        with self._lock:
            sel = self.get_selection(scene_id)
            sel.website = {"url": url} if url else {}
            self._auto_save()
    
    def set_text(self, scene_id: int, content: str, font: str):
        """Set text content and font for a scene"""
        with self._lock:
            sel = self.get_selection(scene_id)
            sel.text = {"content": content, "font": font}
            self._auto_save()
    
    def mark_downloaded(self, scene_id: int, asset_type: str, local_path: str):
        """Mark an asset as downloaded"""
        with self._lock:
            sel = self.get_selection(scene_id)
            
            if asset_type == "video":
                sel.video.downloaded = True
                sel.video.local_path = local_path
            elif asset_type == "image":
                sel.image.downloaded = True
                sel.image.local_path = local_path
            elif asset_type == "logo":
                sel.logo.downloaded = True
                sel.logo.local_path = local_path
            elif asset_type == "icon":
                sel.icon.downloaded = True
                sel.icon.local_path = local_path
            elif asset_type == "sfx":
                sel.sfx.downloaded = True
                sel.sfx.local_path = local_path
            elif asset_type == "website_screenshot":
                sel.website_screenshot.downloaded = True
                sel.website_screenshot.local_path = local_path
            
            self._auto_save()
    
    def _auto_save(self):
        """Auto-save selection.json"""
        try:
            data = {
                "project": {"title": self.project_title},
                "scenes": [sel.to_dict() for sel in self.scene_selections.values()]
            }
            
            if self.selection_path:
                with open(self.selection_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                for callback in self._save_callbacks:
                    callback()
        except Exception as e:
            print(f"Error saving selection: {e}")
    
    def add_save_callback(self, callback: Callable):
        """Add callback for save events"""
        self._save_callbacks.append(callback)


class ApplicationState:
    """Central application state manager"""
    
    def __init__(self, assets_dir: Path = None, cache_dir: Path = None):
        self.assets_dir = assets_dir or Path("./assets")
        self.cache_dir = cache_dir or Path("./cache")
        
        self.blueprint_manager = BlueprintManager()
        self.selection_manager = SelectionManager(self.assets_dir)
        
        self.current_scene_index: int = 0
        self.search_type: str = "Video"
        self.search_query: str = ""
        
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure all required directories exist"""
        dirs = [
            self.assets_dir / "videos",
            self.assets_dir / "images",
            self.assets_dir / "logos",
            self.assets_dir / "screenshots",
            self.assets_dir / "icons",
            self.assets_dir / "fonts",
            self.assets_dir / "sfx",
            self.cache_dir
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def load_project(self, blueprint_path: Path) -> bool:
        """Load a complete project"""
        if self.blueprint_manager.load_blueprint(blueprint_path):
            return self.selection_manager.initialize(blueprint_path)
        return False
    
    def get_current_scene(self) -> Optional[Scene]:
        """Get currently selected scene"""
        return self.blueprint_manager.get_scene(self.current_scene_index)
    
    def get_current_selection(self) -> SceneSelection:
        """Get selection for current scene"""
        scene = self.get_current_scene()
        if scene:
            return self.selection_manager.get_selection(scene.scene_id)
        return SceneSelection(scene_id=0)
    
    def set_scene(self, index: int):
        """Set current scene index"""
        if 0 <= index < self.blueprint_manager.get_scene_count():
            self.current_scene_index = index
