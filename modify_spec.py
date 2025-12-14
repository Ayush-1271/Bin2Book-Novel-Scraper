import re
import os
import sys

# --- Configuration ---
SPEC_FILE = "Bin2Book.spec"

# Define the data additions, including the complex reportlab path
# This path is based on the GitHub Actions Windows runner environment (3.10.11)
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

    # --- 1. Modify the Analysis block (a) for hidden imports and data ---
    # FIX: Pass re.DOTALL separately to re.search
    analysis_pattern = r'a = Analysis\((.*?)\)'
    match = re.search(analysis_pattern, content, re.DOTALL)

    if match:
        # Get the current Analysis content inside the parentheses
        analysis_content = match.group(1)
        
        # Inject custom hidden imports
        # NOTE: This replaces the entire 'hiddenimports=[]' list for simplicity
        hidden_imports_list = str(ANALYSIS_ADDITIONS["hiddenimports"])
        analysis_content = analysis_content.replace('hiddenimports=[]', f'hiddenimports={hidden_imports_list}', 1)

        # Build the datas list string
        datas_injection = "added_datas = [\n"
        for src, dst in ANALYSIS_ADDITIONS["datas"]:
            # PyInstaller spec files use Python tuples
            datas_injection += f"    ('{src}', '{dst}'),\n"
        datas_injection += "]\na.datas += added_datas"

        # Find the PYZ line and inject our custom data *before* it gets processed
        # This is a safe insertion point within the spec file structure.
        pkg_pattern = r'(pyz = PYZ\((.*?)\))', re.DOTALL
        content = re.sub(pkg_pattern, r'\1\n\n' + datas_injection, content, 1)


    # --- 2. Modify the EXE block (for icon and version) ---
    # Find the EXE line and inject icon and version file paths
    # The pattern matches the EXE() call and adds the arguments just before the final ')'
    exe_pattern = r'(exe = EXE\(.*?\)(.*?))$' # Matches the EXE call at the end of the file
    replace_str = r'\1, icon="app_logo.ico", version="version_info.rc"'

    content = re.sub(exe_pattern, replace_str, content, 1)


    # --- 3. Write the updated content back ---
    with open(SPEC_FILE, 'w') as f:
        f.write(content)

    print(f"Successfully modified {SPEC_FILE} for Windows resources.")

if __name__ == "__main__":
    modify_spec()