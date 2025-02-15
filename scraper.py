from pipet import fetch, html
import json
import sys

# Setuptools uyumluluk fix'i
try:
    from markupsafe import soft_unicode
except ImportError:
    from markupsafe import soft_str as soft_unicode

base_url = "https://gosbteknopark.com"

def get_companies(category):
    url = f"{base_url}/firmalarimiz/?category={category}"
    page = fetch(url)
    
    companies = []
    for card in page.select('.company-card'):
        name = card.select_one('.company-name').text.strip()
        website = card.select_one('a[href^="http"]').attrs.get('href', '')
        
        companies.append({
            "name": name,
            "website": website,
            "category": category
        })
    
    return companies

if __name__ == "__main__":
    try:
        arge = get_companies("arge")
        kuluçka = get_companies("kuluçka")
        
        with open("firmalar.json", "w", encoding="utf-8") as f:
            json.dump({
                "AR-GE Firmaları": arge,
                "Kuluçka Firmaları": kuluçka
            }, f, ensure_ascii=False, indent=2)
            
        print("Veriler başarıyla kaydedildi!")
        
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        sys.exit(1) 