import requests
import time
from typing import Dict, List
import logging

class SnovIOFinder:
    """Snov.io API üzerinden email bulma"""
    
    def __init__(self):
        self.base_url = "https://api.snov.io/v2"
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0',
            'Content-Type': 'application/json'
        }
        self.logger = logging.getLogger(__name__)
    
    def _get_access(self) -> str:
        """API erişimi bypass"""
        try:
            # Session token al
            token_url = f"{self.base_url}/auth-user"
            response = self.session.get(token_url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json().get('access_token')
                
            # Plan B: Cookie manipulation
            cookies = self.session.cookies.get_dict()
            if 'snov_token' in cookies:
                return cookies['snov_token']
                
        except Exception as e:
            self.logger.error(f"Access bypass hatası: {str(e)}")
        
        return None
    
    def search_domain(self, domain: str) -> Dict[str, List[str]]:
        """Domain için email adresleri ara"""
        results = {
            'emails': [],
            'patterns': []
        }
        
        try:
            # Access bypass
            token = self._get_access()
            if token:
                self.headers['Authorization'] = f'Bearer {token}'
            
            # Domain search endpoint'i
            search_url = f"{self.base_url}/domain-emails"
            payload = {
                "domain": domain,
                "type": "all",
                "limit": 100
            }
            
            response = self.session.post(
                search_url,
                json=payload,
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Email'leri topla
                for email in data.get('emails', []):
                    if 'email' in email:
                        results['emails'].append(email['email'])
                    if 'pattern' in email:
                        results['patterns'].append(email['pattern'])
                        
            else:
                self.logger.error(f"Search hatası: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Snov.io hatası: {str(e)}")
        
        return results

# Test
if __name__ == "__main__":
    finder = SnovIOFinder()
    results = finder.search_domain("etiya.com")
    print("\nBulunan email'ler:")
    for email in results['emails']:
        print(f"- {email}") 