import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import json
from backend.ai_caller import AICaller
from backend.message_builder import MessageBuilder
from api.send_email import send_email
from api.searcher import multi_search
import shutil
from dotenv import load_dotenv

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
                    "final_email_string":None,

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
            refresh_file_list()

        def refresh_file_list():          
            # Clear previous widgets in right_frame
            for widget in right_frame.winfo_children():
                widget.destroy()
            
            valid_path = os.path.join(self.ads_path,f"matched_email")
            missing_region_path = os.path.join(valid_path,"region_missing")
         
            if not os.listdir(self.ads_path):
                no_files_label = tk.Label(right_frame, text="No files found.", fg="gray")
                no_files_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
                return
            
            for region_index, region in enumerate(self.config_values["regions"]):
                region_path = os.path.join(valid_path, region)

                # region frame
                region_frame = tk.LabelFrame(right_frame, text=region)
                region_frame.grid(row=region_index, column=0, sticky="news", padx=5, pady=5)

                # Allow filename column to expand
                region_frame.columnconfigure(0, weight=1)
                try:
                    files = [f for f in os.listdir(region_path) if os.path.isfile(os.path.join(region_path, f))]
                except FileNotFoundError as e:
                    continue

                if not files:
                    no_files_label = tk.Label(region_frame, text="No files found.", fg="gray")
                    no_files_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
                    continue

                for idx, filename in enumerate(files):
                    full_path = os.path.join(region_path, filename)

                    # File label (left aligned, expandable)
                    file_label = tk.Label(region_frame, text=filename, anchor="w")
                    file_label.grid(row=idx, column=0, padx=5, pady=2, sticky="w")

                    # View button (right aligned)
                    view_btn = tk.Button(region_frame, text="View", width=8,
                                        command=lambda f=full_path: view_file(f))
                    view_btn.grid(row=idx, column=1, padx=5, sticky="e")

                    # Delete button (right aligned)
                    delete_btn = tk.Button(region_frame, text="Delete", width=8,
                                        command=lambda f=full_path: delete_file(f))
                    delete_btn.grid(row=idx, column=2, padx=5, sticky="e")

                 
            missing_region_frame = tk.LabelFrame(right_frame, text="Missing Region")
            missing_region_frame.grid(row=len(self.config_values["regions"]), column=0, sticky="news", padx=5, pady=5)
            missing_region_frame.columnconfigure(0, weight=1)

            try:
                m_region_files = [f for f in os.listdir(missing_region_path) if os.path.isfile(os.path.join(missing_region_path, f))]
            except FileNotFoundError:
                m_region_files = []  # If the folder doesn't exist, treat as empty

            if not m_region_files:
                no_files_label = tk.Label(missing_region_frame, text="No files found.", fg="gray")
                no_files_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            else:
                for m_region_index, m_region in enumerate(m_region_files):
                    full_path = os.path.join(missing_region_path, m_region)
                    file_label = tk.Label(missing_region_frame, text=m_region, anchor="w")
                    file_label.grid(row=m_region_index, column=0, padx=5, pady=2, sticky="w")

                    # View button (right aligned)
                    view_btn = tk.Button(missing_region_frame, text="View", width=8,
                                        command=lambda f=full_path: view_file(f))
                    view_btn.grid(row=m_region_index, column=1, padx=5, sticky="e")

                    # Delete button (right aligned)
                    delete_btn = tk.Button(missing_region_frame, text="Delete", width=8,
                                        command=lambda f=full_path: delete_file(f))
                    delete_btn.grid(row=m_region_index, column=2, padx=5, sticky="e")
                                     
        def view_file(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            content = data["description"]["text"]

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

        def on_personalize_click():
            try:
                self.setup_personal_letter_payload()
                 
            except ValueError as e:
                messagebox.showwarning("Invalid Configuration", str(e))
                return

        def on_sendmails_click():
            try:
                self.validate_send_email()
                print("ok")
                # self.mass_send_email()
            except ValueError as e:
                self.show_large_warning(message=str(e),title="Error")
            except FileNotFoundError as e:
                self.show_large_warning(message=str(e),title="Error")

        def delete_all_click(folder_path):
            confirm = messagebox.askyesno("Confirm Delete all ads?")
            if confirm:
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)  # Remove file or link
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)  # Remove directory and all its contents
                    except Exception as e:
                        print(f'Failed to delete {file_path}. Reason: {e}')
                refresh_file_list()

        # Main UI setup
        self.main_frame = tk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        button_frame = tk.LabelFrame(self.main_frame, text="Buttons")
        button_frame.grid(row=0, column=0, sticky="nsw",padx=5,pady=10)

        ads_frame = tk.Frame(self.main_frame)
        ads_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        ads_frame.columnconfigure(0, weight=1)

        right_frame = tk.LabelFrame(ads_frame, text="Ads with regions")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        # right_frame.columnconfigure(0, weight=1)

        missing_region_frame = tk.LabelFrame(ads_frame, text="Missing regions")
        missing_region_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        # missing_region_frame.columnconfigure(0, weight=1)

        preview_frame = tk.Frame(self.main_frame)
        preview_frame.grid(row=1,column=1,sticky="news",padx=10,pady=10)
        if os.listdir(self.processed_letters_path):
            preview_letters_btn = tk.Button(preview_frame,text="Preview Letters",command=self.init_preview_letters_frame)
            preview_letters_btn.grid(row=0,column=0)   
        else:
            missing_letters_label = tk.Label(preview_frame,text="No processed letters found")
            missing_letters_label.grid(row=0,column=0)

        search_btn = tk.Button(button_frame, text="Search", command=on_search, width=10)
        search_btn.grid(row=0, column=0, padx=10, pady=10)

        personalize_btn = tk.Button(button_frame, text="Personalize letters", command=on_personalize_click, width=15)
        personalize_btn.grid(row=1, column=0, padx=10, pady=10)

        refresh_btn = tk.Button(button_frame, text="Refresh", command=refresh_file_list, width=10)
        refresh_btn.grid(row=2, column=0, padx=10, pady=10)

        delete_all_btn = tk.Button(button_frame, text="Delete all ads",
                            command=lambda:delete_all_click(self.ads_path), width=10)
        delete_all_btn.grid(row=4, column=0, padx=10, pady=10)

        sendmails_btn = tk.Button(button_frame, text="Send emails", command=on_sendmails_click, width=10)
        sendmails_btn.grid(row=7, column=0, padx=10, pady=10)

        allow_missing_region_var = tk.BooleanVar(value=self.config_values["missing_regions"])  

        def on_missing_regions_toggle():
            save_data = {"missing_regions":allow_missing_region_var.get()}
            self.save_config_values(**save_data)
            print("Switch is now", allow_missing_region_var.get())

        allow_missing_region_check= tk.Checkbutton(button_frame, text="Allow missing regions",
            variable=allow_missing_region_var,
            command=on_missing_regions_toggle,
            onvalue=True,
            offvalue=False
        )
        allow_missing_region_check.grid(row=5, column=0, padx=10, pady=10)


        self.show_frame(self.main_frame)
        refresh_file_list()

    def init_preview_letters_frame(self):
        self.preview_letters_frame = tk.Frame(self.root)
        self.preview_letters_frame.grid(row=0, column=0, sticky="nsew")

        letters_frame = tk.Frame(self.preview_letters_frame)
        letters_frame.grid(row=0,column=0,sticky="nsew")

        def show_files():          
            # Clear previous widgets in right_frame
            for widget in letters_frame.winfo_children():
                widget.destroy()
            
            for idx, filename in enumerate(os.listdir(self.processed_letters_path)):
                full_path = os.path.join(self.processed_letters_path, filename)
                
                # File label (left aligned, expandable)
                file_label = tk.Label(letters_frame, text=filename, anchor="w")
                file_label.grid(row=idx, column=0, padx=5, pady=2, sticky="w")

                # View button (right aligned)
                view_btn = tk.Button(letters_frame, text="View", width=8,
                                    command=lambda f=full_path: view_file(f))
                view_btn.grid(row=idx, column=1, padx=5, sticky="e")

                # Delete button (right aligned)
                delete_btn = tk.Button(letters_frame, text="Delete", width=8,
                                    command=lambda f=full_path: delete_file(f))
                delete_btn.grid(row=idx, column=2, padx=5, sticky="e")
       
        def view_file(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            content = data["text"]

            popup = tk.Toplevel(self.root)
            popup.title(f"Viewing: {os.path.basename(filepath)}")

            text_area = tk.Text(popup, wrap="word")
            text_area.insert("1.0", content)
            text_area.pack(expand=True, fill="both")
            text_area.config(state="disabled")

            info_frame = tk.Frame(popup)
            info_frame.pack()

            for key,value in data.items():
                if key != "text":
                    label = tk.Label(info_frame,text=f"{key}: {value}")
                    label.pack()

        def delete_file(filepath):
            confirm = messagebox.askyesno("Confirm Delete", f"Delete {os.path.basename(filepath)}?")
            if confirm:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                ad_id = data["id"]
                if ad_id in self.config_values["processed_ids"]:
                    self.config_values["processed_ids"].remove(ad_id)
                    self.save_config_values(**{"processed_ids":self.config_values["processed_ids"]})
            
                os.remove(filepath)
                show_files()

        def on_back_click():
            self.show_frame(self.main_frame)

        def delete_all_click():
            self.processed_letters_path
            confirm = messagebox.askyesno("Confirm Delete all letters?")
            if confirm:
                for filename in os.listdir(self.processed_letters_path):
                    file_path = os.path.join(self.processed_letters_path, filename)
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)  # remove file or symlink
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  # remove subfolder and all its conten
                self.show_frame(self.main_frame)

        back_btn = tk.Button(self.preview_letters_frame,text="Back",command=on_back_click)
        back_btn.grid(row=1,column=0)

        deleta_all_btn = tk.Button(self.preview_letters_frame,text="Delete all",command=delete_all_click)
        deleta_all_btn.grid(row=1,column=1)

        show_files()
        self.show_frame(self.preview_letters_frame)

    def init_create_profile_frame(self):
        def refresh_profile_list():
            for widget in self.profile_list_frame.winfo_children():
                widget.destroy()

            profile_folders = [
                name for name in os.listdir(self.profiles_path)
                if os.path.isdir(os.path.join(self.profiles_path, name))
            ]
            
            if profile_folders:
                # If currently selected profile doesn't exist anymore, select first
                current = self.selected_profile_var.get()
                if current not in profile_folders:
                    self.selected_profile_var.set(profile_folders[0])
                    self.set_last_used_profile(profile_folders[0])
            else:
                # No profiles left: clear selection and last used
                self.selected_profile_var.set("")
                self.set_last_used_profile("")
                
            if not profile_folders:
                empty_label = tk.Label(self.profile_list_frame, text="(No profiles found)", fg="gray")
                empty_label.grid(row=0, column=0, padx=10, pady=5)
            else:
                for i, prof in enumerate(profile_folders):
                    rb = tk.Radiobutton(
                        self.profile_list_frame,
                        text=prof,
                        variable=self.selected_profile_var,
                        value=prof,
                        command=lambda:self.root.title(f"JetJob - Welcome {self.selected_profile_var.get()}")
                    )
                    rb.grid(row=i, column=0, sticky="w", padx=10, pady=2)

                    del_btn = tk.Button(
                    self.profile_list_frame,
                    text="Delete",
                    fg="red",
                    command=lambda p=prof: delete_profile(p)
                            )
                    del_btn.grid(row=i, column=1, sticky="w", padx=5, pady=2)


            # Only show "Go to main" if there are profiles
            for widget in left_frame.grid_slaves():
                if isinstance(widget, tk.Button) and widget["text"] == "Go to main":
                    widget.destroy()
            if profile_folders:
                return_btn = tk.Button(left_frame, text="Go to main", width=20, command=on_return_click)
                return_btn.grid(row=3, column=0, padx=5, pady=20, sticky="ne")
      
        def delete_profile(profile_name):
            folder_path = os.path.join(self.profiles_path, profile_name)
            try:
                confirm = messagebox.askyesno(title=f"Delete {profile_name}?")
                if confirm:
                    shutil.rmtree(folder_path)  # Remove folder and all its contents
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

            # config parameters
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
                    "final_email_string":None,

                    "processed_ids": [],
                    "sent_ids":[],
                    
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

        self.update_config()

        # URL row
        url_label = tk.Label(self.config_search_param_frame, text="URL")
        url_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        url_var = tk.StringVar(value=self.config_values.get("url", ""))
        url_entry = tk.Entry(self.config_search_param_frame, textvariable=url_var, width=40)
        url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # gmail row
        gmail_label = tk.Label(self.config_search_param_frame, text="Gmail")
        gmail_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        gmail_var = tk.StringVar(value=self.config_values.get("gmail", ""))
        gmail_entry = tk.Entry(self.config_search_param_frame, textvariable=gmail_var, width=40)
        gmail_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Keyword entry
        keywords_label = tk.Label(self.config_search_param_frame, text="Keywords")
        keywords_label.grid(row=2, column=0, padx=10, pady=5, sticky="nw")

        keyword_var = tk.StringVar()
        keyword_entry = tk.Entry(self.config_search_param_frame, textvariable=keyword_var, width=30)
        keyword_entry.grid(row=2, column=1, padx=10, pady=(5, 0), sticky="w")

        # Keyword Listbox
        keyword_listbox = tk.Listbox(self.config_search_param_frame, height=6, width=30, selectmode="multiple")
        keyword_listbox.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        for kw in self.config_values.get("keywords", []):
            keyword_listbox.insert("end", kw)

 
        # --- Regions Section ---
        region_label = tk.Label(self.config_search_param_frame, text="Regions")
        region_label.grid(row=4, column=0, padx=10, pady=5, sticky="nw")

        # Frame to hold listbox and scrollbar
        region_listbox_frame = tk.Frame(self.config_search_param_frame)
        region_listbox_frame.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        # Listbox
        region_box = tk.Listbox(region_listbox_frame, selectmode="multiple", height=10, exportselection=False)
        region_box.grid(row=0, column=0, sticky="ns")

        # Scrollbar
        region_scrollbar = tk.Scrollbar(region_listbox_frame, orient="vertical", command=region_box.yview)
        region_scrollbar.grid(row=0, column=1, sticky="ns")
        region_box.config(yscrollcommand=region_scrollbar.set)

        # Populate listbox
        for region in self.regions:
            region_box.insert(tk.END, region)

        # Pre-select saved regions
        selected_regions = self.config_values.get("regions", [])
        for idx, region in enumerate(self.regions):
            if region in selected_regions:
                region_box.selection_set(idx)

        # Frame to contain both buttons vertically
        region_button_frame = tk.Frame(self.config_search_param_frame)
        region_button_frame.grid(row=4, column=2, padx=10, pady=5, sticky="n")

        # "Select All" button in row 0
        select_all_btn = tk.Button(region_button_frame, text="Select All", command=lambda: region_box.select_set(0, tk.END))
        select_all_btn.grid(row=0, column=0, pady=(0, 10), sticky="ew")

        # "Clear All" button in row 1
        clear_all_btn = tk.Button(region_button_frame, text="Clear All", command=lambda: region_box.selection_clear(0, tk.END))
        clear_all_btn.grid(row=1, column=0, sticky="ew")
            
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
        add_btn.grid(row=2, column=2, padx=5, pady=(5, 0))

        del_btn = tk.Button(self.config_search_param_frame, text="Delete", command=delete_selected)
        del_btn.grid(row=3, column=2, padx=5, pady=5)

        # LIMIT Slider (1–100)
        limit_label = tk.Label(self.config_search_param_frame, text="Limit")
        limit_label.grid(row=5, column=0, padx=10, pady=10, sticky="w")

        limit_var = tk.IntVar(value=self.config_values.get("limit", 10))  # default = 10
        limit_slider = tk.Scale(
            self.config_search_param_frame, from_=1, to=100,
            orient="horizontal", variable=limit_var, resolution=1
        )
        limit_slider.grid(row=5, column=1, padx=10, pady=10, sticky="w")

        # OFFSET Slider (0–500 default range)
        offset_label = tk.Label(self.config_search_param_frame, text="Offset")
        offset_label.grid(row=6, column=0, padx=10, pady=10, sticky="w")

        offset_var = tk.IntVar(value=self.config_values.get("offset", 0))  # default = 0
        offset_slider = tk.Scale(
            self.config_search_param_frame, from_=0, to=500,
            orient="horizontal", variable=offset_var, resolution=1
        )
        offset_slider.grid(row=6, column=1, padx=10, pady=10, sticky="w")


        def on_done_click():
            selected_indices = region_box.curselection()
            selected_regions = [self.regions[i] for i in selected_indices]

            # update config values
            save_data = {
                "url":url_var.get(),
                "gmail":gmail_var.get(),
                "keywords":keyword_listbox.get(0, "end"),
                "regions":selected_regions,
                "limit":limit_var.get(),
                "offset":offset_var.get(),
            }
            
            self.save_config_values(**save_data)
            self.show_frame(self.main_frame)

        # Save Button
        save_button = tk.Button(self.config_search_param_frame, text="Done", command=on_done_click)
        save_button.grid(row=7,column=0,pady=10, padx=10,sticky="we")
 
        self.adjust_window()
        self.show_frame(self.config_search_param_frame)

    def init_data_files_frame(self):
        data_files_frame = tk.Frame(self.root)
        data_files_frame.grid(row=0, column=0, sticky="nsew")
        data_files_frame.columnconfigure(0, weight=1)

        # Title Label
        label = tk.Label(data_files_frame, text="Manage System Prompts, Attachment Files, and More!", font=("Arial", 14))
        label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        def select_file_click(title,keyword,initial_dir):
            selected_file = filedialog.askopenfilename(
                title=title,
                initialdir=initial_dir,
                filetypes=[("Text or Markdown files", "*.txt *.md")]
            )
            if selected_file:
                save_data = {keyword :selected_file}
                self.save_config_values(**save_data)
                print("✅ Config saved")

        def add_files_click():
            selected_files = filedialog.askopenfilenames(
                title="Select data files for mail attachment (CV, grades, etc)",
                initialdir=self.attachement_files_path,
                filetypes=[("All files", "*.*")]
                )
            if selected_files:
                save_data = {"attachment_files" :selected_files}
                self.save_config_values(**save_data)
                print("✅ Config saved")
        

        # System Prompt Frame
        system_prompt_frame = tk.LabelFrame(data_files_frame, text="System Prompt")
        system_prompt_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        system_prompt_frame.columnconfigure(0, weight=1)

        tk.Button(system_prompt_frame, text="Select Premade Prompt",
                command=lambda: select_file_click("Select System Prompt", "system_prompt_path", self.prompts_path)
                ).grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        tk.Button(system_prompt_frame, text="Create New Prompt",
                command=lambda: self.create_text_click(self.prompts_path, "Create new System prompt")
                ).grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Attachment Files Frame
        attachment_files_frame = tk.LabelFrame(data_files_frame, text="Attachment Files")
        attachment_files_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        tk.Button(attachment_files_frame, text="Add Files", command=add_files_click
                ).grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # About Me Frame
        about_me_frame = tk.LabelFrame(data_files_frame, text="About Me")
        about_me_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        about_me_frame.columnconfigure(0, weight=1)

        tk.Button(about_me_frame, text="Select 'About Me' Text",
                command=lambda: select_file_click("About me text", "about_me_path", self.about_me_path)
                ).grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        tk.Button(about_me_frame, text="Add 'About Me' Text",
                command=lambda: self.create_text_click(self.about_me_path, "About me text")
                ).grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Back Button
        tk.Button(data_files_frame, text="Back", command=lambda: self.show_frame(self.main_frame)
                ).grid(row=4, column=0, padx=10, pady=15, sticky="w")

        self.adjust_window()
        self.show_frame(data_files_frame)

    def init_gpt_config_frame(self):
        gpt_config_frame = tk.Frame(self.root, bg="#f4f6f8")  # light background
        gpt_config_frame.grid(row=0, column=0, sticky="nsew")
        gpt_config_frame.columnconfigure(0, weight=1)

        # OpenAI model frame
        models_frame = tk.LabelFrame(
            gpt_config_frame, text="OpenAI Models",
            font=("Arial", 12, "bold"),
            bg="#f4f6f8", fg="#2d4154", padx=16, pady=12, bd=2, relief="groove"
        )
        models_frame.grid(row=0, column=0, sticky="news", padx=18, pady=18)

        # Scrollbar for the listbox
        model_scrollbar = tk.Scrollbar(models_frame)
        model_scrollbar.grid(row=0, column=1, sticky="nsw", padx=(8,0), pady=4)

        # Listbox with padding, font, and yscroll
        listbox = tk.Listbox(
            models_frame, selectmode="single",
            font=("Arial", 11),
            height=min(8, len(self.models)),  # Show up to 8 lines, dynamic height
            activestyle="dotbox", bd=2,
            yscrollcommand=model_scrollbar.set
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

        # Button, larger and with some color
        select_model_btn = tk.Button(
            models_frame, text="Select",
            command=lambda: on_select_model_click(),
            font=("Arial", 11, "bold"),
            bg="#0052cc", fg="#fff",
            activebackground="#003d80", activeforeground="#fff",
            bd=0, relief="ridge", padx=18, pady=6,
            cursor="hand2"
        )
        select_model_btn.grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=(12, 4))

        def on_select_model_click():
            selected = listbox.curselection()
            if selected:
                index = selected[0]
                model_str = listbox.get(index)   # This gets the string!
                save_data = {"model": model_str}
                self.save_config_values(**save_data)
                print(self.config_values["model"])

        models_frame.columnconfigure(0, weight=1)
        models_frame.rowconfigure(0, weight=1)

        # temperature 
        def on_slider(val):
            value_label.config(text=f"Value: {float(val):.1f}")
            

        temp_frame = tk.LabelFrame(gpt_config_frame, text="Temperature", font=("Arial", 12, "bold"),bg="#f4f6f8", fg="#2d4154", padx=16, pady=12, bd=2, relief="groove")
        temp_frame.grid(row=1,column=0)
           
        slider = tk.Scale(
            temp_frame,
            from_=0.0,
            to=2.0,    
            resolution=0.1,
            orient="horizontal",
            length=300,
            command=on_slider,
            showvalue=False,
            
        )
        slider.pack(fill="x", pady=(8, 2))
        slider.set(self.config_values["temperature"])  # Default to 1.0

        value_label = tk.Label(temp_frame, text="Value: 1.0", font=("Arial", 11))
        value_label.pack(anchor="w", pady=(2, 0))

        def on_done_click():
            save_data = {"temperature":slider.get()}
            self.save_config_values(**save_data)
            self.show_frame(self.main_frame)
         

        done_btn = tk.Button(gpt_config_frame,text="Done",width=20 ,command=on_done_click)
        done_btn.grid(row=2,column=0,pady=10)
        
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
                description = ad_data["description"]["text"]
                application_deadline = ad_data["application_deadline"]
                email = self.find_relevant_email(ad=ad_data)
                message_builder.add_message(role="user",message=text_prepend_ad_data+description)

                response = ai_caller.chat_openai(
                    model="gpt-4.1",
                    messages=message_builder.messages,
                    temperature=0.7,
                    response_format=None
                )

                message_builder.reset_messages()

                processed_letters_path = os.path.join(self.profiles_path, self.selected_profile,"processed_letters")
                os.makedirs(processed_letters_path,exist_ok=True)
                filename = ad_headline+".json"
                save_path = os.path.join(processed_letters_path,filename)
               
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
        
        save_data = {"processed_ids":self.config_values["processed_ids"]}
        self.save_config_values(**save_data)
        print(f"ads pre-processed and saved at {processed_letters_path}")

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

        # ask if user wants a final string appended to letter
        if not self.config_values["final_email_string"]:
            confirm = messagebox.askyesno("No final string added to letter/mail. Do you want to proceed?")
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
        with open(self.config_values["final_email_string"]) as f:
            final_string = f.read()
        sent_ids = []
        if os.listdir(self.processed_letters_path):
            for letter in os.listdir(self.processed_letters_path):
                full_path = os.path.join(self.processed_letters_path,letter)
                with open(full_path,encoding="utf-8") as f:
                    letter_data = json.load(f)
                
                text = letter_data["text"]
                text += text+f"\n{final_string}"
                # letter_data["email"]

                env_path = os.path.join(self.profiles_path,self.selected_profile,".env")
                
                load_dotenv(dotenv_path=env_path, override=True)
                
                send_email(
                    subject=letter_data["headline"],
                    body=text,
                    to_email="tony.rmaili@yh.nackademin.se",
                    from_email=self.config_values["gmail"],
                    password=os.getenv("GMAIL_APP_PASSWORD"),
                    attachments=self.config_values["attachment_files"]
                )
                sent_ids.append(letter_data["id"])
            save_data = {"sent_ids":sent_ids}
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


if __name__ == '__main__':
    producer = JetJob(screen_height=0.35,screen_width=0.3)
    producer.root.mainloop()
    
