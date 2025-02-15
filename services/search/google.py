import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from utils.agent import Agent
from utils.config import MAX_SEARCH_RESULTS, SEARCH_TIMEOUT

class GoogleSearch:
    def __init__(self):
        self.agent = Agent()
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://www.google.com/search"
    
    def search(self, query: str, num_results: int = MAX_SEARCH_RESULTS) -> List[str]:
        """Google araması yap ve sonuçları döndür"""
        results = []
        start = 0
        
        while len(results) < num_results:
            try:
                encoded_query = quote_plus(query)
                url = f"{self.base_url}?q={encoded_query}&start={start}&num=100"
                
                response = self.agent.get(url, retry_count=3, use_proxy=True)
                if not response:
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Google sonuç bağlantılarını bul
                for result in soup.select('div.g'):
                    link = result.find('a', href=True)
                    if link and 'http' in link['href']:
                        url = link['href']
                        if url not in results:
                            results.append(url)
                            if len(results) >= num_results:
                                break
                
                # Sonraki sayfa kontrolü
                if not soup.find('a', id='pnnext'):
                    break
                
                start += 100
                
            except Exception as e:
                self.logger.error(f"Arama hatası: {str(e)}")
                break
        
        return results[:num_results] 