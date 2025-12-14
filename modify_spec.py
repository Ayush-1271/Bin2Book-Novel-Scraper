import re
import os
import sys

# --- Configuration ---
SPEC_FILE = "Bin2Book.spec"

# Define the data additions, including the complex reportlab path
ANALYSIS_ADDITIONS = {
    "datas": [
        ("app_logo.ico", "."),
        ("version_info.rc", "."),
        # Using double backslashes for path escaping in Python strings
        ("C:\\hostedtoolcache\\windows\\Python\\3.10.11\\x64\\Lib\\site-packages\\reportlab", "reportlab"),
    ],
    "hiddenimports": [
        "selenium.webdriver.chrome.service",
        "reportlab.graphics.shapes",
        "reportlab.pdfbase.pdfmetrics",
    ],
}
# --- End Configuration ---

def modify_spec():
    try:
        with open(SPEC_FILE, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {SPEC_FILE} not found. Ensure 'python -m PyInstaller --onefile --name Bin2Book gui.py' ran successfully first.")
        sys.exit(1)

    # --- REGEX PATTERN DEFINITIONS ---
    analysis_pattern = r'a = Analysis\((.*?)\)'
    pkg_pattern = r'(pyz = PYZ\((.*?)\))'
    exe_pattern = r'(exe = EXE\(.*?\)(.*?))$'
    # --- END REGEX PATTERN DEFINITIONS ---


    # --- 1. Modify the Analysis block (a) for hidden imports and data ---
    match = re.search(analysis_pattern, content, re.DOTALL)

    if match:
        # Get the current Analysis content inside the parentheses
        analysis_content = match.group(1)
        
        # Inject custom hidden imports
        hidden_imports_list = str(ANALYSIS_ADDITIONS["hiddenimports"])
        analysis_content = analysis_content.replace('hiddenimports=[]', f'hiddenimports={hidden_imports_list}', 1)

        # Build the datas list string (this part contains the Windows paths)
        datas_injection = "added_datas = [\n"
        for src, dst in ANALYSIS_ADDITIONS["datas"]:
            # PyInstaller spec files use Python tuples
            datas_injection += f"    ('{src}', '{dst}'),\n"
        datas_injection += "]\na.datas += added_datas"

        # FINAL FIX: Use simple string concatenation to bypass regex engine's
        # escape sequence checking for complex paths.
        replacement_template = r'\1' + '\n\n' + datas_injection
        
        # Find the PYZ line and inject our custom data *before* it gets processed
        content = re.sub(pkg_pattern, replacement_template, content, 1, flags=re.DOTALL)


    # --- 2. Modify the EXE block (for icon and version) ---
    replace_str = r'\1, icon="app_logo.ico", version="version_info.rc"'

    content = re.sub(exe_pattern, replace_str, content, 1, flags=re.DOTALL)


    # --- 3. Write the updated content back ---
    with open(SPEC_FILE, 'w') as f:
        f.write(content)

    print(f"Successfully modified {SPEC_FILE} for Windows resources.")

if __name__ == "__main__":
    modify_spec()