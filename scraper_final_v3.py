import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin

BASE_URL = "https://gosbteknopark.com"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}

def get_company_details(url):
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Güncellenmiş başlık seçici
        title = soup.select_one('h1.elementor-heading-title') or soup.select_one('h1.page-title')
        
        # Web sitesi için alternatif seçiciler
        website = soup.select_one('a.elementor-button[href*="//"]') or soup.select_one('a[target="_blank"]')
        
        # İletişim bilgileri için yeni yaklaşım
        contact_section = soup.find(lambda tag: 'İletişim' in tag.text and tag.name in ['div', 'section'])
        phone, email = '', ''
        
        if contact_section:
            for line in contact_section.stripped_strings:
                if 'Tel:' in line:
                    phone = line.split('Tel:')[-1].strip()
                if 'E-Posta:' in line:
                    email = line.split('E-Posta:')[-1].strip()

        return {
            'name': title.text.strip() if title else 'İsim bulunamadı',
            'website': website['href'] if website else '',
            'phone': phone,
            'email': email
        }
    
    except Exception as e:
        print(f"Hata ({url}): {str(e)}")
        return None

def main():
    response = requests.get(f"{BASE_URL}/firmalarimiz/", headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Debug: Tüm linkleri yazdır
    all_links = soup.select('a')
    print(f"Toplam link sayısı: {len(all_links)}")
    print("Örnek linkler:")
    for link in all_links[:10]:
        print(f"- {link.get('href')}")
    
    # Firma link filtreleme
    company_links = [
        urljoin(BASE_URL, a['href']) 
        for a in soup.select('a.elementor-post__thumbnail__link[href*="/firmalarimiz/"]')
    ]
    print(f"\nBulunan firma link sayısı: {len(company_links)}")
    
    all_companies = []
    
    for link in company_links:
        print(f"İşleniyor: {link}")
        details = get_company_details(link)
        if details:
            all_companies.append(details)
        time.sleep(1)
    
    with open("gosb_firmalar_son.json", "w", encoding="utf-8") as f:
        json.dump(all_companies, f, ensure_ascii=False, indent=2)
    
    print(f"\nBaşarıyla kaydedilen firma sayısı: {len(all_companies)}")

if __name__ == "__main__":
    main() 