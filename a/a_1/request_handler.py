import time
import random
import requests
from typing import Optional, Dict, Any
from .proxy_manager import ProxyManager

class RequestHandler:
    def __init__(self, proxy_manager: ProxyManager):
        self.proxy_manager = proxy_manager
        self.max_retries = 3
        self.base_timeout = 30
        
    def make_request(self, url: str, headers: Dict[str, str]) -> Optional[requests.Response]:
        """HTTP isteği yap ve sonucu döndür"""
        for attempt in range(self.max_retries):
            try:
                proxy = self.proxy_manager.get_random_proxy()
                timeout = self._calculate_timeout()
                
                response = requests.get(
                    url,
                    headers=headers,
                    proxies=proxy,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    return response
                else:
                    self._handle_error(response.status_code, url)
                    
            except requests.exceptions.RequestException as e:
                self._handle_exception(e, url)
                if proxy:
                    self.proxy_manager.mark_bad_proxy(proxy['http'])
                
            self._wait_before_retry(attempt)
            
        return None
        
    def _calculate_timeout(self) -> float:
        """Rastgele timeout süresi hesapla"""
        return self.base_timeout + random.uniform(0.5, 2.0)
        
    def _handle_error(self, status_code: int, url: str) -> None:
        """HTTP hatalarını işle"""
        if status_code == 404:
            print(f"404 Hatası: {url} bulunamadı")
        elif status_code == 429:
            print("Rate limit aşıldı, bekleniyor...")
            time.sleep(60)
            
    def _handle_exception(self, e: Exception, url: str) -> None:
        """İstek istisnalarını işle"""
        print(f"İstek hatası ({url}): {str(e)}")
        
    def _wait_before_retry(self, attempt: int) -> None:
        """Yeniden denemeden önce bekle"""
        wait_time = (attempt + 1) * 10 + random.uniform(0.5, 2.0)
        time.sleep(wait_time)
