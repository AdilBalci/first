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
    
    # Güncel CSS selector'lerle deneme
    company_cards = soup.select('.elementor-grid-item')
    print(f"Bulunan kart sayısı: {len(company_cards)}")
    
    # Kart içindeki linkleri bul
    company_links = []
    for card in company_cards:
        link = card.select_one('a')
        if link:
            href = urljoin(BASE_URL, link['href'])
            company_links.append(href)
    
    print(f"\nToplam firma linki: {len(company_links)}")
    print("Örnek linkler:")
    for link in company_links[:3]:
        print(link) 