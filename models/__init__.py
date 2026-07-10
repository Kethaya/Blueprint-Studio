"""
Models for Blueprint Asset Builder
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from pathlib import Path


@dataclass
class Project:
    """Project metadata from blueprint.json"""
    title: str = ""
    description: str = ""
    language: str = "English"
    default_font: str = "Bebas Neue"


@dataclass
class AssetSelection:
    """Represents a selected asset for a scene"""
    provider: str = ""
    id: Optional[int] = None
    title: str = ""
    url: str = ""
    local_path: str = ""
    downloaded: bool = False
    name: str = ""  # For logos, fonts, SFX
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.provider:
            result["provider"] = self.provider
        if self.id is not None:
            result["id"] = self.id
        if self.title:
            result["title"] = self.title
        if self.url:
            result["url"] = self.url
        if self.local_path:
            result["local_path"] = self.local_path
        if self.name:
            result["name"] = self.name
        result["downloaded"] = self.downloaded
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssetSelection":
        return cls(
            provider=data.get("provider", ""),
            id=data.get("id"),
            title=data.get("title", ""),
            url=data.get("url", ""),
            local_path=data.get("local_path", ""),
            downloaded=data.get("downloaded", False),
            name=data.get("name", "")
        )


@dataclass
class SceneSelection:
    """Selection data for a single scene"""
    scene_id: int
    video: AssetSelection = field(default_factory=AssetSelection)
    image: AssetSelection = field(default_factory=AssetSelection)
    logo: AssetSelection = field(default_factory=AssetSelection)
    website: Dict[str, str] = field(default_factory=dict)
    website_screenshot: AssetSelection = field(default_factory=AssetSelection)
    icon: AssetSelection = field(default_factory=AssetSelection)
    text: Dict[str, str] = field(default_factory=lambda: {"content": "", "font": ""})
    sfx: AssetSelection = field(default_factory=AssetSelection)
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "scene_id": self.scene_id,
            "selection": {
                "video": self.video.to_dict() if self.video.provider or self.video.title else {},
                "image": self.image.to_dict() if self.image.provider or self.image.title else {},
                "logo": self.logo.to_dict() if self.logo.name or self.logo.local_path else {},
                "website": self.website if self.website else {},
                "website_screenshot": self.website_screenshot.to_dict() if self.website_screenshot.local_path else {},
                "icon": self.icon.to_dict() if self.icon.name or self.icon.local_path else {},
                "text": self.text,
                "sfx": self.sfx.to_dict() if self.sfx.name or self.sfx.local_path else {}
            }
        }
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SceneSelection":
        selection = data.get("selection", {})
        return cls(
            scene_id=data.get("scene_id", 0),
            video=AssetSelection.from_dict(selection.get("video", {})),
            image=AssetSelection.from_dict(selection.get("image", {})),
            logo=AssetSelection.from_dict(selection.get("logo", {})),
            website=selection.get("website", {}),
            website_screenshot=AssetSelection.from_dict(selection.get("website_screenshot", {})),
            icon=AssetSelection.from_dict(selection.get("icon", {})),
            text=selection.get("text", {"content": "", "font": ""}),
            sfx=AssetSelection.from_dict(selection.get("sfx", {}))
        )


@dataclass
class Scene:
    """Scene data from blueprint.json"""
    scene_id: int
    scene_type: str
    title: str
    narration: str
    subtitle: str = ""
    keywords: List[str] = field(default_factory=list)
    search_video: List[str] = field(default_factory=list)
    search_image: List[str] = field(default_factory=list)
    search_logo: List[str] = field(default_factory=list)
    search_website: List[str] = field(default_factory=list)
    search_icon: List[str] = field(default_factory=list)
    search_sfx: List[str] = field(default_factory=list)
    text_enabled: bool = False
    text_content: str = ""
    text_font: str = ""
    editing_note: str = ""
    
    @classmethod
    def from_blueprint(cls, data: Dict[str, Any]) -> "Scene":
        search = data.get("search", {})
        text_data = data.get("text", {})
        return cls(
            scene_id=data.get("scene_id", 0),
            scene_type=data.get("scene_type", "video"),
            title=data.get("title", "Untitled"),
            narration=data.get("narration", ""),
            subtitle=data.get("subtitle", ""),
            keywords=data.get("keywords", []),
            search_video=search.get("video", []),
            search_image=search.get("image", []),
            search_logo=search.get("logo", []),
            search_website=search.get("website", []),
            search_icon=search.get("icon", []),
            search_sfx=search.get("sfx", []),
            text_enabled=text_data.get("enabled", False),
            text_content=text_data.get("content", ""),
            text_font=text_data.get("font", ""),
            editing_note=data.get("editing_note", "")
        )


@dataclass
class SearchResult:
    """Search result from API"""
    id: int
    title: str
    thumbnail_url: str
    download_url: str
    provider: str
    asset_type: str
    width: int = 1920
    height: int = 1080
    duration: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "thumbnail_url": self.thumbnail_url,
            "download_url": self.download_url,
            "provider": self.provider,
            "asset_type": self.asset_type,
            "width": self.width,
            "height": self.height,
            "duration": self.duration
        }


@dataclass
class AppState:
    """Application state"""
    blueprint_path: Optional[Path] = None
    selection_path: Optional[Path] = None
    current_scene_index: int = 0
    search_type: str = "Video"
    search_query: str = ""
    assets_dir: Path = field(default_factory=lambda: Path("./assets"))
    cache_dir: Path = field(default_factory=lambda: Path("./cache"))
    is_downloading: bool = False
    download_queue: List[Dict[str, Any]] = field(default_factory=list)
