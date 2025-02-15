import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://gosbteknopark.com"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}

def get_company_details(url):
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        details = {
            'name': soup.select_one('h1.entry-title').text.strip(),
            'website': '',
            'phone': '',
            'email': ''
        }
        
        # Web sitesi için farklı olasılıklar
        website_selectors = [
            'a.elementor-button:contains("Web Sitesi")',
            'a:has(i.fa-globe)',
            'a[href*="//"]:not([href*="gosbteknopark"])'
        ]
        
        for selector in website_selectors:
            if soup.select_one(selector):
                details['website'] = soup.select_one(selector)['href']
                break
        
        # İletişim bilgileri
        contact_info = soup.select('.elementor-text-editor p')
        for line in contact_info:
            text = line.text.lower()
            if 'tel:' in text:
                details['phone'] = text.split('tel:')[-1].strip()
            if 'mail:' in text:
                details['email'] = text.split('mail:')[-1].strip()
        
        return details
    
    except Exception as e:
        print(f"Detay sayfası hatası ({url}): {str(e)}")
        return None

def main():
    # Ana sayfadan firma linklerini çek
    main_page = requests.get(f"{BASE_URL}/firmalarimiz/", headers=HEADERS)
    soup = BeautifulSoup(main_page.text, 'html.parser')
    
    company_links = [
        a['href'] for a in soup.select('a.elementor-post__thumbnail__link')
        if '/firmalarimiz/' in a['href']
    ]
    
    all_companies = []
    
    for link in company_links:
        print(f"İşleniyor: {link}")
        company = get_company_details(link)
        if company:
            all_companies.append(company)
        time.sleep(1)  # Sunucu yükünü azaltmak için
    
    with open("gosb_firmalar_detayli.json", "w", encoding="utf-8") as f:
        json.dump(all_companies, f, ensure_ascii=False, indent=2)
    
    print(f"Toplam {len(all_companies)} firma detayı kaydedildi.")

if __name__ == "__main__":
    main() 