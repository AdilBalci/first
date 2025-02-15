from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .base_scraper import BaseScraper
from .data_processor import DataProcessor
from typing import Dict, List, Optional

class GoogleScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.data_processor = DataProcessor()
        self.google_url = "https://www.google.com"
        
    def search_company(self, driver, query: str) -> Optional[List[Dict[str, str]]]:
        """Google'da firma araması yap ve sonuçları döndür"""
        driver.get(self.google_url)
        self.human_like_delay()
        
        try:
            # Arama kutusunu bul ve sorguyu gir
            search_box = driver.find_element(By.NAME, "q")
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            self.human_like_delay()
            
            # Sonuçları topla
            results = []
            result_elements = driver.find_elements(
                By.XPATH, "//div[contains(@class, 'g')]"
            )
            
            for element in result_elements:
                try:
                    title = element.find_element(
                        By.XPATH, ".//h3"
                    ).text
                    
                    url = element.find_element(
                        By.XPATH, ".//a"
                    ).get_attribute("href")
                    
                    description = element.find_element(
                        By.XPATH, ".//div[contains(@class, 'VwiC3b')]"
                    ).text
                    
                    results.append({
                        'title': title,
                        'url': url,
                        'description': description
                    })
                    
                except:
                    continue
                    
            return results
            
        except Exception as e:
            print(f"Google arama hatası: {str(e)}")
            return None
            
    def find_company_website(self, driver, company_name: str) -> Optional[str]:
        """Firmanın websitesini bul"""
        query = f"{company_name} official website"
        results = self.search_company(driver, query)
        
        if not results:
            return None
            
        # İlk 5 sonucu kontrol et
        for result in results[:5]:
            url = result['url']
            if self._is_company_website(url, company_name):
                return url
                
        return None
        
    def _is_company_website(self, url: str, company_name: str) -> bool:
        """URL'nin firma websitesi olup olmadığını kontrol et"""
        if not url:
            return False
            
        # URL'de firma adının geçtiğini kontrol et
        company_name_lower = company_name.lower()
        url_lower = url.lower()
        
        # Yaygın domain uzantılarını kontrol et
        common_domains = ['.com', '.com.tr', '.net', '.org']
        if any(ext in url_lower for ext in common_domains):
            if company_name_lower in url_lower:
                return True
                
        return False
