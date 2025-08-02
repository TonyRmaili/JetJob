import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import json
from backend.ai_caller import AICaller
from backend.message_builder import MessageBuilder
from api.send_email import send_email
from api.searcher import multi_search, sanitize_filename, get_unique_path
import shutil
from dotenv import load_dotenv
from tkinter import ttk
from tkinter import scrolledtext
from datetime import datetime
from frontend.style_gui import StyleGUI


# start command 
# py -m frontend.gui

class JetJob:
    def __init__(self, screen_width:float, screen_height:float):
        self.root = tk.Tk()
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.title("JetJob")

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.style_values = {
            "BG_COLOR": "#23272f",
            "BTN_BG": "#334155",
            "BTN_FG": "#f1f5f9",
            "BTN_ACTIVE_BG": "#475569",
            "BTN_ACTIVE_FG": "#ffffff",
            "TEXT_BG": "#1e293b",
            "TEXT_FG": "#f1f5f9",
            "LABEL_FG": "#a3a3a3",
            "FONT": ("Consolas", 12),
            "BTN_FONT": ("Segoe UI", 11, "bold"),
        }

        self.style = StyleGUI()

        self.create_menu()

        # paths
        self.profiles_path = "./profiles"
        os.makedirs(self.profiles_path,exist_ok=True)

        if not self.has_valid_profiles():
            self.selected_profile = None
            self.main_frame = None
            self.config_values = {
                    "url": "https://jobsearch.api.jobtechdev.se/search",
                    "gmail":None,
                    "keywords": [],
                    "regions": [],
                    "missing_regions":False,

                    "limit": 10,
                    "offset": 0,

                    "model":"gpt-4.1",
                    "temperature":0.7,
                   
                    "about_me_path": None,
                    "system_prompt_path": None,
                    "credentials":None,
                    
                    "attachment_files":[],

                    "processed_ids": [],
                    "sent_ids":[],
                    
                }
            self.config_path = None
            self.init_create_profile_frame()
            self.show_frame(self.create_profile_frame)

        else:
            self.selected_profile = self.get_last_used_profile()
            self.config_values , self.config_path = self.load_config_values()
            self.create_profile_subfolders(self.selected_profile)
            self.init_main_frame()
            self.show_frame(self.main_frame)
           
        # gpt models
        self.models = ["gpt-4.1","gpt-4o", "gpt-4o-mini"]

        self.regions = ["Blekinge Län",
                        "Dalarnas Län",
                        "Gotlands Län", 
                        "Gävleborgs Län", 
                        "Hallands Län", 
                        "Jämtlands Län", 
                        "Jönköpings Län", 
                        "Kalmar Län", 
                        "Kronobergs Län", 
                        "Norrbottens Län", 
                        "Skåne Län", 
                        "Stockholms Län", 
                        "Södermanlands Län", 
                        "Uppsala Län", 
                        "Värmlands Län", 
                        "Västerbottens Län", 
                        "Västernorrlands Län", 
                        "Västmanlands Län",
                        "Västra Götalands Län", 
                        "Örebro Län", 
                        "Östergötlands Län"
                        ]

        self.adjust_window()

    def init_main_frame(self):    
        self.root.title(f"JetJob - Welcome {self.selected_profile}")

        BG_COLOR = "#23272f"
        BTN_BG = "#334155"
        BTN_FG = "#f1f5f9"
        BTN_ACTIVE_BG = "#475569"
        BTN_ACTIVE_FG = "#ffffff"
        TEXT_BG = "#1e293b"
        TEXT_FG = "#f1f5f9"
        LABEL_FG = "#a3a3a3"
        FONT = ("Consolas", 12)
        BTN_FONT = ("Segoe UI", 11, "bold")

        def on_search():
            try:
                self.validate_search_values()
            except ValueError as e:
                self.show_large_warning(str(e), title="Error")
                return
            
            multi_search(
                keywords=self.config_values["keywords"],
                BASE_URL=self.config_values["url"],
                limit=self.config_values["limit"],
                offset=self.config_values["offset"],
                filter_key="email",
                output_path=self.ads_path          
            )
                          
        def on_personalize_click():
            try:
                self.validate_personal_letter(test=False)
                self.setup_personal_letter_payload()
                 
            except ValueError as e:
                messagebox.showwarning("Invalid Configuration", str(e))
                return

        def on_sendmails_click():
            try:
                self.validate_send_email()
                self.mass_send_email()
            except ValueError as e:
                self.show_large_warning(message=str(e),title="Error")
            except FileNotFoundError as e:
                self.show_large_warning(message=str(e),title="Error")

    
        # Main UI setup
        self.main_frame = tk.Frame(self.root, bg=self.style_values["BG_COLOR"])
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        button_frame = tk.Frame(self.main_frame, bg=self.style_values["BG_COLOR"])
        button_frame.grid(row=0, column=0, sticky="nsw", padx=10, pady=15)

        def style_button(btn):
            btn.configure(
                bg=BTN_BG, fg=BTN_FG,
                activebackground=BTN_ACTIVE_BG,
                activeforeground=BTN_ACTIVE_FG,
                font=BTN_FONT,
                relief="raised", bd=2, cursor="hand2"
            )
       
        if os.listdir(self.ads_path):
            preview_ads_btn = tk.Button(button_frame, text="Preview Ads", command=self.init_preview_ads_frame, width=14)
            preview_ads_btn.grid(row=1, column=0, sticky="ew", padx=5, pady=8)
            style_button(preview_ads_btn)
        else:
            missing_ads_label = tk.Label(button_frame, text="No ads found", fg=LABEL_FG, bg=BG_COLOR, font=FONT)
            missing_ads_label.grid(row=1, column=0, sticky="ew", padx=5, pady=8)

        if os.listdir(self.processed_letters_path):
            preview_letters_btn = tk.Button(button_frame, text="Preview Letters", command=self.init_preview_letters_frame, width=18)
            preview_letters_btn.grid(row=1, column=1, sticky="ew", padx=5, pady=8)
            style_button(preview_letters_btn)
        else:
            missing_letters_label = tk.Label(button_frame, text="No processed letters found", fg=LABEL_FG, bg=BG_COLOR, font=FONT)
            missing_letters_label.grid(row=1, column=1, sticky="ew", padx=5, pady=8)

                
        search_btn = tk.Button(button_frame, text="Search", command=on_search, width=10)
        search_btn.grid(row=0, column=0, padx=8, pady=8)
        style_button(search_btn)

        personalize_btn = tk.Button(button_frame, text="Personalize letters", command=on_personalize_click, width=16)
        personalize_btn.grid(row=0, column=1, padx=8, pady=8)
        style_button(personalize_btn)

        sendmails_btn = tk.Button(button_frame, text="Send emails", command=on_sendmails_click, width=12)
        sendmails_btn.grid(row=0, column=2, padx=8, pady=8)
        style_button(sendmails_btn)

        test_prompt_btn = tk.Button(button_frame, text="Test prompt", command=self.test_prompt_click, width=12)
        test_prompt_btn.grid(row=0, column=3, padx=8, pady=8)
        style_button(test_prompt_btn)



        # Terminal frame with a nice border and background
        terminal_frame = tk.Frame(self.main_frame, bg=BG_COLOR, bd=2, relief="groove")
        terminal_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=18)

        # Make the grid expand with window resize
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        terminal_frame.rowconfigure(0, weight=1)
        terminal_frame.columnconfigure(0, weight=1)

        # Create a styled, scrollable textarea in terminal_frame
        text_scrollbar = ttk.Scrollbar(terminal_frame, orient="vertical")
        text_scrollbar.grid(row=0, column=1, sticky="ns")

        self.terminal_text = tk.Text(
            terminal_frame, 
            bg=TEXT_BG, fg=TEXT_FG, 
            insertbackground=BTN_ACTIVE_FG,   # Makes the cursor visible
            font=FONT, 
            wrap="word", 
            borderwidth=0, 
            highlightthickness=0
        )
        self.terminal_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.terminal_text.config(yscrollcommand=text_scrollbar.set)
        text_scrollbar.config(command=self.terminal_text.yview)

        # Optional: Insert a welcome message or style more
        self.terminal_text.insert("end", "Welcome to your terminal!\n")

        self.terminal_text.config(state="disabled")

        self.show_frame(self.main_frame)

    def test_prompt_click(self):
        try:
            first_ad_path = self.validate_personal_letter(test=True)
            self.setup_test_prompt(first_ad_path)
        
        except ValueError as e:
            messagebox.showwarning("Invalid Configuration", str(e))
            return

    def setup_test_prompt(self,ad_path):
        with open(ad_path,encoding="utf-8") as f:
            ad_data = json.load(f)

        ad_headline = ad_data["headline"]
        ad_description = ad_data["description"]["text"]
        
        with open(self.config_values["system_prompt_path"],encoding="utf-8") as f:
            system_prompt_text = f.read()

        with open(self.config_values["about_me_path"],encoding="utf-8") as f:
            about_me_text = f.read()

        ai_caller = AICaller()

        message_builder = MessageBuilder()
        text_prepend_ad_data = "Here is the ad:\n"
        text_prepend_about_me_data = "This is the data about me:\n"

        message_builder.add_message(role="system",message=system_prompt_text)

        user_message = text_prepend_ad_data + ad_description + text_prepend_about_me_data + about_me_text

        message_builder.add_message(role="user",message=user_message)

        try:
            response = ai_caller.chat_openai(
                model=self.config_values["model"],
                messages=message_builder.messages,
                response_format=None,
                temperature=self.config_values["temperature"]
            )

            if self.config_values["credentials"]:
                with open(self.config_values["credentials"]) as f:
                    creds = f.read()
                response += response + creds
            
            filename = ad_headline + ".md"
            save_path = os.path.join(self.tests_path,filename)

            with open(save_path,'w',encoding="utf-8") as f:
                f.write(response)

            self.compare_texts(response,ad_data)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
                
    def compare_texts(self, response, ad_data):
        popup = tk.Toplevel(self.root)
        popup.title("Compare Ad vs Response")
        popup.geometry("900x500")

        # Configure grid layout for equal size
        popup.columnconfigure(0, weight=1, uniform="col")
        popup.columnconfigure(1, weight=1, uniform="col")
        popup.rowconfigure(1, weight=1)

        # Labels
        ad_label = tk.Label(popup, text="Job Ad", font=("Segoe UI", 12, "bold"))
        ad_label.grid(row=0, column=0, padx=8, pady=(8, 0), sticky="w")
        resp_label = tk.Label(popup, text="Response", font=("Segoe UI", 12, "bold"))
        resp_label.grid(row=0, column=1, padx=8, pady=(8, 0), sticky="w")

        # Ad Textarea (left)
        ad_text = scrolledtext.ScrolledText(popup, wrap="word", font=("Consolas", 11), bg="#1e293b", fg="#f1f5f9", insertbackground="#f1f5f9")
        ad_text.grid(row=1, column=0, sticky="nsew", padx=(8,4), pady=8)
        ad_text.insert("1.0", ad_data["description"]["text"])
        ad_text.config(state="disabled")  # Readonly

        # Response Textarea (right)
        resp_text = scrolledtext.ScrolledText(popup, wrap="word", font=("Consolas", 11), bg="#1e293b", fg="#f1f5f9", insertbackground="#f1f5f9")
        resp_text.grid(row=1, column=1, sticky="nsew", padx=(4,8), pady=8)
        resp_text.insert("1.0", response)
        resp_text.config(state="disabled")  # Readonly

    def init_preview_letters_frame(self):
        filetype = "letter"

        # Main frame, styled
        frame = self.style.frame(self.root)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=0)  # Button frame
        frame.columnconfigure(1, weight=1)  # Content frame
        frame.rowconfigure(0, weight=1)

        # Subframes
        button_frame = self.style.frame(frame)
        button_frame.grid(row=0, column=0, sticky="nsw", padx=(10, 20), pady=10)
        button_frame.columnconfigure(0, weight=1)

        letters_frame = self.style.frame(frame)
        letters_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        letters_frame.columnconfigure(0, weight=1)
        letters_frame.rowconfigure(0, weight=1)

        extended_regions = self.config_values["regions"].copy()
        if self.config_values["missing_regions"]:
            extended_regions.append("region_missing")

        # Styled buttons
        self.style.button(
            button_frame, text="Back", width=20, anchor="w", justify="left",
            command=self.back_to_main_frame_click
        ).grid(row=0, column=0, sticky="w", pady=(0, 5), padx=10)

        self.style.button(
            button_frame, text="Delete all", width=20, anchor="w", justify="left",
            command=lambda: self.delete_all_ids(filetype, self.processed_letters_path)
        ).grid(row=1, column=0, sticky="w", pady=(0, 5), padx=10)

        self.style.button(
            button_frame, text="Clear all sent ids", width=20, anchor="w", justify="left",
            command=lambda: self.clear_all_ids(filetype)
        ).grid(row=2, column=0, sticky="w", pady=(0, 5), padx=10)

        button_frame.rowconfigure(2, weight=1)

        self.render_preview_files(letters_frame, extended_regions, self.processed_letters_path, filetype)
        self.show_frame(frame)

    def init_preview_ads_frame(self):
        filetype = "ad"
        # Main styled frame
        frame = self.style.frame(self.root)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=0)  # Button frame
        frame.columnconfigure(1, weight=1)  # Content frame
        frame.rowconfigure(0, weight=1)

        # Subframes
        button_frame = self.style.frame(frame)
        button_frame.grid(row=0, column=0, sticky="nsw", padx=(10, 20), pady=10)
        button_frame.columnconfigure(0, weight=1)

        ads_frame = self.style.frame(frame)
        ads_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        ads_frame.columnconfigure(0, weight=1)
        ads_frame.rowconfigure(0, weight=1)

        allow_missing_region_var = tk.BooleanVar(value=self.config_values["missing_regions"])

        def on_missing_regions_toggle():
            save_data = {"missing_regions": allow_missing_region_var.get()}
            self.save_config_values(**save_data)
            self.init_preview_ads_frame()
            print("Switch is now", allow_missing_region_var.get())

        # Styled Checkbutton
        allow_missing_region_check = tk.Checkbutton(
            button_frame, text="Allow missing regions",
            variable=allow_missing_region_var,
            command=on_missing_regions_toggle,
            onvalue=True, offvalue=False,
            anchor="w", justify="left", width=20,
            bg=self.style.style_values["BG_COLOR"],
            fg=self.style.style_values["LABEL_FG"],
            selectcolor=self.style.style_values["BTN_BG"],
            font=self.style.style_values["FONT"],
            activebackground=self.style.style_values["BTN_ACTIVE_BG"],
            activeforeground=self.style.style_values["BTN_ACTIVE_FG"],
            highlightthickness=0
        )
        allow_missing_region_check.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.style.button(
            button_frame, text="Delete all ads", width=20,
            anchor="w", justify="left",
            command=lambda: self.delete_all_ids(filetype=filetype, folder_path=self.ads_path)
        ).grid(row=1, column=0, sticky="w", pady=(0, 5), padx=10)

        self.style.button(
            button_frame, text="Clear all processed ids", width=20,
            anchor="w", justify="left",
            command=lambda: self.clear_all_ids(filetype)
        ).grid(row=2, column=0, sticky="w", pady=(0, 5), padx=10)

        self.style.button(
            button_frame, text="Back", width=20,
            anchor="w", justify="left",
            command=self.back_to_main_frame_click
        ).grid(row=3, column=0, sticky="w", pady=(0, 5), padx=10)

        button_frame.rowconfigure(2, weight=1)

        # Content
        extended_regions = self.config_values["regions"].copy()
        if self.config_values["missing_regions"]:
            extended_regions.append("region_missing")

        self.render_preview_files(ads_frame, extended_regions, self.ads_path, filetype)
        self.show_frame(frame)

    def render_preview_files(self, parent_frame, regions, folder_path, file_type):
        # Remove old children
        for widget in parent_frame.winfo_children():
            widget.destroy()

        # Scrollable frame setup (canvas + vertical scrollbar)
        canvas = tk.Canvas(
            parent_frame, borderwidth=0, highlightthickness=0,
            bg=self.style.style_values["BG_COLOR"]
        )
        vscroll = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        vscroll.grid(row=0, column=1, sticky="ns")
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(0, weight=1)

        # The actual frame to put content in
        scrollable_frame = self.style.frame(canvas)
        window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Mousewheel scroll support
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        scrollable_frame.bind("<Enter>", lambda e: scrollable_frame.bind_all("<MouseWheel>", _on_mousewheel))
        scrollable_frame.bind("<Leave>", lambda e: scrollable_frame.unbind_all("<MouseWheel>"))

        # Keep the scroll region updated
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        scrollable_frame.bind("<Configure>", on_configure)

        # Determine file/ID set
        if file_type == "ad":
            valid_path = os.path.join(folder_path, "matched_email")
            ids = self.config_values["processed_ids"]
        elif file_type == "letter":
            valid_path = folder_path
            ids = self.config_values["sent_ids"]

        # No files found overall
        if not os.listdir(folder_path):
            self.style.label(
                scrollable_frame, text="No files found.", fg="gray"
            ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.adjust_window()
            return

        for region_index, region in enumerate(regions):
            region_path = os.path.join(valid_path, region)

            # Themed region frame
            region_frame = self.style.labelframe(scrollable_frame, region)
            region_frame.grid(row=region_index, column=0, sticky="ew", padx=5, pady=5)
            region_frame.columnconfigure(0, weight=1)
            region_frame.columnconfigure(1, weight=0)
            region_frame.columnconfigure(2, weight=0)
            region_frame.columnconfigure(3, weight=0)

            try:
                files = [f for f in os.listdir(region_path) if os.path.isfile(os.path.join(region_path, f))]
            except FileNotFoundError:
                continue

            if not files:
                self.style.label(region_frame, text="No files found.", fg="gray").grid(row=0, column=0, padx=5, pady=5, sticky="w")
                continue

            for idx, filename in enumerate(files):
                full_path = os.path.join(region_path, filename)
                file_label = self.style.label(region_frame, text=filename, anchor="w")
                file_label.grid(row=idx, column=0, padx=5, pady=2, sticky="ew")

                with open(full_path, encoding="utf-8") as file:
                    data = json.load(file)
                data_id = data.get("id")

                view_btn = self.style.button(
                    region_frame, text="View", width=8,
                    command=lambda f=full_path: self.view_file(f, file_type)
                )
                view_btn.grid(row=idx, column=1, padx=5, sticky="e")

                delete_btn = self.style.button(
                    region_frame, text="Delete", width=8,
                    command=lambda f=full_path: self.delete_file(f, parent_frame, regions, folder_path, file_type)
                )
                delete_btn.grid(row=idx, column=2, padx=5, sticky="e")

                # ID status label
                if data_id in ids:
                    check_label = self.style.label(
                        region_frame, text="Used ID \u2705", font=("Segoe UI Emoji", 14)
                    )
                else:
                    check_label = self.style.label(
                        region_frame, text="No used ID", font=("Segoe UI Emoji", 14)
                    )
                check_label.grid(row=idx, column=3)

        scrollable_frame.update_idletasks()
        frame_width = scrollable_frame.winfo_reqwidth()
        frame_height = scrollable_frame.winfo_reqheight()

        # Set the canvas width to match frame's requested width (for horizontal fill)
        canvas.config(width=frame_width)

        # Set the root window's geometry to match the scrollable_frame's width, capped at max screen width
        win_w = min(max(self.width, frame_width + 40), self.root.winfo_screenwidth())
        win_h = min(max(self.height, frame_height + 40), self.root.winfo_screenheight())
        self.root.geometry(f"{win_w}x{win_h}")

        self.adjust_window()

    def init_create_profile_frame(self):
    
        def refresh_profile_list():
            for widget in self.profile_list_frame.winfo_children():
                widget.destroy()

            profile_folders = [
                name for name in os.listdir(self.profiles_path)
                if os.path.isdir(os.path.join(self.profiles_path, name))
            ]

            # Select or clear selection
            if profile_folders:
                current = self.selected_profile_var.get()
                if current not in profile_folders:
                    self.selected_profile_var.set(profile_folders[0])
                    self.set_last_used_profile(profile_folders[0])
            else:
                self.selected_profile_var.set("")
                self.set_last_used_profile("")

            if not profile_folders:
                empty_label = self.style.label(self.profile_list_frame, text="(No profiles found)", fg="gray")
                empty_label.grid(row=0, column=0, padx=10, pady=5)
            else:
                for i, prof in enumerate(profile_folders):
                    rb = self.style.radiobutton(
                        self.profile_list_frame,
                        text=prof,
                        variable=self.selected_profile_var,
                        value=prof,
                        command=lambda: self.root.title(f"JetJob - Welcome {self.selected_profile_var.get()}")
                    )
                    rb.grid(row=i, column=0, sticky="w", padx=(2, 7), pady=4)
                  
                    del_btn = self.style.button(
                        self.profile_list_frame,
                        text="🗑 Delete",
                        fg="#ef4444",  # bright red for delete
                        command=lambda p=prof: delete_profile(p)
                    )

                    del_btn.grid(row=i, column=1, padx=(4, 0), pady=4)

            # Remove duplicate "Go to main" button if any
            for widget in left_frame.grid_slaves():
                if isinstance(widget, tk.Button) and widget["text"].startswith("Go to main"):
                    widget.destroy()
            if profile_folders:
                return_btn = self.style.button(left_frame, text="Go to main", width=20, command=on_return_click)
                return_btn.grid(row=3, column=0, columnspan=2, padx=5, pady=(24, 5), sticky="ew")

        def delete_profile(profile_name):
            folder_path = os.path.join(self.profiles_path, profile_name)
            try:
                confirm = messagebox.askyesno(title=f"Delete {profile_name}?", message=f"Are you sure you want to delete '{profile_name}'?")
                if confirm:
                    shutil.rmtree(folder_path)
                    print(f"Deleted profile: {profile_name}")
                    refresh_profile_list()
            except Exception as e:
                print(f"Error deleting {profile_name}: {e}")

        def on_add_click():
            name = name_var.get().strip()
            if not name:
                print("❌ Profile name is empty")
                return

            profile_dir = os.path.join(self.profiles_path, name)
            if os.path.exists(profile_dir):
                print("❌ Profile already exists")
                return

            self.config_values = {
                "url": "https://jobsearch.api.jobtechdev.se/search",
                "gmail": None,
                "keywords": [],
                "regions": [],
                "missing_regions": False,
                "limit": 10,
                "offset": 0,
                "model": "gpt-4.1",
                "temperature": 0.7,
                "about_me_path": None,
                "system_prompt_path": None,
                "credentials": None,
                "processed_ids": [],
                "sent_ids": [],
            }

            os.makedirs(profile_dir)
            with open(os.path.join(profile_dir, "config.json"), "w") as f:
                json.dump(self.config_values, f, indent=4)
            self.create_env_file(profile_dir=profile_dir)

            print(f"✅ Created profile: {name}")
            self.root.title(f"JetJob - Welcome {name}")
            self.set_last_used_profile(profile_name=name)
            self.selected_profile_var.set(name)
            name_var.set("")
            self.create_profile_subfolders(name)
            refresh_profile_list()

        def on_return_click():
            selected = self.selected_profile_var.get()
            if not selected:
                messagebox.showwarning("No Selection", "Please select a profile before continuing.")
                return
            self.selected_profile = selected
            self.set_last_used_profile(selected)
            self.create_profile_subfolders(selected)
            self.update_config()
            self.init_main_frame()
            self.show_frame(self.main_frame)

        self.selected_profile_var = tk.StringVar()

        # Main background frame
        self.create_profile_frame = self.style.frame(self.root)
        self.create_profile_frame.grid(row=0, column=0, sticky="nsew")
        self.create_profile_frame.columnconfigure((0, 1), weight=1)

        # Left: Create profile
        left_frame = self.style.frame(self.create_profile_frame)
        left_frame.grid(row=1, column=0, padx=36, pady=12, sticky="n")

        # Use bold/large label for title
        self.style.label(
            left_frame, text="Create a new profile",
            font=("Consolas", 15, "bold"), pady=10
        ).grid(row=0, column=0, columnspan=2, pady=(0, 16), padx=6, sticky="ew")

        name_var = tk.StringVar()
        self.style.label(left_frame, text="Name: ").grid(row=1, column=0, padx=(4, 8), pady=10, sticky="e")
        name_entry = self.style.entry(left_frame, textvariable=name_var, width=16)
        name_entry.grid(row=1, column=1, padx=(0, 6), pady=10, sticky="w")
        self.style.button(left_frame, text="Add profile", command=on_add_click).grid(
            row=2, column=0, columnspan=2, padx=8, pady=(10, 4), sticky="ew"
        )

        # Right: Select profile
        right_frame = self.style.frame(self.create_profile_frame)
        right_frame.grid(row=1, column=1, padx=36, pady=12, sticky="n")
        self.style.label(
            right_frame, text="Select Profile",
            font=("Consolas", 15, "bold"), pady=10
        ).grid(row=0, column=0, columnspan=2, pady=(0, 16), padx=6, sticky="ew")

        self.profile_list_frame = self.style.frame(right_frame)
        self.profile_list_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

        refresh_profile_list()
        self.show_frame(self.create_profile_frame)

    def init_config_env_frame(self):
        # Styled background frame
        self.config_env_frame = self.style.frame(self.root)
        self.config_env_frame.grid(row=0, column=0, sticky="nsew")
        self.config_env_frame.columnconfigure(0, weight=1)

        entries = {}
        env_path = os.path.join(self.profiles_path, self.selected_profile, ".env")

        # Load existing .env values (if file exists)
        env_values = {}
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        env_values[key] = value.strip('"')

        # Styled input with show/hide support
        def add_input(frame, label_text, var_name, masked=False):
            container = self.style.frame(frame)
            container.pack(fill="x", padx=6, pady=4)

            self.style.label(container, text=label_text).pack(side="left", padx=(2, 10))

            var = tk.StringVar(value=env_values.get(var_name, ""))
            entry = self.style.entry(container, textvariable=var, width=32)
            if masked:
                entry.config(show="*")
            entry.pack(side="left", padx=(0, 10), fill="x", expand=True)

            def toggle_visibility():
                if entry.cget("show") == "":
                    entry.config(show="*")
                    toggle_button.config(text="Show")
                else:
                    entry.config(show="")
                    toggle_button.config(text="Hide")

            if masked:
                toggle_button = self.style.button(
                    container, text="Show", width=6, command=toggle_visibility
                )
                toggle_button.pack(side="left", padx=(0, 2))

            entries[var_name] = entry

        # Section: OpenAI
        openai_frame = self.style.labelframe(self.config_env_frame, "OpenAI")
        openai_frame.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 4))
        add_input(openai_frame, "API Key:", "OPENAI_API_KEY", masked=True)

        # Section: Gmail
        gmail_app_pass_frame = self.style.labelframe(self.config_env_frame, "Gmail")
        gmail_app_pass_frame.grid(row=1, column=0, sticky="ew", padx=18, pady=4)
        add_input(gmail_app_pass_frame, "App Password:", "GMAIL_APP_PASSWORD", masked=True)

        # Save/Done button
        def on_done_click():
            lines = []
            for key, entry in entries.items():
                val = entry.get().strip()
                if " " in val:
                    val = f'"{val}"'
                lines.append(f"{key}={val}")

            with open(env_path, "w") as f:
                f.write("\n".join(lines))

            self.show_frame(self.main_frame)

        self.style.button(
            self.config_env_frame,
            text="Done",
            width=24,
            command=on_done_click
        ).grid(row=4, column=0, pady=18, padx=18, sticky="ew")

        self.show_frame(self.config_env_frame)

    def init_config_search_param_frame(self):
        # Use your styled frame
        self.config_search_param_frame = self.style.frame(self.root)
        self.config_search_param_frame.grid(row=0, column=0, sticky="nsew")
        self.config_search_param_frame.columnconfigure(1, weight=1)

        self.update_config()

        # URL row
        self.style.label(self.config_search_param_frame, text="URL").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        url_var = tk.StringVar(value=self.config_values.get("url", ""))
        self.style.entry(self.config_search_param_frame, textvariable=url_var, width=40).grid(row=0, column=1, padx=10, pady=10, sticky="we")

        # Gmail row
        self.style.label(self.config_search_param_frame, text="Gmail").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        gmail_var = tk.StringVar(value=self.config_values.get("gmail", ""))
        self.style.entry(self.config_search_param_frame, textvariable=gmail_var, width=40).grid(row=1, column=1, padx=10, pady=10, sticky="we")

        # Keywords
        self.style.label(self.config_search_param_frame, text="Keywords").grid(row=2, column=0, padx=10, pady=5, sticky="nw")
        keyword_var = tk.StringVar()
        self.style.entry(self.config_search_param_frame, textvariable=keyword_var, width=30).grid(row=2, column=1, padx=10, pady=(5, 0), sticky="w")

        # Keyword Listbox
        keyword_listbox = tk.Listbox(self.config_search_param_frame, height=6, width=30, selectmode="multiple",
                                    bg=self.style.style_values["TEXT_BG"], fg=self.style.style_values["TEXT_FG"],
                                    font=self.style.style_values["FONT"], selectbackground=self.style.style_values["BTN_BG"])
        keyword_listbox.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        for kw in self.config_values.get("keywords", []):
            keyword_listbox.insert("end", kw)

        # --- Regions Section ---
        self.style.label(self.config_search_param_frame, text="Regions").grid(row=4, column=0, padx=10, pady=5, sticky="nw")
        region_listbox_frame = self.style.frame(self.config_search_param_frame)
        region_listbox_frame.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        # Listbox
        region_box = tk.Listbox(region_listbox_frame, selectmode="multiple", height=10, exportselection=False,
                                bg=self.style.style_values["TEXT_BG"], fg=self.style.style_values["TEXT_FG"],
                                font=self.style.style_values["FONT"], selectbackground=self.style.style_values["BTN_BG"])
        region_box.grid(row=0, column=0, sticky="ns")

        # Scrollbar
        region_scrollbar = tk.Scrollbar(region_listbox_frame, orient="vertical", command=region_box.yview)
        region_scrollbar.grid(row=0, column=1, sticky="ns")
        region_box.config(yscrollcommand=region_scrollbar.set)

        for region in self.regions:
            region_box.insert(tk.END, region)
        selected_regions = self.config_values.get("regions", [])
        for idx, region in enumerate(self.regions):
            if region in selected_regions:
                region_box.selection_set(idx)

        # Region select/clear all buttons
        region_button_frame = self.style.frame(self.config_search_param_frame)
        region_button_frame.grid(row=4, column=2, padx=10, pady=5, sticky="n")
        self.style.button(region_button_frame, text="Select All",
                        command=lambda: region_box.select_set(0, tk.END)).grid(row=0, column=0, pady=(0, 10), sticky="ew")
        self.style.button(region_button_frame, text="Clear All",
                        command=lambda: region_box.selection_clear(0, tk.END)).grid(row=1, column=0, sticky="ew")

        # Add + Delete keyword buttons
        def add_keyword():
            word = keyword_var.get().strip()
            if word and word not in keyword_listbox.get(0, "end"):
                keyword_listbox.insert("end", word)
            keyword_var.set("")

        def delete_selected():
            for i in reversed(keyword_listbox.curselection()):
                keyword_listbox.delete(i)

        self.style.button(self.config_search_param_frame, text="Add", command=add_keyword).grid(row=2, column=2, padx=5, pady=(5, 0))
        self.style.button(self.config_search_param_frame, text="Delete", command=delete_selected).grid(row=3, column=2, padx=5, pady=5)

        # LIMIT Slider (1–100)
        self.style.label(self.config_search_param_frame, text="Limit").grid(row=5, column=0, padx=10, pady=10, sticky="w")
        limit_var = tk.IntVar(value=self.config_values.get("limit", 10))
        limit_slider = tk.Scale(self.config_search_param_frame, from_=1, to=100, orient="horizontal",
                                variable=limit_var, resolution=1,
                                bg=self.style.style_values["BG_COLOR"],
                                fg=self.style.style_values["LABEL_FG"],
                                troughcolor=self.style.style_values["BTN_BG"],
                                highlightthickness=0)
        limit_slider.grid(row=5, column=1, padx=10, pady=10, sticky="w")

        # OFFSET Slider (0–500 default range)
        self.style.label(self.config_search_param_frame, text="Offset").grid(row=6, column=0, padx=10, pady=10, sticky="w")
        offset_var = tk.IntVar(value=self.config_values.get("offset", 0))
        offset_slider = tk.Scale(self.config_search_param_frame, from_=0, to=500, orient="horizontal",
                                variable=offset_var, resolution=1,
                                bg=self.style.style_values["BG_COLOR"],
                                fg=self.style.style_values["LABEL_FG"],
                                troughcolor=self.style.style_values["BTN_BG"],
                                highlightthickness=0)
        offset_slider.grid(row=6, column=1, padx=10, pady=10, sticky="w")

        allow_missing_region_var = tk.BooleanVar(value=self.config_values["missing_regions"])

        def on_missing_regions_toggle():
            save_data = {"missing_regions": allow_missing_region_var.get()}
            self.save_config_values(**save_data)
            print("Switch is now", allow_missing_region_var.get())

        # Styled checkbutton (needs manual styling for bg/fg in tkinter)
        allow_missing_region_check = tk.Checkbutton(
            self.config_search_param_frame, text="Allow missing regions",
            variable=allow_missing_region_var,
            command=on_missing_regions_toggle,
            onvalue=True, offvalue=False,
            anchor="w", justify="left", width=20,
            bg=self.style.style_values["BG_COLOR"],
            fg=self.style.style_values["LABEL_FG"],
            selectcolor=self.style.style_values["BTN_BG"],
            font=self.style.style_values["FONT"],
            activebackground=self.style.style_values["BTN_ACTIVE_BG"],
            activeforeground=self.style.style_values["BTN_ACTIVE_FG"],
            highlightthickness=0
        )
        allow_missing_region_check.grid(row=7, column=0, pady=10, padx=10, sticky="we")

        def on_done_click():
            selected_indices = region_box.curselection()
            selected_regions = [self.regions[i] for i in selected_indices]

            # update config values
            save_data = {
                "url": url_var.get(),
                "gmail": gmail_var.get(),
                "keywords": keyword_listbox.get(0, "end"),
                "regions": selected_regions,
                "limit": limit_var.get(),
                "offset": offset_var.get(),
            }
            self.save_config_values(**save_data)
            self.show_frame(self.main_frame)

        # Save Button
        self.style.button(self.config_search_param_frame, text="Done", command=on_done_click).grid(
            row=8, column=0, pady=10, padx=10, sticky="we"
        )

        self.adjust_window()
        self.show_frame(self.config_search_param_frame)

    def init_data_files_frame(self):
        style = self.style_values  # for easy use

        # Main frame
        data_files_frame = tk.Frame(
            self.root,
            bg=style["BG_COLOR"]
        )
        data_files_frame.grid(row=0, column=0, sticky="nsew")
        data_files_frame.columnconfigure(0, weight=1)

        # Title label
        label = tk.Label(
            data_files_frame,
            text="Manage System Prompts, Attachment Files, and More!",
            font=(style["FONT"][0], 16, "bold"),
            fg=style["LABEL_FG"],
            bg=style["BG_COLOR"],
            pady=14
        )
        label.grid(row=0, column=0, sticky="ew", padx=10, pady=(14, 6))

        def select_file_click(title, keyword, initial_dir):
            selected_file = filedialog.askopenfilename(
                title=title,
                initialdir=initial_dir,
                filetypes=[("Text or Markdown files", "*.txt *.md")]
            )
            if selected_file:
                save_data = {keyword: selected_file}
                self.save_config_values(**save_data)
                print("✅ Config saved")

        def add_files_click():
            selected_files = filedialog.askopenfilenames(
                title="Select data files for mail attachment (CV, grades, etc)",
                initialdir=self.attachement_files_path,
                filetypes=[("All files", "*.*")]
            )
            if selected_files:
                save_data = {"attachment_files": selected_files}
                self.save_config_values(**save_data)
                print("✅ Config saved")

        # Helper to style LabelFrame title color
        def styled_labelframe(parent, text):
            lf = tk.LabelFrame(
                parent,
                text=text,
                bg=style["BG_COLOR"],
                fg=style["LABEL_FG"],
                font=(style["FONT"][0], 13, "bold"),
                bd=2,
                relief="ridge",
                labelanchor="nw",
                padx=12, pady=8
            )
            return lf

        # Helper for styled button
        def styled_button(parent, **kwargs):
            return tk.Button(
                parent,
                font=style["BTN_FONT"],
                bg=style["BTN_BG"],
                fg=style["BTN_FG"],
                activebackground=style["BTN_ACTIVE_BG"],
                activeforeground=style["BTN_ACTIVE_FG"],
                relief="flat",
                cursor="hand2",
                bd=0,
                highlightthickness=0,
                pady=6, padx=8,
                **kwargs
            )

        # System Prompt frame
        system_prompt_frame = styled_labelframe(data_files_frame, "System Prompt")
        system_prompt_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(5, 0))
        system_prompt_frame.columnconfigure((0, 1), weight=1)

        styled_button(
            system_prompt_frame,
            text="Select Premade Prompt",
            command=lambda: select_file_click("Select System Prompt", "system_prompt_path", self.prompts_path)
        ).grid(row=0, column=0, padx=6, pady=6, sticky="ew")

        styled_button(
            system_prompt_frame,
            text="Create New Prompt",
            command=lambda: self.create_text_click(self.prompts_path, "Create new System prompt")
        ).grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        # Attachment Files Frame
        attachment_files_frame = styled_labelframe(data_files_frame, "Attachment Files")
        attachment_files_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(8, 0))
        styled_button(
            attachment_files_frame,
            text="Add Attachment File(s)",
            command=add_files_click
        ).grid(row=0, column=0, padx=6, pady=6, sticky="ew")

        # About Me Frame
        about_me_frame = styled_labelframe(data_files_frame, "About Me")
        about_me_frame.grid(row=3, column=0, sticky="ew", padx=16, pady=(8, 0))
        about_me_frame.columnconfigure((0, 1), weight=1)
        styled_button(
            about_me_frame,
            text="Select 'About Me' Text",
            command=lambda: select_file_click("About me text", "about_me_path", self.about_me_path)
        ).grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        styled_button(
            about_me_frame,
            text="Add 'About Me' Text",
            command=lambda: self.create_text_click(self.about_me_path, "About me text")
        ).grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        # Credentials Frame
        credentials_frame = styled_labelframe(data_files_frame, "Credentials")
        credentials_frame.grid(row=4, column=0, sticky="ew", padx=16, pady=(8, 0))
        credentials_frame.columnconfigure((0, 1), weight=1)
        styled_button(
            credentials_frame,
            text="Create New Credential File",
            command=lambda: self.create_text_click(self.credentials_path, "Credentials")
        ).grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        styled_button(
            credentials_frame,
            text="Select a Credential File",
            command=lambda: select_file_click("Credentials text", "credentials", self.credentials_path)
        ).grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        # Back Button
        styled_button(
            data_files_frame,
            text="⟵ Back",
            command=lambda: self.show_frame(self.main_frame)
        ).grid(row=5, column=0, padx=16, pady=(18, 16), sticky="w")

        self.adjust_window()
        self.show_frame(data_files_frame)

    def init_gpt_config_frame(self):
        gpt_config_frame = self.style.frame(self.root)
        gpt_config_frame.grid(row=0, column=0, sticky="nsew")
        gpt_config_frame.columnconfigure(0, weight=1)

        # --- OpenAI Model Frame ---
        models_frame = self.style.labelframe(gpt_config_frame, "OpenAI Models")
        models_frame.grid(row=0, column=0, sticky="news", padx=18, pady=18)

        # Scrollbar for the listbox
        model_scrollbar = tk.Scrollbar(models_frame)
        model_scrollbar.grid(row=0, column=1, sticky="nsw", padx=(8, 0), pady=4)

        # Listbox (styled)
        listbox = tk.Listbox(
            models_frame,
            selectmode="single",
            font=self.style.style_values["FONT"],
            height=min(8, len(self.models)),
            activestyle="dotbox",
            bd=2,
            yscrollcommand=model_scrollbar.set,
            bg=self.style.style_values["TEXT_BG"],
            fg=self.style.style_values["TEXT_FG"],
            selectbackground=self.style.style_values["BTN_BG"],
            highlightthickness=0,
            relief="solid"
        )
        for item in self.models:
            listbox.insert(tk.END, item)
        if self.config_values["model"] in self.models:
            idx = self.models.index(self.config_values["model"])
            listbox.selection_set(idx)
            listbox.activate(idx)
            listbox.see(idx)
        listbox.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=4)
        model_scrollbar.config(command=listbox.yview)
        models_frame.columnconfigure(0, weight=1)
        models_frame.rowconfigure(0, weight=1)

        # --- Select Button ---
        def on_select_model_click():
            selected = listbox.curselection()
            if selected:
                index = selected[0]
                model_str = listbox.get(index)
                save_data = {"model": model_str}
                self.save_config_values(**save_data)
                print(self.config_values["model"])

        self.style.button(
            models_frame,
            text="Select",
            command=on_select_model_click
        ).grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=(12, 4))

        # --- Temperature Slider ---
        temp_frame = self.style.labelframe(gpt_config_frame, "Temperature")
        temp_frame.grid(row=1, column=0, pady=4, padx=18, sticky="ew")

        def on_slider(val):
            value_label.config(text=f"Value: {float(val):.1f}")

        slider = tk.Scale(
            temp_frame,
            from_=0.0,
            to=2.0,
            resolution=0.1,
            orient="horizontal",
            length=300,
            command=on_slider,
            showvalue=False,
            bg=self.style.style_values["BG_COLOR"],
            fg=self.style.style_values["LABEL_FG"],
            troughcolor=self.style.style_values["BTN_BG"],
            highlightthickness=0
        )
        slider.pack(fill="x", pady=(8, 2))
        slider.set(self.config_values["temperature"])

        value_label = self.style.label(
            temp_frame, text=f"Value: {self.config_values['temperature']:.1f}"
        )
        value_label.pack(anchor="w", pady=(2, 0))

        # --- Done Button ---
        def on_done_click():
            save_data = {
                "temperature": slider.get()
            }
            self.save_config_values(**save_data)
            self.show_frame(self.main_frame)

        self.style.button(
            gpt_config_frame, text="Done", width=20, command=on_done_click
        ).grid(row=2, column=0, pady=18, padx=10, sticky="ew")

        self.show_frame(gpt_config_frame)

    def create_text_click(self,save_dir,title):
        def save_prompt():
            filename = filename_var.get().strip()
            extension = extension_var.get()
            content = text_area.get("1.0", tk.END).strip()

            if not filename:
                tk.messagebox.showwarning("Missing filename", "Please enter a filename.")
                return
            if not content:
                tk.messagebox.showwarning("Empty prompt", "Please enter some prompt content.")
                return

            # Ensure extension is correct
            if not filename.endswith(extension):
                filename += extension

            # Save path — change as needed
            os.makedirs(save_dir, exist_ok=True)
            full_path = os.path.join(save_dir, filename)

            try:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
                tk.messagebox.showinfo("Success", f"Saved to:\n{full_path}")
                popup.destroy()
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to save file:\n{e}")

        # --- UI ---
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry("600x500")

        # Filename Entry
        filename_label = tk.Label(popup, text="Filename:")
        filename_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        filename_var = tk.StringVar()
        filename_entry = tk.Entry(popup, textvariable=filename_var, width=40)
        filename_entry.grid(row=0, column=1, padx=5, pady=10, sticky="w")

        # Extension toggle
        extension_var = tk.StringVar(value=".txt")
        extension_menu = tk.OptionMenu(popup, extension_var, ".txt", ".md")
        extension_menu.grid(row=0, column=2, padx=5, pady=10, sticky="w")

        # Text Area
        text_area = tk.Text(popup, wrap="word")
        text_area.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Configure grid for resizing
        popup.columnconfigure(1, weight=1)
        popup.rowconfigure(1, weight=1)

        # Save Button
        save_button = tk.Button(popup, text="Save Prompt", command=save_prompt)
        save_button.grid(row=2, column=0, columnspan=3, pady=10)

    def create_menu(self):
        self.menubar = tk.Menu(self.root)

        self.menubar.add_command(label="Profiles", command=self.init_create_profile_frame)

        # env file creation and config
        self.menubar.add_command(label=".env config", command=self.init_config_env_frame)

        # search param config
        self.menubar.add_command(label="Search Parameter config", command=self.init_config_search_param_frame)

        # Data files
        self.menubar.add_command(label="Data files",command=self.init_data_files_frame)

        # gpt- config
        self.menubar.add_command(label="Gpt config",command=self.init_gpt_config_frame)

        # help (ReadMe link)
        self.menubar.add_command(label="Help",command=self.load_readme)

    def load_readme(self):
        readme_path = os.path.join(os.getcwd(), "readme.md")
        if not os.path.isfile(readme_path):
            messagebox.showinfo("Not Found", "No readme.md file found in the root directory.")
            return

        # Read the readme file
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Create a popup window (Toplevel)
        top = tk.Toplevel(self.root)
        top.title("README.md")
        top.geometry("800x600")  # Large window

        # Scrollbar + Text widget setup
        text_frame = tk.Frame(top)
        text_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        text_area = tk.Text(
            text_frame,
            wrap="word",
            yscrollcommand=scrollbar.set,
            font=("Consolas", 12)
        )
        text_area.insert("1.0", content)
        text_area.config(state="disabled")  # Read-only
        text_area.pack(fill="both", expand=True)

        scrollbar.config(command=text_area.yview)

    def show_frame(self, frame):
        frame.tkraise()

        if frame == self.main_frame:
            self.root.config(menu=self.menubar)
        else:
            self.root.config(menu="")

    def get_last_used_profile(self):
        path = os.path.join(self.profiles_path, "last_used.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                return data.get("last")
        return None

    def set_last_used_profile(self, profile_name):
        path = os.path.join(self.profiles_path, "last_used.json")
        with open(path, "w") as f:
            json.dump({"last": profile_name}, f)

    def has_valid_profiles(self):
        for name in os.listdir(self.profiles_path):
            profile_path = os.path.join(self.profiles_path, name)
            if os.path.isdir(profile_path):
                has_config = os.path.isfile(os.path.join(profile_path, "config.json"))
                has_env = os.path.isfile(os.path.join(profile_path, ".env"))
                if has_config and has_env:
                    return True  # At least one valid profile found
        return False  # No valid profiles found

    def create_env_file(self, profile_dir):
        with open(os.path.join(profile_dir, ".env"), "w") as f:
                f.write(f"OPENAI_API_KEY=\n")
                f.write(f"GMAIL_APP_PASSWORD=\n")

    def adjust_window(self):
        # Set window size to 50% of screen
        self.width = int(self.root.winfo_screenwidth() *self.screen_width)
        self.height = int(self.root.winfo_screenheight() *self.screen_height)
        self.root.geometry(f"{self.width}x{self.height}")

        self.center_window(self.root, self.width, self.height)

        # adjust size to fit all widgets
        self.root.update_idletasks()      

        req_w = self.root.winfo_reqwidth()
        req_h = self.root.winfo_reqheight()
        scr_w = self.root.winfo_screenwidth()
        scr_h = self.root.winfo_screenheight()
        margin = 20                               
    
        win_w = min(max(self.width,  req_w + margin), scr_w)
        win_h = min(max(self.height, req_h + margin), scr_h)

        self.root.geometry(f"{win_w}x{win_h}")

    def center_window(self,window, width, height):
        # Get screen width and height
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Calculate position x, y
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        window.geometry(f"{width}x{height}+{x}+{y}")

    def create_profile_subfolders(self,name):
        # system prompts
        self.prompts_path = os.path.join(self.profiles_path,name,"prompts")
        os.makedirs(self.prompts_path,exist_ok=True)

        # ads
        self.ads_path = os.path.join(self.profiles_path,name,"ads")
        os.makedirs(self.ads_path,exist_ok=True)

        # processed letters (personliga brev)
        self.processed_letters_path = os.path.join(self.profiles_path,name,"processed_letters")
        os.makedirs(self.processed_letters_path,exist_ok=True)

        # attachement files (CV,pictures, others)
        self.attachement_files_path = os.path.join(self.profiles_path,name,"attachement_files")
        os.makedirs(self.attachement_files_path,exist_ok=True)

        # about me text 
        self.about_me_path = os.path.join(self.profiles_path,name,"about_me")
        os.makedirs(self.about_me_path,exist_ok=True)

        # credentials text
        self.credentials_path = os.path.join(self.profiles_path,name,"credentials")
        os.makedirs(self.credentials_path,exist_ok=True)

        # test folder
        self.tests_path = os.path.join(self.profiles_path,name,"tests")
        os.makedirs(self.tests_path,exist_ok=True)

    def save_config_values(self,**kwargs):
        for key,value in kwargs.items():
            self.config_values[key] = value

        with open(self.config_path, "w",encoding="utf-8") as f:
                json.dump(self.config_values, f, indent=4, ensure_ascii=False)
        print("✅ Config saved")
            
    def update_config(self):
        self.config_values, self.config_path = self.load_config_values()

    def load_config_values(self) -> tuple[dict,str]:
        config_path = os.path.join(self.profiles_path, self.selected_profile, "config.json")
        if os.path.exists(config_path):
            with open(config_path,encoding="utf-8") as f:
                config_values = json.load(f)           
        else:
            config_values = {}

        return config_values ,config_path
    
    def setup_personal_letter_payload(self): 
        # paths
        folder_path = os.path.join(self.ads_path,"matched_email")
        system_prompt_path = self.config_values["system_prompt_path"]
        about_me_path = self.config_values["about_me_path"]

        text_prepend_ad_data = "Here is the ad:\n"
        text_prepend_about_me_data = "This is the data about me:\n"

        ai_caller = AICaller()

        with open(system_prompt_path, encoding="utf-8") as f:
            system_prompt = f.read()

        with open(about_me_path, encoding="utf-8") as f:
            about_me_data = f.read()
        
        extended_regions = self.config_values["regions"].copy()
        if self.config_values["missing_regions"]:
            extended_regions.append("region_missing")
          
        for region in extended_regions:
            region_path = os.path.join(folder_path, region)
            for ad in os.listdir(region_path):
                ad_meta_data = {}
                message_builder = MessageBuilder()
                message_builder.add_message(role="system",message=system_prompt)
                message_builder.add_message(role="user",message=text_prepend_about_me_data+about_me_data)

                full_path = os.path.join(region_path, ad)
                with open(full_path, encoding="utf-8") as f:
                    ad_data = json.load(f)

                ad_id = ad_data["id"]
                if ad_id in self.config_values["processed_ids"]:
                    print("this ad already been processed by gpt")
                    continue

                ad_headline = ad_data["headline"]
                
                # new
                ad_headline = sanitize_filename(ad_headline)

                description = ad_data["description"]["text"]
                application_deadline = ad_data["application_deadline"]
                email = self.find_relevant_email(ad=ad_data)
                message_builder.add_message(role="user",message=text_prepend_ad_data+description)

                response = ai_caller.chat_openai(
                    model=self.config_values["model"],
                    messages=message_builder.messages,
                    temperature=self.config_values["temperature"],
                    response_format=None
                )

                message_builder.reset_messages()


                filename = ad_headline+".json"
                save_region_path = os.path.join(self.processed_letters_path,region)
                os.makedirs(save_region_path,exist_ok=True)

                save_path = os.path.join(save_region_path,filename)

                # new 
                save_path = get_unique_path(save_path)
               
                ad_meta_data["id"] = ad_id
                ad_meta_data["text"] = response
                ad_meta_data["email"] = email     
                ad_meta_data["application_deadline"] = application_deadline
                ad_meta_data["path"] = save_path
                ad_meta_data["region"] = region
                ad_meta_data["headline"] = ad_headline

                with open(save_path,'w',encoding="utf-8") as f:
                    json.dump(ad_meta_data,f,indent=4,ensure_ascii=False)

                self.config_values["processed_ids"].append(ad_id)
                print(f"ads pre-processed and saved at {save_path}")
        
        save_data = {"processed_ids":self.config_values["processed_ids"]}
        self.save_config_values(**save_data)
        
    def validate_personal_letter(self,test:bool) -> str:

        if not self.config_values["system_prompt_path"]:
            raise ValueError("no system prompt detected")
        
        if not self.config_values["about_me_path"]:
            raise ValueError("no 'about me' file detected")  
        
        # ask if user wants a final string appended to letter
        if not self.config_values["credentials"]:
            confirm = messagebox.askyesno("No final string added to letter/mail. Do you want to proceed?")
            if confirm:
                pass
            else:
                return
        
        if not test:
            folder_path = os.path.join(self.ads_path,"matched_email")
            if not os.path.isdir(folder_path):
                raise ValueError("no matched ads folder exists, please make an ad search")
                
            json_files = []
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith('.json'):
                        json_files.append(os.path.join(root, file))
            
            if not json_files:
                raise ValueError("no valid json ads found, please make an ad search")
            
        else:
            # any first ad for testing exists
            json_files = []
            for root, dirs, files in os.walk(self.ads_path):
                for file in files:
                    if file.lower().endswith('.json'):
                        json_files.append(os.path.join(root, file))
            
            if not json_files:
                raise ValueError("no valid json ads found, please make an ad search")
            return json_files[0]
        
    def validate_send_email(self):
        # check gmail
        if not self.config_values["gmail"].strip().lower().endswith('@gmail.com'):
            raise ValueError("email must be a gmail!")
        
        # check gmail app pass
        env_path = os.path.join(self.profiles_path,self.selected_profile,".env")
        load_dotenv(dotenv_path=env_path, override=True)
        if not os.getenv("GMAIL_APP_PASSWORD"):
            raise ValueError("gmail app password is missing!")

        # check if there exists letters to send
        if not os.listdir(self.processed_letters_path):
            raise FileNotFoundError("no processed letters found")
        
        # ask if user wants a to send some attachment files such as CV
        if not self.config_values["attachment_files"]:
            confirm = messagebox.askyesno("No attachment files added to letter/mail. Do you want to proceed?")
            if confirm:
                pass
            else:
                return
         
    def validate_search_values(self):
        if self.config_values["url"] != "https://jobsearch.api.jobtechdev.se/search":
            raise ValueError(f"url is not valid: {self.config_values["url"]}")
        if not self.config_values["keywords"] or not self.config_values["regions"]:
            raise ValueError(f"regions or keywords parameter is empty")       
        if not self.ads_path:
            raise ValueError(f"save path missing {self.ads_path}") 
        
    def find_relevant_email(self, ad) -> str:
        # Helper to extract email from dict or list of dicts
        def extract_email(section):
            if isinstance(section, dict):
                return section.get("email")
            elif isinstance(section, list):
                for item in section:
                    if isinstance(item, dict) and item.get("email"):
                        return item["email"]
            return None

        # Try each section in order
        for key in ["application_contacts", "application_details", "employer"]:
            email = extract_email(ad.get(key))
            if email:
                return email

        raise ValueError("No email found")

    def mass_send_email(self):
        if self.config_values["credentials"]:
            with open(self.config_values["credentials"]) as f:
                final_string = f.read()
        else:
            final_string =""

        extended_regions = self.config_values["regions"].copy()
        if self.config_values["missing_regions"]:
            extended_regions.append("region_missing")

    
        sent_ids = set(self.config_values.get("sent_ids", []))
        found_any_letters = False

    
        for region in extended_regions:
            region_path = os.path.join(self.processed_letters_path,region)

            if not os.path.isdir(region_path):
                continue  

            letter_files = os.listdir(region_path)
            if not letter_files:
                continue  # No letters in this region

            for letter in letter_files:
                found_any_letters = True
                full_path = os.path.join(region_path,letter)
                with open(full_path,encoding="utf-8") as f:
                    letter_data = json.load(f)

                letter_id = letter_data.get("id")

                if letter_id in sent_ids:
                    self.terminal_text.config(state="normal")
                    self.terminal_text.insert("end", f"letter id {letter_data['id']} has ALREADY been sent, please clear id for new sending\n")
                    self.terminal_text.config(state="disabled")
                    continue

                text = letter_data["text"] + f"\n\n{final_string}"

                env_path = os.path.join(self.profiles_path,self.selected_profile,".env")
                
                load_dotenv(dotenv_path=env_path, override=True)
                
                send_email(
                    subject=letter_data["headline"],
                    body=text,
                    to_email=letter_data["email"],
                    from_email=self.config_values["gmail"],
                    password=os.getenv("GMAIL_APP_PASSWORD"),
                    attachments=self.config_values["attachment_files"]
                )


                sent_ids.add(letter_data["id"])

                self.terminal_text.config(state="normal")
                self.terminal_text.insert("end", f"letter {letter_data['headline']} has been sent to {letter_data['email']}\n")
                self.terminal_text.config(state="disabled")

        if not found_any_letters:
            raise FileNotFoundError("No letters found in any region folder.")
    
        save_data = {"sent_ids": list(sent_ids)}
        self.save_config_values(**save_data)
    
    def show_large_warning(self, message, title="Warning"):
        warning_win = tk.Toplevel(self.root)
        warning_win.title(title)
        warning_win.geometry("500x300")

        frame = tk.Frame(warning_win)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        text_area = tk.Text(frame, wrap="word", yscrollcommand=scrollbar.set, font=("Arial", 11))
        text_area.insert("1.0", message)
        text_area.config(state="disabled", bg="#fff6f6", fg="#a60000")
        text_area.pack(fill="both", expand=True)

        scrollbar.config(command=text_area.yview)

        # Optional: Close button
        close_btn = tk.Button(warning_win, text="Close", command=warning_win.destroy)
        close_btn.pack(pady=6)

    def back_to_main_frame_click(self):
            self.show_frame(self.main_frame)

    def delete_all_ids(self,filetype,folder_path):
        confirm = messagebox.askyesno(f"Confirm Delete all {filetype}?")
        if confirm:
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # remove file or symlink
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # remove subfolder and all its conten
            self.show_frame(self.main_frame)

    def clear_all_ids(self,filetype):
        if filetype == "ads":
            self.save_config_values(**{"processed_ids":[]})
            self.init_preview_ads_frame()
        elif filetype == "letters":
            self.save_config_values(**{"sent_ids":[]})
            self.init_preview_letters_frame()

    def view_file(self,filepath,filetype):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        popup = tk.Toplevel(self.root)
        popup.title(f"Viewing: {os.path.basename(filepath)}")
        text_area = tk.Text(popup, wrap="word")


        if filetype == "ad":
            content = data["description"]["text"]

        elif filetype == "letter":
            content = data["text"]
            info_frame = tk.Frame(popup)
            info_frame.pack()
            for key,value in data.items():
                if key != "text":
                    label = tk.Label(info_frame,text=f"{key}: {value}")
                    label.pack()

        else:
            self.show_large_warning(message="no valid filetype")
            return

        
        text_area.insert("1.0", content)
        text_area.pack(expand=True, fill="both")
        text_area.config(state="disabled")

    def delete_file(self,filepath,frame,regions,folder_path,file_type):
        confirm = messagebox.askyesno("Confirm Delete", f"Delete {os.path.basename(filepath)}?")
        if confirm:
            os.remove(filepath)
            self.render_preview_files(frame,regions,folder_path,file_type)

    def select_file(self,title,filetypes:list[tuple[str]],keyword,initialdir):
        selected_file = filedialog.askopenfilename(
            title=title,
            filetypes=filetypes,
            initialdir=initialdir
        )
        if selected_file:
            save_data = {keyword: selected_file}
            self.save_config_values(**save_data)
            print("✅ Config saved")



if __name__ == '__main__':
    producer = JetJob(screen_height=0.35,screen_width=0.3)
    producer.root.mainloop()
    
