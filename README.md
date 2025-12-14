# 📖 Bin2Book Novel Scraper

**Developer:** Ayush Ranjan (CipherMoth)  
**Version:** 1.0.0  
**License:** © 2025 Ayush Ranjan (CipherMoth). All rights reserved.

## Overview

Bin2Book is a specialized archival tool designed to reliably scrape content from web novel sites (like NovelBin) and convert chapters into clean, professional, print-ready PDF files. Perfect for archivists and novel enthusiasts who want a local, formatted collection of their favorite web novels.

---

## 📋 Table of Contents

- [Features](#-features)
- [System Requirements](#-system-requirements)
- [Quick Start](#-quick-start)
- [Installation Options](#-installation-options)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Advanced Usage](#-advanced-usage)
- [FAQ](#-faq)

---

## ✨ Features

- **One-Click Downloading** - Enter a URL and chapter range, hit START
- **Smart PDF Generation** - Automatically formats chapters with proper pagination and typography
- **Batch Processing** - Configure batch sizes for memory-efficient downloads
- **Auto-Merge** - Optionally merge all chapters into a single PDF
- **Auto-Cleanup** - Automatically remove intermediate batch files after merging
- **Link Caching** - Caches chapter links to avoid repeated scraping (configurable)
- **Dark/Light Theme** - User-friendly GUI with theme switching
- **Cross-Platform** - Works on Windows and macOS
- **Stealth Browsing** - Anti-detection measures to avoid blocking
- **Resume Capability** - Configuration saved between sessions

---

## 💻 System Requirements

| Requirement | Minimum | Recommended |
|:---|:---|:---|
| **OS** | Windows 7+ / macOS 10.12+ | Windows 10+ / macOS 11+ |
| **Python** | 3.8 | 3.10+ |
| **RAM** | 4 GB | 8 GB+ |
| **Disk Space** | 1 GB free | 5 GB+ free |
| **Browser** | Chrome/Chromium installed | Chrome (latest) |
| **Internet** | Broadband connection | Stable broadband |

---

## 🚀 Quick Start

### For Most Users (Executable)

1. **Download** `Bin2Book.exe` (Windows) or `Bin2Book.app` (macOS)
2. **Double-click** to launch
3. **Enter** your NovelBin URL (e.g., `https://novelbin.com/n/beast-taming-i-can-even-breed-gods-and-demons`)
4. **Set** chapter range (or leave blank for all chapters)
5. **Click** **START DOWNLOAD**

That's it! Your novels will be saved to your Downloads folder by default.

---

## 📦 Installation Options

## � Installation Options

### Option 1: Executable (Recommended for End Users)

#### 🪟 Windows Setup

1. **Locate** the `Bin2Book.exe` file
2. **Double-click** to launch
3. **Run** - First launch may take a few seconds as the app initializes
4. **Done!** - The app will remember your settings

**Location to Save Files:**
- By default, novels are saved to `C:\Users\YourUsername\Downloads\Bin2Book_Novels`
- You can change this in the GUI by clicking the "Browse" button

#### 🍎 macOS Setup

*(**Note:** The macOS version must be built on a Mac. If you received the Windows `.exe`, you'll need to use Option 2 below.)*

1. **Locate** the `Bin2Book` application or `.dmg` installer
2. **Double-click** to open the app
3. **Grant Permission** - macOS may ask for security approval on first launch
4. **Start** entering your URLs and downloading

**First Run Security Note:**
- macOS may block the app initially. Go to **System Settings > Privacy & Security** and click **Open Anyway**

---

### Option 2: Running from Source (For Developers/Advanced Users)

If you prefer running the Python code directly or want to modify the application:

#### Prerequisites

- **Python 3.10+** installed on your system
- **pip** package manager
- **Google Chrome** or Chromium browser installed

#### Installation Steps

1. **Download** the source code or clone the repository
2. **Navigate** to the project directory in your terminal:
   ```bash
   cd path/to/Bin2Book
   ```
3. **Install dependencies** using the requirements file:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application**:
   ```bash
   python gui.py
   ```

#### Requirements File Content

The `requirements.txt` includes:
- `selenium` - Web browser automation
- `undetected-chromedriver` - Anti-detection web driver
- `reportlab` - PDF generation
- `pypdf` - PDF manipulation and merging
- `webdriver-manager` - Automatic Chrome driver management

---

## ⚙️ Configuration

## ⚙️ Configuration

### GUI Settings

When you launch Bin2Book, you'll see the following options:

| Setting | Default | Description |
|:---|:---|:---|
| **Output Folder** | `~/Downloads/Bin2Book_Novels` | Where downloaded novels are saved. Click "Browse" to change. |
| **NovelBin URL** | *(empty)* | Full URL to the novel's main page on NovelBin |
| **Start Chapter** | 1 | First chapter to download |
| **End Chapter** | 0 | Last chapter to download (0 = all available) |
| **Batch Size** | 100 | Number of chapters per PDF file before merging |
| **Auto-Merge PDFs** | Checked | Automatically merge all batch PDFs into one final file |
| **Auto-Delete Batch Files** | Unchecked | Remove intermediate batch files after merging |

### Configuration File (Advanced)

Settings are automatically saved to your user directory:
- **Windows:** `C:\Users\YourUsername\.novel_downloader_config.json`
- **macOS:** `~/.novel_downloader_config.json`

You can manually edit this JSON file if needed. Restart the app for changes to take effect.

**Example Config:**
```json
{
    "start_chapter": 1,
    "end_chapter": 0,
    "batch_size": 100,
    "auto_merge": true,
    "auto_cleanup": false,
    "links_cache_days": 7,
    "output_folder_path": "/Users/yourname/Downloads/Bin2Book_Novels"
}
```

---

## 🔧 Troubleshooting

### ⚠️ "App Crashes When I Click START DOWNLOAD"

This is the most common issue. The application cannot find the Chrome WebDriver required for web scraping.

#### Solution: Manually Provide the Chrome Driver

| OS | Instructions |
|:---|:---|
| **Windows** | 1. Search your PC for `chromedriver.exe` (usually in `C:\Users\YourName\.wdm\drivers\chromedriver\...`) 2. Copy the file 3. Paste it into the **same folder** as `Bin2Book.exe` 4. Restart the app |
| **macOS** | 1. Find `chromedriver` executable (no extension) 2. Copy the file 3. Paste it into the **same folder** as `Bin2Book.app` 4. Right-click `chromedriver` and select "Open" to grant permissions 5. Then restart Bin2Book |

**Alternative:** Go to **Help > Driver Fix** in the app menu for step-by-step instructions tailored to your OS.

### ❌ "Invalid URL" Error

- Ensure the URL starts with `https://` or `http://`
- Verify it's a NovelBin URL (contains `novelbin.com`)
- Check that you copied the full URL correctly

**Example Valid URLs:**
- ✅ `https://novelbin.com/n/beast-taming-i-can-even-breed-gods-and-demons`
- ✅ `https://novelbin.com/n/martial-god-asura`
- ❌ `novelbin.com/n/book` (missing https://)
- ❌ `https://example.com/novel` (wrong site)

### 📵 "Network/Connection Errors"

- Verify your internet connection is stable
- The site may be temporarily down - try again later
- Some ISPs/networks block scraping - consider using a VPN
- The chapter may have been removed from the site

### 📄 "PDF Looks Corrupted or Incomplete"

- Try unchecking "Auto-Merge PDFs" and manually inspect the batch files
- If a specific chapter fails, you'll see `[!] Ch X failed` in the log
- The app automatically retries failed chapters up to 2 times
- Some novel sites have anti-bot protections that may block extraction

### 🔒 "Permission Denied" Error

- Ensure the output folder exists and you have write permissions
- Try changing the output folder to your Downloads or Documents
- On macOS, grant Full Disk Access if prompted by System Settings

---

## 🎮 Advanced Usage

### Running Multiple Downloads

- Start one download, let it complete
- You can queue another URL while the first is running
- The app will show a warning if a download is already in progress

### Using Custom Batch Sizes

- **Smaller batches (25-50):** Slower but uses less RAM, easier to debug
- **Larger batches (150-300):** Faster but consumes more memory
- **Default (100):** Recommended for most systems

### Disabling Auto-Merge

If you want to keep all chapter batches separate:
1. Uncheck "Auto-Merge PDFs"
2. You'll get individual PDF files like `chapters_1_to_100.pdf`, `chapters_101_to_200.pdf`, etc.
3. Merge manually later if needed

### Redownloading with Cache

- The app caches chapter links for 7 days by default
- Delete the `[NovelName]_links.txt` file in the output folder to force a refresh
- Or wait 7 days for the cache to expire automatically

---

## ❓ FAQ

**Q: Is Bin2Book free?**  
A: Yes, Bin2Book is completely free to use. No ads, no paywalls.

**Q: Can I use this on multiple computers?**  
A: Yes. Each computer gets its own config file, so settings are independent.

**Q: What if the website detects and blocks me?**  
A: Bin2Book uses stealth measures to avoid detection, but aggressive sites may still block. This is temporary and usually expires within hours. Retry later.

**Q: Can I contribute to the project?**  
A: This is currently a personal project. For questions or suggestions, reach out to the developer.

**Q: Will this work with other novel sites?**  
A: Currently, Bin2Book is optimized for NovelBin. Other sites may have different structures and would require code modifications.

**Q: How long does a download take?**  
A: Depends on the number of chapters and your connection speed. Expect roughly 2-5 seconds per chapter. A 300-chapter novel might take 15-25 minutes.

**Q: What formats can I export to?**  
A: Currently PDF only. The PDFs are print-ready and work with all PDF readers.

**Q: Does this work offline?**  
A: No, you need an internet connection to scrape the novel site. Once downloaded, you can read the PDFs offline.

**Q: Can I edit the downloaded PDFs?**  
A: The PDFs are standard files and can be edited with any PDF editor, though text extraction may have limitations depending on the source.

---

## 📞 Support & Contact

- **Report Issues:** Check the application log in the GUI for error messages
- **Help Menu:** Click **Help > Driver Fix** for troubleshooting
- **About:** Click **Help > About Bin2Book** for version and developer info

---

## 📜 License & Attribution

Bin2Book is copyrighted © 2025 Ayush Ranjan (CipherMoth). All rights reserved.

**Built with:**
- Python 3.10+
- Selenium & Undetected ChromeDriver
- ReportLab
- PyPDF
- Tkinter

---

*Last Updated: December 2025*
