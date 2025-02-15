# -*- coding: utf-8 -*-

import pandas as pd
import re
import sys
import os
from tqdm import tqdm  # İlerleme çubuğu için
from datetime import datetime

def debug_log(message):
    """Detaylı log kaydı"""
    with open('debug.log', 'a', encoding='utf-8') as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

def get_column_letter(col_idx):
    """Excel sütun harfi dönüşümü (0-based index)"""
    letters = []
    col_idx += 1  # 1-based'e çevir
    while col_idx > 0:
        col_idx, rem = divmod(col_idx - 1, 26)
        letters.append(chr(65 + rem))
    return ''.join(reversed(letters))

def test_regex(value):
    pattern = re.compile(
        r'(?!.*\d{4}-\d{2}-\d{2})'
        r'(?:\+?90\s?)?'
        r'(?:\(\d{3}\)\s?|\d{3}[\s-]?)'
        r'\d{3}[\s-]?\d{2}[\s-]?\d{2}'
        r'|\d{10,}', 
        re.IGNORECASE
    )
    return pattern.search(str(value))

def find_phone_columns(df, sample_size=50):
    """Telefon içeren sütunları otomatik bul"""
    phone_cols = []
    # Güncellenmiş regex pattern
    pattern = re.compile(
        r'(?<!\d)(?:\+?90\s?[-]?)?'  # +90 veya 0 ile başlayanlar
        r'(?:\(\d{3}\)\s?|\d{1,3}[-\.\s]?)'  # Alan kodu için esnek yapı
        r'(?:\d{3}[-\.\s]?){2}\d{2,4}'  # Ana numara bölümleri
        r'(?![\d-])'  # Sonrasında rakam/tire olmayacak
    )
    
    for col in tqdm(df.columns, desc="Sütunlar taranıyor"):
        # NaN ve NaT değerleri temizle
        values = df[col].dropna().astype(str).str.strip().tolist()
        values = [v for v in values if v not in ['NaT', 'nan', '']]
        
        if not values:
            debug_log(f"{get_column_letter(col)} sütunu: TAMAMEN BOŞ")
            continue
            
        debug_log(f"{get_column_letter(col)} sütunu örnekleri:\n{values[:3]}")
        
        match_count = 0
        for v in values[:sample_size]:
            # Gelişmiş temizleme ve normalizasyon
            clean_v = re.sub(r'[^\d+]', '', v)
            if pattern.search(clean_v):
                match_count += 1
                if match_count >= 3:
                    phone_cols.append(col)
                    print(f"✅ {get_column_letter(col)} sütununda telefon bulundu!")
                    break

    # Test caseleri için özel kontrol
    test_cases = [
        "BURAK ÇOLAK(2)0-536 817 26 26(700TL)NAKİT ODAMAX",
        "MERTCAN ŞAHİN 05434952276(2)ETKİN PROJE İNFO KEMAL SİDAR H/U",
        "BATUHAN BEY 05389319862(2)550TL NAKİT"
    ]
    
    print("\n🔍 Test Sonuçları:")
    for case in test_cases:
        matches = pattern.findall(case)
        print(f"Metin: {case[:30]}...")
        print(f"Bulunanlar: {matches}\n")

    return phone_cols

def test_regex():
    test_cases = [
        "Ahmet 0555 123 45 67",    # Beklenen: Eşleşme
        "(555) 1234567",           # Beklenen: Eşleşme  
        "555-123-45-67",           # Beklenen: Eşleşme
        "2023-01-01",              # Beklenen: Eşleşme YOK
        "5551234567"               # Beklenen: Eşleşme
    ]
    
    pattern = re.compile(
        r'(?!.*\d{4}-\d{2}-\d{2})'
        r'(\+?90\s?)?'
        r'(\(?\d{3}\)?\s?|\d{3}[\s\-]?)'
        r'\d{3}[\s\-]?\d{2}[\s\-]?\d{2}'
        r'|\b\d{10,}\b',
        re.IGNORECASE
    )
    
    for case in test_cases:
        match = pattern.search(case)
        print(f"'{case}': {'✅' if match else '❌'}")

def find_phones(text):
    """Metin içindeki tüm telefon numaralarını bul"""
    pattern = re.compile(
        r'(?:0|\+90)(?:\s?-?\d{3}){3,}\d{2,3}'
        r'|\d{3}[\s-]?\d{3}[\s-]?\d{4}'
        r'|\d{10,}'
    )
    return pattern.findall(str(text))

def main():
    # 1. Excel'i oku
    df = pd.read_excel('2021REZERVASYON TAKİP.xlsx', header=None)
    
    # 2. Tüm satırları tara
    kayitlar = []
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Tüm veri taranıyor"):
        try:
            # 3. Tüm hücreleri birleştir
            full_text = ' '.join([str(cell) for cell in row])
            
            # 4. Telefon numarası ara
            numbers = find_phones(full_text)
            
            # 5. Geçerli numaraları kaydet
            for tel in numbers:
                clean_tel = re.sub(r'\D', '', tel)
                if len(clean_tel) >= 10:
                    kayitlar.append([clean_tel[-10:]])  # Son 10 hane
                    break  # İlk numarayı al ve diğerlerini atla
        except:
            continue

    # 6. Sonuçları kaydet
    pd.DataFrame(kayitlar, columns=['Telefon']).to_excel('SONUÇLAR.xlsx', index=False)
    print(f"\n🎉 {len(kayitlar)} kayıt bulundu!")

if __name__ == "__main__":
    main() 