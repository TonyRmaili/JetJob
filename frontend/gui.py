import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import json
from backend.ai_caller import AICaller
from backend.message_builder import MessageBuilder
from api.send_email import send_email
from api.searcher import search_ads


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

        self.create_menu()

        # paths
        self.profiles_path = "./profiles"
        os.makedirs(self.profiles_path,exist_ok=True)


        if not self.has_valid_profiles():
            self.selected_profile = None
            self.main_frame = None
            self.init_create_profile_frame()
            self.show_frame(self.create_profile_frame)

        else:
            self.selected_profile = self.get_last_used_profile()
            self.init_main_frame()
            self.show_frame(self.main_frame)
           

        # gpt models
        self.models = ["gpt-4o", "gpt-4o-mini","gpt-4.1"]

        self.regions = ["Blekinge",
                        "Dalarnas",
                        "Gotlands", 
                        "Gävleborgs", 
                        "Hallands", 
                        "Jämtlands", 
                        "Jönköpings", 
                        "Kalmar", 
                        "Kronobergs", 
                        "Norrbottens", 
                        "Skåne", 
                        "Stockholms", 
                        "Södermanlands", 
                        "Uppsala", 
                        "Värmlands", 
                        "Västerbottens", 
                        "Västernorrlands", 
                        "Västmanlands",
                        "Västra Götalands", 
                        "Örebro", 
                        "Östergötlands" 
                    ]


        # selected variables
        self.selected_system_prompt_file = None
        self.selected_data_files = []
        self.output_folder = None
        self.output_filename = None

        self.adjust_window()


    def init_main_frame(self):
        valid_folder_path = os.path.join(self.profiles_path,self.selected_profile,"responses/valid")

        def on_search():
            pass  

        def refresh_file_list():
            # Clear previous widgets in right_frame
            for widget in right_frame.winfo_children():
                widget.destroy()

            if not os.path.exists(valid_folder_path):
                os.makedirs(valid_folder_path)

            files = [f for f in os.listdir(valid_folder_path) if os.path.isfile(os.path.join(valid_folder_path, f))]

            if not files:
                no_files_label = tk.Label(right_frame, text="No files found.", fg="gray")
                no_files_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
                return

            for idx, filename in enumerate(files):
                full_path = os.path.join(valid_folder_path, filename)

                # File label
                file_label = tk.Label(right_frame, text=filename, anchor="w")
                file_label.grid(row=idx, column=0, sticky="w", padx=5, pady=2)

                # View button
                view_btn = tk.Button(right_frame, text="View", width=8,
                                    command=lambda f=full_path: view_file(f))
                view_btn.grid(row=idx, column=1, padx=5)

                # Delete button
                delete_btn = tk.Button(right_frame, text="Delete", width=8,
                                    command=lambda f=full_path: delete_file(f))
                delete_btn.grid(row=idx, column=2, padx=5)

        def view_file(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            popup = tk.Toplevel(self.root)
            popup.title(f"Viewing: {os.path.basename(filepath)}")
            text_area = tk.Text(popup, wrap="word")
            text_area.insert("1.0", content)
            text_area.pack(expand=True, fill="both")
            text_area.config(state="disabled")

        def delete_file(filepath):
            confirm = messagebox.askyesno("Confirm Delete", f"Delete {os.path.basename(filepath)}?")
            if confirm:
                os.remove(filepath)
                refresh_file_list()

        # Main UI setup
        self.main_frame = tk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        left_frame = tk.LabelFrame(self.main_frame, text="Buttons")
        left_frame.grid(row=0, column=0, sticky="nsw")

        right_frame = tk.LabelFrame(self.main_frame, text="Responses")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_frame.columnconfigure(0, weight=1)

        search_btn = tk.Button(left_frame, text="Search", command=on_search, width=10)
        search_btn.grid(row=0, column=0, padx=10, pady=10)

        self.show_frame(self.main_frame)
        refresh_file_list()

        
    def init_create_profile_frame(self):
        def refresh_profile_list():
            for widget in self.profile_list_frame.winfo_children():
                widget.destroy()

            profile_folders = [
                name for name in os.listdir(self.profiles_path)
                if os.path.isdir(os.path.join(self.profiles_path, name))
            ]
            
            if profile_folders and not self.selected_profile_var.get():
                self.selected_profile_var.set(self.get_last_used_profile())

            if not profile_folders:
                empty_label = tk.Label(self.profile_list_frame, text="(No profiles found)", fg="gray")
                empty_label.grid(row=0, column=0, padx=10, pady=5)
            else:
                for i, prof in enumerate(profile_folders):
                    rb = tk.Radiobutton(
                        self.profile_list_frame,
                        text=prof,
                        variable=self.selected_profile_var,
                        value=prof
                    )
                    rb.grid(row=i, column=0, sticky="w", padx=10, pady=2)

            if self.has_valid_profiles():
                return_btn = tk.Button(left_frame, text="Go to main", width=20 ,command=on_return_click)
                return_btn.grid(row=3, column=0, padx=5, pady=20, sticky="ne")

        def on_add_click():
            name = name_var.get().strip()
            if not name:
                print("❌ Profile name is empty")
                return

            profile_dir = os.path.join(self.profiles_path, name)
            if os.path.exists(profile_dir):
                print("❌ Profile already exists")
                return

            # config parameters
            default_config_data = {
                "url":"https://jobsearch.api.jobtechdev.se/search",
                "keywords":[
                    "python"
                ],
                "limit":10,
                "offset":0
            }

            os.makedirs(profile_dir)
            with open(os.path.join(profile_dir, "config.json"), "w") as f:
                json.dump(default_config_data, f, indent=4)
            self.create_env_file(profile_dir=profile_dir)

            print(f"✅ Created profile: {name}")
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
            self.init_main_frame()
            self.show_frame(self.main_frame)


        self.selected_profile_var = tk.StringVar()

        self.create_profile_frame = tk.Frame(self.root)
        self.create_profile_frame.grid(row=0, column=0, sticky="nsew")

        # Left frame: Create profile
        left_frame = tk.Frame(self.create_profile_frame)
        left_frame.grid(row=1, column=0, padx=10, sticky="n")

        left_label = tk.Label(left_frame, text="Create a new profile", font=("Arial", 14))
        left_label.grid(row=0, column=0, columnspan=2, pady=10, padx=20)

        name_var = tk.StringVar()
        name_label = tk.Label(left_frame, text="Name: ")
        name_label.grid(row=1, column=0, padx=5, pady=20)
        name_entry = tk.Entry(left_frame, textvariable=name_var)
        name_entry.grid(row=1, column=1, padx=5, pady=20)

        add_btn = tk.Button(left_frame, text="Add profile", command=on_add_click)
        add_btn.grid(row=2, column=1, padx=5, pady=20)

        # Right frame: Select profile
        right_frame = tk.Frame(self.create_profile_frame)
        right_frame.grid(row=1, column=1, padx=20, sticky="n")

        right_label = tk.Label(right_frame, text="Select Profile", font=("Arial", 14))
        right_label.grid(row=0, column=0, columnspan=2, pady=10, padx=20)

        self.profile_list_frame = tk.Frame(right_frame)
        self.profile_list_frame.grid(row=1, column=0)

        refresh_profile_list()
        self.show_frame(self.create_profile_frame)

    def init_config_env_frame(self):
        self.config_env_frame = tk.Frame(self.root)
        self.config_env_frame.grid(row=0, column=0, sticky="nsew")

        entries = {}
        env_path = os.path.join(self.profiles_path,self.selected_profile,".env")
        
        # # Load existing .env values (if file exists)
        env_values = {}
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        env_values[key] = value.strip('"')
        
        def add_input(frame, label_text, var_name, masked=False):
            container = tk.Frame(frame)
            container.pack(fill="x", padx=5, pady=2)

            label = tk.Label(container, text=label_text)
            label.pack(side="left")

            var = tk.StringVar(value=env_values.get(var_name, ""))  # store value in StringVar
            entry = tk.Entry(container, width=40, textvariable=var)
            if masked:
                entry.config(show="*")
            entry.pack(side="left", padx=5)

            def toggle_visibility():
                if entry.cget("show") == "":
                    entry.config(show="*")
                    toggle_button.config(text="Show")
                else:
                    entry.config(show="")
                    toggle_button.config(text="Hide")

            if masked:
                toggle_button = tk.Button(container, text="Show", command=toggle_visibility, width=5)
                toggle_button.pack(side="left")

            entries[var_name] = entry

       
        # OpenAI
        openai_frame = tk.LabelFrame(self.config_env_frame, text="OpenAI")
        openai_frame.grid(row=0, column=0, sticky="news", padx=10, pady=5)
        add_input(openai_frame, "API Key:", "OPENAI_API_KEY", masked=True)

        # gmail
        gmail_app_pass_frame = tk.LabelFrame(self.config_env_frame, text="Gmail")
        gmail_app_pass_frame.grid(row=1,column=0,sticky="news",padx=10,pady=5)
        add_input(gmail_app_pass_frame,"App Password:" ,"GMAIL_APP_PASSWORD",masked=True)


        def on_done_click():
            lines = []
            for key, entry in entries.items():
                val = entry.get().strip()
                if " " in val:
                    val = f'"{val}"'
                lines.append(f"{key}={val}")

            
            with open(env_path, "w") as f:
                f.write("\n".join(lines))

            # self.init_create_profile_frame()
            self.show_frame(self.main_frame)

        
        # Save Button
        save_button = tk.Button(self.config_env_frame, text="Done", command=on_done_click,width=20)
        save_button.grid(row=4, column=0, pady=10, padx=10,sticky="ns")

        self.show_frame(self.config_env_frame)

    def init_config_search_param_frame(self):
        self.config_search_param_frame = tk.Frame(self.root)
        self.config_search_param_frame.grid(row=0, column=0, sticky="nsew")

        config_path = os.path.join(self.profiles_path, self.selected_profile, "config.json")

        if os.path.exists(config_path):
            with open(config_path) as f:
                config_values = json.load(f)
        else:
            config_values = {}

        print(config_values)

        # URL row
        url_label = tk.Label(self.config_search_param_frame, text="URL")
        url_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        url_var = tk.StringVar(value=config_values.get("url", ""))
        url_entry = tk.Entry(self.config_search_param_frame, textvariable=url_var, width=40)
        url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Keyword entry
        keywords_label = tk.Label(self.config_search_param_frame, text="Keywords")
        keywords_label.grid(row=1, column=0, padx=10, pady=5, sticky="nw")

        keyword_var = tk.StringVar()
        keyword_entry = tk.Entry(self.config_search_param_frame, textvariable=keyword_var, width=30)
        keyword_entry.grid(row=1, column=1, padx=10, pady=(5, 0), sticky="w")

        # Keyword Listbox
        keyword_listbox = tk.Listbox(self.config_search_param_frame, height=6, width=30, selectmode="multiple")
        keyword_listbox.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        for kw in config_values.get("keywords", []):
            keyword_listbox.insert("end", kw)


         # Add + Delete keyword buttons
        def add_keyword():
            word = keyword_var.get().strip()
            if word and word not in keyword_listbox.get(0, "end"):
                keyword_listbox.insert("end", word)
            keyword_var.set("")

        def delete_selected():
            for i in reversed(keyword_listbox.curselection()):
                keyword_listbox.delete(i)

        
        add_btn = tk.Button(self.config_search_param_frame, text="Add", command=add_keyword)
        add_btn.grid(row=1, column=2, padx=5, pady=(5, 0))

        del_btn = tk.Button(self.config_search_param_frame, text="Delete", command=delete_selected)
        del_btn.grid(row=2, column=2, padx=5, pady=5)

        # LIMIT Slider (1–100)
        limit_label = tk.Label(self.config_search_param_frame, text="Limit")
        limit_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        limit_var = tk.IntVar(value=config_values.get("limit", 10))  # default = 10
        limit_slider = tk.Scale(
            self.config_search_param_frame, from_=1, to=100,
            orient="horizontal", variable=limit_var, resolution=1
        )
        limit_slider.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        # OFFSET Slider (0–500 default range)
        offset_label = tk.Label(self.config_search_param_frame, text="Offset")
        offset_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        offset_var = tk.IntVar(value=config_values.get("offset", 0))  # default = 0
        offset_slider = tk.Scale(
            self.config_search_param_frame, from_=0, to=500,
            orient="horizontal", variable=offset_var, resolution=1
        )
        offset_slider.grid(row=4, column=1, padx=10, pady=10, sticky="w")


        def on_done_click():
            data = {
                "url": url_var.get(),
                "keywords": keyword_listbox.get(0, "end"),
                "limit": limit_var.get(),
                "offset": offset_var.get()
            }
            with open(config_path, "w") as f:
                json.dump(data, f, indent=4)
            print("✅ Config saved")

            self.show_frame(self.main_frame)

        
        # Save Button
        save_button = tk.Button(self.config_search_param_frame, text="Done", command=on_done_click)
        save_button.grid(row=5,column=0,pady=10, padx=10,sticky="we")

        self.show_frame(self.config_search_param_frame)

    def init_data_files_frame(self):
        pass


    def create_menu(self):
        self.menubar = tk.Menu(self.root)

        self.menubar.add_command(label="Profiles", command=self.init_create_profile_frame)

        # env file creation and config
        self.menubar.add_command(label=".env config", command=self.init_config_env_frame)

        # search param config
        self.menubar.add_command(label="Search Parameter config", command=self.init_config_search_param_frame)

        self.menubar.add_command(label="Data files",command=self.init_data_files_frame)


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
        # make subfolder
        prompts_path = os.path.join(self.profiles_path,name,"prompts")
        os.makedirs(prompts_path,exist_ok=True)

        responses_path = os.path.join(self.profiles_path,name,"responses")
        os.makedirs(responses_path,exist_ok=True)

        valid_responses_path = os.path.join(responses_path,"valid")
        os.makedirs(valid_responses_path,exist_ok=True)

        rest_responses_path = os.path.join(responses_path,"rest")
        os.makedirs(rest_responses_path,exist_ok=True)

        attachement_files_path = os.path.join(self.profiles_path,name,"attachement_files")
        os.makedirs(attachement_files_path,exist_ok=True)












    # def scan_for_profile_config(self) -> bool:
    #     pass


    # def scan_for_env(self) -> bool:
    #     top_level_files = os.listdir('.')
    #     if '.env' in top_level_files:
    #         self.response_text.delete("1.0", "end")  # Clear previous content
    #         self.response_text.insert("end", f".env found at root:\n")
    #         return True
    #     else:
    #         self.response_text.delete("1.0", "end")  # Clear previous content
    #         self.response_text.insert("end", f"No .env found\n")
    #         self.configure_env_file()
    #         return False
    
    

    # def create_labelframes(self):
    #     # base frame config
    #     self.root.grid_rowconfigure(0, weight=1)   # top half grows vertically
    #     self.root.grid_rowconfigure(1, weight=0)   # bottom row: just its natural size
    #     self.root.grid_columnconfigure((0, 1), weight=1)


    #     # top left frame
    #     self.config_frame = tk.LabelFrame(self.root, bg="lightgrey", text="Config values")
    #     self.config_frame.grid(row=0, column=0 , sticky="nsew")
    #     self.add_to_config_frame()
    
    #     # top right frame
    #     self.files_frame = tk.LabelFrame(self.root, bg="lightgrey", text="Selected Files")
    #     self.files_frame.grid(row=0, column=1, sticky="nsew")
    #     self.add_to_files_frame()

        
    #     # bottom frame
    #     self.response_frame = tk.LabelFrame(self.root, bg="lightblue", text="terminal")
    #     self.response_frame.grid(row=1, column=0, columnspan=3, sticky="news")
    #     self.add_to_response_frame()
     
    # def add_to_response_frame(self):
    #     # --- scrolling text area (unchanged) ---------------------------------
    #     text_container = tk.Frame(self.response_frame)
    #     text_container.pack(side="top", fill="both", expand=True)

    #     scrollbar = tk.Scrollbar(text_container, width=12)
    #     scrollbar.pack(side="right", fill="y")

    #     self.response_text = tk.Text(
    #         text_container,
    #         height=6,
    #         wrap="word",
    #         yscrollcommand=scrollbar.set,
    #         borderwidth=0,
    #         highlightthickness=0
    #     )
    #     self.response_text.pack(side="left", fill="both", expand=True)
    #     scrollbar.config(command=self.response_text.yview)

    #     # --- centred button --------------------------------------------------
    #     run_btn = tk.Button(
    #         self.response_frame,
    #         text="Run / Send",
    #         width=20,
    #         command=self.on_run_click
    #     )
    #     # no fill, no expand → keep natural width; anchor keeps it centred
    #     run_btn.pack(side="top", pady=4, anchor="center")

    # def add_to_config_frame(self):
    #     # response format
    #     self.use_json_var = tk.BooleanVar()
    #     self.response_format_box = tk.Checkbutton(self.config_frame,text="Use Json Response", variable=self.use_json_var)
    #     self.response_format_box.pack(anchor="w", padx=10, pady=5)

    #     # temperature
    #     self.temperature_var = tk.DoubleVar(value=0.0)

    #     temp_slider_row = tk.Frame(self.config_frame)
    #     temp_slider_row.pack(anchor="w", padx=10, pady=5)
  
    #     tk.Label(temp_slider_row, text="Set temp value (0.0 to 2.0):").pack(side="left")
       
    #     self.temp_slider = tk.Scale(
    #         temp_slider_row,
    #         from_=0.0,
    #         to=2.0,
    #         resolution=0.1,
    #         orient="horizontal",
    #         variable=self.temperature_var,
    #         length=100
    #     )
    #     self.temp_slider.pack(side="left", padx=10)

       
    #     # LLM models
    #     self.model = tk.StringVar(value=self.models[0])  # default to first option

    #     # Create a horizontal frame for label + dropdown
    #     model_row = tk.Frame(self.config_frame)
    #     model_row.pack(anchor="w", padx=10, pady=5)
    #     tk.Label(model_row, text="Select Model:").pack(side="left")

    #     # Dropdown
    #     self.model_dropdown = tk.OptionMenu(model_row, self.model, *self.models)
    #     self.model_dropdown.pack(side="left", padx=10)

    # def refresh_model_dropdown(self):
    #     menu = self.model_dropdown["menu"]
    #     menu.delete(0, "end")  # Clear existing options

    #     for model in self.models:
    #         menu.add_command(label=model, command=lambda m=model: self.model.set(m))

    #     # Optional: Reset selection if current value is invalid
    #     if self.model.get() not in self.models:
    #         self.model.set(self.models[0])

    # def add_to_files_frame(self):
    #     # system prompt label
    #     self.selected_sys_prompt_label = tk.Label(self.files_frame, text="No system prompt selected")
    #     self.selected_sys_prompt_label.pack(pady=10)
        
    #     # Data files label
    #     self.selected_data_files_label = tk.Label(self.files_frame, text="No data files selected")
    #     self.selected_data_files_label.pack(pady=10)

    #     # Output folder label
    #     self.output_folder_label = tk.Label(self.files_frame, text="No output folder selected")
    #     self.output_folder_label.pack(pady=10)

    #     # Output filename label
    #     self.output_filename_label = tk.Label(self.files_frame, text="No output filename selected")
    #     self.output_filename_label.pack(pady=10)

    # def select_profile(self):
    #     pass

    # def create_profile(self):
    #     # Create a new popup window
    #     popup = tk.Toplevel(self.root)
    #     popup.title("Create Profile")

    #     # Entry label and field
    #     tk.Label(popup, text="Enter a new profile name:").pack(pady=5)
        
    #     name_entry = tk.Entry(popup, width=50)
    #     name_entry.pack(pady=5)

    #     # Button to create folder
    #     def submit():
    #         folder_path = name_entry.get().strip()
    #         if folder_path:
    #             try:
                    
                    
    #                 pass

    #             except Exception as e:
    #                 tk.Label(popup, text=f"Error:\n{e}", fg="red").pack(pady=5)

    #     tk.Button(popup, text="Create Folder", command=submit).pack(pady=10)

    

    # def create_output_filename(self):
    #     popup = tk.Toplevel(self.root)
    #     popup.title("Output filename")

    #     # Entry label and field
    #     tk.Label(popup, text="Enter filename:").pack(pady=5)

    #     filename_var = tk.StringVar()
    #     path_entry = tk.Entry(popup, width=50, textvariable=filename_var)
    #     path_entry.pack(pady=5)

    #     # Save button
    #     def save_filename():
    #         self.output_filename = filename_var.get().strip()
    #         self.output_filename_label.config(text=f"Select filename:\n{self.output_filename}")
    #         popup.destroy()

    #     tk.Button(popup, text="Save", command=save_filename).pack(pady=10)

    # def reset_system_prompt(self):
    #     self.selected_system_prompt_file = None
    #     self.selected_sys_prompt_label.config(text=f"No system prompt selected")

    # def reset_data_files(self):
    #     self.selected_data_files = []
    #     self.selected_data_files_label.config(text="No data files selected")

    # def select_system_prompt(self):
    #     file_path = filedialog.askopenfilename(
    #         title="Select a system prompt file",
    #         filetypes=[("All files", "*.*")]
    #     )
    #     if file_path:
    #         filename = os.path.basename(file_path)
    #         self.selected_sys_prompt_label.config(text=f"Selected System Prompt: {filename}")
    #         self.selected_system_prompt_file = file_path

    # def select_data_files(self):
    #     file_paths = filedialog.askopenfilenames(
    #         title="Select one or more data files",
    #         filetypes=[("All files", "*.*")]
    #     )
    #     if file_paths:
    #         # Convert new file_paths to dicts
    #         new_files = [
    #             {
    #                 "full_path": fp,
    #                 "filename": os.path.basename(fp),
    #                 "filename_no_ext": os.path.splitext(os.path.basename(fp))[0]
    #             }
    #             for fp in file_paths
    #         ]

    #         # Combine with previous selections, remove duplicates by full_path
    #         prev_files = getattr(self, 'selected_data_files', [])
    #         prev_paths = {f['full_path'] for f in prev_files}
            
    #         # Only add new files not already in the list
    #         combined_files = prev_files + [f for f in new_files if f['full_path'] not in prev_paths]
            
    #         self.selected_data_files = combined_files

    #         # Display filenames
    #         filenames = [f['filename'] for f in self.selected_data_files]
    #         self.selected_data_files_label.config(text="Data Files:\n" + "\n".join(filenames))

    # def select_folder(self):
    #     folder_path = filedialog.askdirectory(
    #         title="Select a folder",
    #         mustexist=True  # Only allow selecting existing folders
    #     )
    #     if folder_path:
    #         self.output_folder = folder_path
    #         # Optional: update a label to display the selected folder
    #         basename = os.path.basename(self.output_folder)
    #         self.output_folder_label.config(text=f"Selected Folder:\n{basename}")

    # def create_folder(self):
    #     # Create a new popup window
    #     popup = tk.Toplevel(self.root)
    #     popup.title("Create Folder")

    #     # Entry label and field
    #     tk.Label(popup, text="Enter base folder path:").pack(pady=5)
        
    #     path_entry = tk.Entry(popup, width=50)
    #     path_entry.pack(pady=5)

    #     # Button to create folder
    #     def submit():
    #         folder_path = path_entry.get().strip()
    #         if folder_path:
    #             try:
    #                 if os.path.exists(folder_path):
    #                     tk.Label(popup, text=f"Folder already exists:\n{folder_path}", fg="orange").pack(pady=5)
    #                 else:
    #                     os.makedirs(folder_path)
    #                     tk.Label(popup, text=f"Folder created:\n{folder_path}", fg="green").pack(pady=5)
                    
    #                 self.output_folder = folder_path  # Save regardless of existence
    #                 basename = os.path.basename(self.output_folder)
    #                 self.output_folder_label.config(text=f"Selected Folder:\n{basename}")

    #             except Exception as e:
    #                 tk.Label(popup, text=f"Error:\n{e}", fg="red").pack(pady=5)

    #     tk.Button(popup, text="Create Folder", command=submit).pack(pady=10)

    # def validate_required_fields(self):
    #     if not self.selected_system_prompt_file:
    #         raise ValueError("System prompt file is not selected.")
    #     if not self.selected_data_files:
    #         raise ValueError("No data files selected.")
    #     if not self.output_folder:
    #         raise ValueError("Output folder is not set.")
    #     if not self.output_filename:
    #         raise ValueError("Output filename is not set.")

    # def construct_message(self):
    #     # init Azure and MessageBuilder 
    #     self.response_text.delete("1.0", "end")  # Clear previous content

    #     message_builder = MessageBuilder(
    #         response_format=self.use_json_var.get()      
    #     )
    #     azure_ai = AICaller()

    #     system_prompt_data = self.load_file(filepath=self.selected_system_prompt_file,json_format=False)

    #     for file in self.selected_data_files:
    #         message_builder.add_message(role="system",message=system_prompt_data)
    #         data = self.load_file(filepath=file["full_path"], json_format=False)

    #         message_builder.add_message(role="user",message=data)

    #         response = azure_ai.chat_openai(
    #             model=self.model.get(),
    #             messages=message_builder.messages,
    #             temperature=self.temperature_var.get(),
    #             response_format=self.use_json_var.get()
    #         )

            
    #         output_path = os.path.join(self.output_folder,file["filename_no_ext"])
    #         os.makedirs(output_path,exist_ok=True)

    #         if self.use_json_var.get():
    #             full_output_path = os.path.join(output_path,self.output_filename+".json")
    #         else:
    #             full_output_path = os.path.join(output_path,self.output_filename+".txt")

    #         self.save_file(
    #             filepath=full_output_path,
    #             data=response,
    #             json_format=self.use_json_var.get()
    #         )

    #         self.response_text.insert("end", f"Successful response. File saved at {full_output_path}")

    #         message_builder.reset_messages()

    # def save_file(self,filepath, data, json_format:bool):
    #     with open(filepath,'w',encoding='utf-8') as f:
    #         if not json_format:
    #             f.write(data)
    #         else:
    #             data = json.loads(data)
    #             json.dump(data,f,indent=4, ensure_ascii=False)

    # def load_file(self,filepath,json_format:bool):
    #     with open(filepath) as f:
    #         if not json_format:  
    #                 data = f.read()
    #         else:
    #             data = json.load(f)
    #     return data

    # def on_run_click(self):
    #     try:
    #         self.validate_required_fields()
    #         self.construct_message()

    #     except ValueError as e:
    #         print(f"[Error] {e}")
    #         messagebox.showerror("Missing Input", str(e))
        
        
if __name__ == '__main__':
    producer = JetJob(screen_height=0.35,screen_width=0.3)
    producer.root.mainloop()
    
