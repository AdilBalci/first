import requests
import random
import logging
from typing import Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Agent:
    def __init__(self):
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
        # Basit retry stratejisi
        retry_strategy = Retry(
            total=2,
            connect=2,
            read=2,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        # Session ayarları
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        
        # Basit headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
            'Accept': 'text/html,*/*',
            'Connection': 'close'  # Keep-alive kullanma
        }
        
        self.session.headers.update(self.headers)
        self.session.verify = False
    
    def get(self, url: str, retry_count: int = None) -> Optional[requests.Response]:
        """GET isteği gönder"""
        # Kesinlikle HTTP kullan
        url = url.replace('https://', 'http://')
        
        try:
            response = self.session.get(
                url,
                timeout=5,  # Tek ve kısa timeout
                allow_redirects=True
            )
            
            if response.status_code == 200:
                return response
                
        except:
            pass
            
        return None
