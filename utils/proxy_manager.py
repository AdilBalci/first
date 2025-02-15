import requests
from bs4 import BeautifulSoup
import random
import time

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.failed_proxies = set()
        self.last_update = 0
        self.update_interval = 300  # 5 dakikada bir güncelle
        self.max_failures = 3  # Bir proxy'nin maksimum hata sayısı
        self.proxy_failures = {}  # Her proxy'nin hata sayısını tutacak
        self.timeout = 5  # Timeout süresini düşür
        self.verify_ssl = False  # SSL doğrulamasını kapat
    
    def _update_proxies(self):
        """Proxy listesini güncelle"""
        try:
            # Free proxy listelerinden çek
            sources = [
                'https://free-proxy-list.net/',
                'https://www.sslproxies.org/',
                'https://www.us-proxy.org/'
            ]
            
            new_proxies = []
            
            for url in sources:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Proxy tablolarını bul
                for row in soup.find_all('tr'):
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        ip = cols[0].text.strip()
                        port = cols[1].text.strip()
                        if ip and port:
                            proxy = f"{ip}:{port}"
                            new_proxies.append({
                                'http': f'http://{proxy}',
                                'https': f'http://{proxy}'
                            })
            
            # Proxy listesini güncelle
            self.proxies = new_proxies
            self.failed_proxies.clear()
            self.last_update = time.time()
            
            print(f"{len(self.proxies)} proxy bulundu")
            
        except Exception as e:
            print(f"Proxy güncelleme hatası: {str(e)}")
    
    def get_proxy(self):
        """Çalışan bir proxy döndür"""
        if time.time() - self.last_update > self.update_interval:
            self._update_proxies()
        
        # Kullanılabilir proxy'leri filtrele
        available_proxies = []
        for proxy in self.proxies:
            proxy_str = f"{proxy.get('http', '')}_{proxy.get('https', '')}"
            if proxy_str not in self.failed_proxies:
                available_proxies.append(proxy)
        
        # Proxy kalmadıysa listeyi güncelle
        if not available_proxies:
            self._update_proxies()
            available_proxies = self.proxies
        
        return random.choice(available_proxies) if available_proxies else None
    
    def mark_proxy_failed(self, proxy):
        """Çalışmayan proxy'i işaretle"""
        if proxy:
            proxy_str = f"{proxy.get('http', '')}_{proxy.get('https', '')}"
            if proxy_str not in self.proxy_failures:
                self.proxy_failures[proxy_str] = 1
            else:
                self.proxy_failures[proxy_str] += 1
                
            if self.proxy_failures[proxy_str] >= self.max_failures:
                self.failed_proxies.add(proxy_str) 