import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from utils.agent import Agent
import re

class CompanyScraper:
    def __init__(self):
        self.agent = Agent()
        self.logger = logging.getLogger(__name__)
    
    def get_company_links(self, base_url: str) -> List[str]:
        """Sayfadaki tüm firma linklerini topla"""
        try:
            response = self.agent.get(base_url)
            if not response:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            company_links = []
            
            # Tüm firma kartlarını bul
            company_cards = soup.find_all('div', class_='service-block_six')
            
            for card in company_cards:
                # Her karttaki linki bul
                link = card.find('a', class_='theme-btn')
                if link and link.get('href'):
                    href = link.get('href')
                    # Tam URL'yi oluştur
                    if not href.startswith(('http://', 'https://')):
                        href = f"http://www.yildizteknopark.com.tr{href}"
                    company_links.append(href)
            
            if company_links:
                self.logger.info(f"{len(company_links)} firma linki bulundu")
            else:
                # HTML içeriğini kontrol et
                self.logger.debug(f"HTML içeriği: {soup.prettify()[:500]}")
            
            return company_links
            
        except Exception as e:
            self.logger.error(f"Firma linkleri toplanırken hata: {str(e)}")
            return []
    
    def _get_company_details(self, url: str) -> Optional[Dict]:
        """Firma detaylarını ve web sitesini çek"""
        try:
            response = self.agent.get(url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Tablo içeriğini bul
            website = None
            tables = soup.find_all('table', class_='table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        header = cols[0].get_text(strip=True).lower()
                        if 'web' in header:
                            website = cols[1].get_text(strip=True)
                            # URL'yi temizle
                            website = website.replace('http://', '').replace('https://', '')
                            website = website.split('/')[0]  # Path'i kaldır
                            website = re.sub(r'^www\.', '', website)  # www. kaldır
                            website = website.strip()
                            
                            return {
                                'url': url,
                                'website': website,
                                'domain': website
                            }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Firma detayları çekilemedi ({url}): {str(e)}")
            return None 