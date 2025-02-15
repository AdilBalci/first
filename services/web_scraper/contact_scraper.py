from .base_scraper import BaseScraper
from typing import List, Dict, Set
import re
import logging
from urllib.parse import urljoin, urlparse

class ContactScraper(BaseScraper):
    """İletişim bilgilerini toplayan scraper"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.contact_keywords = ['contact', 'iletisim', 'contact-us', 'about', 'hakkimizda']
    
    def find_contact_pages(self, soup, base_url: str) -> List[str]:
        """İletişim sayfası linklerini bulur"""
        contact_links = set()
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            text = link.get_text().lower()
            
            # Link veya metin içinde iletişim ile ilgili kelime var mı?
            if any(keyword in href or keyword in text for keyword in self.contact_keywords):
                # Tam URL oluştur
                full_url = urljoin(base_url, href)
                # Aynı domain'de mi kontrol et
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    contact_links.add(full_url)
        
        return list(contact_links)
    
    def extract_contact_info(self, soup) -> Dict:
        """Sayfadan iletişim bilgilerini çıkarır"""
        contact_info = {
            'emails': set(),
            'phones': set(),
            'addresses': set(),
            'social_media': {}
        }
        
        # Email adresleri
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        for element in soup.find_all(string=re.compile(email_pattern)):
            emails = re.findall(email_pattern, element.string)
            contact_info['emails'].update(emails)
        
        # Telefon numaraları
        phone_patterns = [
            r'\+90[0-9\s]{10,}',
            r'0\s*[0-9]{3}\s*[0-9]{3}\s*[0-9]{2}\s*[0-9]{2}',
            r'\([0-9]{3}\)\s*[0-9]{3}\s*[0-9]{2}\s*[0-9]{2}'
        ]
        
        for pattern in phone_patterns:
            for element in soup.find_all(string=re.compile(pattern)):
                phones = re.findall(pattern, element.string)
                contact_info['phones'].update(phones)
        
        # Adresler
        address_keywords = ['adres', 'address', 'location']
        for element in soup.find_all(['p', 'div']):
            text = element.get_text().lower().strip()
            if any(keyword in text for keyword in address_keywords):
                if len(text) > 20:  # Kısa metinleri ele
                    contact_info['addresses'].add(text)
        
        # Sosyal medya linkleri
        social_patterns = {
            'linkedin': r'linkedin\.com/company/[\w-]+',
            'twitter': r'twitter\.com/[\w-]+',
            'facebook': r'facebook\.com/[\w-]+',
            'instagram': r'instagram\.com/[\w-]+'
        }
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            for platform, pattern in social_patterns.items():
                if re.search(pattern, href):
                    contact_info['social_media'][platform] = href
        
        return contact_info
    
    def scrape(self, url: str) -> Dict:
        """Ana scraping metodu"""
        try:
            results = {
                'emails': set(),
                'phones': set(),
                'addresses': set(),
                'social_media': {},
                'source_pages': []
            }
            
            # Ana sayfayı çek
            soup = self.get_page(url)
            if not soup:
                return results
            
            # İletişim sayfalarını bul
            contact_pages = self.find_contact_pages(soup, url)
            contact_pages.append(url)  # Ana sayfayı da ekle
            
            # Tüm sayfaları tara
            for page_url in set(contact_pages):
                try:
                    self.logger.info(f"Sayfa taranıyor: {page_url}")
                    page_soup = self.get_page(page_url)
                    if page_soup:
                        info = self.extract_contact_info(page_soup)
                        
                        # Bilgileri birleştir
                        results['emails'].update(info['emails'])
                        results['phones'].update(info['phones'])
                        results['addresses'].update(info['addresses'])
                        results['social_media'].update(info['social_media'])
                        results['source_pages'].append(page_url)
                        
                except Exception as e:
                    self.logger.error(f"Sayfa tarama hatası ({page_url}): {str(e)}")
                    continue
            
            # Set'leri list'e çevir
            return {
                'emails': list(results['emails']),
                'phones': list(results['phones']),
                'addresses': list(results['addresses']),
                'social_media': results['social_media'],
                'source_pages': results['source_pages']
            }
            
        except Exception as e:
            self.logger.error(f"Scraping hatası: {str(e)}")
            return {
                'emails': [],
                'phones': [],
                'addresses': [],
                'social_media': {},
                'source_pages': []
            } 