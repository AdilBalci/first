from .base_finder import BaseEmailFinder
from typing import Dict, List
import requests
import logging
from utils.config import HUNTER_API_KEY

class HunterIOFinder(BaseEmailFinder):
    """Hunter.io API entegrasyonu"""
    
    def __init__(self):
        super().__init__()
        self.api_key = HUNTER_API_KEY
        self.base_url = "https://api.hunter.io/v2"
        self.logger = logging.getLogger(__name__)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 ...',
            'Accept': 'text/html,application/xhtml+xml...',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1'
        }
    
    def find_emails(self, domain: str) -> Dict[str, List[str]]:
        """Domain için email adresleri arar"""
        results = {
            'confirmed': [],
            'possible': []
        }
        
        if not self.api_key:
            self.logger.warning("Hunter.io API anahtarı bulunamadı")
            return results
            
        try:
            # Domain search endpoint'ini çağır
            response = requests.get(
                f"{self.base_url}/domain-search",
                params={
                    'domain': domain,
                    'api_key': self.api_key
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Bulunan emailleri işle
                for email in data['data']['emails']:
                    if email['confidence'] >= 75:
                        results['confirmed'].append(email['value'])
                    else:
                        results['possible'].append(email['value'])
                        
                # Email pattern'i bul
                if data['data']['pattern']:
                    results['pattern'] = data['data']['pattern']
                    
            else:
                self.logger.error(f"Hunter.io API hatası: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Hunter.io sorgu hatası: {str(e)}")
        
        return results 