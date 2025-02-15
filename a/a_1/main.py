import argparse
from .linkedin_scraper import LinkedInScraper
from .google_scraper import GoogleScraper
from .data_processor import DataProcessor
from .proxy_manager import ProxyManager
from selenium import webdriver
from typing import List, Dict
import json
import os

class ScraperApp:
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.data_processor = DataProcessor()
        self.linkedin_scraper = LinkedInScraper()
        self.google_scraper = GoogleScraper()
        
    def run(self, company_names: List[str], output_dir: str):
        """Ana çalıştırma metodu"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # WebDriver ayarları
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Proxy ayarları
        proxy = self.proxy_manager.get_proxy()
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
            
        driver = webdriver.Chrome(options=options)
        
        try:
            results = []
            for company_name in company_names:
                print(f"\n{company_name} için veri toplanıyor...")
                
                # Google'dan website bul
                website = self.google_scraper.find_company_website(driver, company_name)
                if not website:
                    print(f"{company_name} için website bulunamadı")
                    continue
                    
                # LinkedIn'den veri çek
                linkedin_data = self.linkedin_scraper.scrape_company_page(driver, website)
                if not linkedin_data:
                    print(f"{company_name} için LinkedIn verisi bulunamadı")
                    continue
                    
                # Veriyi temizle ve kaydet
                cleaned_data = self.data_processor.clean_company_data(linkedin_data)
                results.append(cleaned_data)
                
                # Dosyaya kaydet
                output_file = os.path.join(output_dir, f"{company_name}.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
                    
                print(f"{company_name} verileri başarıyla kaydedildi: {output_file}")
                
            return results
            
        finally:
            driver.quit()
            
def main():
    parser = argparse.ArgumentParser(description="Firma Bilgi Toplama Aracı")
    parser.add_argument(
        'companies',
        nargs='+',
        help='Aranacak firma isimleri (boşlukla ayrılmış)'
    )
    parser.add_argument(
        '-o', '--output',
        default='output',
        help='Çıktı dosyalarının kaydedileceği dizin (varsayılan: output)'
    )
    
    args = parser.parse_args()
    
    app = ScraperApp()
    results = app.run(args.companies, args.output)
    
    print(f"\nToplam {len(results)} firma için veri toplandı")

if __name__ == "__main__":
    main()
