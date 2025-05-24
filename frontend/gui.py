import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import json
from backend.ai_caller import AICaller
from backend.message_builder import MessageBuilder

class JetJob:
    def __init__(self, screen_width:float, screen_height:float):
        self.root = tk.Tk()
        self.root.title("JetJob")

    
        # Create frames
        self.profile_frame = tk.Frame(self.root)
        self.main_gui_frame = tk.Frame(self.root)

        
    
        for frame in (self.profile_frame, self.main_gui_frame):
            frame.grid(row=0, column=0, sticky="nsew")

        self.test_profile_frame()
        self.test_main_frame()  # Optional pre-setup

        # Show profile screen first
        self.show_frame(self.profile_frame)


        # Set window size to 50% of screen
        self.width = int(self.root.winfo_screenwidth() *screen_width)
        self.height = int(self.root.winfo_screenheight() * screen_height)
        self.root.geometry(f"{self.width}x{self.height}")

        # gpt models
        self.default_models = ["gpt-4o", "gpt-4o-mini","gpt-4.1"]
        self.models = self.default_models.copy()


        # selected variables
        self.selected_system_prompt_file = None
        self.selected_data_files = []
        self.output_folder = None
        self.output_filename = None

        self.selected_profile = None

        self.config_data = {
            "name":None,
        }



        # Menu and UI
        # self.create_menu()
        # self.create_labelframes()

        # variable file validations 
        # if self.scan_for_env():
        #    pass

        # if self.scan_for_profile_config():
        #     pass

        # paths 
        # self.profiles_path = "./profiles"
        # os.makedirs(self.profiles_path,exist_ok=True)

        # config_path = os.path.join(self.profiles_path, "config.json")
        # if not os.path.exists(config_path):
        #     with open(config_path, "w") as f:
        #         json.dump(self.config_data,f,indent=4)

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

    def show_frame(self,frame):
        frame.tkraise()


    def test_profile_frame(self):
        label = tk.Label(self.profile_frame, text="👤 Select or Create Profile", font=("Arial", 16))
        label.pack(pady=20)

        btn_select = tk.Button(self.profile_frame, text="Select Profile", width=20, command=self.test_main_frame)
        btn_create = tk.Button(self.profile_frame, text="Create New Profile", width=20, command=self.test_main_frame)

        btn_select.pack(pady=10)
        btn_create.pack(pady=10)


    def test_main_frame(self):
        # You can clear the frame here if needed, for repeated calls
        for widget in self.main_gui_frame.winfo_children():
            widget.destroy()

        label = tk.Label(self.main_gui_frame, text="✅ Main GUI Loaded", font=("Arial", 16))
        label.pack(pady=20)

        btn_back = tk.Button(self.main_gui_frame, text="← Back to Profile Menu", command=lambda: self.show_frame(self.profile_frame))
        btn_back.pack(pady=10)

        self.show_frame(self.main_gui_frame)

    
    def center_window(self,window, width, height):
        # Get screen width and height
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Calculate position x, y
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        window.geometry(f"{width}x{height}+{x}+{y}")


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
    
    # def configure_env_file(self):
    #     popup = tk.Toplevel(self.root)
    #     popup.title("Configure .env")
    #     popup.geometry(f"{self.width}x{self.height}")

    #     entries = {}

       
    #     # Load existing .env values (if file exists)
    #     env_values = {}
    #     if os.path.exists(".env"):
    #         with open(".env", "r") as f:
    #             for line in f:
    #                 if "=" in line:
    #                     key, value = line.strip().split("=", 1)
    #                     env_values[key] = value.strip('"')
        
    #     # Filter out defaults when loading from .env
    #     env_llms = env_values.get("LLM_MODELS", "")
    #     llm_models = [m.strip() for m in env_llms.split(",") if m and m not in self.default_models]


    #     def add_input(frame, label_text, var_name, masked=False):
    #         container = tk.Frame(frame)
    #         container.pack(fill="x", padx=5, pady=2)

    #         label = tk.Label(container, text=label_text)
    #         label.pack(side="left")

    #         var = tk.StringVar(value=env_values.get(var_name, ""))  # store value in StringVar
    #         entry = tk.Entry(container, width=40, textvariable=var)
    #         if masked:
    #             entry.config(show="*")
    #         entry.pack(side="left", padx=5)

    #         def toggle_visibility():
    #             if entry.cget("show") == "":
    #                 entry.config(show="*")
    #                 toggle_button.config(text="Show")
    #             else:
    #                 entry.config(show="")
    #                 toggle_button.config(text="Hide")

    #         if masked:
    #             toggle_button = tk.Button(container, text="Show", command=toggle_visibility, width=5)
    #             toggle_button.pack(side="left")

    #         entries[var_name] = entry

       
    #     # OpenAI
    #     openai_frame = tk.LabelFrame(popup, text="OpenAI")
    #     openai_frame.grid(row=0, column=0, sticky="news", padx=10, pady=5)
    #     add_input(openai_frame, "API Key:", "OPENAI_API_KEY", masked=True)

    #     gmail_app_pass_frame = tk.LabelFrame(popup, text="Gmail")
    #     gmail_app_pass_frame.grid(row=1,column=0,sticky="news",padx=10,pady=5)
    #     add_input(gmail_app_pass_frame,"App Password:" ,"GMAIL_APP_PASSWORD",masked=True)

    #     # LLM Models input
    #     llm_frame = tk.LabelFrame(popup, text="LLM Models")
    #     llm_frame.grid(row=2, column=0, sticky="news", padx=10, pady=5)

    #     llm_models = []
    #     models_var = tk.StringVar()

    #     # Load from .env if available
    #     env_llms = env_values.get("LLM_MODELS", "")
    #     if env_llms:
    #         llm_models = [m.strip() for m in env_llms.split(",") if m]

    #     models_display = tk.Label(llm_frame, text=", ".join(llm_models), wraplength=400, anchor="w", justify="left")
    #     models_display.pack(padx=5, pady=(0, 5), fill="x")

    #     def refresh_llm_display():
    #         models_display.config(text=", ".join(llm_models))

    #     def add_model():
    #         model = models_var.get().strip()
    #         if model and model not in llm_models:
    #             llm_models.append(model)
    #             refresh_llm_display()
    #         models_var.set("")

    #     def remove_last_model():
    #         if llm_models:
    #             llm_models.pop()
    #             refresh_llm_display()

    #     input_row = tk.Frame(llm_frame)
    #     input_row.pack(fill="x", padx=5)

    #     model_entry = tk.Entry(input_row, textvariable=models_var, width=30)
    #     model_entry.pack(side="left")

    #     add_btn = tk.Button(input_row, text="Add", command=add_model)
    #     add_btn.pack(side="left", padx=5)

    #     remove_btn = tk.Button(input_row, text="Remove Last", command=remove_last_model)
    #     remove_btn.pack(side="left")

       
    #     def save_env():
    #         lines = []
    #         for key, entry in entries.items():
    #             val = entry.get().strip()
    #             if " " in val:
    #                 val = f'"{val}"'
    #             lines.append(f"{key}={val}")

    #         if llm_models:
    #             lines.append(f'LLM_MODELS="{",".join(llm_models)}"')
    #         else:
    #             lines.append('LLM_MODELS=""')

    #         with open(".env", "w") as f:
    #             f.write("\n".join(lines))

            
    #         popup.destroy()
    #         self.models = list(dict.fromkeys(self.default_models + llm_models))  # deduplicated and ordered
    #         self.refresh_model_dropdown()

    #     # Save Button
    #     save_button = tk.Button(popup, text="Save .env", command=save_env)
    #     save_button.grid(row=4, column=0, pady=10)

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

    # def create_menu(self):
    #     menubar = tk.Menu(self.root)

    #     # System Prompt - single file
    #     profile_bar = tk.Menu(menubar, tearoff=0)
    #     profile_bar.add_command(label="Select", command=self.select_profile)
    #     profile_bar.add_command(label="Create new", command=self.create_profile)
    #     menubar.add_cascade(label="Profiles",menu=profile_bar)

    #     system_prompt_bar = tk.Menu(menubar, tearoff=0)
    #     system_prompt_bar.add_command(label="Select Prompt", command=self.select_system_prompt)
    #     system_prompt_bar.add_command(label="Reset Prompt", command=self.reset_system_prompt)
    #     menubar.add_cascade(label="System Prompt",menu=system_prompt_bar)

    #     # Data Files - multiple files
    #     data_files_menu = tk.Menu(menubar,tearoff=0)
    #     data_files_menu.add_command(label="Add Data Files", command=self.select_data_files)
    #     data_files_menu.add_command(label="Reset Files", command=self.reset_data_files)
    #     menubar.add_cascade(label="Data Files", menu=data_files_menu)

    #     # Output folder
    #     output_menu = tk.Menu(menubar, tearoff=0)
    #     output_menu.add_command(label="Create folder", command=self.create_folder)
    #     output_menu.add_command(label="Select folder", command=self.select_folder)
    #     output_menu.add_command(label="Enter output filename" , command=self.create_output_filename)
    #     menubar.add_cascade(label="Output", menu=output_menu)

    #     self.root.config(menu=menubar)

    #     # env file creation and config
    #     menubar.add_command(label=".env config", command=self.configure_env_file)

    #     self.root.config(menu=menubar)

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
    
