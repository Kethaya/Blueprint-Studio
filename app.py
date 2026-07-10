"""
Blueprint Asset Builder - Main Application
A professional desktop application for documentary editors to build asset libraries.
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

# Import application modules
from models import Project, Scene, SceneSelection, AssetSelection
from services import SearchManager, DownloadService
from core import ApplicationState, BlueprintManager, SelectionManager
from ui import SceneCard, AssetCard, MediaBlock, StatusBarItem
from utils import sanitize_filename, get_file_extension, get_asset_folder_name

# Configure appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize state
        self.state = ApplicationState()
        self.search_manager = SearchManager(self.state.assets_dir)
        self.download_service = DownloadService(self.state.assets_dir)
        
        # UI state
        self.scene_cards: List[SceneCard] = []
        self.asset_cards: List[AssetCard] = []
        self.media_blocks: Dict[str, MediaBlock] = {}
        self.current_search_results: List[Dict[str, Any]] = []
        
        # Window setup
        self.title("Blueprint Asset Builder")
        self.geometry("1700x950")
        self.minsize(1400, 800)
        self.configure(fg_color="#0F1012")
        
        # Build UI
        self._build_top_toolbar()
        self._build_status_bar()
        self._build_main_container()
        self._build_left_panel()
        self._build_right_panel()
        self._build_center_panel()
        
        # Load default blueprint if exists
        self._load_default_blueprint()
        
        # Setup save callback
        self.state.selection_manager.add_save_callback(self._on_selection_saved)
    
    def _build_top_toolbar(self):
        """Build the top toolbar with action buttons"""
        toolbar = ctk.CTkFrame(self, height=55, fg_color="#1A1C1E", corner_radius=0, 
                              border_width=1, border_color="#26292E")
        toolbar.pack(fill="x", side="top")
        toolbar.pack_propagate(False)
        
        # Left group - Title
        left_grp = ctk.CTkFrame(toolbar, fg_color="transparent")
        left_grp.pack(side="left", padx=15, fill="y")
        
        title_lbl = ctk.CTkLabel(left_grp, text="Blueprint Asset Builder", 
                                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), 
                                text_color="#E2E8F0")
        title_lbl.pack(side="left", anchor="center")
        
        ver_lbl = ctk.CTkLabel(left_grp, text="v1.0.0", 
                              font=ctk.CTkFont(family="Segoe UI", size=10), 
                              text_color="#64748B")
        ver_lbl.pack(side="left", padx=(6, 0), anchor="center")
        
        # Separator
        sep = ctk.CTkFrame(toolbar, width=1, fg_color="#26292E")
        sep.pack(side="left", fill="y", pady=12, padx=10)
        
        # Project label
        self.proj_lbl = ctk.CTkLabel(toolbar, text="Project: Not Loaded", 
                                    font=ctk.CTkFont(family="Segoe UI", size=13), 
                                    text_color="#94A3B8")
        self.proj_lbl.pack(side="left", padx=5)
        
        # Right group - Action buttons
        right_grp = ctk.CTkFrame(toolbar, fg_color="transparent")
        right_grp.pack(side="right", padx=15, fill="y")
        
        btn_opts = {
            "font": ctk.CTkFont(family="Segoe UI", size=12),
            "height": 32,
            "fg_color": "#2D3139",
            "hover_color": "#3D424E",
            "text_color": "#E2E8F0",
            "corner_radius": 6
        }
        
        # Import Blueprint button
        btn_imp = ctk.CTkButton(right_grp, text="📂 Import Blueprint", **btn_opts,
                               command=self._import_blueprint)
        btn_imp.pack(side="left", padx=4)
        
        # Scene Board button
        btn_sb = ctk.CTkButton(right_grp, text="🖼 Scene Board", 
                              font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                              height=32, fg_color="#4F46E5", hover_color="#4338CA", 
                              text_color="#FFFFFF", corner_radius=6, 
                              command=self._open_scene_board)
        btn_sb.pack(side="left", padx=4)
        
        # Save Project button
        btn_save = ctk.CTkButton(right_grp, text="💾 Save Project", **btn_opts,
                                command=self._save_project)
        btn_save.pack(side="left", padx=4)
        
        # Download All button
        btn_dlall = ctk.CTkButton(right_grp, text="⬇ Download All", 
                                 font=ctk.CTkFont(family="Segoe UI", size=12),
                                 height=32, fg_color="#10B981", hover_color="#059669", 
                                 text_color="#FFFFFF", corner_radius=6,
                                 command=self._download_all_assets)
        btn_dlall.pack(side="left", padx=4)
        
        # Assets Folder button
        btn_assets = ctk.CTkButton(right_grp, text="📁 Assets Folder", **btn_opts,
                                  command=self._open_assets_folder)
        btn_assets.pack(side="left", padx=4)
        
        # Refresh button
        btn_refresh = ctk.CTkButton(right_grp, text="🔄 Refresh", **btn_opts,
                                   command=self._refresh_view)
        btn_refresh.pack(side="left", padx=4)
    
    def _build_status_bar(self):
        """Build the bottom status bar"""
        sb = ctk.CTkFrame(self, height=28, fg_color="#1A1C1E", corner_radius=0, 
                         border_width=1, border_color="#26292E")
        sb.pack(fill="x", side="bottom")
        sb.pack_propagate(False)
        
        # Status indicators
        self.status_left = ctk.CTkLabel(sb, text="✓ Ready", 
                                       font=ctk.CTkFont(family="Segoe UI", size=11), 
                                       text_color="#10B981")
        self.status_left.pack(side="left", padx=15)
        
        sep1 = ctk.CTkFrame(sb, width=1, fg_color="#26292E")
        sep1.pack(side="left", fill="y", pady=6, padx=10)
        
        self.status_scene = ctk.CTkLabel(sb, text="Current Scene: None", 
                                        font=ctk.CTkFont(family="Segoe UI", size=11), 
                                        text_color="#94A3B8")
        self.status_scene.pack(side="left", padx=5)
        
        sep2 = ctk.CTkFrame(sb, width=1, fg_color="#26292E")
        sep2.pack(side="left", fill="y", pady=6, padx=10)
        
        self.status_search = ctk.CTkLabel(sb, text="Search Type: Video", 
                                         font=ctk.CTkFont(family="Segoe UI", size=11), 
                                         text_color="#94A3B8")
        self.status_search.pack(side="left", padx=5)
        
        # Queue status (right aligned)
        self.status_queue = ctk.CTkLabel(sb, text="Queue: Idle", 
                                        font=ctk.CTkFont(family="Segoe UI", size=11), 
                                        text_color="#64748B")
        self.status_queue.pack(side="right", padx=15)
    
    def _build_main_container(self):
        """Build the main container frame"""
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=8, pady=0)
    
    def _build_left_panel(self):
        """Build the left panel with scene list"""
        lp = ctk.CTkFrame(self.main_container, width=290, fg_color="#141517", 
                         corner_radius=0)
        lp.pack(side="left", fill="y", padx=(0, 4), pady=6)
        lp.pack_propagate(False)
        
        # Header
        hdr = ctk.CTkLabel(lp, text="SCENES & STORYBOARD", 
                          font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), 
                          text_color="#64748B")
        hdr.pack(anchor="w", padx=15, pady=(12, 8))
        
        # Scrollable frame for scene cards
        self.scene_scroll = ctk.CTkScrollableFrame(lp, fg_color="transparent", 
                                                   corner_radius=0)
        self.scene_scroll.pack(fill="both", expand=True, padx=6, pady=(0, 6))
    
    def _build_right_panel(self):
        """Build the right panel with asset browser"""
        self.rp = ctk.CTkFrame(self.main_container, width=440, fg_color="#141517", 
                              corner_radius=0)
        self.rp.pack(side="right", fill="y", padx=(4, 0), pady=6)
        self.rp.pack_propagate(False)
        
        # Header
        hdr = ctk.CTkLabel(self.rp, text="ASSET BROWSER & MEDIALIBRARY", 
                          font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), 
                          text_color="#64748B")
        hdr.pack(anchor="w", padx=16, pady=(12, 6))
        
        # Control box
        ctrl_box = ctk.CTkFrame(self.rp, fg_color="#1E2024", border_width=1, 
                               border_color="#2D3139", corner_radius=6)
        ctrl_box.pack(fill="x", padx=12, pady=6)
        
        # Search type dropdown
        self.search_type_combo = ctk.CTkOptionMenu(
            ctrl_box, 
            values=["Video", "Image", "Logo", "Website", "Website Screenshot", 
                   "Icon", "Font", "SFX"], 
            font=ctk.CTkFont(family="Segoe UI", size=12), 
            fg_color="#2D3139", button_color="#3D424E", 
            button_hover_color="#4F46E5", dropdown_fg_color="#1E2024", 
            dropdown_hover_color="#2D3139", height=32, 
            command=self._on_search_type_changed
        )
        self.search_type_combo.pack(fill="x", padx=12, pady=(12, 6))
        
        # Search row
        srow = ctk.CTkFrame(ctrl_box, fg_color="transparent")
        srow.pack(fill="x", padx=12, pady=(0, 12))
        
        self.search_bar = ctk.CTkEntry(srow, placeholder_text="Search assets...", 
                                      font=ctk.CTkFont(family="Segoe UI", size=12), 
                                      fg_color="#0F1012", border_color="#2D3139", 
                                      height=32)
        self.search_bar.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.search_bar.bind("<Return>", lambda e: self._perform_search())
        
        sbtn = ctk.CTkButton(srow, text="Search", width=75, height=32, 
                            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
                            fg_color="#4F46E5", hover_color="#4338CA",
                            command=self._perform_search)
        sbtn.pack(side="right")
        
        # Asset scroll area
        self.asset_scroll = ctk.CTkScrollableFrame(self.rp, fg_color="transparent")
        self.asset_scroll.pack(fill="both", expand=True, padx=6, pady=4)
        
        # Grid container for asset cards
        self.asset_grid_container = ctk.CTkFrame(self.asset_scroll, fg_color="transparent")
        self.asset_grid_container.pack(fill="both", expand=True)
        
        # Load more button
        self.load_more_btn = ctk.CTkButton(
            self.asset_scroll, text="Load More Assets", 
            fg_color="#2D3139", hover_color="#3D424E", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="normal"), 
            height=35, command=self._load_more_assets
        )
        self.load_more_btn.pack(fill="x", padx=8, pady=12)
        
        # Generate initial asset cards
        self._generate_asset_cards("Video")
    
    def _build_center_panel(self):
        """Build the center panel with preview and editor"""
        cp = ctk.CTkFrame(self.main_container, fg_color="transparent")
        cp.pack(side="left", fill="both", expand=True, padx=4, pady=6)
        
        # Scene header box
        self.scene_hdr_box = ctk.CTkFrame(cp, height=75, fg_color="#1A1C1E", 
                                         border_width=1, border_color="#26292E", 
                                         corner_radius=6)
        self.scene_hdr_box.pack(fill="x", side="top", pady=(0, 4))
        self.scene_hdr_box.pack_propagate(False)
        
        # Scene number label
        self.hdr_num_lbl = ctk.CTkLabel(self.scene_hdr_box, text="SCENE 000", 
                                       font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), 
                                       text_color="#4F46E5")
        self.hdr_num_lbl.place(x=15, y=10)
        
        # Scene title label
        self.hdr_title_lbl = ctk.CTkLabel(self.scene_hdr_box, text="No Scene Selected", 
                                         font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), 
                                         text_color="#E2E8F0")
        self.hdr_title_lbl.place(x=15, y=28)
        
        # Narration label
        self.hdr_narr_lbl = ctk.CTkLabel(self.scene_hdr_box, 
                                        text="Select a scene to view details", 
                                        font=ctk.CTkFont(family="Segoe UI", size=11), 
                                        text_color="#64748B", anchor="w", 
                                        justify="left", height=45)
        self.hdr_narr_lbl.place(x=400, y=15, relwidth=0.58)
        
        # Preview box
        self.preview_box = ctk.CTkFrame(cp, height=340, fg_color="#000000", 
                                       border_width=1, border_color="#26292E", 
                                       corner_radius=6)
        self.preview_box.pack(fill="x", side="top", pady=(0, 4))
        self.preview_box.pack_propagate(False)
        
        # Preview center label
        self.p_center_lbl = ctk.CTkLabel(self.preview_box, text="[ NO SCENE SELECTED ]", 
                                        font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), 
                                        text_color="#475569")
        self.p_center_lbl.place(relx=0.5, rely=0.5, anchor="center")
        
        # Preview title
        self.p_title_lbl = ctk.CTkLabel(self.preview_box, text="Preview Monitor", 
                                       font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), 
                                       text_color="#334155")
        self.p_title_lbl.place(x=12, y=10)
        
        # Live badge
        self.p_badge = ctk.CTkFrame(self.preview_box, fg_color="#334155", 
                                   corner_radius=3, height=18)
        self.p_badge.place(relx=0.98, rely=0.04, anchor="ne")
        self.p_badge_lbl = ctk.CTkLabel(self.p_badge, text="LIVE", 
                                       font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), 
                                       text_color="#FFFFFF", height=18, padx=6)
        self.p_badge_lbl.pack()
        
        # Editor scroll area
        self.editor_scroll = ctk.CTkScrollableFrame(cp, fg_color="#141517", 
                                                   corner_radius=6, border_width=1, 
                                                   border_color="#26292E")
        self.editor_scroll.pack(fill="both", expand=True, pady=(4, 0))
        
        # Build blueprint fields
        self._build_blueprint_fields()
    
    def _build_blueprint_fields(self):
        """Build the blueprint editor fields"""
        f = self.editor_scroll
        
        # Title section
        t_box = self._create_section_frame(f, "Title & Basic Config")
        ctk.CTkLabel(t_box, text="Scene Entry Title", 
                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
                    text_color="#94A3B8").pack(anchor="w", padx=15, pady=(8, 2))
        self.ent_title = ctk.CTkEntry(t_box, font=ctk.CTkFont(family="Segoe UI", size=13), 
                                     fg_color="#0F1012", border_color="#2D3139", 
                                     height=32)
        self.ent_title.pack(fill="x", padx=15, pady=(0, 12))
        self.ent_title.bind("<KeyRelease>", self._on_title_changed)
        
        # Narration section
        n_box = self._create_section_frame(f, "Voiceover Narration Script")
        self.txt_narr = ctk.CTkTextbox(n_box, font=ctk.CTkFont(family="Segoe UI", size=13), 
                                      fg_color="#0F1012", border_color="#2D3139", 
                                      height=85)
        self.txt_narr.pack(fill="x", padx=15, pady=12)
        self.txt_narr.bind("<KeyRelease>", self._on_narration_changed)
        
        # Keywords section
        k_box = self._create_section_frame(f, "Extracted Keywords (Read-Only)")
        self.txt_keys = ctk.CTkEntry(k_box, font=ctk.CTkFont(family="Segoe UI", size=12), 
                                    fg_color="#1E2024", border_color="#2D3139", 
                                    text_color="#38BDF8", height=32)
        self.txt_keys.pack(fill="x", padx=15, pady=12)
        
        # Media blocks
        target_blocks = ["Video", "Image", "Logo", "Website", "Website Screenshot", 
                        "Icon", "Font", "SFX"]
        
        for m_type in target_blocks:
            m_box = self._create_section_frame(f, f"Primary {m_type.upper()} Asset Blueprint")
            
            crow = ctk.CTkFrame(m_box, fg_color="transparent")
            crow.pack(fill="x", padx=15, pady=(8, 8))
            
            dp = ctk.CTkOptionMenu(crow, 
                                  values=[f"Suggested {m_type} 1", f"Suggested {m_type} 2", 
                                         f"Alternative {m_type}"], 
                                  font=ctk.CTkFont(family="Segoe UI", size=12), 
                                  fg_color="#2D3139", button_color="#3D424E", 
                                  height=30, width=200)
            dp.pack(side="left", padx=(0, 8))
            
            s_btn = ctk.CTkButton(crow, text="Search", 
                                 font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
                                 fg_color="#4F46E5", hover_color="#4338CA", 
                                 height=30, width=85,
                                 command=lambda mt=m_type: self._trigger_search_switch(mt))
            s_btn.pack(side="left", padx=(0, 4))
            
            d_btn = ctk.CTkButton(crow, text="Download", 
                                 font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
                                 fg_color="#10B981", hover_color="#059669", 
                                 height=30, width=85,
                                 command=lambda mt=m_type: self._download_asset(mt))
            d_btn.pack(side="left")
            
            card_p = ctk.CTkFrame(m_box, fg_color="#0F1012", border_width=1, 
                                 border_color="#2D3139", corner_radius=5, height=65)
            card_p.pack(fill="x", padx=15, pady=(0, 12))
            card_p.pack_propagate(False)
            
            cthumb = ctk.CTkFrame(card_p, fg_color="#1E2024", width=80, 
                                 height=45, corner_radius=3)
            cthumb.place(x=10, y=10)
            cthumb.pack_propagate(False)
            cthlbl = ctk.CTkLabel(cthumb, text="THUMB", 
                                 font=ctk.CTkFont(family="Segoe UI", size=9), 
                                 text_color="#475569")
            cthlbl.pack(expand=True)
            
            ctlbl = ctk.CTkLabel(card_p, 
                                text=f"No {m_type} asset selected for this slot Blueprint", 
                                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
                                text_color="#64748B")
            ctlbl.place(x=105, y=10)
            
            csub = ctk.CTkLabel(card_p, 
                               text="Click Search to pull relevant elements from cloud library", 
                               font=ctk.CTkFont(family="Segoe UI", size=11), 
                               text_color="#475569")
            csub.place(x=105, y=32)
            
            act_grp = ctk.CTkFrame(card_p, fg_color="transparent")
            act_grp.place(relx=0.98, rely=0.5, anchor="e")
            
            r_btn = ctk.CTkButton(act_grp, text="Replace", width=70, height=24, 
                                 font=ctk.CTkFont(family="Segoe UI", size=11), 
                                 fg_color="#2D3139", hover_color="#3D424E",
                                 command=lambda mt=m_type: self._trigger_search_switch(mt))
            r_btn.pack(side="left", padx=2)
            
            card_d_btn = ctk.CTkButton(act_grp, text="Download", width=70, height=24, 
                                      font=ctk.CTkFont(family="Segoe UI", size=11), 
                                      fg_color="#10B981", hover_color="#059669",
                                      command=lambda mt=m_type: self._download_asset(mt))
            card_d_btn.pack(side="left", padx=2)
            
            self.media_blocks[m_type] = (ctlbl, csub, cthlbl, dp)
        
        # Text content section
        f_box = self._create_section_frame(f, "Text")
        
        ctk.CTkLabel(f_box, text="Text Content", 
                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
                    text_color="#94A3B8").pack(anchor="w", padx=15, pady=(8, 2))
        self.txt_content_editor = ctk.CTkTextbox(f_box, 
                                                 font=ctk.CTkFont(family="Segoe UI", size=13), 
                                                 fg_color="#0F1012", 
                                                 border_color="#2D3139", height=100)
        self.txt_content_editor.pack(fill="x", padx=15, pady=(0, 10))
        self.txt_content_editor.bind("<KeyRelease>", self._on_text_content_changed)
        
        # Font control bar
        font_control_bar = ctk.CTkFrame(f_box, fg_color="transparent")
        font_control_bar.pack(fill="x", padx=15, pady=(0, 12))
        
        font_info_subgrp = ctk.CTkFrame(font_control_bar, fg_color="transparent")
        font_info_subgrp.pack(side="left")
        
        ctk.CTkLabel(font_info_subgrp, text="Current Font", 
                    font=ctk.CTkFont(family="Segoe UI", size=11), 
                    text_color="#64748B", anchor="w").pack(anchor="w")
        self.lbl_selected_font_display = ctk.CTkLabel(font_info_subgrp, text="Bebas Neue", 
                                                     font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), 
                                                     text_color="#E2E8F0", anchor="w")
        self.lbl_selected_font_display.pack(anchor="w")
        
        btn_change_font = ctk.CTkButton(font_control_bar, text="Change Font", 
                                       width=110, height=30, 
                                       font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
                                       fg_color="#2D3139", hover_color="#3D424E", 
                                       text_color="#E2E8F0", 
                                       command=lambda: self._trigger_search_switch("Font"))
        btn_change_font.pack(side="right", anchor="center")
        
        # Editing notes section
        note_box = self._create_section_frame(f, "Editing Notes")
        self.txt_notes = ctk.CTkTextbox(note_box, 
                                       font=ctk.CTkFont(family="Segoe UI", size=13), 
                                       fg_color="#0F1012", border_color="#2D3139", 
                                       height=75)
        self.txt_notes.pack(fill="x", padx=15, pady=12)
        self.txt_notes.bind("<KeyRelease>", self._on_notes_changed)
    
    def _create_section_frame(self, parent, title):
        """Create a section frame with header"""
        box = ctk.CTkFrame(parent, fg_color="#1E2024", border_width=1, 
                          border_color="#2D3139", corner_radius=6)
        box.pack(fill="x", pady=6, padx=8)
        
        lbl = ctk.CTkLabel(box, text=title.upper(), 
                          font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), 
                          text_color="#475569")
        lbl.pack(anchor="w", padx=15, pady=(10, 2))
        
        sep = ctk.CTkFrame(box, height=1, fg_color="#26292E")
        sep.pack(fill="x", padx=15, pady=2)
        
        return box
    
    def _load_default_blueprint(self):
        """Load the default blueprint.json if it exists"""
        blueprint_path = Path("./blueprint.json")
        if blueprint_path.exists():
            self._load_blueprint_file(blueprint_path)
    
    def _load_blueprint_file(self, path: Path):
        """Load a blueprint file"""
        try:
            if self.state.load_project(path):
                self.proj_lbl.configure(text=f"Project: {self.state.blueprint_manager.project.title}")
                self._populate_scene_list()
                self._select_scene(0)
                self._update_status("✓ Project loaded")
            else:
                messagebox.showerror("Error", "Failed to load blueprint file")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load blueprint: {e}")
    
    def _import_blueprint(self):
        """Import a blueprint file via file dialog"""
        file_path = filedialog.askopenfilename(
            title="Import Blueprint",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self._load_blueprint_file(Path(file_path))
    
    def _populate_scene_list(self):
        """Populate the scene list from loaded blueprint"""
        # Clear existing cards
        for widget in self.scene_scroll.winfo_children():
            widget.destroy()
        self.scene_cards.clear()
        
        # Create scene cards
        for i, scene in enumerate(self.state.blueprint_manager.scenes):
            scene_num = f"Scene {scene.scene_id:03d}"
            card = SceneCard(
                self.scene_scroll,
                scene_id=i,
                scene_num=scene_num,
                title=scene.title,
                scene_type=scene.scene_type,
                callback=lambda idx: self._select_scene(idx)
            )
            card.pack(fill="x", pady=5, padx=2)
            self.scene_cards.append(card)
    
    def _select_scene(self, idx: int):
        """Select a scene and update the UI"""
        if idx < 0 or idx >= len(self.state.blueprint_manager.scenes):
            return
        
        self.state.set_scene(idx)
        scene = self.state.get_current_scene()
        selection = self.state.get_current_selection()
        
        # Update scene cards visual state
        for i, card in enumerate(self.scene_cards):
            card.set_selected(i == idx)
        
        # Update status bar
        self.status_scene.configure(text=f"Current Scene: Scene {scene.scene_id:03d} ({scene.scene_type.upper()})")
        
        # Update center panel
        self._update_center_panel(scene, selection)
    
    def _update_center_panel(self, scene: Scene, selection: SceneSelection):
        """Update the center panel with scene data"""
        # Header
        self.hdr_num_lbl.configure(text=f"SCENE {scene.scene_id:03d} [{scene.scene_type.upper()}]")
        self.hdr_title_lbl.configure(text=scene.title)
        self.hdr_narr_lbl.configure(text=scene.narration)
        
        # Preview
        self.p_center_lbl.configure(text=f"▋▋ PREVIEW: SCENE {scene.scene_id:03d} [{scene.scene_type.upper()}] ▋▋\n\n{scene.title.upper()}")
        
        # Title entry
        self.ent_title.delete(0, "end")
        self.ent_title.insert(0, scene.title)
        
        # Narration
        self.txt_narr.delete("1.0", "end")
        self.txt_narr.insert("1.0", scene.narration)
        
        # Keywords
        keywords_str = ", ".join(scene.keywords) if scene.keywords else f"corporate, {scene.scene_type.lower()}, professional"
        self.txt_keys.delete(0, "end")
        self.txt_keys.insert(0, keywords_str)
        
        # Update media blocks based on selection
        self._update_media_blocks(selection, scene.scene_type)
        
        # Text content
        if scene.text_enabled:
            self.txt_content_editor.delete("1.0", "end")
            self.txt_content_editor.insert("1.0", scene.text_content)
            self.lbl_selected_font_display.configure(text=scene.text_font or "Bebas Neue")
        else:
            self.txt_content_editor.delete("1.0", "end")
            self.txt_content_editor.insert("1.0", f"TEXT BLUEPRINT PAYLOAD: {scene.title.upper()}")
            self.lbl_selected_font_display.configure(text="Inter Sans-Serif" if scene.scene_type != "text_only" else "Bebas Neue")
        
        # Editing notes
        self.txt_notes.delete("1.0", "end")
        self.txt_notes.insert("1.0", scene.editing_note or "Write simple editing notes for this scene...")
    
    def _update_media_blocks(self, selection: SceneSelection, scene_type: str):
        """Update media blocks with selection data"""
        # Map of asset types to selection attributes
        asset_mappings = {
            "Video": (selection.video, "video"),
            "Image": (selection.image, "image"),
            "Logo": (selection.logo, "logo"),
            "Icon": (selection.icon, "icon"),
            "SFX": (selection.sfx, "sfx"),
            "Website Screenshot": (selection.website_screenshot, "website_screenshot")
        }
        
        for asset_type, (sel, attr_name) in asset_mappings.items():
            if asset_type in self.media_blocks:
                ctlbl, csub, cthlbl, dp = self.media_blocks[asset_type]
                
                if sel and (sel.title or sel.name or sel.local_path):
                    title = sel.title or sel.name or Path(sel.local_path).name if sel.local_path else asset_type
                    subtitle = f"Asset matched blueprint definition • Status: {'Downloaded' if sel.downloaded else 'Not downloaded'}"
                    ctlbl.configure(text=f"Active Linked {asset_type}: {title}", text_color="#10B981")
                    csub.configure(text=subtitle, text_color="#64748B")
                    cthlbl.configure(text="MEDIA", text_color="#10B981")
                elif asset_type == "Website Screenshot" and selection.website:
                    url = selection.website.get("url", "")
                    if url:
                        ctlbl.configure(text=f"Website: {url}", text_color="#10B981")
                        csub.configure(text="Screenshot can be captured", text_color="#64748B")
                else:
                    ctlbl.configure(text=f"No active {asset_type} bound to slot definition", text_color="#64748B")
                    csub.configure(text="Click Search to pull relevant alternative elements from cloud library", text_color="#475569")
                    cthlbl.configure(text="EMPTY", text_color="#475569")
        
        # Website is special - show URL
        if "Website" in self.media_blocks:
            ctlbl, csub, cthlbl, dp = self.media_blocks["Website"]
            if selection.website and selection.website.get("url"):
                url = selection.website.get("url")
                ctlbl.configure(text=f"Website URL: {url}", text_color="#10B981")
                csub.configure(text="Enter URL in blueprint search", text_color="#64748B")
            else:
                ctlbl.configure(text="No website URL specified", text_color="#64748B")
                csub.configure(text="Add URL in blueprint search terms", text_color="#475569")
    
    def _on_search_type_changed(self, selected: str):
        """Handle search type change"""
        self.state.search_type = selected
        self.status_search.configure(text=f"Search Type: {selected}")
        self._generate_asset_cards(selected)
    
    def _generate_asset_cards(self, asset_type: str):
        """Generate asset cards for the browser"""
        # Clear existing cards
        for widget in self.asset_grid_container.winfo_children():
            widget.destroy()
        self.asset_cards.clear()
        
        # Get mock results for display
        titles_dict = {
            "Video": ["Cinematic Skyline", "Corporate Interview", "Tech Server Room", 
                     "Abstract Data Flow", "People Cheering", "Network Plexus"],
            "Image": ["Modern Office Space", "Team Meeting", "Creative Brainstorming", 
                     "Financial Chart", "Server Rack", "Success Handshake"],
            "Logo": ["Global Logistics Icon", "Alpha Tech Monogram", "Infinity Health Badge", 
                    "Quantum Energy Emblem", "Fintech Crown", "Apex Peak Vector"],
            "Website": ["SaaS Dashboard", "E-Commerce Checkout", "Corporate Portfolio", 
                       "Web3 Analytics Hub", "Tech Agency Concept", "AI Processing"],
            "Website Screenshot": ["Desktop Capture v1", "Mobile Matrix View", "SaaS Billing", 
                                  "Analytics Table", "Hero Module Render", "Dark UI Panel"],
            "Icon": ["Linear Arrow Right", "Solid Warning Hexagon", "Interface Gear", 
                    "Cloud Upload Outlined", "Secure Shield Badge", "User Profile Round"],
            "Font": ["Inter Sans-Serif", "Roboto Pro Variable", "JetBrains Mono Code", 
                    "Montserrat ExtraBold", "Playfair Display Serif", "Fira Code Ligatures"],
            "SFX": ["Deep Sub Drone Boom", "Interface UI Click", "Whoosh Transition", 
                   "Ambient Office hum", "Error Alert Prompt", "Success Chime Ring"]
        }
        
        res_dict = {
            "Video": "1920x1080", "Image": "3840x2160", "Logo": "SVG Vector", 
            "Website": "1440p Capture", "Website Screenshot": "PNG Image", 
            "Icon": "Vector", "Font": "TTF/OTF", "SFX": "24-bit WAV"
        }
        
        dur_dict = {
            "Video": "0:15", "Image": "N/A", "Logo": "N/A", "Website": "Static", 
            "Website Screenshot": "N/A", "Icon": "N/A", "Font": "Variable", "SFX": "0:04"
        }
        
        t_list = titles_dict.get(asset_type, ["Asset Placeholder"])
        res_val = res_dict.get(asset_type, "Standard")
        dur_val = dur_dict.get(asset_type, "N/A")
        
        # Create grid of cards
        for r in range(6):
            for c in range(2):
                idx = (r * 2) + c
                title = f"{t_list[idx % len(t_list)]} ({idx+1:02d})"
                
                result = {
                    "id": idx + 1,
                    "title": title,
                    "asset_type": asset_type.lower().replace(" ", "_"),
                    "width": int(res_val.split("x")[0]) if "x" in res_val else 0,
                    "height": int(res_val.split("x")[1]) if "x" in res_val else 0,
                    "duration": dur_val,
                    "thumbnail_url": "",
                    "download_url": ""
                }
                
                card = AssetCard(
                    self.asset_grid_container,
                    result=result,
                    select_callback=lambda r: self._select_asset(r),
                    preview_callback=lambda r: self._preview_asset(r)
                )
                card.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
                card.grid_propagate(False)
                
                self.asset_cards.append(card)
        
        # Configure grid columns
        self.asset_grid_container.grid_columnconfigure(0, weight=1)
        self.asset_grid_container.grid_columnconfigure(1, weight=1)
    
    def _select_asset(self, result: Dict[str, Any]):
        """Handle asset selection"""
        asset_type = result.get("asset_type", "unknown")
        scene = self.state.get_current_scene()
        
        if not scene:
            return
        
        # Create selection object
        selection = AssetSelection(
            provider=result.get("provider", "Unknown"),
            id=result.get("id"),
            title=result.get("title", "Untitled"),
            url=result.get("download_url", ""),
            downloaded=False
        )
        
        # Update selection based on asset type
        if asset_type == "video":
            self.state.selection_manager.set_video_selection(scene.scene_id, selection)
        elif asset_type == "image":
            self.state.selection_manager.set_image_selection(scene.scene_id, selection)
        elif asset_type == "logo":
            self.state.selection_manager.set_logo_selection(scene.scene_id, selection)
        elif asset_type == "icon":
            self.state.selection_manager.set_icon_selection(scene.scene_id, selection)
        elif asset_type == "sfx":
            self.state.selection_manager.set_sfx_selection(scene.scene_id, selection)
        
        # Update UI
        self._update_status(f"✓ Selected: {result.get('title')}")
        self._refresh_media_block(asset_type, selection)
    
    def _preview_asset(self, result: Dict[str, Any]):
        """Preview an asset"""
        # In production, would open a preview dialog
        self._update_status(f"Preview: {result.get('title')}")
    
    def _refresh_media_block(self, asset_type: str, selection: AssetSelection):
        """Refresh a media block with new selection"""
        type_map = {
            "video": "Video",
            "image": "Image",
            "logo": "Logo",
            "icon": "Icon",
            "sfx": "SFX"
        }
        
        block_key = type_map.get(asset_type)
        if block_key and block_key in self.media_blocks:
            ctlbl, csub, cthlbl, dp = self.media_blocks[block_key]
            ctlbl.configure(text=f"Selected: {selection.title}", text_color="#10B981")
            csub.configure(text="Ready for download", text_color="#64748B")
            cthlbl.configure(text="SELECTED", text_color="#10B981")
    
    def _perform_search(self):
        """Perform a search based on current query"""
        query = self.search_bar.get().strip()
        asset_type = self.search_type_combo.get()
        
        if not query:
            # Use keywords from current scene
            scene = self.state.get_current_scene()
            if scene:
                query = scene.keywords[0] if scene.keywords else scene.title.split()[0]
        
        self._update_status(f"Searching for {query}...")
        self.status_queue.configure(text="Queue: Searching")
        
        # Perform async search
        def do_search():
            results = self.search_manager.search(asset_type, query)
            self.after(0, lambda: self._display_search_results(results, asset_type))
        
        thread = threading.Thread(target=do_search)
        thread.daemon = True
        thread.start()
    
    def _display_search_results(self, results: List[Dict[str, Any]], asset_type: str):
        """Display search results in the asset browser"""
        self.current_search_results = results
        self._update_status(f"Found {len(results)} results")
        self.status_queue.configure(text="Queue: Idle")
        
        # Clear and regenerate cards with actual results
        for widget in self.asset_grid_container.winfo_children():
            widget.destroy()
        self.asset_cards.clear()
        
        for r, result in enumerate(results[:12]):  # Show max 12 results
            row = r // 2
            col = r % 2
            
            card = AssetCard(
                self.asset_grid_container,
                result=result,
                select_callback=lambda r: self._select_asset(r),
                preview_callback=lambda r: self._preview_asset(r)
            )
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            card.grid_propagate(False)
            self.asset_cards.append(card)
    
    def _load_more_assets(self):
        """Load more assets (pagination)"""
        self._update_status("Loading more assets...")
        # In production, would fetch next page of results
    
    def _trigger_search_switch(self, target_type: str):
        """Switch search type and focus"""
        normalizer = {
            "Website Screenshot": "Website Screenshot",
            "Font": "Font",
            "SFX": "SFX"
        }
        target_normalized = normalizer.get(target_type, target_type.capitalize())
        
        if target_normalized in ["Video", "Image", "Logo", "Website", 
                                 "Website Screenshot", "Icon", "Font", "SFX"]:
            self.search_type_combo.set(target_normalized)
            self._on_search_type_changed(target_normalized)
        
        # Auto-populate search with context
        scene = self.state.get_current_scene()
        if scene:
            search_terms = {
                "Video": scene.search_video,
                "Image": scene.search_image,
                "Logo": scene.search_logo,
                "Website": scene.search_website,
                "Icon": scene.search_icon,
                "SFX": scene.search_sfx
            }
            terms = search_terms.get(target_type, [])
            if terms:
                self.search_bar.delete(0, "end")
                self.search_bar.insert(0, terms[0])
    
    def _download_asset(self, asset_type: str):
        """Download the selected asset"""
        scene = self.state.get_current_scene()
        if not scene:
            return
        
        self._update_status(f"Downloading {asset_type}...")
        self.status_queue.configure(text="Queue: Downloading")
        
        # Get the selection
        selection = self.state.get_current_selection()
        
        # Map asset type to selection attribute
        type_map = {
            "Video": ("video", selection.video),
            "Image": ("image", selection.image),
            "Logo": ("logo", selection.logo),
            "Icon": ("icon", selection.icon),
            "SFX": ("sfx", selection.sfx),
            "Website Screenshot": ("website_screenshot", selection.website_screenshot)
        }
        
        if asset_type not in type_map:
            self._update_status(f"Unknown asset type: {asset_type}")
            return
        
        attr_name, sel = type_map[asset_type]
        
        if not sel.url and not sel.title:
            self._update_status(f"No {asset_type} selected for download")
            self.status_queue.configure(text="Queue: Idle")
            return
        
        # Generate filename
        filename = sanitize_filename(sel.title or f"{asset_type}_{scene.scene_id}")
        ext = get_file_extension(sel.url) if sel.url else f".{asset_type.lower()}"
        
        def on_download_complete(success: bool, path: str):
            if success:
                self.state.selection_manager.mark_downloaded(scene.scene_id, attr_name, path)
                self.after(0, lambda: self._update_status(f"✓ Downloaded: {Path(path).name}"))
                self.after(0, lambda: self._refresh_media_block(attr_name, sel))
            else:
                self.after(0, lambda: self._update_status(f"✗ Download failed: {path}"))
            self.after(0, lambda: self.status_queue.configure(text="Queue: Idle"))
        
        self.download_service.download_in_background(
            sel.url,
            f"{filename}{ext}",
            attr_name,
            on_download_complete
        )
    
    def _download_all_assets(self):
        """Download all selected assets for all scenes"""
        self._update_status("Starting batch download...")
        
        downloaded = 0
        total = 0
        
        for scene in self.state.blueprint_manager.scenes:
            selection = self.state.selection_manager.get_selection(scene.scene_id)
            
            # Check each asset type
            for attr_name in ["video", "image", "logo", "icon", "sfx"]:
                sel = getattr(selection, attr_name, None)
                if sel and sel.url and not sel.downloaded:
                    total += 1
                    # Queue download
                    self._download_asset_by_type(scene.scene_id, attr_name, sel)
        
        if total == 0:
            self._update_status("No assets to download")
        else:
            self._update_status(f"Queued {total} assets for download")
    
    def _download_asset_by_type(self, scene_id: int, asset_type: str, sel: AssetSelection):
        """Download a specific asset by type"""
        filename = sanitize_filename(sel.title or f"{asset_type}_{scene_id}")
        ext = get_file_extension(sel.url) if sel.url else f".{asset_type}"
        
        def on_complete(success: bool, path: str):
            if success:
                self.state.selection_manager.mark_downloaded(scene_id, asset_type, path)
        
        self.download_service.download_in_background(sel.url, f"{filename}{ext}", asset_type, on_complete)
    
    def _open_scene_board(self):
        """Open the scene board popup"""
        sb_win = ctk.CTkToplevel(self)
        sb_win.title("Storyboard Matrix View")
        sb_win.geometry("1100x700")
        sb_win.configure(fg_color="#0F1012")
        sb_win.after(200, lambda: sb_win.lift())
        
        # Info label
        lbl_info = ctk.CTkLabel(sb_win, text="PROJECT STORYBOARD MATRIX OVERVIEW", 
                               font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
                               text_color="#64748B")
        lbl_info.pack(anchor="w", padx=25, pady=(20, 10))
        
        # Scroll area
        scroll = ctk.CTkScrollableFrame(sb_win, fg_color="#141517", border_width=1, 
                                       border_color="#26292E", corner_radius=8)
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Grid frame
        grid_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Color mapping
        colors = {
            "VIDEO": "#3B82F6", "IMAGE": "#10B981", "TEXT": "#8B5CF6",
            "LOGO": "#F59E0B", "WEBSITE": "#EC4899", "CHART": "#06B6D4",
            "DOCUMENT": "#6366F1", "TIMELINE": "#14B8A6", "TEXT_ONLY": "#8B5CF6"
        }
        
        # Create scene cards in grid
        for i, scene in enumerate(self.state.blueprint_manager.scenes):
            stype = scene.scene_type.upper()
            num = f"Scene {scene.scene_id:03d}"
            
            is_selected = (i == self.state.current_scene_index)
            b_color = "#4F46E5" if is_selected else "#2D3139"
            f_color = "#1A1D24" if is_selected else "#1E2024"
            
            card = ctk.CTkFrame(grid_frame, width=225, height=140, fg_color=f_color, 
                               border_width=1, border_color=b_color, corner_radius=6)
            row = i // 4
            col = i % 4
            card.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
            card.grid_propagate(False)
            
            # Thumbnail area
            thumb = ctk.CTkFrame(card, fg_color="#0F1012", corner_radius=4)
            thumb.place(relx=0.05, rely=0.06, relwidth=0.9, relheight=0.65)
            
            # Scene number
            lbl_n = ctk.CTkLabel(thumb, text=num, 
                                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), 
                                text_color="#475569")
            lbl_n.place(x=8, y=6)
            
            # Type badge
            badge_color = colors.get(stype, "#64748B")
            badge = ctk.CTkFrame(thumb, fg_color=badge_color, corner_radius=3, height=16)
            badge.place(relx=0.95, rely=0.08, anchor="ne")
            blbl = ctk.CTkLabel(badge, text=stype, 
                               font=ctk.CTkFont(family="Segoe UI", size=8, weight="bold"), 
                               text_color="#FFFFFF", height=16, padx=4)
            blbl.pack()
            
            # Icon placeholder
            icn = ctk.CTkLabel(thumb, text="▋▋ 16:9 CARD ▋▋", 
                              font=ctk.CTkFont(family="Segoe UI", size=9), 
                              text_color="#22252A")
            icn.place(relx=0.5, rely=0.55, anchor="center")
            
            # Bottom label
            btm_lbl = ctk.CTkLabel(card, text=scene.title, 
                                  font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), 
                                  text_color="#64748B" if not is_selected else "#E2E8F0")
            btm_lbl.place(relx=0.06, rely=0.76)
            
            # Double-click to open scene
            def make_select(idx):
                return lambda e: [sb_win.destroy(), self._select_scene(idx)]
            
            for widget in [card, thumb, lbl_n, icn, btm_lbl, badge, blbl]:
                widget.bind("<Double-Button-1>", make_select(i))
        
        # Configure grid
        for c in range(4):
            grid_frame.grid_columnconfigure(c, weight=1)
        grid_frame.grid_rowconfigure((len(self.state.blueprint_manager.scenes) // 4) + 1, weight=1)
    
    def _save_project(self):
        """Save the current project"""
        try:
            # Force save selection
            self.state.selection_manager._auto_save()
            self._update_status("✓ Project saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save project: {e}")
    
    def _open_assets_folder(self):
        """Open the assets folder in file explorer"""
        import subprocess
        import sys
        
        assets_path = self.state.assets_dir.absolute()
        
        try:
            if sys.platform == 'win32':
                subprocess.startfile(assets_path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', assets_path])
            else:
                subprocess.run(['xdg-open', assets_path])
        except Exception as e:
            messagebox.showinfo("Assets Folder", f"Assets location:\n{assets_path}")
    
    def _refresh_view(self):
        """Refresh the current view"""
        scene = self.state.get_current_scene()
        if scene:
            selection = self.state.get_current_selection()
            self._update_center_panel(scene, selection)
        self._update_status("✓ View refreshed")
    
    def _on_selection_saved(self):
        """Callback when selection is saved"""
        self._update_status("✓ Auto-saved")
    
    def _on_title_changed(self, event=None):
        """Handle title change"""
        scene = self.state.get_current_scene()
        if scene:
            new_title = self.ent_title.get()
            # In production, would update blueprint
            self._update_status("Title updated")
    
    def _on_narration_changed(self, event=None):
        """Handle narration change"""
        self._update_status("Narration updated")
    
    def _on_text_content_changed(self, event=None):
        """Handle text content change"""
        scene = self.state.get_current_scene()
        if scene:
            content = self.txt_content_editor.get("1.0", "end").strip()
            font = self.lbl_selected_font_display.cget("text")
            self.state.selection_manager.set_text(scene.scene_id, content, font)
    
    def _on_notes_changed(self, event=None):
        """Handle notes change"""
        self._update_status("Notes updated")
    
    def _update_status(self, message: str):
        """Update the status bar message"""
        self.status_left.configure(text=message)


def main():
    """Main entry point"""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
