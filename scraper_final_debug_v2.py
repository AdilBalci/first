import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://gosbteknopark.com"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def debug_link_extraction():
    response = requests.get(f"{BASE_URL}/firmalarimiz/", headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Tüm <a> etiketlerini bul
    all_links = soup.find_all('a')
    print(f"Toplam bulunan link sayısı: {len(all_links)}")
    
    # Firma linklerini filtrele
    company_links = []
    for link in all_links:
        href = link.get('href', '')
        if '/firmalarimiz/' in href and not href.startswith('#'):
            full_url = urljoin(BASE_URL, href)
            company_links.append(full_url)
    
    # Tekil linkler
    unique_links = list(set(company_links))
    print(f"\nFiltrelenmiş benzersiz firma linkleri ({len(unique_links)}):")
    for idx, link in enumerate(unique_links[:10]):
        print(f"{idx+1}. {link}")

if __name__ == "__main__":
    debug_link_extraction() 