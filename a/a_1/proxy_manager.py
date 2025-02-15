import random
import requests
from typing import List, Optional, Dict

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.current_proxy = None
        self.proxy_timeout = 30
        
    def load_proxies(self, proxy_list: List[str]) -> None:
        """Proxy listesini yükle ve doğrula"""
        self.proxies = [p.strip() for p in proxy_list if p.strip()]
        self._validate_proxies()
        
    def _validate_proxies(self) -> None:
        """Proxy'leri test ederek geçerli olanları filtrele"""
        valid_proxies = []
        for proxy in self.proxies:
            if self._test_proxy(proxy):
                valid_proxies.append(proxy)
        self.proxies = valid_proxies
        
    def _test_proxy(self, proxy: str) -> bool:
        """Tek bir proxy'yi test et"""
        try:
            proxies = {'http': proxy, 'https': proxy}
            response = requests.get(
                'https://httpbin.org/ip',
                proxies=proxies,
                timeout=self.proxy_timeout
            )
            return response.status_code == 200
        except:
            return False
            
    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Rastgele bir proxy döndür"""
        if not self.proxies:
            return None
            
        proxy = random.choice(self.proxies)
        return {
            'http': proxy,
            'https': proxy
        }
        
    def mark_bad_proxy(self, proxy: str) -> None:
        """Kötü çalışan proxy'yi listeden çıkar"""
        if proxy in self.proxies:
            self.proxies.remove(proxy)
