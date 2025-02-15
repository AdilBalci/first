import os
import pandas as pd
from openpyxl import load_workbook

def verileri_birlestir(input_path, output_path):
    try:
        # 1. Gelişmiş dosya kontrolleri
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"{input_path} dosyası bulunamadı!")
        
        # 2. Veri okuma iyileştirmeleri
        df = pd.read_excel(
            input_path,
            header=None,
            engine='openpyxl',
            keep_default_na=False,
            dtype=str
        )
        
        # 3. Veri işleme optimizasyonu
        tum_veriler = (
            df.stack()
            .astype(str)
            .str.replace(r'\s+', ' ', regex=True)  # Çoklu boşlukları tek boşluğa çevir
            .str.strip()
            .replace(['', 'nan', 'None'], pd.NA)
            .dropna()
            .drop_duplicates()
            .reset_index(drop=True)
        )
        
        # 4. Gelişmiş terminal çıktısı
        print("\n--- ÖNİZLEME (İlk 5 Kayıt) ---")
        for i, deger in tum_veriler.head().items():
            print(f"{i+1}. {deger}")
            
        print("\n--- ÖNİZLEME (Son 5 Kayıt) ---")
        for i, deger in tum_veriler.tail().items():
            print(f"{len(tum_veriler)-4 + i}. {deger}")
            
        print(f"\nToplam Kayıt Sayısı: {len(tum_veriler)}")
        
        onay = input("\nExcel dosyası oluşturmak için [E] tuşlayın, çıkmak için diğer tuşlar: ")
        if onay.lower() != 'e':
            print("İşlem iptal edildi.")
            return

        # 4. Güvenli yazma işlemi (DÜZELTİLMİŞ KISIM)
        with pd.ExcelWriter(
            output_path,
            engine='openpyxl',
            mode='w'  # 'a' yerine 'w' kullanılıyor
        ) as writer:
            # Mevcut sayfaları kontrol et
            if 'TopluVeriler' in writer.book.sheetnames:
                writer.book.remove(writer.book['TopluVeriler'])
            
            tum_veriler.to_excel(
                writer,
                index=False,
                header=['Tüm Veriler'],
                sheet_name='TopluVeriler'
            )
            
        print(f"İşlem başarılı! Yeni dosya: {os.path.abspath(output_path)}")

    except Exception as e:
        print(f"HATA DETAYI: {str(e)}")
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except:
                print("Hatalı dosya silinemedi!")

if __name__ == "__main__":
    input_file = '2021REZERVASYON TAKİP.xlsx'
    output_file = 'SONUC_REZERVASYON.xlsx'
    
    # Dosya varlık kontrolü
    if not os.path.exists(input_file):
        print(f"Lütfen {input_file} dosyasını betiğin yanına koyun!")
    else:
        verileri_birlestir(input_file, output_file)
    
    input("Çıkış için ENTER'a basın...") 