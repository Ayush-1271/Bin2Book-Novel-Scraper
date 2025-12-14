import json
import re
import os

SPEC_FILE = "Bin2Book.spec"

# Define the additions for the Analysis section (Analysis block is where
# hidden imports and manual data files go).
# Note: Data path uses double backslashes for string escaping in Python.
ANALYSIS_ADDITIONS = {
    "datas": [
        ("app_logo.ico", "."),
        ("version_info.rc", "."),
        # FIX: Use the collected info from the log for reportlab path
        ("C:\\hostedtoolcache\\windows\\Python\\3.10.11\\x64\\Lib\\site-packages\\reportlab", "reportlab"),
    ],
    "hiddenimports": [
        "selenium.webdriver.chrome.service",
        "reportlab.graphics.shapes",
        "reportlab.pdfbase.pdfmetrics",
    ],
}

def modify_spec():
    with open(SPEC_FILE, 'r') as f:
        content = f.read()

    # --- 1. Modify the Analysis block (a) ---
    # Find the Analysis block content
    analysis_pattern = r'a = Analysis\((.*?)\)', re.DOTALL
    match = re.search(analysis_pattern, content)

    if match:
        analysis_content = match.group(1)
        
        # Inject custom hidden imports
        for imp in ANALYSIS_ADDITIONS["hiddenimports"]:
            if imp not in analysis_content:
                analysis_content = analysis_content.replace('hiddenimports=[]', f'hiddenimports={ANALYSIS_ADDITIONS["hiddenimports"]}', 1)
        
        # Inject custom data files
        # We manually append the datas list to ensure it's included
        data_injection = "added_datas = [\n"
        for src, dst in ANALYSIS_ADDITIONS["datas"]:
            # PyInstaller spec files use Python tuples
            data_injection += f"    ('{src}', '{dst}'),\n"
        data_injection += "]\na.datas += added_datas"

        # Find the PKG line to know where to insert our custom data
        pkg_pattern = r'(pyz = PYZ\((.*?)\))', re.DOTALL
        content = re.sub(pkg_pattern, r'\1\n\n' + data_injection, content, 1)


    # --- 2. Modify the EXE block (for icon and version) ---
    # Find the EXE line and inject icon and version file paths
    # We use a pattern that matches the EXE() call and adds the arguments
    exe_pattern = r'(exe = EXE\(.*?\)(.*?))'
    replace_str = r'\1, icon="app_logo.ico", version="version_info.rc"'

    content = re.sub(exe_pattern, replace_str, content, 1)


    # --- 3. Write the updated content back ---
    with open(SPEC_FILE, 'w') as f:
        f.write(content)

    print(f"Successfully modified {SPEC_FILE} for Windows resources.")

if __name__ == "__main__":
    modify_spec()