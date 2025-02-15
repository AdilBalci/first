import requests
import time
from typing import Dict, List, Set
import logging
import random
import json
from bs4 import BeautifulSoup
import re
import base64
from utils.proxy_manager import ProxyManager

class MultiFinder:
    def __init__(self):
        self.session = requests.Session()
        self.proxy_manager = ProxyManager()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1'
        }
        self.logger = logging.getLogger(__name__)
        
    def _make_request(self, url, headers=None):
        proxy = self.proxy_manager.get_proxy()
        try:
            response = self.session.get(
                url,
                headers=headers or self.headers,
                proxies=proxy,
                timeout=10
            )
            return response
        except:
            self.proxy_manager.mark_proxy_failed(proxy)
            return None
        
    def _try_hunter_io(self, domain: str, max_retries: int = 2) -> Set[str]:
        """Hunter.io demo kullan (optimize edilmiş)"""
        emails = set()
        
        # Sadece en etkili yaklaşımı dene
        approach = {
            'base_url': 'https://hunter.io',
            'search_path': f'/search/{domain}',
            'demo_path': f'/try/search/{domain}'
        }
        
        try:
            # Direkt demo sayfasına git
            demo_url = f"{approach['base_url']}{approach['demo_path']}"
            response = self._make_request(demo_url)
            
            if response and response.status_code == 200:
                # Hızlı parsing
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Sadece en yaygın pattern'leri kontrol et
                patterns = [
                    ('div', {'data-email': True}),
                    ('a', {'href': lambda x: x and 'mailto:' in x})
                ]
                
                for tag, attrs in patterns:
                    elements = soup.find_all(tag, attrs)
                    for element in elements:
                        if 'data-email' in element.attrs:
                            email = element['data-email']
                        elif 'href' in element.attrs:
                            email = element['href'].replace('mailto:', '')
                            
                        if '@' in email and domain in email:
                            emails.add(email)
                
                if emails:
                    print(f"Hunter.io: {len(emails)} email bulundu")
                    
        except Exception as e:
            print(f"Hunter.io hatası: {str(e)}")
        
        return emails
        
    def _try_rocketreach(self, domain: str) -> Set[str]:
        """RocketReach demo kullan"""
        emails = set()
        
        # Farklı yaklaşımlar
        approaches = [
            # Yaklaşım 1: Company profile
            {
                'base_url': 'https://rocketreach.co',
                'search_path': f'/company/{domain.split(".")[0]}',
                'demo_path': '/emails'
            },
            # Yaklaşım 2: API endpoint
            {
                'base_url': 'https://api.rocketreach.co',
                'search_path': '/v2/company/lookup',
                'demo_path': '/v2/company/emails'
            },
            # Yaklaşım 3: Domain search
            {
                'base_url': 'https://rocketreach.co',
                'search_path': f'/domain/{domain}',
                'demo_path': '/trial'
            }
        ]
        
        for approach in approaches:
            try:
                # 1. Ana sayfadan cookie al
                self.session.get(approach['base_url'], headers=self.headers)
                time.sleep(random.uniform(10, 15))
                
                # 2. Company sayfasına git
                search_url = f"{approach['base_url']}{approach['search_path']}"
                response = self.session.get(search_url, headers={
                    **self.headers,
                    'Referer': approach['base_url']
                })
                
                # 3. Demo sayfasına git
                if approach['demo_path']:
                    demo_url = f"{search_url}{approach['demo_path']}"
                    response = self.session.get(demo_url, headers={
                        **self.headers,
                        'Referer': search_url
                    })
                
                if response.status_code == 200:
                    # JSON response kontrolü
                    try:
                        data = response.json()
                        if 'emails' in data:
                            emails.update(data['emails'])
                    except:
                        pass
                    
                    # HTML parsing
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Email pattern'leri
                    patterns = [
                        ('div', {'class': ['email-container', 'contact-info']}),
                        ('span', {'class': ['email-text', 'contact-email']}),
                        ('td', {'data-original-email': True}),
                        ('a', {'href': lambda x: x and 'mailto:' in x}),
                        ('*', {'data-email': True})
                    ]
                    
                    for tag, attrs in patterns:
                        elements = soup.find_all(tag, attrs)
                        for element in elements:
                            # Attribute'lardan email bul
                            for attr in ['data-email', 'data-original-email', 'href']:
                                if attr in element.attrs:
                                    email = element[attr].replace('mailto:', '')
                                    if '@' in email and domain in email:
                                        emails.add(email)
                            
                            # Text içeriğini kontrol et
                            email = element.get_text().strip()
                            if '@' in email and domain in email:
                                emails.add(email)
                    
                    # JavaScript içinde gizlenmiş emailleri ara
                    scripts = soup.find_all('script')
                    for script in scripts:
                        script_text = str(script)
                        
                        # Base64 encoded emailleri dene
                        try:
                            encoded_patterns = re.findall(r'base64,([^"\']+)', script_text)
                            for encoded in encoded_patterns:
                                try:
                                    decoded = base64.b64decode(encoded).decode('utf-8')
                                    if '@' in decoded and domain in decoded:
                                        emails.add(decoded)
                                except:
                                    continue
                        except:
                            pass
                        
                        # Obfuscated emailleri dene
                        email_parts = re.findall(r'[\'"]([\w\.-]+)[\'"]\s*\+?\s*[\'"]\@[\'"]?\s*\+?\s*[\'"]('+domain+')', script_text)
                        for parts in email_parts:
                            email = f"{parts[0]}@{parts[1]}"
                            emails.add(email)
                
                if emails:
                    print(f"RocketReach: {len(emails)} email bulundu (Yaklaşım {approaches.index(approach)+1})")
                    break
                    
                time.sleep(random.uniform(10, 15))
                
            except Exception as e:
                print(f"RocketReach hatası (Yaklaşım {approaches.index(approach)+1}): {str(e)}")
                continue
        
        return emails
        
    def _try_snov_io(self, domain: str) -> Set[str]:
        """Snov.io demo kullan (optimize edilmiş)"""
        emails = set()
        
        # Direkt API endpoint'i dene
        url = f"https://app.snov.io/domain-search?name={domain}"
        
        try:
            response = self._make_request(url)
            
            if response and response.status_code == 200:
                # Hızlı parsing
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Sadece email içeren elementleri bul
                email_elements = soup.find_all(['div', 'span', 'a'], 
                    class_=lambda x: x and 'email' in str(x).lower())
                
                for element in email_elements:
                    email = element.get_text().strip()
                    if '@' in email and domain in email:
                        emails.add(email)
                
                if emails:
                    print(f"Snov.io: {len(emails)} email bulundu")
                    
        except Exception as e:
            print(f"Snov.io hatası: {str(e)}")
        
        return emails

    def _try_findthatlead(self, domain: str) -> Set[str]:
        """FindThatLead demo kullan"""
        emails = set()
        
        # Farklı yaklaşımlar
        approaches = [
            # Yaklaşım 1: Domain search
            {
                'base_url': 'https://findthatlead.com',
                'search_path': '/domain-search',
                'demo_path': f'?domain={domain}'
            },
            # Yaklaşım 2: API endpoint
            {
                'base_url': 'https://api.findthatlead.com',
                'search_path': '/v2/company-emails',
                'demo_path': '/trial'
            }
        ]
        
        for approach in approaches:
            try:
                # 1. Ana sayfadan cookie al
                self.session.get(approach['base_url'], headers=self.headers)
                time.sleep(random.uniform(10, 15))
                
                # 2. Search sayfasına git
                search_url = f"{approach['base_url']}{approach['search_path']}"
                response = self.session.get(search_url, headers={
                    **self.headers,
                    'Referer': approach['base_url']
                })
                
                # 3. Demo sayfasına git
                if approach['demo_path']:
                    demo_url = f"{search_url}{approach['demo_path']}"
                    response = self.session.get(demo_url, headers={
                        **self.headers,
                        'Referer': search_url
                    })
                
                if response.status_code == 200:
                    # HTML parsing
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Email pattern'leri
                    patterns = [
                        ('div', {'class': ['email-container', 'email-result']}),
                        ('span', {'class': ['email-text', 'email-value']}),
                        ('td', {'data-email': True}),
                        ('*', {'data-original-email': True})
                    ]
                    
                    for tag, attrs in patterns:
                        elements = soup.find_all(tag, attrs)
                        for element in elements:
                            # Email attributelerini kontrol et
                            for attr in ['data-email', 'data-original-email']:
                                if attr in element.attrs:
                                    email = element[attr]
                                    if '@' in email and domain in email:
                                        emails.add(email)
                            
                            # Text içeriğini kontrol et
                            email = element.get_text().strip()
                            if '@' in email and domain in email:
                                emails.add(email)
                    
                    if emails:
                        print(f"FindThatLead: {len(emails)} email bulundu")
                        break
                    
                    time.sleep(random.uniform(10, 15))
                    
            except Exception as e:
                print(f"FindThatLead hatası: {str(e)}")
                continue
        
        return emails

    def _try_skrapp(self, domain: str) -> Set[str]:
        """Skrapp.io demo kullan"""
        emails = set()
        
        # Farklı yaklaşımlar
        approaches = [
            # Yaklaşım 1: Domain search
            {
                'base_url': 'https://skrapp.io',
                'search_path': '/domain-search',
                'demo_path': f'?domain={domain}'
            },
            # Yaklaşım 2: API endpoint
            {
                'base_url': 'https://api.skrapp.io',
                'search_path': '/v2/domain',
                'demo_path': '/trial'
            }
        ]
        
        for approach in approaches:
            try:
                # 1. Ana sayfadan cookie al
                self.session.get(approach['base_url'], headers=self.headers)
                time.sleep(random.uniform(10, 15))
                
                # 2. Search sayfasına git
                search_url = f"{approach['base_url']}{approach['search_path']}"
                response = self.session.get(search_url, headers={
                    **self.headers,
                    'Referer': approach['base_url']
                })
                
                # 3. Demo sayfasına git
                if approach['demo_path']:
                    demo_url = f"{search_url}{approach['demo_path']}"
                    response = self.session.get(demo_url, headers={
                        **self.headers,
                        'Referer': search_url
                    })
                
                if response.status_code == 200:
                    # HTML parsing
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Email pattern'leri
                    patterns = [
                        ('div', {'class': ['email-box', 'email-result']}),
                        ('span', {'class': ['email', 'email-value']}),
                        ('td', {'data-email': True}),
                        ('*', {'data-original-email': True})
                    ]
                    
                    for tag, attrs in patterns:
                        elements = soup.find_all(tag, attrs)
                        for element in elements:
                            # Email attributelerini kontrol et
                            for attr in ['data-email', 'data-original-email']:
                                if attr in element.attrs:
                                    email = element[attr]
                                    if '@' in email and domain in email:
                                        emails.add(email)
                            
                            # Text içeriğini kontrol et
                            email = element.get_text().strip()
                            if '@' in email and domain in email:
                                emails.add(email)
                    
                    if emails:
                        print(f"Skrapp.io: {len(emails)} email bulundu")
                        break
                    
                    time.sleep(random.uniform(10, 15))
                    
            except Exception as e:
                print(f"Skrapp.io hatası: {str(e)}")
                continue
        
        return emails

    def search_domain(self, domain: str):
        results = {
            'emails': set(),
            'sources': []
        }
        
        # Sadece hunter.io kullanalım ve düzgün simüle edelim
        try:
            print(f"\n{domain} için arama yapılıyor...")
            
            # 1. Ana sayfaya git ve biraz bekle
            self.session.get("https://hunter.io", headers=self.headers)
            time.sleep(random.uniform(2, 4))
            
            # 2. Login sayfasına git
            login_page = self.session.get("https://hunter.io/users/sign_in", headers=self.headers)
            time.sleep(random.uniform(1, 2))
            
            # 3. Mouse hareketlerini simüle et
            # (Bu kısım sadece göstermelik, gerçekte bir etkisi yok)
            
            # 4. Login ol (gerçek hesap bilgileri ile)
            login_data = {
                'email': 'your_email@example.com',  # Gerçek hesap bilgileriniz
                'password': 'your_password'         # Gerçek hesap bilgileriniz
            }
            self.session.post("https://hunter.io/users/sign_in", data=login_data, headers=self.headers)
            time.sleep(random.uniform(2, 3))
            
            # 5. Domain search yap
            search_url = f"https://hunter.io/v2/domain-search?domain={domain}"
            response = self.session.get(search_url, headers=self.headers)
            
            if response.status_code == 200:
                # Email'leri topla
                soup = BeautifulSoup(response.text, 'html.parser')
                email_elements = soup.find_all(['span', 'div'], class_=lambda x: x and 'email' in x.lower())
                
                for element in email_elements:
                    email = element.get_text().strip()
                    if '@' in email and domain in email:
                        results['emails'].add(email)
                
                if results['emails']:
                    results['sources'].append('hunter.io')
                    print(f"Hunter.io: {len(results['emails'])} email bulundu")
                    
        except Exception as e:
            print(f"Hunter.io hatası: {str(e)}")
        
        return results

# Test
if __name__ == "__main__":
    # SSL uyarılarını kapat
    import urllib3
    urllib3.disable_warnings()
    
    # Test domain
    test_domain = "etiya.com"
    print(f"\n{test_domain} domain'i için email adresleri aranıyor...\n")
    
    finder = MultiFinder()
    results = finder.search_domain(test_domain)
    
    print("\nToplam bulunan email'ler:")
    for email in sorted(results['emails']):
        print(f"- {email}") 