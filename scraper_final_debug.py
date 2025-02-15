import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://gosbteknopark.com"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}

def debug_main():
    # Ana sayfayı çek
    main_page = requests.get(f"{BASE_URL}/firmalarimiz/", headers=HEADERS)
    soup = BeautifulSoup(main_page.text, 'html.parser')
    
    # Tüm linkleri bul
    all_links = soup.select('a')
    company_links = []
    
    print("Bulunan tüm linkler:")
    for idx, link in enumerate(all_links[:20]):  # İlk 20 linki göster
        href = link.get('href', '')
        full_url = urljoin(BASE_URL, href)
        print(f"{idx+1}. {full_url}")
        
        # Firma linki kriterleri
        if '/firmalarimiz/' in href and not href.endswith('/firmalarimiz/'):
            company_links.append(full_url)
    
    print(f"\nToplam firma linki: {len(company_links)}")
    print("Örnek firma linkleri:")
    for link in company_links[:3]:
        print(link)

if __name__ == "__main__":
    debug_main() 