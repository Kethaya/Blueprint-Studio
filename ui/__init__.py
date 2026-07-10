"""
UI Components for Blueprint Asset Builder
"""
import customtkinter as ctk
from typing import Optional, Callable, List, Dict, Any
from pathlib import Path


class SceneCard(ctk.CTkFrame):
    """Scene card widget for the left panel"""
    
    def __init__(self, parent, scene_id: int, scene_num: str, title: str, 
                 scene_type: str, callback: Callable, **kwargs):
        super().__init__(parent, height=138, fg_color="#1E2024", border_width=1, 
                        border_color="#2D3139", corner_radius=6, **kwargs)
        
        self.scene_id = scene_id
        self.scene_num = scene_num
        self.title = title
        self.scene_type = scene_type
        self.callback = callback
        self.is_selected = False
        
        self._build_ui()
        self._bind_events()
    
    def _build_ui(self):
        # Thumbnail area
        self.thumb = ctk.CTkFrame(self, fg_color="#0F1012", corner_radius=4)
        self.thumb.place(relx=0.03, rely=0.05, relwidth=0.94, relheight=0.68)
        
        # Scene number
        self.lbl_num = ctk.CTkLabel(self.thumb, text=self.scene_num, 
                                   font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), 
                                   text_color="#475569")
        self.lbl_num.place(x=8, y=6)
        
        # Type badge
        colors = {
            "VIDEO": "#3B82F6", "IMAGE": "#10B981", "TEXT": "#8B5CF6",
            "LOGO": "#F59E0B", "WEBSITE": "#EC4899", "CHART": "#06B6D4",
            "DOCUMENT": "#6366F1", "TIMELINE": "#14B8A6", "TEXT_ONLY": "#8B5CF6"
        }
        badge_color = colors.get(self.scene_type.upper(), "#64748B")
        
        self.badge = ctk.CTkFrame(self.thumb, fg_color=badge_color, corner_radius=3, height=16)
        self.badge.place(relx=0.95, rely=0.08, anchor="ne")
        self.blbl = ctk.CTkLabel(self.badge, text=self.scene_type.upper(), 
                                font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"), 
                                text_color="#FFFFFF", height=16, padx=5)
        self.blbl.pack()
        
        # Placeholder icon
        self.icon_lbl = ctk.CTkLabel(self.thumb, text=f"▋▋ {self.scene_type.upper()} PLACEHOLDER ▋▋", 
                                    font=ctk.CTkFont(family="Segoe UI", size=10), 
                                    text_color="#22252A")
        self.icon_lbl.place(relx=0.5, rely=0.55, anchor="center")
        
        # Title label
        self.lbl_title = ctk.CTkLabel(self, text=self.title, 
                                     font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
                                     text_color="#C8D2DD", anchor="w")
        self.lbl_title.place(relx=0.05, rely=0.76, relwidth=0.9)
    
    def _bind_events(self):
        widgets = [self, self.thumb, self.lbl_title, self.lbl_num, self.icon_lbl, self.blbl, self.badge]
        for widget in widgets:
            widget.bind("<Button-1>", lambda e: self.callback(self.scene_id))
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event=None):
        if not self.is_selected:
            self.configure(border_color="#4F46E5")
    
    def _on_leave(self, event=None):
        if not self.is_selected:
            self.configure(border_color="#2D3139")
    
    def set_selected(self, selected: bool):
        self.is_selected = selected
        if selected:
            self.configure(border_color="#4F46E5", fg_color="#1A1D24")
        else:
            self.configure(border_color="#2D3139", fg_color="#1E2024")
    
    def update_thumbnail(self, image_path: Optional[Path] = None):
        """Update thumbnail with actual image"""
        if image_path and image_path.exists():
            # In production, would load actual image
            self.icon_lbl.configure(text="★ LIVE RENDER ★", text_color="#10B981")


