import requests
from bs4 import BeautifulSoup
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class BaseScraper(ABC):
    """Temel web scraping sınıfı"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
    
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Verilen URL'den sayfa içeriğini çeker"""
        try:
            response = self.session.get(url, headers=self.headers, verify=False, timeout=10)
            if response.status_code == 200:
                return BeautifulSoup(response.text, 'html.parser')
            self.logger.warning(f"Sayfa yüklenemedi: {url} (Durum: {response.status_code})")
            return None
        except Exception as e:
            self.logger.error(f"Sayfa çekme hatası: {str(e)}")
            return None
    
    @abstractmethod
    def scrape(self, url: str) -> Dict:
        """Ana scraping metodu - alt sınıflar tarafından uygulanmalı"""
        pass 