import requests
from bs4 import BeautifulSoup
import re
import time
from typing import List
import random

class GoogleFinder:
    """Google üzerinden email adresi bulucu"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def find_emails(self, domain: str) -> List[str]:
        """Domain için email adresleri ara"""
        found_emails = set()
        
        # Arama terimleri
        queries = [
            f'site:{domain} "@{domain}"',
            f'site:{domain} email',
            f'site:{domain} contact',
            f'site:{domain} iletişim',
            f'filetype:pdf site:{domain}'
        ]
        
        for query in queries:
            try:
                print(f"\nArama yapılıyor: {query}")
                
                # Google'da ara
                url = f'https://www.google.com/search?q={query}&num=100'
                response = requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Tüm linkleri topla
                    links = [a.get('href') for a in soup.find_all('a') if a.get('href', '').startswith('http')]
                    
                    # Her linki kontrol et
                    for link in links:
                        try:
                            print(f"Link kontrol ediliyor: {link}")
                            page = requests.get(link, headers=self.headers, timeout=5)
                            
                            if page.status_code == 200:
                                # Email adreslerini bul
                                emails = re.findall(r'[\w\.-]+@' + domain.replace('.', '\.'), page.text)
                                
                                # Bulunan mailleri ekle
                                for email in emails:
                                    if email not in found_emails:
                                        found_emails.add(email)
                                        print(f"Email bulundu: {email}")
                        
                        except:
                            continue
                
                # Rate limiting
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"Arama hatası: {str(e)}")
                continue
        
        return list(found_emails)

# Test
if __name__ == "__main__":
    finder = GoogleFinder()
    emails = finder.find_emails("etiya.com")
    print("\nBulunan email adresleri:")
    for email in emails:
        print(f"- {email}") 