class AssetCard(ctk.CTkFrame):
    """Asset card widget for the right panel browser"""
    
    def __init__(self, parent, result: Dict[str, Any], select_callback: Callable, 
                 preview_callback: Optional[Callable] = None, **kwargs):
        super().__init__(parent, width=195, height=175, fg_color="#1E2024", 
                        border_width=1, border_color="#2D3139", corner_radius=6, **kwargs)
        
        self.result = result
        self.select_callback = select_callback
        self.preview_callback = preview_callback
        
        self._build_ui()
        self._bind_events()
    
    def _build_ui(self):
        # Thumbnail
        self.thumb = ctk.CTkFrame(self, fg_color="#0F1012", corner_radius=4)
        self.thumb.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.48)
        
        asset_type = self.result.get("asset_type", "unknown").upper()
        self.tlbl = ctk.CTkLabel(self.thumb, text=asset_type, 
                                font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"), 
                                text_color="#475569")
        self.tlbl.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        self.lbl_title = ctk.CTkLabel(self, text=self.result.get("title", "Untitled"), 
                                     font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), 
                                     text_color="#C8D2DD", anchor="w")
        self.lbl_title.place(relx=0.06, rely=0.56, relwidth=0.88)
        
        # Info (resolution/duration)
        width = self.result.get("width", 0)
        height = self.result.get("height", 0)
        duration = self.result.get("duration", "")
        
        if duration and duration != "N/A":
            info_str = f"{width}x{height}  •  {duration}"
        else:
            info_str = f"{width}x{height}" if width else "Standard"
        
        self.lbl_info = ctk.CTkLabel(self, text=info_str, 
                                    font=ctk.CTkFont(family="Segoe UI", size=10), 
                                    text_color="#64748B", anchor="w")
        self.lbl_info.place(relx=0.06, rely=0.69, relwidth=0.88)
        
        # Preview button
        self.pbtn = ctk.CTkButton(self, text="Preview", width=85, height=24, 
                                 font=ctk.CTkFont(family="Segoe UI", size=11), 
                                 fg_color="#2D3139", hover_color="#3D424E", 
                                 text_color="#E2E8F0")
        self.pbtn.place(relx=0.05, rely=0.83)
        self.pbtn.configure(command=lambda: self.preview_callback(self.result) if self.preview_callback else None)
        
        # Select button
        self.sbtn = ctk.CTkButton(self, text="Select", width=85, height=24, 
                                 font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), 
                                 fg_color="#3B82F6", hover_color="#2563EB")
        self.sbtn.place(relx=0.53, rely=0.83)
        self.sbtn.configure(command=lambda: self.select_callback(self.result))
    
    def _bind_events(self):
        self.bind("<Enter>", lambda e: self.configure(border_color="#4F46E5"))
        self.bind("<Leave>", lambda e: self.configure(border_color="#2D3139"))


