import sys
import time
from multiprocessing import Pool, cpu_count
from openpyxl import load_workbook
from tqdm import tqdm
from itertools import product
import pythoncom
from win32com.client import Dispatch
import zipfile
import os
import xml.etree.ElementTree as ET
from pathlib import Path

def attempt_unlock(args):
    file_path, password = args
    try:
        wb = load_workbook(filename=file_path, password=str(password))
        wb.close()
        return password
    except Exception as e:
        return None

def generate_numeric_combinations(length):
    return (str(n).zfill(length) for n in range(10**length))

def crack_excel_password(excel_file, min_length=4, max_length=5):
    start_time = time.time()
    total_attempts = sum(10**l for l in range(min_length, max_length+1))
    
    with Pool(processes=cpu_count()) as pool:
        with tqdm(total=total_attempts, desc="Şifre Deneniyor", unit="try") as progress_bar:
            for length in range(min_length, max_length+1):
                combinations = ((excel_file, pwd) for pwd in generate_numeric_combinations(length))
                
                for result in pool.imap_unordered(attempt_unlock, combinations):
                    progress_bar.update(1)
                    if result:
                        pool.terminate()
                        print(f"\n✅ Şifre Başarıyla Kırıldı: {result}")
                        print(f"⏱️ Toplam Süre: {time.time() - start_time:.2f} saniye")
                        return result
    print("\n❌ Şifre bulunamadı! Parametreleri kontrol edin.")
    return None

def break_protection(file_path):
    pythoncom.CoInitialize()  # COM kütüphanesini başlat
    excel = Dispatch('Excel.Application')
    excel.Visible = False
    
    try:
        wb = excel.Workbooks.Open(file_path)
        for sheet in wb.Sheets:
            if sheet.ProtectContents:
                print(f"Koruma bulundu: {sheet.Name}")
                sheet.Unprotect("")
                if not sheet.ProtectContents:
                    print("Koruma başarıyla kaldırıldı!")
        wb.Save()
        wb.Close()
    finally:
        excel.Quit()
        pythoncom.CoUninitialize()

def remove_protection_via_zip(file_path):
    try:
        # 1. Dosyayı yedekle
        backup = file_path.replace(".xlsx", "_BACKUP.xlsx")
        Path(file_path).rename(backup)
        
        # 2. ZIP olarak aç
        with zipfile.ZipFile(backup, 'r') as zip_ref:
            zip_ref.extractall("temp_xlsx")
        
        # 3. Tüm sheet*.xml dosyalarını işle
        for sheet in Path("temp_xlsx/xl/worksheets").glob("sheet*.xml"):
            tree = ET.parse(sheet)
            root = tree.getroot()
            
            # Koruma etiketini bul ve sil
            for protection in root.findall(".//{*}sheetProtection"):
                root.remove(protection)
            
            tree.write(sheet, encoding="UTF-8", xml_declaration=True)
        
        # 4. Yeni dosyayı oluştur
        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for folder, _, files in os.walk("temp_xlsx"):
                for file in files:
                    file_path = os.path.join(folder, file)
                    zipf.write(file_path, os.path.relpath(file_path, "temp_xlsx"))
        
        # 5. Temizlik
        os.rename(backup, file_path)
        print("✔️ Koruma başarıyla kaldırıldı!")
        return True
        
    except Exception as e:
        print(f"❌ Hata oluştu: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file = sys.argv[1]
    else:
        file = input("Excel dosya yolu: ").strip('"')
    
    if file.endswith(".xlsx"):
        remove_protection_via_zip(file)
    else:
        print("❌ Sadece .xlsx dosyaları destekleniyor!")

# Python konsolunda test edin:
import win32com.client
print("Başarıyla yüklendi!")  # Hata almamalısınız 