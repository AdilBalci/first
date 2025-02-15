import requests
import logging
from typing import Dict, List
import re
import random
import time
from bs4 import BeautifulSoup
import socks
import socket
from stem import Signal
from stem.control import Controller
import urllib3
urllib3.disable_warnings()

class HunterAnonymous:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.use_tor = self._check_tor_connection()
        self.session = requests.Session()
        
        if self.use_tor:
            self._setup_tor_connection()
            print("Tor bağlantısı aktif")
        else:
            print("Normal bağlantı kullanılıyor")
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }
        
    def _check_tor_connection(self) -> bool:
        """Tor bağlantısını kontrol et"""
        try:
            # SOCKS proxy test
            test_socket = socks.socksocket()
            test_socket.set_proxy(socks.SOCKS5, "127.0.0.1", 9150)
            test_socket.settimeout(5)
            test_socket.connect(("www.google.com", 80))
            test_socket.close()
            return True
        except:
            return False
    
    def _setup_tor_connection(self):
        """SOCKS proxy üzerinden Tor bağlantısı kur"""
        self.session.proxies = {
            'http': 'socks5h://127.0.0.1:9150',
            'https': 'socks5h://127.0.0.1:9150'
        }
    
    def _get_new_identity(self):
        """Tor üzerinden yeni IP al"""
        if not self.use_tor:
            return
            
        try:
            with Controller.from_port(port=9151) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
                time.sleep(2)
        except:
            pass
    
    def _make_request(self, url: str, retry: int = 3) -> str:
        """Anti-detection ile request at"""
        for _ in range(retry):
            try:
                time.sleep(random.uniform(1, 3))
                
                response = self.session.get(
                    url,
                    headers=self.headers,
                    timeout=10,
                    verify=False
                )
                
                if response.status_code == 200:
                    return response.text
                elif response.status_code in [403, 429]:
                    if self.use_tor:
                        self._get_new_identity()
                    continue
                    
            except Exception as e:
                self.logger.error(f"Request hatası ({url}): {str(e)}")
                if self.use_tor:
                    self._get_new_identity()
                else:
                    time.sleep(5)  # Rate limiting için bekle
        
        return ""
    
    def _extract_emails(self, text: str, domain: str) -> List[str]:
        """Gelişmiş email extraction"""
        emails = set()
        
        # Normal email pattern
        pattern = r'[\w\.-]+@' + domain.replace('.', '\.')
        found = re.findall(pattern, text, re.IGNORECASE)
        emails.update(found)
        
        # Obfuscated email pattern
        obfuscated = re.findall(r'[\w\.-]+\s*[\[\(]at\[\)\]\s*' + domain.replace('.', '\.'), text, re.IGNORECASE)
        cleaned = [e.replace('[at]', '@').replace('(at)', '@').replace(' ', '') for e in obfuscated]
        emails.update(cleaned)
        
        # JavaScript'te gizlenmiş email'ler
        js_emails = re.findall(r'[\'"]([\w\.-]+)[\'"]\s*\+?\s*[\'"]\@[\'"]?\s*\+?\s*[\'"]('+domain+')[\'"]', text)
        if js_emails:
            emails.update([f"{user}@{domain}" for user, _ in js_emails])
        
        return list(emails)
    
    def search_domain(self, domain: str) -> Dict:
        """Domain için email adresleri ara"""
        results = {
            'emails': []
        }
        
        try:
            domain = domain.replace('www.', '').strip()
            print(f"\n{domain} için email adresleri aranıyor...")
            
            paths = ['', 'contact', 'iletisim', 'about', 'hakkimizda', 'team', 'contact-us']
            
            for path in paths:
                url = f"https://{domain}/{path}"
                print(f"URL kontrol ediliyor: {url}")
                
                content = self._make_request(url)
                if not content:
                    continue
                
                found_emails = self._extract_emails(content, domain)
                
                for email in found_emails:
                    if email not in results['emails']:
                        results['emails'].append(email)
                        print(f"Email bulundu: {email}")
                
                if len(results['emails']) >= 5:
                    break
            
        except Exception as e:
            self.logger.error(f"Tarama hatası: {str(e)}")
        
        return results 