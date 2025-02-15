import requests
from bs4 import BeautifulSoup

def test_detail_page():
    test_url = "https://gosbteknopark.com/firmalarimiz/adam-arge-hab-tekn-ar-ge-ltd-sti/"
    response = requests.get(test_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Kritik elementlerin varlığını kontrol et
    checks = {
        'title': bool(soup.select_one('h1.entry-title')),
        'website': bool(soup.select('a[href*="//"]:not([href*="gosbteknopark"])')),
        'contact_info': bool(soup.select('.elementor-text-editor'))
    }
    
    print(f"Test sonuçları ({test_url}):")
    for key, exists in checks.items():
        print(f"{key.upper()}: {'Var' if exists else 'Yok'}")

    # Alternatif selector'ler
    details = {
        'name': soup.select_one('.page-header h1'),
        'website': soup.select_one('div.contact-info a:contains("Web")'),
        'phone': soup.select_one('div.contact-info:contains("Tel")')
    }

    # Yeni CSS selector ile deneme
    company_cards = soup.select('.company-grid .item')
    for card in company_cards:
        link = card.select_one('a.more-button')['href']

if __name__ == "__main__":
    test_detail_page() 