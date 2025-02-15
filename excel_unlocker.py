import zipfile
import os
import glob
import xml.etree.ElementTree as ET
import shutil
import sys

NS = {
    'x': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
}

def repair_excel(file_path):
    try:
        # 1. Orijinal dosyayı yedekle
        backup = file_path.replace('.xlsx', '_CORRUPTED_BACKUP.xlsx')
        shutil.copyfile(file_path, backup)
        
        # 2. Geçici dizini temizle
        temp_dir = 'temp_excel_repaired'
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        
        # 3. ZIP'i düzgün aç
        with zipfile.ZipFile(file_path, 'r') as z:
            z.extractall(temp_dir)
        
        # 4. Tüm XML'leri düzenle
        for xml_file in glob.glob(os.path.join(temp_dir, '**/*.xml'), recursive=True):
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                # Workbook korumasını kaldır
                for prot in root.findall('.//x:workbookProtection', NS):
                    root.remove(prot)
                
                # Sheet korumalarını kaldır
                for prot in root.findall('.//x:sheetProtection', NS):
                    root.remove(prot)
                
                # Değişiklikleri kaydet
                tree.write(xml_file, encoding='UTF-8', xml_declaration=True)
            except ET.ParseError:
                continue  # XML olmayan dosyaları atla
        
        # 5. Yeni ZIP oluştur
        new_file = file_path.replace('.xlsx', '_REPAIRED.xlsx')
        with zipfile.ZipFile(new_file, 'w', zipfile.ZIP_DEFLATED) as z:
            for root_dir, _, files in os.walk(temp_dir):
                for file in files:
                    abs_path = os.path.join(root_dir, file)
                    rel_path = os.path.relpath(abs_path, temp_dir)
                    z.write(abs_path, rel_path)
        
        print(f"✅ Dosya başarıyla onarıldı: {new_file}")
        return True
    
    except Exception as e:
        print(f"❌ Kritik hata: {str(e)}")
        return False
    
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Kullanım: python excel_unlocker.py <dosya_yolu>")
        sys.exit(1)
    
    input_file = sys.argv[1].strip('"')
    if not input_file.endswith('.xlsx'):
        print("Sadece .xlsx dosyaları desteklenir!")
        sys.exit(1)
    
    repair_excel(input_file) 