class MediaBlock(ctk.CTkFrame):
    """Media asset block for the center panel editor"""
    
    def __init__(self, parent, asset_type: str, search_callback: Callable, 
                 download_callback: Callable, replace_callback: Callable, **kwargs):
        super().__init__(parent, fg_color="#1E2024", border_width=1, 
                        border_color="#2D3139", corner_radius=6, **kwargs)
        
        self.asset_type = asset_type
        self.search_callback = search_callback
        self.download_callback = download_callback
        self.replace_callback = replace_callback
        
        self._build_ui()
    
    def _build_ui(self):
        # Section header
        lbl = ctk.CTkLabel(self, text=f"Primary {self.asset_type.upper()} Asset Blueprint", 
                          font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), 
                          text_color="#475569")
        lbl.pack(anchor="w", padx=15, pady=(10, 2))
        
        sep = ctk.CTkFrame(self, height=1, fg_color="#26292E")
        sep.pack(fill="x", padx=15, pady=2)
        
        # Control row
        crow = ctk.CTkFrame(self, fg_color="transparent")
        crow.pack(fill="x", padx=15, pady=(8, 8))
        
        self.dp = ctk.CTkOptionMenu(crow, values=[f"Suggested {self.asset_type} 1", 
                                                  f"Suggested {self.asset_type} 2", 
                                                  f"Alternative {self.asset_type}"], 
                                   font=ctk.CTkFont(family="Segoe UI", size=12), 
                                   fg_color="#2D3139", button_color="#3D424E", 
                                   height=30, width=200)
        self.dp.pack(side="left", padx=(0, 8))
        
        self.s_btn = ctk.CTkButton(crow, text="Search", 
                                  font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
                                  fg_color="#4F46E5", hover_color="#4338CA", 
                                  height=30, width=85, 
                                  command=lambda: self.search_callback(self.asset_type))
        self.s_btn.pack(side="left", padx=(0, 4))
        
        self.d_btn = ctk.CTkButton(crow, text="Download", 
                                  font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
                                  fg_color="#10B981", hover_color="#059669", 
                                  height=30, width=85,
                                  command=lambda: self.download_callback(self.asset_type))
        self.d_btn.pack(side="left")
        
        # Asset card
        self.card_p = ctk.CTkFrame(self, fg_color="#0F1012", border_width=1, 
                                  border_color="#2D3139", corner_radius=5, height=65)
        self.card_p.pack(fill="x", padx=15, pady=(0, 12))
        self.card_p.pack_propagate(False)
        
        # Thumbnail
        self.cthumb = ctk.CTkFrame(self.card_p, fg_color="#1E2024", width=80, 
                                  height=45, corner_radius=3)
        self.cthumb.place(x=10, y=10)
        self.cthumb.pack_propagate(False)
        self.cthlbl = ctk.CTkLabel(self.cthumb, text="THUMB", 
                                  font=ctk.CTkFont(family="Segoe UI", size=9), 
                                  text_color="#475569")
        self.cthlbl.pack(expand=True)
        
        # Labels
        self.ctlbl = ctk.CTkLabel(self.card_p, 
                                 text=f"No {self.asset_type} asset selected for this slot Blueprint", 
                                 font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
                                 text_color="#64748B")
        self.ctlbl.place(x=105, y=10)
        
        self.csub = ctk.CTkLabel(self.card_p, 
                                text="Click Search to pull relevant elements from cloud library", 
                                font=ctk.CTkFont(family="Segoe UI", size=11), 
                                text_color="#475569")
        self.csub.place(x=105, y=32)
        
        # Action group
        self.act_grp = ctk.CTkFrame(self.card_p, fg_color="transparent")
        self.act_grp.place(relx=0.98, rely=0.5, anchor="e")
        
        self.r_btn = ctk.CTkButton(self.act_grp, text="Replace", width=70, height=24, 
                                  font=ctk.CTkFont(family="Segoe UI", size=11), 
                                  fg_color="#2D3139", hover_color="#3D424E",
                                  command=lambda: self.replace_callback(self.asset_type))
        self.r_btn.pack(side="left", padx=2)
        
        self.card_d_btn = ctk.CTkButton(self.act_grp, text="Download", width=70, height=24, 
                                       font=ctk.CTkFont(family="Segoe UI", size=11), 
                                       fg_color="#10B981", hover_color="#059669",
                                       command=lambda: self.download_callback(self.asset_type))
        self.card_d_btn.pack(side="left", padx=2)
    
    def update_asset(self, title: str, subtitle: str, has_thumbnail: bool = False):
        """Update the displayed asset information"""
        self.ctlbl.configure(text=title, text_color="#10B981")
        self.csub.configure(text=subtitle, text_color="#64748B")
        if has_thumbnail:
            self.cthlbl.configure(text="MEDIA", text_color="#10B981")


class StatusBarItem(ctk.CTkLabel):
    """Status bar item widget"""
    
    def __init__(self, parent, text: str, color: str = "#94A3B8", **kwargs):
        super().__init__(parent, text=text, 
                        font=ctk.CTkFont(family="Segoe UI", size=11), 
                        text_color=color, **kwargs)
