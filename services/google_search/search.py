import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Set, Dict
import re
from urllib.parse import quote_plus
import time

class GoogleSearchService:
    """Google arama entegrasyonu"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
        }
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://www.google.com/search"
        self.delay = 2  # Aramalar arası bekleme süresi
    
    def search_emails(self, domain: str) -> Set[str]:
        """Domain için Google'da email adresleri arar"""
        found_emails = set()
        
        # Arama terimleri
        search_queries = [
            f'site:{domain} "@{domain}"',
            f'site:{domain} "email" OR "mail" OR "contact"',
            f'site:{domain} "iletişim" OR "e-posta"',
            f'site:linkedin.com "{domain}"'
        ]
        
        for query in search_queries:
            try:
                self.logger.info(f"Google araması: {query}")
                
                # Aramayı yap
                response = requests.get(
                    self.base_url,
                    params={
                        'q': query,
                        'num': 100  # Sayfa başına sonuç
                    },
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Sonuç metinlerini tara
                    for div in soup.find_all('div'):
                        text = div.get_text()
                        
                        # Email adreslerini bul
                        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
                        emails = re.findall(email_pattern, text)
                        
                        # Domain'e ait mailleri filtrele
                        for email in emails:
                            if domain in email.lower():
                                found_emails.add(email.lower())
                
                # Rate limiting
                time.sleep(self.delay)
                
            except Exception as e:
                self.logger.error(f"Google arama hatası: {str(e)}")
                continue
        
        return found_emails
    
    def find_social_profiles(self, company_name: str) -> Dict[str, str]:
        """Şirketin sosyal medya profillerini arar"""
        social_profiles = {}
        
        # Sosyal medya platformları
        platforms = {
            'linkedin': r'linkedin\.com/company/[\w-]+',
            'twitter': r'twitter\.com/[\w-]+',
            'facebook': r'facebook\.com/[\w-]+'
        }
        
        try:
            # Şirket adıyla ara
            query = f'"{company_name}" site:linkedin.com OR site:twitter.com OR site:facebook.com'
            
            response = requests.get(
                self.base_url,
                params={
                    'q': query,
                    'num': 10
                },
                headers=self.headers
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Linkleri kontrol et
                for a in soup.find_all('a', href=True):
                    href = a.get('href', '').lower()
                    
                    # Platform desenlerini kontrol et
                    for platform, pattern in platforms.items():
                        if re.search(pattern, href):
                            social_profiles[platform] = href
                            break
            
        except Exception as e:
            self.logger.error(f"Sosyal medya arama hatası: {str(e)}")
        
        return social_profiles 