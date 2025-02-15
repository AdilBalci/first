import requests
import time
from typing import Dict, List
import logging

class RocketReachFinder:
    """RocketReach API üzerinden email bulma"""
    
    def __init__(self):
        self.base_url = "https://api.rocketreach.co/v2"
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0',
            'Content-Type': 'application/json'
        }
        self.logger = logging.getLogger(__name__)
    
    def _bypass_auth(self) -> str:
        """API token bypass"""
        try:
            auth_url = f"{self.base_url}/login"
            payload = {
                "email": "test@test.com",
                "password": "test123"
            }
            
            # Login request'i manipüle et
            response = self.session.post(
                auth_url,
                json=payload,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json().get('token')
            
            # Plan B: Token extraction
            cookies = self.session.cookies.get_dict()
            if 'rr_jwt' in cookies:
                return cookies['rr_jwt']
                
        except Exception as e:
            self.logger.error(f"Auth bypass hatası: {str(e)}")
        
        return None
    
    def search_domain(self, domain: str) -> Dict[str, List[str]]:
        """Domain için email adresleri ara"""
        results = {
            'emails': [],
            'patterns': []
        }
        
        try:
            # Auth bypass
            token = self._bypass_auth()
            if token:
                self.headers['Authorization'] = f'Bearer {token}'
            
            # Domain search endpoint'i
            search_url = f"{self.base_url}/api/search"
            payload = {
                "domain": domain,
                "page_size": 100
            }
            
            response = self.session.post(
                search_url,
                json=payload,
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Email ve pattern'leri topla
                for profile in data.get('profiles', []):
                    if 'email' in profile:
                        results['emails'].append(profile['email'])
                    if 'email_pattern' in profile:
                        results['patterns'].append(profile['email_pattern'])
                        
            else:
                self.logger.error(f"Search hatası: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"RocketReach hatası: {str(e)}")
        
        return results

# Test
if __name__ == "__main__":
    finder = RocketReachFinder()
    results = finder.search_domain("etiya.com")
    print("\nBulunan email'ler:")
    for email in results['emails']:
        print(f"- {email}")
    print("\nEmail pattern'leri:")
    for pattern in results['patterns']:
        print(f"- {pattern}") 