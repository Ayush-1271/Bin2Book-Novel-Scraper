# modify_spec.py - Final, Stable Version

SPEC_FILE = "Bin2Book.spec"

def modify_spec_stable():
    try:
        # 1. Read the spec file content
        with open(SPEC_FILE, 'r') as f:
            content = f.readlines()
    except FileNotFoundError:
        print(f"Error: {SPEC_FILE} not found. Build failed before spec file creation.")
        return

    new_content = []
    
    # 2. Define the exact path (using forward slashes is best practice)
    REPORTLAB_PATH = "C:/hostedtoolcache/windows/Python/3.10.11/x64/Lib/site-packages/reportlab"

    for line in content:
        # A. Inject Hidden Imports and Data Files into the Analysis (a) block
        if line.startswith('a = Analysis('):
            # This line defines the Analysis block which contains all data/imports
            
            # --- HIDDEN IMPORTS ---
            # Replace default hiddenimports with custom list
            line = line.replace('hiddenimports=[]', 
                'hiddenimports=[\'selenium.webdriver.chrome.service\', \'reportlab.graphics.shapes\', \'reportlab.pdfbase.pdfmetrics\']')
            
            # --- DATA FILES (app_logo.ico, reportlab) ---
            # Append the data items directly to the 'datas' list within the Analysis call
            line = line.replace('datas=[]', 
                f"datas=[('app_logo.ico', '.'), ('version_info.rc', '.'), ('{REPORTLAB_PATH}', 'reportlab')]")
        
        # B. Inject Icon and Version File into the EXE block
        elif line.startswith('exe = EXE('):
            # This line defines the EXE executable
            # We insert the icon and version file arguments
            line = line.replace('console=False)', 'console=False, icon="app_logo.ico", version="version_info.rc")')

        new_content.append(line)

    # 3. Write the modified content back
    with open(SPEC_FILE, 'w') as f:
        f.writelines(new_content)

    print(f"Successfully modified {SPEC_FILE} using stable Python string replacement.")

if __name__ == "__main__":
    modify_spec_stable()