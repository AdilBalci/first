import re
import logging
from typing import List, Set
from bs4 import BeautifulSoup
from utils.agent import Agent

class EmailFinder:
    def __init__(self):
        self.agent = Agent()
        self.logger = logging.getLogger(__name__)
        
        # Öncelikli email prefixleri
        self.priority_prefixes = [
            'info', 'bilgi', 'iletisim',
            'contact', 'hr', 'ik'
        ]
    
    def find_emails(self, domain: str, max_emails: int = 3) -> List[str]:
        """Verilen domain için email adreslerini bul (maksimum 3 adet)"""
        found_emails = set()
        
        try:
            # 1. Öncelikli email adreslerini kontrol et
            for prefix in self.priority_prefixes:
                if len(found_emails) >= max_emails:
                    break
                    
                email = f"{prefix}@{domain}"
                found_emails.add(email)
            
            # 2. Ana sayfayı kontrol et
            if len(found_emails) < max_emails:
                urls = [
                    f"https://www.{domain}",
                    f"https://{domain}",
                    f"https://www.{domain}/iletisim",
                    f"https://www.{domain}/contact"
                ]
                
                for url in urls:
                    if len(found_emails) >= max_emails:
                        break
                        
                    try:
                        response = self.agent.get(url, retry_count=1, use_proxy=False)
                        if response:
                            text = response.text
                            found = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
                            
                            for email in found:
                                if domain in email.lower() and len(found_emails) < max_emails:
                                    found_emails.add(email.lower())
                    except:
                        continue
            
            return sorted(list(found_emails))[:max_emails]
            
        except Exception as e:
            self.logger.error(f"Email arama hatası: {str(e)}")
            return sorted(list(found_emails))[:max_emails] 