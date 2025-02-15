import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin

BASE_URL = "https://gosbteknopark.com"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_soup(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Sayfa yüklenemedi: {url} - Hata: {e}")
        return None

def extract_company_info(card):
    name_elem = card.select_one('h3.company-title')
    website_elem = card.select_one('a[href*="//"]:not([href*="gosbteknopark"])')
    
    return {
        "name": name_elem.text.strip() if name_elem else "İsim bulunamadı",
        "website": website_elem['href'] if website_elem else "",
        "description": card.select_one('.company-excerpt').text.strip() if card.select_one('.company-excerpt') else ""
    }

def get_companies(category):
    soup = get_soup(f"{BASE_URL}/firmalarimiz/?category={category}")
    if not soup:
        return []
    
    companies = []
    for card in soup.select('.company-item'):
        company_info = extract_company_info(card)
        companies.append(company_info)
        time.sleep(0.5)  # Sunucu yükünü azaltmak için
    
    return companies

if __name__ == "__main__":
    try:
        print("Veri toplama başlıyor...")
        
        data = {
            "AR-GE Firmaları": get_companies("arge"),
            "Kuluçka Firmaları": get_companies("kuluçka")
        }
        
        with open("gosb_firmalar.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
            
        print(f"Toplam {len(data['AR-GE Firmaları']) + len(data['Kuluçka Firmaları'])} firma kaydedildi.")
        
    except Exception as e:
        print(f"Kritik hata: {str(e)}") 