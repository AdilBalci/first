from .base_finder import BaseEmailFinder
from typing import Dict, List
import requests
import logging
from utils.config import VOILA_NORBERT_API_KEY

class VoilaNorbertFinder(BaseEmailFinder):
    """Voila Norbert API entegrasyonu"""
    
    def __init__(self):
        super().__init__()
        self.api_key = VOILA_NORBERT_API_KEY
        self.base_url = "https://api.voilanorbert.com/2018-01-08"
        self.logger = logging.getLogger(__name__)
    
    def find_emails(self, domain: str) -> Dict[str, List[str]]:
        """Domain için email adresleri arar"""
        results = {
            'confirmed': [],
            'possible': []
        }
        
        if not self.api_key:
            self.logger.warning("Voila Norbert API anahtarı bulunamadı")
            return results
            
        try:
            # Domain search endpoint'ini çağır
            headers = {'Authorization': f'Bearer {self.api_key}'}
            response = requests.get(
                f"{self.base_url}/search/domain",
                headers=headers,
                params={'domain': domain}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Bulunan emailleri işle
                for result in data.get('data', []):
                    email = result.get('email')
                    if email:
                        if result.get('score', 0) >= 80:
                            results['confirmed'].append(email)
                        else:
                            results['possible'].append(email)
                            
            else:
                self.logger.error(f"Voila Norbert API hatası: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Voila Norbert sorgu hatası: {str(e)}")
        
        return results 