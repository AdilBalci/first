from ..core import BaseEmailService
import requests
from typing import Set, Optional
import random
import string
import time
from bs4 import BeautifulSoup

class HunterIOService(BaseEmailService):
    """Hunter.io servisi"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.hunter.io/v2"
        
    def search_emails(self, domain: str) -> Set[str]:
        emails = set()
        
        try:
            # Direkt web sitesinden mail adresleri ara
            url = f"https://hunter.io/v2/domains-suggestion?domain={domain}"
            headers = self._get_headers()
            
            response = requests.get(
                url,
                headers=headers,
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    for item in data['data']:
                        if '@' in item:
                            emails.add(item)
                            self.logger.info(f"Mail bulundu: {item}")
            
            # Alternatif arama yöntemi
            search_url = f"https://hunter.io/v2/domain-search?domain={domain}"
            response = requests.get(
                search_url,
                headers=headers,
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Mail adreslerini ara
                email_elements = soup.find_all('div', {'class': 'email-field'})
                for element in email_elements:
                    email = element.get_text().strip()
                    if '@' in email and domain in email:
                        emails.add(email)
                        self.logger.info(f"Mail bulundu: {email}")
                        
        except Exception as e:
            self.logger.error(f"Hunter.io arama hatası: {str(e)}")
            
        return emails
    
    def _create_account(self) -> Optional[str]:
        """Yeni hesap oluştur ve API key döndür"""
        try:
            # Rastgele kullanıcı bilgileri oluştur
            name = ''.join(random.choices(string.ascii_lowercase, k=8))
            surname = ''.join(random.choices(string.ascii_lowercase, k=8))
            email = f"{name}.{surname}@gmail.com"
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            
            # Kayıt sayfasını aç
            session = requests.Session()
            response = session.get(
                "https://hunter.io/users/sign_up",
                headers=self._get_headers()
            )
            
            # CSRF token'ı al
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']
            
            # Hesap oluştur
            data = {
                'user[email]': email,
                'user[first_name]': name.capitalize(),
                'user[last_name]': surname.capitalize(),
                'user[password]': password,
                'authenticity_token': csrf_token
            }
            
            response = session.post(
                "https://hunter.io/users",
                data=data,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                # API key'i al
                response = session.get(
                    "https://hunter.io/api_keys",
                    headers=self._get_headers()
                )
                
                soup = BeautifulSoup(response.text, 'html.parser')
                api_key = soup.find('input', {'id': 'api_key'})['value']
                
                self.logger.info(f"Yeni hesap oluşturuldu: {email}")
                return api_key
                
        except Exception as e:
            self.logger.error(f"Hesap oluşturma hatası: {str(e)}")
            
        return None 