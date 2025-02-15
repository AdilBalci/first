import os
import pandas as pd
import re
from datetime import datetime

def dosya_sec():
    # Mevcut dizindeki Excel dosyalarını listele
    excel_dosyalari = [f for f in os.listdir() if f.endswith(('.xlsx', '.xls'))]
    
    if not excel_dosyalari:
        print("\nHATA: Bu klasörde Excel dosyası bulunamadı!")
        return None
    
    # Dosyaları listele
    print("\n=== MEVCUT EXCEL DOSYALARI ===")
    for i, dosya in enumerate(excel_dosyalari, 1):
        print(f"{i}. {dosya}")
    
    # Kullanıcıdan seçim iste
    while True:
        try:
            secim = int(input("\nİşlenecek dosyayı seçin (1-{}): ".format(len(excel_dosyalari))))
            if 1 <= secim <= len(excel_dosyalari):
                return excel_dosyalari[secim-1]
            print("Hatalı seçim! Lütfen tekrar deneyin.")
        except ValueError:
            print("Lütfen sadece sayı girin!")

def kisiler_topla(input_path):
    try:
        # 1. Excel dosyasını oku
        print(f"\nDosya okunuyor: {input_path}")
        df = pd.read_excel(
            input_path,
            header=None,
            dtype=str,
            keep_default_na=False
        )
        
        # 2. Tüm verileri düzleştir
        tum_veriler = df.stack().astype(str).str.strip()
        
        # 3. İsim/Soyisim ve Telefon Numaralarını Bul
        kisiler = []  # [isim, telefon] şeklinde kayıtlar için
        
        for veri in tum_veriler:
            # Boş verileri atla
            if not veri or veri.lower() in ['nan', 'none', '']:
                continue
            
            # Telefon numarası arama pattern'leri
            tel_patterns = [
                r'0?\s*5\d{2}\s*\d{3}\s*\d{2}\s*\d{2}',
                r'0?\d{10}',
                r'\+\d{11,12}'
            ]
            
            # İsim bul (parantez öncesi kısmı al)
            isim = veri.split('(')[0].strip()
            isim = re.sub(r'\d', '', isim).strip()
            isim = re.sub(r'[^\w\sÇĞİÖŞÜçğıöşü]', '', isim).strip()
            
            # Telefon bul
            tel = None
            for pattern in tel_patterns:
                match = re.search(pattern, veri)
                if match:
                    tel = match.group()
                    tel = re.sub(r'[^\d]', '', tel)
                    if len(tel) == 10:
                        tel = '0' + tel
                    break
            
            # Eğer geçerli bir isim ve telefon varsa listeye ekle
            if isim and tel and len(tel) >= 10:
                isim = ' '.join(word.capitalize() for word in isim.split())
                kisiler.append([isim, tel])
        
        # 4. Benzersiz kayıtları al ve sırala
        kisiler = [list(x) for x in set(tuple(x) for x in kisiler)]
        kisiler.sort()
        
        # 5. Terminal çıktısı
        print("\n=== BULUNAN KAYITLAR ===")
        for i, (isim, tel) in enumerate(kisiler, 1):
            print(f"{i}. {isim:<30} - {tel}")
            
        print(f"\nToplam: {len(kisiler)} kayıt bulundu.")
        
        # 6. Kaydetme onayı
        onay = input("\nBu kayıtları Excel'e kaydetmek istiyor musunuz? (E/H): ")
        if onay.lower() != 'e':
            print("İşlem iptal edildi.")
            return
        
        # 7. Excel'e kaydet
        simdi = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"MUSTERI_LISTESI_{simdi}.xlsx"
        
        df_sonuc = pd.DataFrame(kisiler, columns=['Müşteri İsmi', 'Telefon'])
        df_sonuc.to_excel(output_path, index=False, sheet_name='Müşteri Listesi')
            
        print(f"\nVeriler başarıyla kaydedildi: {output_path}")
        
    except Exception as e:
        print(f"\nHATA: {str(e)}")

def main():
    print("=" * 50)
    print("MÜŞTERİ BİLGİLERİ TOPLAMA PROGRAMI")
    print("=" * 50)
    
    while True:
        # Dosya seç
        input_file = dosya_sec()
        if not input_file:
            break
            
        # İşlemi başlat
        kisiler_topla(input_file)
        
        # Devam etmek istiyor mu?
        devam = input("\nBaşka dosya işlemek ister misiniz? (E/H): ")
        if devam.lower() != 'e':
            break
    
    print("\nProgram sonlandırılıyor...")
    input("Çıkmak için ENTER'a basın...")

if __name__ == "__main__":
    main() 