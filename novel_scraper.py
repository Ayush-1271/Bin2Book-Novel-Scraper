# novel_scraper.py
import os
import time
import random
import datetime
import re
import sys
import platform # Added for OS detection
from xml.sax.saxutils import escape
import threading
import os.path

# Web Automation
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# PDF Generation & Merging
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from pypdf import PdfWriter 

# Local Import
from app_config import AppConfig 

class NovelScraper:
    def __init__(self, config: AppConfig, logger_callback):
        self.config = config
        self.log_callback = logger_callback
        self.driver = None 
        self.stop_requested = False
        
    def _log(self, message):
        """Sends message to the GUI log box."""
        self.log_callback(f"{datetime.datetime.now().strftime('[%H:%M:%S]')} {message}")
        
    def request_stop(self):
        self.stop_requested = True

    # --- 1. HELPER FUNCTIONS ---

    def _get_local_driver_path(self):
        """
        Checks if the user has placed 'chromedriver' or 'chromedriver.exe' 
        next to the application (as per the Help menu instructions).
        """
        system = platform.system()
        driver_filename = "chromedriver.exe" if system == "Windows" else "chromedriver"
        
        # Check current working directory (where the .exe or script is running)
        local_path = os.path.abspath(driver_filename)
        
        if os.path.exists(local_path):
            self._log(f" [System] Found manual driver at: {local_path}")
            return local_path
        return None

    def _get_paths_from_url(self, url):
        """Generates folder and filenames based on the URL and configured output path."""
        try:
            if "/b/" in url:
                slug = url.split('/b/')[1].split('#')[0].split('/')[0]
            else:
                parts = [p for p in url.split('/') if p]
                slug = parts[-1] if 'novelbin.com' in parts[-2] else "novel_download"
                
            novel_name = slug.replace('-', ' ').title()
            folder_name = novel_name
            links_file = f"{novel_name}_links.txt"
            
            base_output_dir = self.config.get("output_folder_path") 
            
            full_folder_path = os.path.join(base_output_dir, folder_name)
            full_links_path = os.path.join(full_folder_path, links_file)

            os.makedirs(full_folder_path, exist_ok=True)
            
            return novel_name, full_folder_path, full_links_path
        except Exception as e:
            self._log(f"[ERROR] Error parsing URL/Path: {e}")
            return None, None, None

    def _is_link_file_fresh(self, filepath):
        """Checks if file exists and respects the configured cache time."""
        if not os.path.exists(filepath):
            return False
            
        file_time = os.path.getmtime(filepath)
        cache_days = self.config.get("links_cache_days")
        
        if (time.time() - file_time) / (24 * 3600) > cache_days:
            self._log(f"  > Link file is older than {cache_days} days. Refreshing...")
            return False
            
        self._log("  > Found fresh link file. Using cache.")
        return True

    def _sanitize_for_pdf(self, text):
        if not text: return ""
        return escape(text)

    # --- 2. CORE LOGIC ---

    def _fetch_links(self, target_url, output_path):
        self._log("\n[Step 1] Initializing Link Scraper...")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        options = webdriver.ChromeOptions()
        # Add headless for link fetching to be faster/cleaner
        options.add_argument("--headless=new") 
        
        try:
            # PRIORITY: Use local driver if exists, otherwise auto-install
            local_driver = self._get_local_driver_path()
            if local_driver:
                service = Service(executable_path=local_driver)
            else:
                service = Service(ChromeDriverManager().install())

            self.driver = webdriver.Chrome(service=service, options=options)
            
        except Exception as e:
            self._log(f"[FATAL] Chrome Driver initialization failed: {e}")
            self.driver = None
            return

        try:
            self._log(f"  > Navigating to: {target_url}")
            self.driver.get(target_url)
            time.sleep(3)

            self._log("  > Scrolling...")
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                if self.stop_requested: break
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height: break
                last_height = new_height

            self._log("  > Extracting links...")
            links = self.driver.find_elements(By.CSS_SELECTOR, "div.panel-body div.row a") 
            valid_links = [l.get_attribute('href') for l in links if l.get_attribute('href') and "novelbin.com/b/" in l.get_attribute('href')]

            if valid_links:
                with open(output_path, "w", encoding="utf-8") as f:
                    for url in valid_links: f.write(url + "\n")
                self._log(f"  [Success] Saved {len(valid_links)} links.")
            else:
                self._log("  [Error] No links found.")
        except Exception as e:
            self._log(f"  [Error] Link scraping failed: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None

    def _generate_pdf_batch(self, data_list, filename):
        doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
        story = []
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=16, spaceAfter=12)
        body_style = ParagraphStyle('Body', parent=styles['Normal'], alignment=TA_JUSTIFY, fontSize=11, leading=14, spaceAfter=6)

        for title, text in data_list:
            story.append(Paragraph(self._sanitize_for_pdf(title), title_style))
            story.append(Spacer(1, 6*mm))
            for para in text.split('\n'):
                if para.strip():
                    story.append(Paragraph(self._sanitize_for_pdf(para.strip()), body_style))
                    story.append(Spacer(1, 2*mm))
            story.append(PageBreak())
            
        try:
            doc.build(story)
            self._log(f"    [PDF] Saved: {filename}")
        except Exception as e:
            self._log(f"    [PDF Error] {e}")


    def _download_content(self, links_path, start_chap, end_chap, step_size):
        self._log("\n[Step 2] Content Downloader...")
        
        with open(links_path, 'r', encoding='utf-8') as f:
            all_links = [line.strip() for line in f.readlines() if "http" in line]
        
        total_chapters = len(all_links)
        if end_chap <= 0 or end_chap > total_chapters: end_chap = total_chapters
        if step_size > (end_chap - start_chap + 1): step_size = (end_chap - start_chap + 1)

        self._log(f"  > Range: {start_chap}-{end_chap} | Batch: {step_size}")
        self._log("  > Launching Stealth Browser...")
        
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        try:
            # PRIORITY: Check for local driver to allow 'Fix' to work
            local_driver = self._get_local_driver_path()
            if local_driver:
                self.driver = uc.Chrome(options=options, driver_executable_path=local_driver)
            else:
                self.driver = uc.Chrome(options=options)
        except Exception as e:
            self._log(f"[FATAL] Stealth Driver failed to initialize: {e}")
            self.driver = None
            raise e # Re-raise so GUI can catch it and show Help

        wait = WebDriverWait(self.driver, 15)
        generated_pdfs = []

        try:
            for batch_start in range(start_chap, end_chap + 1, step_size):
                if self.stop_requested: break 
                
                batch_end = min(batch_start + step_size - 1, end_chap)
                output_folder = os.path.dirname(links_path)
                base_name = f"chapters_{batch_start}_to_{batch_end}"
                txt_file = os.path.join(output_folder, base_name + ".txt")
                pdf_file = os.path.join(output_folder, base_name + ".pdf")
                
                generated_pdfs.append(pdf_file)
                self._log(f"\n  >>> Batch: {base_name}")
                
                batch_data = []

                with open(txt_file, 'w', encoding='utf-8') as f:
                    for i in range(batch_start, batch_end + 1):
                        if self.stop_requested: break 
                        
                        url = all_links[i - 1]
                        retry = 0
                        success = False
                        
                        while not success and retry < 2:
                            try:
                                self.driver.get(url)
                                try:
                                    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, "a.chr-title"))
                                except:
                                    time.sleep(2)
                                    # Simple Cloudflare Clicker
                                    if len(self.driver.find_elements(By.XPATH, "//iframe[starts-with(@src, 'https://challenges')]")) > 0:
                                        self.driver.switch_to.frame(self.driver.find_element(By.XPATH, "//iframe[starts-with(@src, 'https://challenges')]"))
                                        self.driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']").click()
                                        self.driver.switch_to.default_content()
                                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.chr-title")))

                                title = self.driver.find_element(By.CSS_SELECTOR, "a.chr-title").text.strip()
                                content = self.driver.find_element(By.ID, "chr-content").text
                                
                                if len(content) < 50: raise Exception("Empty content or redirect.")

                                f.write(f"Chapter {i}: {title}\n" + "-"*50 + "\n" + content + "\n" + "="*50 + "\n\n")
                                f.flush()
                                batch_data.append((f"Chapter {i}: {title}", content))
                                self._log(f"    [✓] Ch {i}")
                                success = True
                            except Exception as ex:
                                self._log(f"    [!] Ch {i} failed ({retry+1}/2). Retrying...")
                                retry += 1
                                time.sleep(random.uniform(2, 4))
                                if retry == 1: self.driver.refresh()
                            
                        if not success: f.write(f"Chapter {i} FAILED\n\n")

                if batch_data: self._generate_pdf_batch(batch_data, pdf_file)

        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
            return generated_pdfs, total_chapters

    # --- 3. MERGE LOGIC ---
    
    def _merge_pdfs(self, pdf_list, output_folder, novel_name, start, end, total_avail):
        """Merges PDFs based on configuration."""
        if not pdf_list or not self.config.get("auto_merge"):
            self._log("Skipping merge based on user preference.")
            return

        self._log("\n" + "="*40)
        self._log("          PDF MERGE UTILITY")
        self._log("="*40)

        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        if start == 1 and (end == total_avail or end == 0):
            final_name = f"{novel_name.upper()}_FULL_TILL_{date_str}.pdf"
        else:
            final_name = f"{novel_name}_{start}_to_{end}.pdf"
            
        output_path = os.path.join(output_folder, final_name)
        
        self._log(f"  > Merging into: {final_name}...")
        
        try:
            merger = PdfWriter()
            for pdf in pdf_list:
                if os.path.exists(pdf):
                    merger.append(pdf)
            
            merger.write(output_path)
            merger.close()
            self._log("  [Success] Merge Complete.")
        except Exception as e:
            self._log(f"[ERROR] PDF Merge Failed: {e}")
            
        # Cleanup Logic
        if self.config.get("auto_cleanup"):
            for pdf in pdf_list:
                try:
                    os.remove(pdf)
                    txt_path = pdf.replace('.pdf', '.txt')
                    if os.path.exists(txt_path): os.remove(txt_path)
                except: pass
            self._log("  [Cleaned] Partial files and TXT logs deleted.")
        else:
            self._log("Skipping cleanup.")


    # --- 4. MAIN APP RUNNER ---
    
    def run_app(self, url, start, end, step):
        self.stop_requested = False
        self._log("="*40)
        self._log(f"Starting Download for URL: {url}")
        
        try:
            # 1. Get Paths and Check Cache
            novel_name, folder_path, links_path = self._get_paths_from_url(url)
            if not novel_name: return

            if not self._is_link_file_fresh(links_path):
                self._fetch_links(url, links_path)
                
            if not os.path.exists(links_path):
                self._log("[FATAL] Link file does not exist. Cannot continue.")
                return

            # 2. Get Total Chapters
            with open(links_path, 'r') as f:
                total_avail = len([l for l in f.readlines() if "http" in l])
                
            self._log(f"Total Chapters Available: {total_avail}")

            # 3. Download Content
            generated_pdfs, total_scraped = self._download_content(links_path, start, end, step)
            
            # 4. Merge
            self._merge_pdfs(generated_pdfs, folder_path, novel_name, start, end, total_avail)
            
            self._log("\n[All Operations Finished Successfully]")

        except Exception as e:
            self._log(f"\n[CRITICAL ERROR] Application failed: {e}")
            raise e # Raise to let GUI handle specific errors
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None