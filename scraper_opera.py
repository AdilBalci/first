from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import json
import time
import os

# Opera için Chrome seçeneklerini kullanma
def setup_opera_driver():
    # Opera ayarları
    opera_path = r'C:\Users\adil\AppData\Local\Programs\Opera\opera.exe'
    driver_path = os.path.join(os.getcwd(), 'operadriver.exe')
    
    # Chrome seçenekleriyle Opera'yı yapılandır
    options = Options()
    options.binary_location = opera_path
    options.add_argument("--headless=new")  # Yeni headless mod
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3")
    
    # Service nesnesi oluştur
    service = Service(executable_path=driver_path)
    
    return webdriver.Chrome(
        service=service,
        options=options
    )

def get_company_details(driver, url):
    try:
        driver.get(url)
        time.sleep(1)  # Sayfanın yüklenmesini bekle
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Firma bilgilerini çek
        data = {
            'name': soup.select_one('h1.entry-title').text.strip(),
            'website': soup.select_one('a[target="_blank"]')['href'] if soup.select_one('a[target="_blank"]') else '',
            'phone': '',
            'email': ''
        }
        
        # İletişim bilgilerini ara
        for p in soup.select('div.elementor-text-editor p'):
            text = p.text.lower()
            if 'tel:' in text:
                data['phone'] = text.split('tel:')[-1].strip()
            if 'e-posta:' in text:
                data['email'] = text.split('e-posta:')[-1].strip()
        
        return data
    
    except Exception as e:
        print(f"Hata ({url}): {str(e)}")
        return None

def main():
    driver = setup_opera_driver()
    try:
        # Ana sayfadan linkleri topla
        driver.get("https://gosbteknopark.com/firmalarimiz/")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        company_links = [
            a['href'] for a in soup.select('a.elementor-post__thumbnail__link[href*="/firmalarimiz/"]')
        ]
        
        # Firma detaylarını topla
        results = []
        for link in company_links:
            print(f"İşleniyor: {link}")
            details = get_company_details(driver, link)
            if details:
                results.append(details)
            time.sleep(1)
        
        # Sonuçları kaydet
        with open("firmalar.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"\nToplam {len(results)} firma başarıyla kaydedildi!")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main() 