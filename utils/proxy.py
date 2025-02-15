import requests
from bs4 import BeautifulSoup
import random
import time
from typing import Dict, List, Optional
import logging
from utils.config import PROXY_TIMEOUT, PROXY_UPDATE_INTERVAL, PROXY_MAX_FAILURES

class ProxyManager:
    def __init__(self):
        self.proxies: List[Dict] = []
        self.failed_proxies: set = set()
        self.last_update = 0
        self.update_interval = PROXY_UPDATE_INTERVAL
        self.max_failures = PROXY_MAX_FAILURES
        self.proxy_failures: Dict[str, int] = {}
        self.timeout = PROXY_TIMEOUT
        self.logger = logging.getLogger(__name__)
        
        # Sabit proxy listesi
        self.static_proxies = [
            {'http': 'http://34.142.51.21:80', 'https': 'http://34.142.51.21:80'},
            {'http': 'http://34.84.56.140:80', 'https': 'http://34.84.56.140:80'},
            {'http': 'http://34.84.124.13:80', 'https': 'http://34.84.124.13:80'},
            {'http': 'http://34.85.199.178:80', 'https': 'http://34.85.199.178:80'},
            {'http': 'http://35.187.224.178:80', 'https': 'http://35.187.224.178:80'},
            {'http': 'http://35.220.167.144:80', 'https': 'http://35.220.167.144:80'},
            {'http': 'http://35.221.104.58:80', 'https': 'http://35.221.104.58:80'},
            {'http': 'http://35.221.104.219:80', 'https': 'http://35.221.104.219:80'},
            {'http': 'http://35.229.95.36:80', 'https': 'http://35.229.95.36:80'},
            {'http': 'http://35.229.95.219:80', 'https': 'http://35.229.95.219:80'}
        ]
        
        # İlk proxy listesini yükle
        self._update_proxies()
    
    def _format_proxy(self, ip: str, port: str) -> Dict[str, str]:
        """Proxy formatını düzenle"""
        proxy_str = f"{ip}:{port}"
        return {
            'http': f'http://{proxy_str}',
            'https': f'http://{proxy_str}'  # HTTPS için de HTTP protokolünü kullan
        }
    
    def _update_proxies(self) -> None:
        """Proxy listesini güncelle"""
        try:
            # Önce statik proxy'leri kullan
            self.proxies = self.static_proxies.copy()
            self.failed_proxies.clear()
            self.last_update = time.time()
            self.logger.info(f"{len(self.proxies)} proxy hazır")
            
            # Ek proxy'leri getir
            sources = [
                'https://proxylist.geonode.com/api/proxy-list?limit=100&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps&anonymityLevel=elite&anonymityLevel=anonymous',
                'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all'
            ]
            
            for url in sources:
                try:
                    response = requests.get(url, timeout=self.timeout)
                    if response.status_code == 200:
                        if 'geonode' in url:
                            data = response.json()
                            for proxy in data.get('data', []):
                                self.proxies.append(self._format_proxy(proxy['ip'], proxy['port']))
                        else:
                            proxy_list = response.text.strip().split('\n')
                            for proxy in proxy_list:
                                if ':' in proxy:
                                    ip, port = proxy.strip().split(':')
                                    self.proxies.append(self._format_proxy(ip, port))
                except Exception as e:
                    self.logger.error(f"Proxy kaynağı hatası ({url}): {str(e)}")
                    continue
            
            self.logger.info(f"Toplam {len(self.proxies)} proxy bulundu")
            
        except Exception as e:
            self.logger.error(f"Proxy güncelleme hatası: {str(e)}")
            # Hata durumunda sadece statik proxy'leri kullan
            self.proxies = self.static_proxies.copy()
    
    def get_proxy(self) -> Optional[Dict]:
        """Çalışan bir proxy döndür"""
        if time.time() - self.last_update > self.update_interval:
            self._update_proxies()
        
        available_proxies = [
            proxy for proxy in self.proxies 
            if f"{proxy.get('http', '')}_{proxy.get('https', '')}" not in self.failed_proxies
        ]
        
        if not available_proxies:
            self._update_proxies()
            available_proxies = self.proxies
        
        return random.choice(available_proxies) if available_proxies else None
    
    def mark_proxy_failed(self, proxy: Dict) -> None:
        """Çalışmayan proxy'i işaretle"""
        if proxy:
            proxy_str = f"{proxy.get('http', '')}_{proxy.get('https', '')}"
            self.proxy_failures[proxy_str] = self.proxy_failures.get(proxy_str, 0) + 1
            
            if self.proxy_failures[proxy_str] >= self.max_failures:
                self.failed_proxies.add(proxy_str)
                self.logger.warning(f"Proxy başarısız olarak işaretlendi: {proxy_str}") 