# gui.py
import tkinter as tk
from tkinter import messagebox, filedialog
from threading import Thread
import os
import os.path
import platform  # Added to detect Mac vs Windows

# Local Imports
from app_config import AppConfig
from novel_scraper import NovelScraper

class NovelApp(tk.Tk):
    # --- Define Window Sizes ---
    WINDOW_HEIGHT_FULL = 700 
    WINDOW_HEIGHT_MIN = 418
    WINDOW_WIDTH = 750
    
    # --- Color Palette ---
    COLOR_START = '#4CAF50'  # Green
    COLOR_STOP = '#F44336'   # Red
    
    THEME_LIGHT = {
        'bg': '#F5F5F5', 'fg': '#000000', 'entry_bg': '#FFFFFF', 'entry_fg': '#000000',
        'btn_bg': '#E0E0E0', 'btn_fg': '#000000', 'select': '#F5F5F5'
    }
    
    THEME_DARK = {
        'bg': '#212121', 'fg': '#FFFFFF', 'entry_bg': '#424242', 'entry_fg': '#FFFFFF',
        'btn_bg': '#616161', 'btn_fg': '#FFFFFF', 'select': '#212121'
    }

    def __init__(self):
        super().__init__()
        self.title("Novel Downloader")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT_FULL}")
        
        # Lock Min Size
        self.minsize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT_MIN)
        self.protocol("WM_DELETE_WINDOW", self._on_closing) 

        self.config_manager = AppConfig()
        
        # --- DYNAMIC PATH FIX ---
        # 1. Get path from config
        saved_path = self.config_manager.get("output_folder_path")
        
        # 2. Check if that path actually exists on THIS computer
        if saved_path and os.path.exists(saved_path):
            self.default_output = saved_path
        else:
            # 3. If not (e.g. we are on Mac but config has Windows path), use Downloads folder
            self.default_output = os.path.join(os.path.expanduser("~"), "Downloads", "Bin2Book_Novels")

        self.download_thread = None
        self.log_visible = True
        self.is_dark_mode = False 
        self.log_text = None 
        
        self._create_widgets()
        self.create_menu_bar()
        
        # Initialize Scraper
        self.scraper = NovelScraper(self.config_manager, self.log_message)
        
        self._load_config_to_ui()
        self.apply_theme(self.THEME_LIGHT)

    def create_menu_bar(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Driver Fix / Troubleshooting", command=self.show_driver_help)
        help_menu.add_separator()
        help_menu.add_command(label="About Bin2Book", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

    def show_driver_help(self):
        """Displays instructions dynamically based on OS."""
        is_mac = platform.system() == "Darwin"
        
        if is_mac:
            msg = (
                "⚠️ Mac Driver Troubleshooting\n\n"
                "1. Make sure Google Chrome is installed.\n"
                "2. If the app crashes, download 'chromedriver' for Mac.\n"
                "3. Place the 'chromedriver' file in the SAME folder as this app.\n"
                "4. Go to System Settings > Privacy & Security and allow 'chromedriver' to run."
            )
        else:
            msg = (
                "⚠️ Chrome Driver Troubleshooting\n\n"
                "If the app crashes, the browser driver might be missing.\n\n"
                "1. Search your PC for 'chromedriver.exe'.\n"
                "   (Often in C:\\Users\\<You>\\.wdm\\drivers...)\n"
                "2. Copy that file.\n"
                "3. Paste it into the SAME folder as 'Bin2Book.exe'."
            )
        messagebox.showwarning("Driver Help", msg)

    def show_about(self):
        about_win = tk.Toplevel(self)
        about_win.title("About Bin2Book")
        about_win.geometry("420x320")
        about_win.resizable(False, False)
        
        # Center Window safely
        try:
            x = self.winfo_x() + (self.WINDOW_WIDTH // 2) - 210
            y = self.winfo_y() + (self.WINDOW_HEIGHT_FULL // 2) - 160
            about_win.geometry(f"+{x}+{y}")
        except:
            pass
        
        current_theme = self.THEME_DARK if self.is_dark_mode else self.THEME_LIGHT
        self._recursive_theme_update(about_win, current_theme)

        tk.Label(about_win, text="Bin2Book Downloader", font=("Segoe UI", 16, "bold"), bg=current_theme['bg'], fg=current_theme['fg']).pack(pady=(20, 5))
        tk.Label(about_win, text="Version 1.0.0 (Stable Release)", font=("Segoe UI", 9), bg=current_theme['bg'], fg=current_theme['fg']).pack()
        
        tk.Frame(about_win, height=2, bd=1, relief="sunken").pack(fill="x", padx=40, pady=15)
        
        tk.Label(about_win, text="Developed by", font=("Segoe UI", 10, "italic"), fg="#888", bg=current_theme['bg']).pack()
        tk.Label(about_win, text="Ayush Ranjan (CipherMoth)", font=("Segoe UI", 11, "bold"), bg=current_theme['bg'], fg=current_theme['fg']).pack(pady=(0, 10))
        
        desc = "A specialized archival tool designed to scrape,\nformat, and convert web novels into clean,\nprint-ready PDF e-books."
        tk.Label(about_win, text=desc, justify="center", font=("Segoe UI", 9), bg=current_theme['bg'], fg=current_theme['fg']).pack(pady=5)
        
        tk.Button(about_win, text="Close", command=about_win.destroy, width=10, bg=current_theme['btn_bg'], fg=current_theme['btn_fg']).pack(side="bottom", pady=(0, 20))

    def _on_closing(self):
        if self.download_thread and self.download_thread.is_alive():
            if messagebox.askyesno("Exit Confirmation", "A download is running. Stop and exit?"):
                self.stop_download()
                self.after(1000, self.destroy)
        else:
            self._save_ui_to_config() 
            self.destroy()

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        theme = self.THEME_DARK if self.is_dark_mode else self.THEME_LIGHT
        self.apply_theme(theme)
        self.theme_btn.config(text="Light Mode" if self.is_dark_mode else "Dark Mode")

    def apply_theme(self, theme):
        self.configure(bg=theme['bg'])
        self._recursive_theme_update(self, theme)

    def _recursive_theme_update(self, widget, theme):
        try:
            w_class = widget.winfo_class()
            
            if w_class in ('Frame', 'Labelframe', 'Tk', 'Toplevel'):
                widget.config(bg=theme['bg'])
                if w_class == 'Labelframe':
                    widget.config(fg=theme['fg']) 

            elif w_class in ('Label', 'Checkbutton'):
                widget.config(bg=theme['bg'], fg=theme['fg'])
                if w_class == 'Checkbutton':
                    widget.config(selectcolor=theme['bg'], activebackground=theme['bg'], activeforeground=theme['fg'])

            elif w_class in ('Entry', 'Text'):
                widget.config(bg=theme['entry_bg'], fg=theme['entry_fg'], insertbackground=theme['fg'])

            elif w_class == 'Button':
                if widget not in [self.start_button, self.stop_button]:
                    widget.config(bg=theme['btn_bg'], fg=theme['btn_fg'], activebackground=theme['btn_bg'], activeforeground=theme['btn_fg'])
        except Exception:
            pass 
        
        for child in widget.winfo_children():
            self._recursive_theme_update(child, theme)

    def _create_widgets(self):
        # ------------------- INPUT FRAME -------------------
        input_frame = tk.LabelFrame(self, text="Download Settings", padx=15, pady=15)
        input_frame.pack(side="top", padx=15, pady=(15, 5), fill="x")

        input_frame.columnconfigure(1, weight=1) 
        input_frame.columnconfigure(3, weight=1)

        # 0. Output Folder
        tk.Label(input_frame, text="Output Folder:").grid(row=0, column=0, sticky="w", pady=5)
        # Fix: Initialize with the Safe/Dynamic Path
        self.output_path_var = tk.StringVar(value=self.default_output)
        tk.Entry(input_frame, textvariable=self.output_path_var).grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        tk.Button(input_frame, text="Browse", command=self._browse_output_folder).grid(row=0, column=3, sticky="e", padx=5)

        # 1. URL
        tk.Label(input_frame, text="NovelBin URL:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.url_var = tk.StringVar()
        tk.Entry(input_frame, textvariable=self.url_var).grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        
        # 2. Chapters
        tk.Label(input_frame, text="Start Chapter:").grid(row=3, column=0, sticky="w", pady=5)
        self.start_chap_var = tk.StringVar(value=str(self.config_manager.get("start_chapter")))
        tk.Entry(input_frame, textvariable=self.start_chap_var).grid(row=3, column=1, sticky="ew", padx=5)
        
        tk.Label(input_frame, text="End Chapter:").grid(row=3, column=2, sticky="w", padx=(20, 5), pady=5)
        self.end_chap_var = tk.StringVar(value=str(self.config_manager.get("end_chapter")))
        tk.Entry(input_frame, textvariable=self.end_chap_var).grid(row=3, column=3, sticky="ew", padx=5)

        tk.Label(input_frame, text="Batch Size:").grid(row=4, column=0, sticky="w", pady=5)
        self.batch_size_var = tk.StringVar(value=str(self.config_manager.get("batch_size")))
        tk.Entry(input_frame, textvariable=self.batch_size_var).grid(row=4, column=1, sticky="ew", padx=5)

        # Options
        opt_frame = tk.Frame(input_frame)
        opt_frame.grid(row=5, column=0, columnspan=4, pady=15)
        
        self.auto_merge_var = tk.BooleanVar()
        tk.Checkbutton(opt_frame, text="Auto-Merge PDFs", variable=self.auto_merge_var).pack(side="left", padx=15)
        
        self.auto_cleanup_var = tk.BooleanVar()
        tk.Checkbutton(opt_frame, text="Auto-Delete Batch Files", variable=self.auto_cleanup_var).pack(side="left", padx=15)
        
        # Action Buttons
        self.start_button = tk.Button(input_frame, text="START DOWNLOAD", command=self.start_download_thread, bg=self.COLOR_START, fg='white', height=2, font=('Arial', 10, 'bold'))
        self.start_button.grid(row=6, column=0, columnspan=4, sticky="ew", padx=5, pady=(0, 5))
        
        self.stop_button = tk.Button(input_frame, text="STOP", command=self.stop_download, bg=self.COLOR_STOP, fg='white', height=2, font=('Arial', 10, 'bold'), state=tk.DISABLED)
        self.stop_button.grid(row=7, column=0, columnspan=4, sticky="ew", padx=5)

        # ------------------- CONTROL BAR -------------------
        self.control_bar = tk.Frame(self)
        self.control_bar.pack(side="top", fill="x", padx=15, pady=(5, 0))
        
        self.log_label = tk.Label(self.control_bar, text="Application Log", font=("Segoe UI", 9, "bold"))
        self.log_label.pack(side="left")
        
        self.theme_btn = tk.Button(self.control_bar, text="Dark Mode", command=self.toggle_theme, width=12)
        self.theme_btn.pack(side="right", padx=5)

        self.log_toggle_button = tk.Button(self.control_bar, text="Hide Log", command=self._toggle_log_visibility, width=10)
        self.log_toggle_button.pack(side="right")
        
        # ------------------- LOG FRAME -------------------
        self.log_frame = tk.LabelFrame(self, padx=5, pady=5)
        self.log_frame.pack(side="bottom", padx=15, pady=5, fill="both", expand=True)
        
        self.log_text = tk.Text(self.log_frame, state='disabled', wrap='word', height=15)
        self.log_text.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(self.log_frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)
        
    def _browse_output_folder(self):
        directory = filedialog.askdirectory(initialdir=self.output_path_var.get())
        if directory:
            self.output_path_var.set(directory)

    def _toggle_log_visibility(self):
        if self.log_visible:
            self.log_frame.pack_forget()
            self.log_toggle_button.config(text="Show Log")
            self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT_MIN}") 
        else:
            self.log_frame.pack(side="bottom", padx=15, pady=5, fill="both", expand=True)
            self.log_toggle_button.config(text="Hide Log")
            self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT_FULL}")
        
        self.log_visible = not self.log_visible
        
    def _load_config_to_ui(self):
        # FIX: We handled the path in __init__, so we only update if needed.
        # But for numeric fields we load normally.
        self.start_chap_var.set(str(self.config_manager.get("start_chapter")))
        self.end_chap_var.set(str(self.config_manager.get("end_chapter")))
        self.batch_size_var.set(str(self.config_manager.get("batch_size")))
        self.auto_merge_var.set(self.config_manager.get("auto_merge"))
        self.auto_cleanup_var.set(self.config_manager.get("auto_cleanup"))
        self.log_message("Configuration loaded successfully.")

    def _save_ui_to_config(self):
        try:
            output_dir = self.output_path_var.get().strip()
            if not os.path.isdir(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            self.config_manager.set("output_folder_path", output_dir) 

            start_val = self.start_chap_var.get()
            end_val = self.end_chap_var.get()
            batch_val = self.batch_size_var.get()
            
            self.config_manager.set("start_chapter", int(start_val) if start_val.strip() else 1)
            self.config_manager.set("end_chapter", int(end_val) if end_val.strip() else 0)
            self.config_manager.set("batch_size", int(batch_val) if batch_val.strip() else 100)

            self.config_manager.set("auto_merge", self.auto_merge_var.get())
            self.config_manager.set("auto_cleanup", self.auto_cleanup_var.get())
            self.config_manager.save_config()
            return True
        except ValueError:
            messagebox.showerror("Input Error", "Chapter and Batch Size must be valid numbers.")
            return False
        except Exception as e:
            messagebox.showerror("Path Error", f"Could not create or access output directory: {e}")
            return False

    def log_message(self, message):
        if self.log_text:
            self.log_text.after(0, lambda: self._update_log_text(message))

    def _update_log_text(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def start_download_thread(self):
        if self.download_thread and self.download_thread.is_alive():
            messagebox.showwarning("Busy", "A download is already in progress.")
            return

        if not self._save_ui_to_config(): return

        url = self.url_var.get().strip()
        
        url_is_valid = (
            url.startswith("http://") or url.startswith("https://")
        ) and (
            "novelbin.com" in url.lower()
        )

        if not url_is_valid:
            messagebox.showerror("Input Error", "Please enter a valid NovelBin URL. Must start with http/https and contain 'novelbin.com'.")
            return
        
        start = self.config_manager.get("start_chapter")
        end = self.config_manager.get("end_chapter")
        step = self.config_manager.get("batch_size")

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state='disabled')

        self.download_thread = Thread(target=self.run_scraper_logic, args=(url, start, end, step))
        self.download_thread.start()

    def run_scraper_logic(self, url, start, end, step):
        """Runs the scraper in a thread and catches driver errors."""
        try:
            self.scraper.run_app(url, start, end, step)
        except Exception as e:
            # Check for common webdriver errors
            err_msg = str(e).lower()
            if "executable needs to be in path" in err_msg or "chromedriver" in err_msg or "driver" in err_msg:
                self.after(0, self.show_driver_help)
            else:
                self.log_message(f"Error during download: {e}")
        finally:
            self.after(0, self.finish_download)

    def stop_download(self):
        if self.download_thread and self.download_thread.is_alive():
            self.scraper.request_stop()
            self.log_message("\n[USER REQUEST] Attempting to gracefully stop the scraper...")
            self.stop_button.config(state=tk.DISABLED, text="Stopping...")
    
    def finish_download(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED, text="STOP")
        self.log_message("[GUI Status] Application ready for next task.")
        self.download_thread = None

if __name__ == "__main__":
    app = NovelApp()
    app.mainloop()