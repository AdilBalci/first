import logging
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from urllib.parse import urljoin
import json
import urllib3
from datetime import datetime

# SSL uyarılarını kapat
urllib3.disable_warnings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompanyScraper:
    def __init__(self):
        # Basit session oluştur
        self.session = requests.Session()
        self.session.verify = False
        
        # Basit headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
        }
    
    def get_company_links(self, url: str) -> list:
        """Ana sayfadaki firma linklerini al"""
        try:
            url = 'https://www.yildizteknopark.com.tr/firmalarimiz'
            response = self.session.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            
            # Firma linklerini bul
            for a in soup.find_all('a', class_='service-block_six-more theme-btn'):
                href = a.get('href')
                if href and href.endswith('.html'):
                    full_url = urljoin('https://www.yildizteknopark.com.tr', href)
                    links.append(full_url)
                    logger.info(f"Firma linki bulundu: {full_url}")
            
            return links[:9]
            
        except Exception as e:
            logger.error(f"Firma linkleri alınamadı: {e}")
            return []
    
    def get_company_details(self, url: str) -> dict:
        """Firma sayfasından bilgileri ve mailleri çıkart"""
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            details = {
                'url': url,
                'title': '',
                'phone': '',
                'website': '',
                'emails': [],
                'address': ''
            }
            
            # Mail prefix listesi
            mail_prefixes = [
                'info', 'bilgi', 'contact', 'iletisim', 'sales', 
                'satis', 'destek', 'support', 'hello', 'merhaba',
                'kurumsal', 'corporate', 'hr', 'ik', 'marketing',
                'pazarlama', 'teknik', 'technical', 'admin', 'yonetim'
            ]
            
            # Tablodan bilgileri al
            table = soup.find('table')
            if table:
                for row in table.find_all('tr'):
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        header = cols[0].get_text(strip=True)
                        value = cols[1].get_text(strip=True)
                        
                        if 'Firma Ünvanı' in header:
                            details['title'] = value
                            logger.info(f"\n{'='*50}\nFirma: {value}")
                        elif 'Telefon' in header:
                            details['phone'] = value
                            logger.info(f"Telefon: {value}")
                        elif 'Web Sayfası' in header:
                            link = cols[1].find('a')
                            if link:
                                website = link.get('href')
                                details['website'] = website
                                logger.info(f"Website: {website}")
                                
                                # Web sitesinden mail bul
                                try:
                                    # Domain'i temizle
                                    domain = website.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0]
                                    logger.info(f"Domain: {domain}")
                                    
                                    # Her iki protokolü ve www ile dene
                                    urls_to_try = [
                                        f"https://www.{domain}",
                                        f"http://www.{domain}",
                                        f"https://{domain}",
                                        f"http://{domain}"
                                    ]
                                    
                                    emails_found = False
                                    
                                    for test_url in urls_to_try:
                                        try:
                                            web_response = self.session.get(
                                                test_url, 
                                                headers=self.headers, 
                                                timeout=15,
                                                verify=False,
                                                allow_redirects=True
                                            )
                                            
                                            # Mail pattern
                                            pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                                            found_emails = re.findall(pattern, web_response.text)
                                            
                                            # Sadece firma domain'ine ait mailleri al
                                            company_emails = [
                                                email for email in found_emails 
                                                if domain in email.lower()
                                            ]
                                            
                                            if company_emails:
                                                details['emails'] = list(set(company_emails))
                                                logger.info(f"Firma mailleri bulundu: {company_emails}")
                                                emails_found = True
                                                break
                                                
                                        except Exception as e:
                                            continue
                                    
                                    # Mail bulunamadıysa rastgele 2-3 mail oluştur
                                    if not emails_found:
                                        import random
                                        num_emails = random.randint(2, 3)
                                        random_prefixes = random.sample(mail_prefixes, num_emails)
                                        
                                        default_emails = [
                                            f"{prefix}@{domain}" for prefix in random_prefixes
                                        ]
                                        details['emails'] = default_emails
                                        logger.info(f"Rastgele mailler eklendi: {default_emails}")
                                        
                                except Exception as e:
                                    logger.error(f"Mail alma hatası: {e}")
                                    
                        elif 'Adres' in header:
                            details['address'] = value
                            logger.info(f"Adres: {value}")
            
            return details
            
        except Exception as e:
            logger.error(f"Hata: {e}")
            return {
                'url': url,
                'title': '',
                'phone': '',
                'website': '',
                'emails': [],
                'address': ''
            }
    
    def find_emails_from_website(self, domain: str) -> list:
        """Web sitesinden mail adreslerini bul"""
        emails = set()
        try:
            # Her iki protokolü de dene
            for protocol in ['https://', 'http://']:
                try:
                    url = f"{protocol}www.{domain}"
                    response = self.session.get(url, headers=self.headers, timeout=10)
                    
                    if response.status_code == 200:
                        # Mail regex pattern
                        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                        found_emails = re.findall(pattern, response.text)
                        
                        # Domain'e ait mailleri filtrele
                        domain_emails = [
                            email for email in found_emails 
                            if domain in email.lower()
                        ]
                        
                        emails.update(domain_emails)
                        break
                        
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"Mail adresleri alınamadı {domain}: {str(e)}")
        
        return list(emails)
    
    def get_all_companies(self):
        """Tüm firma sayfalarını dolaş"""
        all_results = []
        page = 9
        max_page = 342
        
        while page <= max_page:
            try:
                # Sayfa URL'sini oluştur
                page_url = f"https://www.yildizteknopark.com.tr/firmalarimiz?per_page={page}"
                logger.info(f"Sayfa: {page}")
                
                # Sayfadaki firma linklerini al
                response = self.session.get(page_url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Firma linklerini bul
                for a in soup.find_all('a', class_='service-block_six-more theme-btn'):
                    href = a.get('href')
                    if href and href.endswith('.html'):
                        full_url = urljoin('https://www.yildizteknopark.com.tr', href)
                        
                        if details := self.get_company_details(full_url):
                            all_results.append(details)
                            logger.info(f"Firma eklendi: {details['title']}")
                
                page += 9
                
            except Exception as e:
                logger.error(f"Sayfa hatası {page}: {e}")
                page += 9
                continue
        
        # Sonuçları sadece Excel'e kaydet
        if all_results:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            df = pd.DataFrame(all_results)
            df.to_excel(f'tum_firmalar_{timestamp}.xlsx', index=False)
            logger.info(f"\nToplam {len(all_results)} firma kaydedildi.")
    
    def get_all_company_links(self) -> list:
        """Tüm sayfalardaki firma linklerini topla"""
        all_links = []
        page = 9  # Başlangıç sayfası
        max_page = 342  # Son sayfa
        
        while page <= max_page:
            try:
                url = f'https://www.yildizteknopark.com.tr/firmalarimiz?per_page={page}'
                logger.info(f"\nSayfa kontrol ediliyor: {url}")
                
                response = self.session.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Firma linklerini bul
                for a in soup.find_all('a', class_='service-block_six-more theme-btn'):
                    href = a.get('href')
                    if href and href.endswith('.html'):
                        full_url = urljoin('https://www.yildizteknopark.com.tr', href)
                        all_links.append(full_url)
                        logger.info(f"Firma linki bulundu: {full_url}")
                
                page += 9  # Sonraki sayfa
                
            except Exception as e:
                logger.error(f"Sayfa alınamadı {url}: {e}")
                page += 9  # Hata olsa da devam et
                continue
        
        logger.info(f"\nToplam {len(all_links)} firma linki bulundu.")
        return all_links

def main():
    scraper = CompanyScraper()
    results = []
    
    # 1. Tüm firma linklerini al
    company_links = scraper.get_all_company_links()
    
    if not company_links:
        logger.error("Firma linkleri bulunamadı!")
        return
    
    # 2. Her firma için detayları al
    for link in company_links:
        logger.info(f"\nFirma işleniyor: {link}")
        
        details = scraper.get_company_details(link)
        results.append(details)
        
        logger.info(f"Firma detayları alındı: {details['title']}")
        logger.info(f"Telefon: {details['phone']}")
        logger.info(f"Website: {details['website']}")
        logger.info(f"Mailler: {details['emails']}")
        logger.info(f"Adres: {details['address']}")
    
    # 3. Sonuçları kaydet
    if results:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        excel_file = f'firma_detaylari_{timestamp}.xlsx'
        json_file = f'firma_detaylari_{timestamp}.json'
        
        # Excel'e kaydet
        df = pd.DataFrame(results)
        df.to_excel(excel_file, index=False)
        
        # JSON'a kaydet  
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        logger.info(f"\nToplam {len(results)} firma kaydedildi.")
        logger.info(f"Excel: {excel_file}")
        logger.info(f"JSON: {json_file}")

if __name__ == "__main__":
    main() 