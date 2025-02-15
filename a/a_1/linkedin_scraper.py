from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base_scraper import BaseScraper
from .data_processor import DataProcessor
from typing import Dict, Optional

class LinkedInScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.data_processor = DataProcessor()
        self.linkedin_login_url = "https://www.linkedin.com/login"
        
    def scrape_company_page(self, driver, url: str) -> Optional[Dict[str, Any]]:
        """LinkedIn firma sayfasından veri çıkar"""
        if not self._login(driver):
            return None
            
        driver.get(url)
        self.human_like_delay()
        
        try:
            company_data = {}
            
            # Firma adı
            name = self._get_company_name(driver)
            if name:
                company_data['name'] = name
                
            # Website
            website = self._get_company_website(driver)
            if website:
                company_data['website'] = website
                
            # Çalışanlar
            employees = self._get_employees(driver)
            if employees:
                company_data['employees'] = employees
                
            return self.data_processor.clean_company_data(company_data)
            
        except Exception as e:
            print(f"LinkedIn scraping hatası: {str(e)}")
            return None
            
    def _login(self, driver) -> bool:
        """LinkedIn'e giriş yap"""
        driver.get(self.linkedin_login_url)
        self.human_like_delay()
        
        try:
            # Kullanıcı adı ve şifre alanlarını doldur
            username = driver.find_element(By.ID, "username")
            password = driver.find_element(By.ID, "password")
            
            username.send_keys("your_username")
            password.send_keys("your_password")
            
            # Giriş butonuna tıkla
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            # Giriş başarılı mı kontrol et
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "global-nav"))
            )
            return True
            
        except Exception as e:
            print(f"LinkedIn giriş hatası: {str(e)}")
            return False
            
    def _get_company_name(self, driver) -> Optional[str]:
        """Firma adını al"""
        try:
            return driver.find_element(
                By.XPATH, 
                "//h1[contains(@class, 'org-top-card-summary__title')]"
            ).text
        except:
            return None
            
    def _get_company_website(self, driver) -> Optional[str]:
        """Firma websitesini al"""
        try:
            return driver.find_element(
                By.XPATH,
                "//a[contains(@class, 'org-top-card-summary-info__website')]"
            ).get_attribute("href")
        except:
            return None
            
    def _get_employees(self, driver) -> Optional[List[Dict[str, str]]]:
        """Çalışan bilgilerini al"""
        try:
            employees = []
            employee_elements = driver.find_elements(
                By.XPATH,
                "//li[contains(@class, 'org-people-profile-card__profile-item')]"
            )
            
            for element in employee_elements:
                name = element.find_element(
                    By.XPATH, ".//span[contains(@class, 'name')]"
                ).text
                
                title = element.find_element(
                    By.XPATH, ".//span[contains(@class, 'title')]"
                ).text
                
                employees.append({
                    'name': name,
                    'title': title
                })
                
            return employees
            
        except:
            return None
