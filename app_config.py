# app_config.py
import json
import os
import os.path

class AppConfig:
    """Manages application settings like batch size, merge options, etc."""
    
    DEFAULT_CONFIG = {
        "start_chapter": 1,
        "end_chapter": 0, # 0 means all chapters
        "batch_size": 100,
        "auto_merge": True,
        "auto_cleanup": False,
        "links_cache_days": 7,
        # Default to a safe 'Downloads' subfolder on any OS
        "output_folder_path": os.path.join(os.path.expanduser('~'), "Downloads", "Bin2Book_Novels")
    }
    
    def __init__(self, filename="config.json"):
        # Save config in the user's home directory (Hidden file)
        self.filename = os.path.join(os.path.expanduser('~'), ".novel_downloader_config.json")
        self.config = self.load_config()
        
        # REMOVED: os.makedirs(...) 
        # Reason: If the loaded config has a path from a different OS (e.g. D:\ on Mac),
        # trying to create it immediately here will cause errors or messy folders.
        # We let the GUI handle path validation.

    def load_config(self):
        """Loads configuration from JSON file or returns defaults."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    # Merge loaded config with defaults to catch new settings
                    loaded_config = json.load(f)
                    return {**self.DEFAULT_CONFIG, **loaded_config}
            except:
                print("Warning: Could not load config. Using defaults.")
        return self.DEFAULT_CONFIG

    def save_config(self):
        """Saves current configuration to JSON file."""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False

    def get(self, key):
        return self.config.get(key)

    def set(self, key, value):
        self.config[key] = value