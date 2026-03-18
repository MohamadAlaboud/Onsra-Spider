import cv2
import numpy as np
import pytesseract
import imutils
import time
import random
import urllib.parse
import re
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import threading

# 🥷 HAYALET KÜTÜPHANE VE STEALTH AYARLARI
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "onsra_av_raporu.txt"

class OnsraSpiderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ONSRA - OSINT Spider v32 (The Mimic)")
        self.root.geometry("450x600")
        self.root.configure(bg="#050505")
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.root, text="🕸️ ONSRA SPIDER 🕸️", font=("Consolas", 24, "bold"), bg="#050505", fg="#ff0055").pack(pady=20)
        input_frame = tk.Frame(self.root, bg="#050505")
        input_frame.pack(pady=20, padx=30, fill="x")

        def create_input(parent, label_text, placeholder=""):
            row = tk.Frame(parent, bg="#050505")
            row.pack(fill="x", pady=8)
            tk.Label(row, text=label_text, width=12, anchor="w", bg="#050505", fg="#00ffcc", font=("Arial", 11, "bold")).pack(side="left")
            entry = tk.Entry(row, bg="#1a1a1a", fg="#ffffff", font=("Arial", 12), relief="flat")
            entry.pack(side="right", expand=True, fill="x", padx=(10, 0))
            if placeholder: entry.insert(0, placeholder)
            return entry

        self.ent_plaka = create_input(input_frame, "🎯 Hedef Plaka:", "34ABC123")
        self.ent_marka = create_input(input_frame, "🚘 Marka:", "Citroen")
        self.ent_seri = create_input(input_frame, "🏷️ Seri:", "C3")
        self.ent_renk = create_input(input_frame, "🎨 Renk:", "Bej")

        self.status = tk.Label(self.root, text="Sistem Hazır.", bg="#050505", fg="#aaaaaa", font=("Arial", 11))
        self.status.pack(pady=10)

        self.btn = tk.Button(self.root, text="🚀 MIMIC AVI BAŞLAT", command=self.start_spider, 
                             bg="#1a1a1a", fg="#ffaa00", font=("Arial", 13, "bold"), padx=20, pady=15)
        self.btn.pack(pady=10)

    def strict_plate_filter(self, text):
        pattern = re.compile(r'^[0-9]{2}[A-Z]{2,3}[0-9]{2,4}$')
        return bool(pattern.match(text))

    def master_ocr(self, image_path):
        try:
            img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            img = imutils.resize(img, width=1200)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            distort = cv2.bilateralFilter(gray, 11, 17, 17)
            thresh = cv2.adaptiveThreshold(distort, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            text = pytesseract.image_to_string(thresh, config=config)
            clean = "".join(e for e in text if e.isalnum()).upper()
            if self.strict_plate_filter(clean): return clean
            return ""
        except: return ""

    def human_scroll(self, driver):
        """İnsan gibi sayfayı aşağı yukarı kaydırarak bot tespitini atlatır."""
        try:
            scroll_amount = random.randint(300, 700)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(1.0, 2.5))
            driver.execute_script(f"window.scrollBy(0, -{scroll_amount // 2});")
        except: pass

    def start_spider(self):
        plaka = self.ent_plaka.get().strip().upper().replace(" ", "")
        arama = f"{self.ent_marka.get()} {self.ent_seri.get()} {self.ent_renk.get()}".strip()
        self.status.configure(text=f"Hedef: {plaka} İzleniyor...", fg="#00ff00")
        self.btn.configure(state="disabled")
        threading.Thread(target=self.run_spider, args=(plaka, arama), daemon=True).start()

    def run_spider(self, plaka, arama_metni):
        driver = None
        try:
            options = uc.ChromeOptions()
            options.add_argument(f"--user-data-dir={str(BASE_DIR / 'Onsra_Spider_Data_V32')}")
            options.add_argument("--disable-blink-features=AutomationControlled")
            driver = uc.Chrome(options=options, use_subprocess=True, version_main=145)
            wait = WebDriverWait(driver, 20)

            driver.get(f"https://www.sahibinden.com/kelime-ile-arama?query_text={urllib.parse.quote_plus(arama_metni)}")
            
            # Doğrulama / Giriş Döngüsü
            while True:
                curr = driver.current_url.lower()
                if "olagan-disi" in curr:
                    self.root.after(0, lambda: self.status.configure(text="🚨 IP BAN! UÇAK MODUNU AÇ KAPA", fg="#ff0000"))
                    time.sleep(3)
                elif "giris" in curr:
                    self.root.after(0, lambda: self.status.configure(text="🚨 LÜTFEN BİR KEZ GİRİŞ YAPIN", fg="#ffaa00"))
                    time.sleep(3)
                else:
                    break 

            self.root.after(0, lambda: self.status.configure(text="Linkler Toplanıyor...", fg="#00ffcc"))
            time.sleep(4)
            
            links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/ilan/']")
            urls = list(set([el.get_attribute("href") for el in links if "/ilan/" in el.get_attribute("href") and any(c.isdigit() for c in el.get_attribute("href"))]))

            if not urls:
                self.root.after(0, lambda: messagebox.showwarning("Sonuç", "Ağda ilan bulunamadı."))
                return

            foto_yolu = str(BASE_DIR / "temp_mimic.png")
            bulundu = False

            for i, url in enumerate(urls):
                self.root.after(0, lambda i=i, t=len(urls): self.status.configure(text=f"İNSAN SİMÜLASYONU: {i+1}/{t}...", fg="#ffff00"))
                driver.get(url)
                
                # Rastgele bekleme ve insan gibi Scroll yapma
                time.sleep(random.uniform(4.0, 7.0)) 
                self.human_scroll(driver)
                
                try:
                    if "olagan-disi" in driver.current_url:
                        self.root.after(0, lambda: messagebox.showerror("Engellendi", "IP Adresiniz engellendi. Uçak modunu aç-kapa yapıp tekrar deneyin."))
                        break
                        
                    if "bulunamıyor" in driver.page_source.lower():
                        continue

                    foto_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".classifiedDetailMainPhoto")))
                    foto_el.screenshot(foto_yolu)
                    
                    okunan = self.master_ocr(foto_yolu)
                    print(f"İlan {i+1} Analiz: {okunan if okunan else 'ELENDİ'}")
                                                                                 
                    if plaka in okunan:
                        bulundu = True
                        self.root.after(0, lambda: self.status.configure(text="🎯 HEDEF TESPİT EDİLDİ!", fg="#00ff00"))
                        numara_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#phoneInfoPart")))
                        numara_btn.click()
                        time.sleep(3)
                        satici = driver.find_element(By.CSS_SELECTOR, ".username-info-area h5").text
                        tel = driver.find_element(By.CSS_SELECTOR, ".phone-area span").text
                        res = f"PLAKA: {plaka} | SATICI: {satici} | TEL: {tel} | LINK: {url}"
                        
                        with open(LOG_FILE, "a", encoding="utf-8") as f:
                            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {res}\n")
                            
                        self.root.after(0, lambda r=res: messagebox.showinfo("🎯 BİNGO!", r))
                        break
                except: continue

            if not bulundu:
                self.root.after(0, lambda: messagebox.showwarning("Bitti", "Hedef plaka bulunamadı."))

        except Exception as e: print(f"Hata: {e}")
        finally:
            self.root.after(0, lambda: self.status.configure(text="Sistem Beklemede.", fg="#aaaaaa"))
            self.root.after(0, lambda: self.btn.configure(state="normal"))
            if driver: driver.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = OnsraSpiderGUI(root)
    root.mainloop()