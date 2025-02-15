import requests
from bs4 import BeautifulSoup
import json

base_url = "https://gosbteknopark.com"

def get_companies(category):
    response = requests.get(f"{base_url}/firmalarimiz/?category={category}")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    companies = []
    for card in soup.select('.company-card'):
        name = card.select_one('.company-name').text.strip()
        website = card.select_one('a.external-link')['href'] if card.select_one('a.external-link') else ''
        
        companies.append({
            "name": name,
            "website": website,
            "category": category
        })
    
    return companies

if __name__ == "__main__":
    try:
        data = {
            "AR-GE Firmaları": get_companies("arge"),
            "Kuluçka Firmaları": get_companies("kuluçka")
        }
        
        with open("firmalar.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print("Veriler başarıyla kaydedildi!")
        
    except Exception as e:
        print(f"Hata oluştu: {str(e)}") 