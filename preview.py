import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Blueprint Studio Pro")
        self.geometry("1700x950")
        self.minsize(1400, 800)
        self.configure(fg_color="#0F1012")
        
        self.scene_cards = []
        self.asset_cards = []
        
        self.build_top_toolbar()
        self.build_status_bar()
        
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=8, pady=0)
        
        self.build_left_panel()
        self.build_right_panel()
        self.build_center_panel()
        
        self.select_scene(0)

    def build_top_toolbar(self):
        toolbar = ctk.CTkFrame(self, height=55, fg_color="#1A1C1E", corner_radius=0, border_width=1, border_color="#26292E")
        toolbar.pack(fill="x", side="top")
        toolbar.pack_propagate(False)
        
        left_grp = ctk.CTkFrame(toolbar, fg_color="transparent")
        left_grp.pack(side="left", padx=15, fill="y")
        
        title_lbl = ctk.CTkLabel(left_grp, text="Blueprint Studio Pro", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color="#E2E8F0")
        title_lbl.pack(side="left", anchor="center")
        
        ver_lbl = ctk.CTkLabel(left_grp, text="v4.2.0-Beta", font=ctk.CTkFont(family="Segoe UI", size=10), text_color="#64748B")
        ver_lbl.pack(side="left", padx=(6, 0), anchor="center")
        
        sep = ctk.CTkFrame(toolbar, width=1, fg_color="#26292E")
        sep.pack(side="left", fill="y", pady=12, padx=10)
        
        proj_lbl = ctk.CTkLabel(toolbar, text="Project: Corporate_Vision_2026.blu", font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"), text_color="#94A3B8")
        proj_lbl.pack(side="left", padx=5)
        
        right_grp = ctk.CTkFrame(toolbar, fg_color="transparent")
        right_grp.pack(side="right", padx=15, fill="y")
        
        btn_opts = {"font": ctk.CTkFont(family="Segoe UI", size=12, weight="normal"), "height": 32, "fg_color": "#2D3139", "hover_color": "#3D424E", "text_color": "#E2E8F0", "corner_radius": 6}
        
        btn_imp = ctk.CTkButton(right_grp, text="📂 Import Blueprint", **btn_opts)
        btn_imp.pack(side="left", padx=4)
        
        btn_sb = ctk.CTkButton(right_grp, text="🖼 Scene Board", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), height=32, fg_color="#4F46E5", hover_color="#4338CA", text_color="#FFFFFF", corner_radius=6, command=self.open_scene_board)
        btn_sb.pack(side="left", padx=4)
        
        btn_save = ctk.CTkButton(right_grp, text="💾 Save Project", **btn_opts)
        btn_save.pack(side="left", padx=4)
        
        btn_dlall = ctk.CTkButton(right_grp, text="⬇ Download All", font=ctk.CTkFont(family="Segoe UI", size=12, weight="normal"), height=32, fg_color="#10B981", hover_color="#059669", text_color="#FFFFFF", corner_radius=6)
        btn_dlall.pack(side="left", padx=4)
        
        btn_assets = ctk.CTkButton(right_grp, text="📁 Assets Folder", **btn_opts)
        btn_assets.pack(side="left", padx=4)
        
        btn_refresh = ctk.CTkButton(right_grp, text="🔄 Refresh", **btn_opts)
        btn_refresh.pack(side="left", padx=4)

    def build_status_bar(self):
        sb = ctk.CTkFrame(self, height=28, fg_color="#1A1C1E", corner_radius=0, border_width=1, border_color="#26292E")
        sb.pack(fill="x", side="bottom")
        sb.pack_propagate(False)
        
        self.status_left = ctk.CTkLabel(sb, text=" Ready", font=ctk.CTkFont(family="Segoe UI", size=11), text_color="#10B981")
        self.status_left.pack(side="left", padx=15)
        
        sep1 = ctk.CTkFrame(sb, width=1, fg_color="#26292E")
        sep1.pack(side="left", fill="y", pady=6, padx=10)
        
        self.status_scene = ctk.CTkLabel(sb, text="Current Scene: Scene 001", font=ctk.CTkFont(family="Segoe UI", size=11), text_color="#94A3B8")
        self.status_scene.pack(side="left", padx=5)
        
        sep2 = ctk.CTkFrame(sb, width=1, fg_color="#26292E")
        sep2.pack(side="left", fill="y", pady=6, padx=10)
        
        self.status_search = ctk.CTkLabel(sb, text="Search Type: Video", font=ctk.CTkFont(family="Segoe UI", size=11), text_color="#94A3B8")
        self.status_search.pack(side="left", padx=5)
        
        self.status_queue = ctk.CTkLabel(sb, text="Queue Status: Idle", font=ctk.CTkFont(family="Segoe UI", size=11), text_color="#64748B")
        self.status_queue.pack(side="right", padx=15)

    def build_left_panel(self):
        lp = ctk.CTkFrame(self.main_container, width=290, fg_color="#141517", corner_radius=0)
        lp.pack(side="left", fill="y", padx=(0, 4), pady=6)
        lp.pack_propagate(False)
        
        hdr = ctk.CTkLabel(lp, text="SCENES & STORYBOARD", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#64748B")
        hdr.pack(anchor="w", padx=15, pady=(12, 8))
        
        self.scene_scroll = ctk.CTkScrollableFrame(lp, fg_color="transparent", corner_radius=0)
        self.scene_scroll.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        
        types = ["VIDEO", "IMAGE", "TEXT", "LOGO", "WEBSITE", "CHART", "DOCUMENT", "TIMELINE", "VIDEO", "TEXT", "IMAGE", "LOGO", "CHART", "WEBSITE", "DOCUMENT"]
        titles = ["Government Decision", "Keynote Speaker", "Main Typography Intro", "Brand Overlay", "Product Landing", "Q4 Growth Chart", "Whitepaper Summary", "Historical Roadmap", "CEO Interview", "Credits Slide", "Team Presentation", "Footer Identity", "Market Share Split", "Contact Reference", "Legal Terms"]
        colors = {"VIDEO": "#3B82F6", "IMAGE": "#10B981", "TEXT": "#8B5CF6", "LOGO": "#F59E0B", "WEBSITE": "#EC4899", "CHART": "#06B6D4", "DOCUMENT": "#6366F1", "TIMELINE": "#14B8A6"}
        
        for i in range(15):
            stype = types[i]
            title = titles[i]
            num = f"Scene {i+1:03d}"
            
            card = ctk.CTkFrame(self.scene_scroll, height=138, fg_color="#1E2024", border_width=1, border_color="#2D3139", corner_radius=6)
            card.pack(fill="x", pady=5, padx=2)
            card.pack_propagate(False)
            
            thumb = ctk.CTkFrame(card, fg_color="#0F1012", corner_radius=4)
            thumb.place(relx=0.03, rely=0.05, relwidth=0.94, relheight=0.68)
            
            lbl_num = ctk.CTkLabel(thumb, text=num, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#475569")
            lbl_num.place(x=8, y=6)
            
            badge_color = colors.get(stype, "#64748B")
            badge = ctk.CTkFrame(thumb, fg_color=badge_color, corner_radius=3, height=16)
            badge.place(relx=0.95, rely=0.08, anchor="ne")
            blbl = ctk.CTkLabel(badge, text=stype, font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"), text_color="#FFFFFF", height=16, padx=5)
            blbl.pack()
            
            icon_lbl = ctk.CTkLabel(thumb, text=f"▋▋ {stype} PLACEHOLDER ▋▋", font=ctk.CTkFont(family="Segoe UI", size=10, weight="normal"), text_color="#22252A")
            icon_lbl.place(relx=0.5, rely=0.55, anchor="center")
            
            lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#C8D2DD", anchor="w")
            lbl_title.place(relx=0.05, rely=0.76, relwidth=0.9)
            
            self.scene_cards.append((card, num, title, stype, icon_lbl))
            
            def make_cb(idx):
                return lambda e: self.select_scene(idx)
            def make_hover_in(c):
                return lambda e: c.configure(border_color="#4F46E5") if self.scene_cards.index(next(x for x in self.scene_cards if x[0]==c)) != self.current_selected_scene_idx else None
            def make_hover_out(c):
                return lambda e: c.configure(border_color="#2D3139") if self.scene_cards.index(next(x for x in self.scene_cards if x[0]==c)) != self.current_selected_scene_idx else None
            
            card.bind("<Button-1>", make_cb(i))
            thumb.bind("<Button-1>", make_cb(i))
            lbl_title.bind("<Button-1>", make_cb(i))
            lbl_num.bind("<Button-1>", make_cb(i))
            icon_lbl.bind("<Button-1>", make_cb(i))
            blbl.bind("<Button-1>", make_cb(i))
            badge.bind("<Button-1>", make_cb(i))
            
            card.bind("<Enter>", make_hover_in(card))
            card.bind("<Leave>", make_hover_out(card))

    def build_right_panel(self):
        self.rp = ctk.CTkFrame(self.main_container, width=440, fg_color="#141517", corner_radius=0)
        self.rp.pack(side="right", fill="y", padx=(4, 0), pady=6)
        self.rp.pack_propagate(False)
        
        hdr = ctk.CTkLabel(self.rp, text="ASSET BROWSER & MEDIALIBRARY", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#64748B")
        hdr.pack(anchor="w", padx=16, pady=(12, 6))
        
        ctrl_box = ctk.CTkFrame(self.rp, fg_color="#1E2024", border_width=1, border_color="#2D3139", corner_radius=6)
        ctrl_box.pack(fill="x", padx=12, pady=6)
        
        self.search_type_combo = ctk.CTkOptionMenu(ctrl_box, values=["Video", "Image", "Logo", "Website", "Website Screenshot", "Icon", "Font", "SFX"], font=ctk.CTkFont(family="Segoe UI", size=12), fg_color="#2D3139", button_color="#3D424E", button_hover_color="#4F46E5", dropdown_fg_color="#1E2024", dropdown_hover_color="#2D3139", height=32, command=self.search_type_changed)
        self.search_type_combo.pack(fill="x", padx=12, pady=(12, 6))
        
        srow = ctk.CTkFrame(ctrl_box, fg_color="transparent")
        srow.pack(fill="x", padx=12, pady=(0, 12))
        
        self.search_bar = ctk.CTkEntry(srow, placeholder_text="Search assets...", font=ctk.CTkFont(family="Segoe UI", size=12), fg_color="#0F1012", border_color="#2D3139", height=32)
        self.search_bar.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        sbtn = ctk.CTkButton(srow, text="Search", width=75, height=32, font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), fg_color="#4F46E5", hover_color="#4338CA")
        sbtn.pack(side="right")
        
        self.asset_scroll = ctk.CTkScrollableFrame(self.rp, fg_color="transparent")
        self.asset_scroll.pack(fill="both", expand=True, padx=6, pady=4)
        
        self.asset_grid_container = ctk.CTkFrame(self.asset_scroll, fg_color="transparent")
        self.asset_grid_container.pack(fill="both", expand=True)
        
        self.load_more_btn = ctk.CTkButton(self.asset_scroll, text="Load More Assets", fg_color="#2D3139", hover_color="#3D424E", font=ctk.CTkFont(family="Segoe UI", size=12, weight="normal"), height=35)
        self.load_more_btn.pack(fill="x", padx=8, pady=12)
        
        self.generate_asset_cards("Video")

    def generate_asset_cards(self, asset_type):
        for widget in self.asset_grid_container.winfo_children():
            widget.destroy()
        self.asset_cards.clear()
        
        titles_dict = {
            "Video": ["Cinematic Skyline", "Corporate Interview Alpha", "Tech Server Room Loop", "Abstract Data Flow", "People Cheering CloseUp", "Abstract Network Plexus"],
            "Image": ["Modern Office Space", "Team Meeting Candid", "Creative Brainstorming", "Financial Chart Overlay", "Server Rack Close", "Success Handshake"],
            "Logo": ["Global Logistics Icon", "Alpha Tech Monogram", "Infinity Health Badge", "Quantum Energy Emblem", "Fintech Crown Minimal", "Apex Peak Vector"],
            "Website": ["SaaS Premium Dashboard", "E-Commerce Checkout Minimal", "Corporate Portfolio Live", "Web3 Analytics Hub", "Tech Agency Concept", "AI Processing Showcase"],
            "Website Screenshot": ["Full Desktop Capture v1", "Mobile Matrix View", "SaaS Billing Blueprint", "Analytics Table Light", "Hero Module Render", "Dark UI Panel Snap"],
            "Icon": ["Linear Arrow Right", "Solid Warning Hexagon", "Interface Gear Smooth", "Cloud Upload Outlined", "Secure Shield Badge", "User Profile Round"],
            "Font": ["Inter Sans-Serif", "Roboto Pro Variable", "JetBrains Mono Code", "Montserrat ExtraBold", "Playfair Display Serif", "Fira Code Ligatures"],
            "SFX": ["Deep Sub Drone Boom", "Interface UI Digital Click", "Whoosh Transition Clean", "Ambient Office hum", "Error Alert Prompt", "Success Chime Ring"]
        }
        
        res_dict = {"Video": "1920x1080", "Image": "3840x2160", "Logo": "SVG Vector", "Website": "1440p Capture", "Website Screenshot": "PNG Image", "Icon": "Vector", "Font": "TTF / OTF", "SFX": "24-bit WAV"}
        dur_dict = {"Video": "0:15", "Image": "N/A", "Logo": "N/A", "Website": "Static", "Website Screenshot": "N/A", "Icon": "N/A", "Font": "Variable", "SFX": "0:04"}
        
        t_list = titles_dict.get(asset_type, ["Asset Placeholder"])
        res_val = res_dict.get(asset_type, "Standard")
        dur_val = dur_dict.get(asset_type, "N/A")
        
        for r in range(6):
            for c in range(2):
                idx = (r * 2) + c
                title = t_list[idx % len(t_list)] + f" ({idx+1:02d})"
                
                card = ctk.CTkFrame(self.asset_grid_container, width=195, height=175, fg_color="#1E2024", border_width=1, border_color="#2D3139", corner_radius=6)
                card.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
                card.grid_propagate(False)
                
                thumb = ctk.CTkFrame(card, fg_color="#0F1012", corner_radius=4)
                thumb.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.48)
                
                tlbl = ctk.CTkLabel(thumb, text=asset_type.upper(), font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"), text_color="#475569")
                tlbl.place(relx=0.5, rely=0.5, anchor="center")
                
                lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#C8D2DD", anchor="w")
                lbl_title.place(relx=0.06, rely=0.56, relwidth=0.88)
                
                info_str = f"{res_val}" if dur_val == "N/A" else f"{res_val}  •  {dur_val}"
                lbl_info = ctk.CTkLabel(card, text=info_str, font=ctk.CTkFont(family="Segoe UI", size=10), text_color="#64748B", anchor="w")
                lbl_info.place(relx=0.06, rely=0.69, relwidth=0.88)
                
                pbtn = ctk.CTkButton(card, text="Preview", width=85, height=24, font=ctk.CTkFont(family="Segoe UI", size=11), fg_color="#2D3139", hover_color="#3D424E", text_color="#E2E8F0")
                pbtn.place(relx=0.05, rely=0.83)
                
                sbtn = ctk.CTkButton(card, text="Select", width=85, height=24, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), fg_color="#3B82F6", hover_color="#2563EB")
                sbtn.place(relx=0.53, rely=0.83)
                
                def make_card_hover_in(cd):
                    return lambda e: cd.configure(border_color="#4F46E5")
                def make_card_hover_out(cd):
                    return lambda e: cd.configure(border_color="#2D3139")
                
                card.bind("<Enter>", make_card_hover_in(card))
                card.bind("<Leave>", make_card_hover_out(card))
                
                self.asset_cards.append(card)
                
        self.asset_grid_container.grid_columnconfigure(0, weight=1)
        self.asset_grid_container.grid_columnconfigure(1, weight=1)

    def search_type_changed(self, selected):
        self.status_search.configure(text=f"Search Type: {selected}")
        self.generate_asset_cards(selected)

    def select_scene(self, idx):
        self.current_selected_scene_idx = idx
        for i, (card, num, title, stype, icon_lbl) in enumerate(self.scene_cards):
            if i == idx:
                card.configure(border_color="#4F46E5", fg_color="#1A1D24")
                self.status_scene.configure(text=f"Current Scene: {num} ({stype})")
                self.update_center_panel_data(num, title, stype, icon_lbl)
            else:
                card.configure(border_color="#2D3139", fg_color="#1E2024")

    def open_scene_board(self):
        sb_win = ctk.CTkToplevel(self)
        sb_win.title("Storyboard Matrix View")
        sb_win.geometry("1100x700")
        sb_win.configure(fg_color="#0F1012")
        sb_win.after(200, lambda: sb_win.lift())
        
        lbl_info = ctk.CTkLabel(sb_win, text="PROJECT STORYBOARD MATRIX OVERVIEW", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#64748B")
        lbl_info.pack(anchor="w", padx=25, pady=(20, 10))
        
        scroll = ctk.CTkScrollableFrame(sb_win, fg_color="#141517", border_width=1, border_color="#26292E", corner_radius=8)
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        grid_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        types = ["VIDEO", "IMAGE", "TEXT", "LOGO", "WEBSITE", "CHART", "DOCUMENT", "TIMELINE", "VIDEO", "TEXT", "IMAGE", "LOGO", "CHART", "WEBSITE", "DOCUMENT"]
        colors = {"VIDEO": "#3B82F6", "IMAGE": "#10B981", "TEXT": "#8B5CF6", "LOGO": "#F59E0B", "WEBSITE": "#EC4899", "CHART": "#06B6D4", "DOCUMENT": "#6366F1", "TIMELINE": "#14B8A6"}
        
        for i in range(15):
            stype = types[i]
            num = f"Scene {i+1:03d}"
            
            is_selected = (i == self.current_selected_scene_idx)
            b_color = "#4F46E5" if is_selected else "#2D3139"
            f_color = "#1A1D24" if is_selected else "#1E2024"
            
            card = ctk.CTkFrame(grid_frame, width=225, height=140, fg_color=f_color, border_width=1, border_color=b_color, corner_radius=6)
            row = i // 4
            col = i % 4
            card.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
            card.grid_propagate(False)
            
            thumb = ctk.CTkFrame(card, fg_color="#0F1012", corner_radius=4)
            thumb.place(relx=0.05, rely=0.06, relwidth=0.9, relheight=0.65)
            
            lbl_n = ctk.CTkLabel(thumb, text=num, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#475569")
            lbl_n.place(x=8, y=6)
            
            badge_color = colors.get(stype, "#64748B")
            badge = ctk.CTkFrame(thumb, fg_color=badge_color, corner_radius=3, height=16)
            badge.place(relx=0.95, rely=0.08, anchor="ne")
            blbl = ctk.CTkLabel(badge, text=stype, font=ctk.CTkFont(family="Segoe UI", size=8, weight="bold"), text_color="#FFFFFF", height=16, padx=4)
            blbl.pack()
            
            icn = ctk.CTkLabel(thumb, text="▋▋ 16:9 CARD ▋▋", font=ctk.CTkFont(family="Segoe UI", size=9), text_color="#22252A")
            icn.place(relx=0.5, rely=0.55, anchor="center")
            
            btm_lbl = ctk.CTkLabel(card, text=f"System Stack Identity", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color="#64748B" if not is_selected else "#E2E8F0")
            btm_lbl.place(relx=0.06, rely=0.76)
            
        for c in range(4):
            grid_frame.grid_columnconfigure(c, weight=1)

    def build_center_panel(self):
        cp = ctk.CTkFrame(self.main_container, fg_color="transparent")
        cp.pack(side="left", fill="both", expand=True, padx=4, pady=6)
        
        self.scene_hdr_box = ctk.CTkFrame(cp, height=75, fg_color="#1A1C1E", border_width=1, border_color="#26292E", corner_radius=6)
        self.scene_hdr_box.pack(fill="x", side="top", pady=(0, 4))
        self.scene_hdr_box.pack_propagate(False)
        
        self.hdr_num_lbl = ctk.CTkLabel(self.scene_hdr_box, text="SCENE 000", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#4F46E5")
        self.hdr_num_lbl.place(x=15, y=10)
        
        self.hdr_title_lbl = ctk.CTkLabel(self.scene_hdr_box, text="No Scene Selected", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color="#E2E8F0")
        self.hdr_title_lbl.place(x=15, y=28)
        
        self.hdr_narr_lbl = ctk.CTkLabel(self.scene_hdr_box, text="No active script compilation configured.", font=ctk.CTkFont(family="Segoe UI", size=11), text_color="#64748B", anchor="w", justify="left", height=45)
        self.hdr_narr_lbl.place(x=400, y=15, relwidth=0.58)
        
        self.preview_box = ctk.CTkFrame(cp, height=340, fg_color="#000000", border_width=1, border_color="#26292E", corner_radius=6)
        self.preview_box.pack(fill="x", side="top", pady=(0, 4))
        self.preview_box.pack_propagate(False)
        
        self.p_center_lbl = ctk.CTkLabel(self.preview_box, text="[ NO SCENE SELECTED ]", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color="#475569")
        self.p_center_lbl.place(relx=0.5, rely=0.5, anchor="center")
        
        self.p_title_lbl = ctk.CTkLabel(self.preview_box, text="Preview Monitor", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#334155")
        self.p_title_lbl.place(x=12, y=10)
        
        self.p_badge = ctk.CTkFrame(self.preview_box, fg_color="#334155", corner_radius=3, height=18)
        self.p_badge.place(relx=0.98, rely=0.04, anchor="ne")
        self.p_badge_lbl = ctk.CTkLabel(self.p_badge, text="LIVE", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color="#FFFFFF", height=18, padx=6)
        self.p_badge_lbl.pack()
        
        self.editor_scroll = ctk.CTkScrollableFrame(cp, fg_color="#141517", corner_radius=6, border_width=1, border_color="#26292E")
        self.editor_scroll.pack(fill="both", expand=True, pady=(4, 0))
        
        self.build_blueprint_fields()

    def build_blueprint_fields(self):
        f = self.editor_scroll
        
        t_box = self.create_section_frame(f, "Title & Basic Config")
        ctk.CTkLabel(t_box, text="Scene Entry Title", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#94A3B8").pack(anchor="w", padx=15, pady=(8, 2))
        self.ent_title = ctk.CTkEntry(t_box, font=ctk.CTkFont(family="Segoe UI", size=13), fg_color="#0F1012", border_color="#2D3139", height=32)
        self.ent_title.pack(fill="x", padx=15, pady=(0, 12))
        
        n_box = self.create_section_frame(f, "Voiceover Narration Script")
        self.txt_narr = ctk.CTkTextbox(n_box, font=ctk.CTkFont(family="Segoe UI", size=13), fg_color="#0F1012", border_color="#2D3139", height=85)
        self.txt_narr.pack(fill="x", padx=15, pady=12)
        
        k_box = self.create_section_frame(f, "Extracted Keywords (Read-Only)")
        self.txt_keys = ctk.CTkEntry(k_box, font=ctk.CTkFont(family="Segoe UI", size=12), fg_color="#1E2024", border_color="#2D3139", text_color="#38BDF8", height=32)
        self.txt_keys.pack(fill="x", padx=15, pady=12)
        
        self.media_blocks = {}
        target_blocks = ["Video", "Image", "Logo", "Website", "Website Screenshot", "Icon", "Font", "SFX"]
        
        for m_type in target_blocks:
            m_box = self.create_section_frame(f, f"Primary {m_type.upper()} Asset Blueprint")
            
            crow = ctk.CTkFrame(m_box, fg_color="transparent")
            crow.pack(fill="x", padx=15, pady=(8, 8))
            
            dp = ctk.CTkOptionMenu(crow, values=[f"Suggested {m_type} 1", f"Suggested {m_type} 2", f"Alternative {m_type}"], font=ctk.CTkFont(family="Segoe UI", size=12), fg_color="#2D3139", button_color="#3D424E", height=30, width=200)
            dp.pack(side="left", padx=(0, 8))
            
            def make_search_cb(mt=m_type):
                return lambda: self.trigger_search_switch(mt)
            
            s_btn = ctk.CTkButton(crow, text="Search", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), fg_color="#4F46E5", hover_color="#4338CA", height=30, width=85, command=make_search_cb())
            s_btn.pack(side="left", padx=(0, 4))
            
            d_btn = ctk.CTkButton(crow, text="Download", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), fg_color="#10B981", hover_color="#059669", height=30, width=85)
            d_btn.pack(side="left")
            
            card_p = ctk.CTkFrame(m_box, fg_color="#0F1012", border_width=1, border_color="#2D3139", corner_radius=5, height=65)
            card_p.pack(fill="x", padx=15, pady=(0, 12))
            card_p.pack_propagate(False)
            
            cthumb = ctk.CTkFrame(card_p, fg_color="#1E2024", width=80, height=45, corner_radius=3)
            cthumb.place(x=10, y=10)
            cthumb.pack_propagate(False)
            cthlbl = ctk.CTkLabel(cthumb, text="THUMB", font=ctk.CTkFont(family="Segoe UI", size=9), text_color="#475569")
            cthlbl.pack(expand=True)
            
            ctlbl = ctk.CTkLabel(card_p, text=f"No {m_type} asset selected for this slot Blueprint", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#64748B")
            ctlbl.place(x=105, y=10)
            
            csub = ctk.CTkLabel(card_p, text="Click Search to pull relevant elements from cloud library", font=ctk.CTkFont(family="Segoe UI", size=11), text_color="#475569")
            csub.place(x=105, y=32)
            
            act_grp = ctk.CTkFrame(card_p, fg_color="transparent")
            act_grp.place(relx=0.98, rely=0.5, anchor="e")
            
            r_btn = ctk.CTkButton(act_grp, text="Replace", width=70, height=24, font=ctk.CTkFont(family="Segoe UI", size=11), fg_color="#2D3139", hover_color="#3D424E")
            r_btn.pack(side="left", padx=2)
            
            card_d_btn = ctk.CTkButton(act_grp, text="Download", width=70, height=24, font=ctk.CTkFont(family="Segoe UI", size=11), fg_color="#10B981", hover_color="#059669")
            card_d_btn.pack(side="left", padx=2)
            
            self.media_blocks[m_type] = (ctlbl, csub, cthlbl)
            
        f_box = self.create_section_frame(f, "Text")
        
        ctk.CTkLabel(f_box, text="Text Content", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#94A3B8").pack(anchor="w", padx=15, pady=(8, 2))
        self.txt_content_editor = ctk.CTkTextbox(f_box, font=ctk.CTkFont(family="Segoe UI", size=13), fg_color="#0F1012", border_color="#2D3139", height=100)
        self.txt_content_editor.pack(fill="x", padx=15, pady=(0, 10))
        
        font_control_bar = ctk.CTkFrame(f_box, fg_color="transparent")
        font_control_bar.pack(fill="x", padx=15, pady=(0, 12))
        
        font_info_subgrp = ctk.CTkFrame(font_control_bar, fg_color="transparent")
        font_info_subgrp.pack(side="left")
        
        ctk.CTkLabel(font_info_subgrp, text="Current Font", font=ctk.CTkFont(family="Segoe UI", size=11), text_color="#64748B", anchor="w").pack(anchor="w")
        self.lbl_selected_font_display = ctk.CTkLabel(font_info_subgrp, text="Bebas Neue", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color="#E2E8F0", anchor="w")
        self.lbl_selected_font_display.pack(anchor="w")
        
        def mock_font_browser_trigger():
            self.trigger_search_switch("Font")
            
        btn_change_font = ctk.CTkButton(font_control_bar, text="Change Font", width=110, height=30, font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), fg_color="#2D3139", hover_color="#3D424E", text_color="#E2E8F0", command=mock_font_browser_trigger)
        btn_change_font.pack(side="right", anchor="center")
        
        # EDITING NOTES SECTION: Structured minimalist layout for pure scene directions
        note_box = self.create_section_frame(f, "Editing Notes")
        self.txt_notes = ctk.CTkTextbox(note_box, font=ctk.CTkFont(family="Segoe UI", size=13), fg_color="#0F1012", border_color="#2D3139", height=75)
        self.txt_notes.pack(fill="x", padx=15, pady=12)

    def create_section_frame(self, parent, title):
        box = ctk.CTkFrame(parent, fg_color="#1E2024", border_width=1, border_color="#2D3139", corner_radius=6)
        box.pack(fill="x", pady=6, padx=8)
        
        lbl = ctk.CTkLabel(box, text=title.upper(), font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#475569")
        lbl.pack(anchor="w", padx=15, pady=(10, 2))
        
        sep = ctk.CTkFrame(box, height=1, fg_color="#26292E")
        sep.pack(fill="x", padx=15, pady=2)
        
        return box

    def update_center_panel_data(self, num, title, stype, left_panel_icon_lbl):
        narr_text = f"This narration flow maps to {num}. It provides full context for the visual sequence featuring '{title}'. High emphasis is placed on strategic clarity and pacing."
        
        self.hdr_num_lbl.configure(text=f"{num.upper()} [{stype}]")
        self.hdr_title_lbl.configure(text=title)
        self.hdr_narr_lbl.configure(text=narr_text)
        
        self.p_center_lbl.configure(text=f"▋▋ PREVIEW: {num} [{stype}] ▋▋\n\n{title.upper()}")
        
        self.ent_title.delete(0, "end")
        self.ent_title.insert(0, title)
        
        self.txt_narr.delete("1.0", "end")
        self.txt_narr.insert("1.0", narr_text)
        
        self.txt_keys.delete(0, "end")
        self.txt_keys.insert(0, f"corporate, {stype.lower()}, professional, vision, 2026, asset, {title.split()[0].lower()}")
        
        left_panel_icon_lbl.configure(text="★ LIVE RENDER ★", text_color="#10B981")
        
        for m_type, (lbl, sub, cthlbl) in self.media_blocks.items():
            if m_type == stype.capitalize() or (stype in ["CHART", "DOCUMENT", "TIMELINE"] and m_type == "Image"):
                lbl.configure(text=f"Active Linked {m_type}: High-Res Production {stype} Resource", text_color="#10B981")
                sub.configure(text="Asset matched blueprint definition  •  Status: Verified Ready", text_color="#64748B")
                cthlbl.configure(text="MEDIA", text_color="#10B981")
            else:
                lbl.configure(text=f"No active {m_type} bound to slot definition", text_color="#64748B")
                sub.configure(text="Click Search to pull relevant alternative elements from cloud library", text_color="#475569")
                cthlbl.configure(text="EMPTY", text_color="#475569")
                
        self.txt_content_editor.delete("1.0", "end")
        self.txt_content_editor.insert("1.0", f"TEXT BLUEPRINT PAYLOAD: {title.upper()}\nBound dynamically to live system node sequence.")
        self.lbl_selected_font_display.configure(text="Bebas Neue" if stype == "TEXT" else "Inter Sans-Serif")
            
        # Refactored data loop parsing simple layout directions into the dedicated textbox
        example_notes = {
            0: "Use black screen with large white text.",
            1: "Slow zoom into logo.",
            2: "Fade in after narration.",
            3: "Replace this shot if better footage is found.",
            4: "Add cinematic whoosh before transition."
        }
        selected_note = example_notes.get(idx := self.current_selected_scene_idx % 5, "Write simple editing notes for this scene...")
        
        self.txt_notes.delete("1.0", "end")
        self.txt_notes.insert("1.0", f"{selected_note}")

    def trigger_search_switch(self, target_type):
        normalizer = {"Website Screenshot": "Website Screenshot", "Font": "Font", "SFX": "SFX"}
        target_normalized = normalizer.get(target_type, target_type.capitalize())
        
        if target_normalized in ["Video", "Image", "Logo", "Website", "Website Screenshot", "Icon", "Font", "SFX"]:
            self.search_type_combo.set(target_normalized)
            self.search_type_changed(target_normalized)
            
        self.search_bar.delete(0, "end")
        self.search_bar.insert(0, f"Auto-query context: {target_type}")

if __name__ == "__main__":
    app = App()
    app.mainloop()