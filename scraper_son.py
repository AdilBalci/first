import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService

BASE_URL = "https://gosbteknopark.com"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9'
}

def setup_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    
    # Firefox için binary yolu belirtme
    options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
    
    service = FirefoxService(GeckoDriverManager().install())
    return webdriver.Firefox(service=service, options=options)

def get_company_links():
    response = requests.get(f"{BASE_URL}/firmalarimiz/", headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    links = set()
    for a in soup.select('a.elementor-post__thumbnail__link[href*="/firmalarimiz/"]'):
        href = a.get('href')
        full_url = urljoin(BASE_URL, href)
        links.add(full_url)
    
    return list(links)

def get_company_details(url):
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Başlık için alternatif seçiciler
        title = (soup.select_one('h1.elementor-heading-title') or 
                soup.select_one('h1.entry-title') or 
                soup.select_one('h1.page-title'))
        
        # Web sitesi için çoklu seçenekler
        website = None
        for selector in [
            'a.elementor-button[href*="//"]',
            'a[target="_blank"]',
            'a:contains("Web Sitesi")'
        ]:
            if soup.select_one(selector):
                website = soup.select_one(selector)['href']
                break
        
        # İletişim bilgileri
        contact_text = soup.get_text().lower()
        phone = extract_info(contact_text, r'tel[:\s]*([0-9+ ()-]{10,})')
        email = extract_info(contact_text, r'[\w.-]+@[\w.-]+\.\w+')
        
        return {
            'name': title.text.strip() if title else 'İsim bulunamadı',
            'website': website or '',
            'phone': phone or '',
            'email': email or '',
            'source_url': url
        }
    
    except Exception as e:
        print(f"Hata ({url}): {str(e)}")
        return None

def extract_info(text, pattern):
    import re
    match = re.search(pattern, text)
    return match.group() if match else ''

def main():
    print("Firma linkleri toplanıyor...")
    company_links = get_company_links()
    print(f"Bulunan firma sayısı: {len(company_links)}")
    
    companies = []
    for idx, link in enumerate(company_links, 1):
        print(f"[{idx}/{len(company_links)}] İşleniyor: {link}")
        details = get_company_details(link)
        if details:
            companies.append(details)
        time.sleep(1.5)  # Sunucu yükünü azalt
    
    with open("gosb_firmalar_son.json", "w", encoding="utf-8") as f:
        json.dump(companies, f, ensure_ascii=False, indent=2)
    
    print(f"\nİşlem tamamlandı. Kaydedilen firma: {len(companies)}")

if __name__ == "__main__":
    main() 