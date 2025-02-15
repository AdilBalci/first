import requests
import random
import time
from utils.proxy_manager import ProxyManager

class Agent:
    def __init__(self):
        # Sabit user agent listesi kullanalım
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        self.proxy_manager = ProxyManager()
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_delay = 2
        self.max_delay = 5
    
    def _get_headers(self):
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def _wait(self):
        """İstekler arası rastgele bekleme süresi"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_delay:
            wait_time = random.uniform(self.min_delay, self.max_delay)
            time.sleep(wait_time)
        self.last_request_time = time.time()
    
    def get(self, url, retry_count=3, use_proxy=True):
        """Bot korumalı GET isteği"""
        for attempt in range(retry_count):
            try:
                self._wait()
                
                if use_proxy:
                    proxy = self.proxy_manager.get_proxy()
                else:
                    proxy = None
                    
                headers = self._get_headers()
                
                response = self.session.get(
                    url,
                    headers=headers,
                    proxies=proxy,
                    timeout=5
                )
                
                # Başarılı ise döndür
                if response.status_code == 200:
                    return response
                
                # Rate limit veya bot koruması varsa proxy değiştir
                if response.status_code in [403, 429]:
                    self.proxy_manager.mark_proxy_failed(proxy)
                    continue
                
            except Exception as e:
                print(f"Hata (Deneme {attempt+1}/{retry_count}): {str(e)}")
                if proxy:
                    self.proxy_manager.mark_proxy_failed(proxy)
                continue
        
        return None
