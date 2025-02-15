import logging
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from urllib.parse import urljoin
import json
import urllib3
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os
import random
from typing import Optional
from requests.exceptions import RequestException
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from threading import Lock
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_autoinstaller
import itertools
from openpyxl import load_workbook
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

# SSL uyarılarını kapat
urllib3.disable_warnings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MontenegroScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        
        # More diverse user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]
        
        # More realistic headers
        self.headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.google.com/',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1'
        }
        
        # Mail prefix listesi - İK odaklı
        self.mail_prefixes = [
            'hr', 'ik', 'kariyer', 'career', 'recruitment', 'jobs',
            'info', 'contact', 'iletisim', 'kurumsal', 'corporate',
            'is', 'basvuru', 'apply', 'hiring', 'humanresources'
        ]
        
        # Arama yapılacak kaynaklar - Tamamen güncellendi
        self.sources = [
            'https://www.tmb.org.tr/tr/uyeler',
            'https://www.deik.org.tr/uluslararasi-teskilatlar/karadag-is-konseyi',
            'https://www.invest.gov.tr/tr/sectors/construction',
            'https://www.ticaret.gov.tr/ulkeler/karadag/turk-firmalari'
        ]
        
        # DEİK özel URL'leri - Güncellendi
        self.deik_urls = {
            'is_konseyi': 'https://www.deik.org.tr/bilateral-business-councils-european-business-councils',
            'firma_listesi': 'https://www.deik.org.tr/bilateral-business-councils-turkey-montenegro-business-council'
        }
        
        # TMB özel URL'leri - Güncellendi
        self.tmb_urls = {
            'members': 'https://www.tmb.org.tr/tr/uyeler',
            'search': 'https://www.tmb.org.tr/tr/arama'
        }
        
        # Ticaret Bakanlığı özel URL'leri - Yeni eklendi
        self.ticaret_urls = {
            'yurtdisi': 'https://www.ticaret.gov.tr/yurtdisi-teskilati/balkanlar/karadag',
            'firmalar': 'https://www.ticaret.gov.tr/yurtdisi-teskilati/balkanlar/karadag/turk-firmalari'
        }
        
        # Yatırım Ofisi özel URL'leri - Yeni eklendi
        self.invest_urls = {
            'companies': 'https://www.invest.gov.tr/tr/why-turkey/foreign-direct-investment'
        }
        
        # TOBB özel URL'leri - Güncellendi
        self.tobb_url = 'https://www.tobb.org.tr/Sayfalar/FirmaSorgulamaSonuc.php'
        
        # TİM özel URL'leri - Güncellendi
        self.tim_urls = {
            'ihracatci_birlikleri': 'https://tim.org.tr/tr/ihracat-rakamlari',
            'uye_sorgula': 'https://tim.org.tr/tr/uye-sorgula'
        }
        
        # Selenium driver ayarları
        self.driver = None
        
        # Proxy ayarları
        self.proxies = self.load_proxies()
        self.current_proxy = None
        
        # Rate limiting ayarları
        self.min_delay = 2  # Minimum bekleme süresi
        self.max_delay = 5  # Maximum bekleme süresi
        
        # Retry ayarları
        self.setup_session()
        
        # Thread-safe yapılar
        self.results_queue = Queue()
        self.results_lock = Lock()
        
        # Paralel çalışma ayarları
        self.max_workers = 5  # Maksimum thread sayısı
        self.timeout = 300  # Maksimum bekleme süresi (saniye)
        
        # Arama terimlerini ekle
        self.search_terms = [
            'turkish construction companies in montenegro',
            'türk inşaat şirketleri karadağ',
            'montenegro turkish contractors',
            'karadağ türk müteahhitler',
            'turkish construction projects montenegro'
        ]
    
    def load_proxies(self) -> list:
        """Proxy listesini yükle ve geçerli olanları filtrele"""
        try:
            # Örnek proxy listesi - Gerçek uygulamada harici kaynaktan yüklenecek
            raw_proxies = [
                'http://proxy1.example.com:8080',
                'http://proxy2.example.com:8080',
                'http://proxy3.example.com:8080'
            ]
            
            # Proxy'leri doğrula
            valid_proxies = []
            for proxy in raw_proxies:
                if self.validate_proxy(proxy):
                    valid_proxies.append(proxy)
            
            if not valid_proxies:
                logger.warning("Geçerli proxy bulunamadı! Direkt bağlantı kullanılacak.")
            
            return valid_proxies
            
        except Exception as e:
            logger.error(f"Proxy yükleme hatası: {str(e)}")
            return []
    
    def validate_proxy(self, proxy: str) -> bool:
        """Proxy'nin çalışır durumda olup olmadığını kontrol et"""
        try:
            test_url = "https://www.google.com"
            response = requests.get(
                test_url,
                proxies={"http": proxy, "https": proxy},
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def rotate_proxy(self):
        """Bir sonraki geçerli proxy'ye geç"""
        if not self.proxies:
            return
            
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        self.current_proxy = self.proxies[self.proxy_index]
        self.session.proxies = {
            'http': self.current_proxy,
            'https': self.current_proxy
        }
        logger.info(f"Yeni proxy: {self.current_proxy}")
    
    def make_request_with_retry(self, url, method='get', **kwargs):
        """Geliştirilmiş istek metodu - Üstel geri çekilme ile"""
        for attempt in range(self.max_retries):
            try:
                # Proxy başarısız olmuşsa değiştir
                if self.proxy_fail_count >= self.max_proxy_fails:
                    self.rotate_proxy()
                    self.proxy_fail_count = 0
                
                response = self.session.request(
                    method,
                    url,
                    headers=self.headers,
                    timeout=30,
                    **kwargs
                )
                
                # Başarılı yanıt
                if 200 <= response.status_code < 300:
                    return response
                
                # 4xx hataları için yeniden deneme yapma
                if 400 <= response.status_code < 500:
                    logger.warning(f"İstemci hatası ({response.status_code}): {url}")
                    return None
                
                # Diğer hatalar için yeniden dene
                logger.warning(f"Sunucu hatası ({response.status_code}): {url}. Yeniden denenecek...")
                
            except Exception as e:
                self.proxy_fail_count += 1
                logger.error(f"İstek hatası ({url}): {str(e)}")
                
            # Üstel geri çekilme
            if attempt < len(self.retry_delays):
                delay = self.retry_delays[attempt]
                logger.info(f"{delay} saniye bekleniyor...")
                time.sleep(delay)
        
        logger.error(f"İstek başarısız: {url}")
        return None
    
    def setup_session(self):
        """Session'ı retry ve timeout ile yapılandır"""
        retry_strategy = Retry(
            total=3,  # toplam deneme sayısı
            backoff_factor=1,  # her denemede beklenecek süre
            status_forcelist=[429, 500, 502, 503, 504]  # retry yapılacak HTTP kodları
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def rotate_proxy(self):
        """Yeni bir proxy seç ve user agent'ı değiştir"""
        if self.proxies:
            self.current_proxy = random.choice(self.proxies)
            self.session.proxies = {'http': self.current_proxy, 'https': self.current_proxy}
            logger.info(f"Proxy değiştirildi: {self.current_proxy}")
            
        # User agent'ı da değiştir
        self.headers['User-Agent'] = random.choice(self.user_agents)
        logger.info(f"User-Agent değiştirildi: {self.headers['User-Agent']}")
    
    def make_request(self, url, method='get', **kwargs):
        """Geliştirilmiş istek metodu"""
        try:
            # URL kontrolü
            if not url.startswith('http'):
                raise ValueError(f"Geçersiz URL: {url}")
            
            response = self.session.request(
                method,
                url,
                headers=self.headers,
                timeout=30,
                **kwargs
            )
            
            if response.status_code == 404:
                logger.warning(f"404 Hatası: {url} bulunamadı")
                return None
            
            return response if 200 <= response.status_code < 300 else None
        
        except Exception as e:
            logger.error(f"İstek hatası ({url}): {str(e)}")
            return None
    
    def setup_selenium(self):
        """Son ChromeDriver kurulum metodu"""
        try:
            # Chrome sürümünü tespit et
            chrome_version = chromedriver_autoinstaller.get_chrome_version()
            logger.info(f"Chrome sürümü: {chrome_version}")
            
            # Driver'ı yükle
            chromedriver_path = chromedriver_autoinstaller.install()
            logger.info(f"ChromeDriver yolu: {chromedriver_path}")
            
            options = webdriver.ChromeOptions()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(f'user-agent={self.headers["User-Agent"]}')
            
            service = Service(executable_path=chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
            
            return True
        
        except Exception as e:
            logger.error(f"Son ChromeDriver hatası: {str(e)}")
            return False
    
    def linkedin_login(self) -> bool:
        """LinkedIn'e giriş yap"""
        try:
            if not self.linkedin_email or not self.linkedin_password:
                logger.error("LinkedIn credentials bulunamadı!")
                return False
            
            self.driver.get(self.linkedin_urls['login'])
            time.sleep(3)  # Sayfa yüklenme beklemesi
            
            # Login form
            email_input = self.driver.find_element(By.ID, 'username')
            password_input = self.driver.find_element(By.ID, 'password')
            
            email_input.send_keys(self.linkedin_email)
            password_input.send_keys(self.linkedin_password)
            
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
            
            # Login kontrolü
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.global-nav'))
                )
                logger.info("LinkedIn login başarılı")
                return True
                
            except TimeoutException:
                logger.error("LinkedIn login başarısız - Timeout")
                return False
            
        except Exception as e:
            logger.error(f"LinkedIn login hatası: {e}")
            return False
    
    def parse_linkedin(self) -> list:
        """LinkedIn'den firma bilgilerini çek"""
        companies = []
        
        try:
            if not self.setup_selenium():
                return companies
            
            if not self.linkedin_login():
                return companies
            
            # Arama sayfasına git
            self.driver.get(self.linkedin_urls['search'])
            time.sleep(3)
            
            # Scroll ve firma toplama
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # Firma kartlarını bul
                company_cards = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    '.reusable-search__result-container'
                )
                
                for card in company_cards:
                    try:
                        name = card.find_element(By.CSS_SELECTOR, '.entity-result__title-text').text
                        description = card.find_element(By.CSS_SELECTOR, '.entity-result__primary-subtitle').text.lower()
                        
                        # İnşaat/mimarlık filtresi
                        if any(keyword in description for keyword in ['construction', 'architecture', 'building']):
                            company_url = card.find_element(By.CSS_SELECTOR, 'a.app-aware-link').get_attribute('href')
                            
                            # Detay sayfasına git
                            self.driver.execute_script(f'window.open("{company_url}", "_blank");')
                            self.driver.switch_to.window(self.driver.window_handles[-1])
                            time.sleep(2)
                            
                            # Website linkini bul
                            try:
                                website = self.driver.find_element(
                                    By.CSS_SELECTOR, 
                                    'a[href*="http"]:not([href*="linkedin"])'
                                ).get_attribute('href')
                            except:
                                website = ''
                            
                            company_data = {
                                'name': name,
                                'sector': 'Construction/Architecture',
                                'website': website,
                                'source': 'LinkedIn',
                                'linkedin_url': company_url
                            }
                            
                            companies.append(company_data)
                            logger.info(f"LinkedIn firma bulundu: {name}")
                            
                            # Detay sekmesini kapat
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])
                    
                    except Exception as e:
                        logger.error(f"LinkedIn firma kartı parse hatası: {e}")
                        continue
                
                # Scroll
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                    
                last_height = new_height
            
        except Exception as e:
            logger.error(f"LinkedIn parse hatası: {e}")
            
        finally:
            if self.driver:
                self.driver.quit()
        
        return companies

    def parse_deik(self) -> list:
        """DEİK websitesinden firma bilgilerini çek"""
        companies = []
        
        try:
            # İş konseyi sayfasını kontrol et
            response = self.make_request(self.deik_urls['is_konseyi'])
            if not response:
                return companies
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Üye firma listesi sayfasını kontrol et
            response = self.make_request(self.deik_urls['firma_listesi'])
            if not response:
                return companies
                
            # Firma tablosunu bul
            table = soup.find('table', {'class': 'table'})
            if table:
                rows = table.find_all('tr')[1:]  # Başlık satırını atla
                
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        company_name = cols[0].get_text(strip=True)
                        sector = cols[1].get_text(strip=True).lower()
                        
                        # Sadece inşaat/mimarlık sektöründeki firmaları al
                        if any(keyword in sector for keyword in ['inşaat', 'yapi', 'mimari', 'construction', 'architecture']):
                            company_data = {
                                'name': company_name,
                                'sector': sector,
                                'website': '',
                                'source': 'DEİK'
                            }
                            
                            # Website linkini bul
                            website_link = cols[2].find('a')
                            if website_link:
                                company_data['website'] = website_link.get('href', '')
                            
                            companies.append(company_data)
                            logger.info(f"DEİK firma bulundu: {company_name}")
            
        except Exception as e:
            logger.error(f"DEİK parse hatası: {e}")
        
        return companies

    def parse_tobb(self) -> list:
        """TOBB websitesinden firma bilgilerini çek"""
        companies = []
        
        try:
            # TOBB firma arama sayfasına POST isteği gönder
            search_data = {
                'sektor': 'İnşaat',
                'il': '',  # Tüm iller
                'arama': '1'
            }
            
            response = self.session.post(
                self.tobb_url,
                data=search_data,
                headers=self.headers,
                timeout=15
            )
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Firma listesini bul
            firma_table = soup.find('table', {'id': 'firmaTable'})
            if firma_table:
                for row in firma_table.find_all('tr')[1:]:  # Başlık satırını atla
                    cols = row.find_all('td')
                    if len(cols) >= 4:
                        company_data = {
                            'name': cols[0].get_text(strip=True),
                            'sector': cols[1].get_text(strip=True),
                            'website': '',
                            'source': 'TOBB'
                        }
                        
                        # Detay sayfası linkini al
                        detay_link = cols[0].find('a')
                        if detay_link:
                            detay_url = urljoin(self.tobb_url, detay_link['href'])
                            
                            # Detay sayfasından website ve diğer bilgileri al
                            try:
                                detay_response = self.session.get(detay_url, headers=self.headers, timeout=15)
                                detay_soup = BeautifulSoup(detay_response.text, 'html.parser')
                                
                                website_elem = detay_soup.find('a', text=re.compile(r'www|http'))
                                if website_elem:
                                    company_data['website'] = website_elem['href']
                                
                                companies.append(company_data)
                                logger.info(f"TOBB firma bulundu: {company_data['name']}")
                                
                            except Exception as e:
                                logger.error(f"TOBB detay sayfası hatası: {e}")
                                continue
            
        except Exception as e:
            logger.error(f"TOBB parse hatası: {e}")
        
        return companies

    def parse_tim(self) -> list:
        """TİM websitesinden firma bilgilerini çek"""
        companies = []
        
        try:
            # İhracatçı birliklerini kontrol et
            response = self.session.get(self.tim_urls['ihracatci_birlikleri'], headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # İnşaat/mimarlık ile ilgili birlikleri bul
            construction_unions = []
            for union in soup.find_all('a', href=re.compile(r'birlik|insaat|yapi')):
                construction_unions.append(union['href'])
            
            # Her birlik için üye sorgula
            for union_url in construction_unions:
                try:
                    search_data = {
                        'sektor': 'İnşaat',
                        'ulke': 'Karadağ',
                        'arama': '1'
                    }
                    
                    response = self.session.post(
                        urljoin(self.tim_urls['uye_sorgula'], union_url),
                        data=search_data,
                        headers=self.headers,
                        timeout=15
                    )
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Firma listesini bul
                    for company_div in soup.find_all('div', class_='company-item'):
                        name = company_div.find('h3').get_text(strip=True)
                        website = company_div.find('a', href=re.compile(r'www|http'))
                        
                        company_data = {
                            'name': name,
                            'sector': 'İnşaat',
                            'website': website['href'] if website else '',
                            'source': 'TİM'
                        }
                        
                        companies.append(company_data)
                        logger.info(f"TİM firma bulundu: {name}")
                        
                except Exception as e:
                    logger.error(f"TİM birlik parse hatası: {e}")
                    continue
                
        except Exception as e:
            logger.error(f"TİM parse hatası: {e}")
        
        return companies

    def parse_tmb(self) -> list:
        """TMB websitesinden firma bilgilerini çek"""
        companies = []
        
        try:
            # Üye listesi sayfasını al
            response = self.session.get(self.tmb_urls['members'], headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Firma kartlarını bul
            company_cards = soup.find_all('div', class_='member-card')
            
            for card in company_cards:
                try:
                    name = card.find('h3', class_='member-name').get_text(strip=True)
                    
                    # Detay linkini al
                    detail_link = card.find('a', class_='member-detail-link')
                    if detail_link:
                        detail_url = urljoin(self.tmb_urls['members'], detail_link['href'])
                        
                        # Detay sayfasını kontrol et
                        detail_response = self.session.get(detail_url, headers=self.headers, timeout=15)
                        detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                        
                        # Firma bilgilerini topla
                        company_data = {
                            'name': name,
                            'sector': 'İnşaat/Müteahhitlik',
                            'website': '',
                            'source': 'TMB',
                            'phone': '',
                            'address': '',
                            'projects': []
                        }
                        
                        # Website ve iletişim bilgilerini bul
                        contact_div = detail_soup.find('div', class_='contact-info')
                        if contact_div:
                            website_link = contact_div.find('a', href=re.compile(r'www|http'))
                            if website_link:
                                company_data['website'] = website_link['href']
                                
                            phone = contact_div.find('span', class_='phone')
                            if phone:
                                company_data['phone'] = phone.get_text(strip=True)
                                
                            address = contact_div.find('address')
                            if address:
                                company_data['address'] = address.get_text(strip=True)
                        
                        # Karadağ projelerini kontrol et
                        projects_div = detail_soup.find('div', class_='projects')
                        if projects_div:
                            project_items = projects_div.find_all('div', class_='project-item')
                            for project in project_items:
                                location = project.find('span', class_='location')
                                if location and any(keyword in location.text.lower() for keyword in ['montenegro', 'karadağ']):
                                    project_name = project.find('h4').get_text(strip=True)
                                    company_data['projects'].append(project_name)
                        
                        # Eğer Karadağ'da projesi varsa listeye ekle
                        if company_data['projects']:
                            companies.append(company_data)
                            logger.info(f"TMB firma bulundu: {name} (Karadağ projeleri: {len(company_data['projects'])})")
                        else:
                            # Firma açıklamasında Karadağ geçiyor mu kontrol et
                            description = detail_soup.find('div', class_='company-description')
                            if description and any(keyword in description.text.lower() for keyword in ['montenegro', 'karadağ']):
                                companies.append(company_data)
                                logger.info(f"TMB firma bulundu: {name} (Karadağ ilişkili)")
                
                except Exception as e:
                    logger.error(f"TMB firma detay hatası: {e}")
                    continue
                
        except Exception as e:
            logger.error(f"TMB parse hatası: {e}")
        
        return companies

    def search_chambers(self) -> list:
        """Resmi kurumlardan firma ara"""
        companies = []
        sources = [
            self.tmb_urls['members'],
            self.deik_urls['firma_listesi'],
            self.ticaret_urls['firmalar'],
            self.invest_urls['companies']
        ]
        
        try:
            for source in sources:
                response = self.make_request(source)
                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # TMB üyeleri için
                    if 'tmb.org.tr' in source:
                        company_elements = soup.find_all('div', class_='member-item')
                        for element in company_elements:
                            name = element.find('h3')
                            if name:
                                company_data = {
                                    'name': name.text.strip(),
                                    'sector': 'İnşaat',
                                    'website': '',
                                    'source': 'TMB'
                                }
                                companies.append(company_data)
                    
                    # DEİK üyeleri için
                    elif 'deik.org.tr' in source:
                        company_elements = soup.find_all('div', class_='council-member')
                        for element in company_elements:
                            name = element.find('h4')
                            if name:
                                company_data = {
                                    'name': name.text.strip(),
                                    'sector': 'İnşaat/Ticaret',
                                    'website': '',
                                    'source': 'DEİK'
                                }
                                companies.append(company_data)
                    
                    # Ticaret Bakanlığı firmaları için
                    elif 'ticaret.gov.tr' in source:
                        company_elements = soup.find_all('tr')
                        for element in company_elements[1:]:  # Başlık satırını atla
                            cols = element.find_all('td')
                            if len(cols) >= 2:
                                company_data = {
                                    'name': cols[0].text.strip(),
                                    'sector': cols[1].text.strip(),
                                    'website': '',
                                    'source': 'Ticaret Bakanlığı'
                                }
                                companies.append(company_data)
                    
                    # Yatırım Ofisi firmaları için
                    elif 'invest.gov.tr' in source:
                        company_elements = soup.find_all('div', class_='company-card')
                        for element in company_elements:
                            name = element.find('h3')
                            if name:
                                company_data = {
                                    'name': name.text.strip(),
                                    'sector': 'İnşaat/Yatırım',
                                    'website': '',
                                    'source': 'Yatırım Ofisi'
                                }
                                companies.append(company_data)
                    
        except Exception as e:
            logger.error(f"Kaynak tarama hatası: {e}")
        
        return companies

    def parallel_search(self) -> list:
        """Tüm kaynakları paralel olarak ara"""
        all_results = []
        
        # Parse fonksiyonları ve yedekleri
        search_functions = [
            # Ana fonksiyonlar
            (self.parse_deik, "DEİK"),
            (self.parse_tobb, "TOBB"),
            (self.parse_tim, "TİM"),
            (self.parse_tmb, "TMB"),
            # Yedek aramalar - farklı yaklaşımlar
            (self.search_chambers, "Ticaret Odası"),
            (self.search_google, "Google"),
            (self.search_yandex, "Yandex")
        ]
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Tüm fonksiyonları paralel başlat
            future_to_source = {
                executor.submit(func): source 
                for func, source in search_functions
            }
            
            # Sonuçları topla
            for future in as_completed(future_to_source, timeout=self.timeout):
                source = future_to_source[future]
                try:
                    companies = future.result()
                    if companies:
                        with self.results_lock:
                            all_results.extend(companies)
                            logger.info(f"{source}'den {len(companies)} firma bulundu")
                    else:
                        # Ana kaynak başarısız olduysa yedek aramayı dene
                        backup_companies = self.try_backup_search(source)
                        if backup_companies:
                            with self.results_lock:
                                all_results.extend(backup_companies)
                                logger.info(f"{source} (Yedek) {len(backup_companies)} firma bulundu")
                
                except Exception as e:
                    logger.error(f"{source} arama hatası: {e}")
                    # Hata durumunda yedek aramayı dene
                    backup_companies = self.try_backup_search(source)
                    if backup_companies:
                        with self.results_lock:
                            all_results.extend(backup_companies)
        
        return self.clean_results(all_results)
    
    def try_backup_search(self, failed_source: str) -> list:
        """Başarısız kaynak için yedek arama yöntemlerini dene"""
        companies = []
        
        try:
            if failed_source == "DEİK":
                # TOBB üzerinden cross-check
                companies.extend(self.search_tobb_international())
            
            elif failed_source == "TOBB":
                # Ticaret odaları üzerinden arama
                companies.extend(self.search_chambers())
            
            elif failed_source == "LinkedIn":
                # Google üzerinden şirket araması
                companies.extend(self.search_google())
            
            elif failed_source == "TMB":
                # Yandex üzerinden müteahhit firma araması
                companies.extend(self.search_yandex())
                
        except Exception as e:
            logger.error(f"Yedek arama hatası ({failed_source}): {e}")
        
        return companies
    
    def search_google(self) -> list:
        """Geliştirilmiş Google arama metodu"""
        companies = []
        
        for term in self.search_terms:
            try:
                # More random delays with human-like patterns
                base_delay = random.uniform(15, 45)
                jitter = random.uniform(0.5, 1.5)
                delay = base_delay * jitter
                
                # Add random mouse movement simulation delay
                mouse_delay = random.uniform(0.1, 0.5)
                
                total_delay = delay + mouse_delay
                logger.info(f"Human-like delay: {total_delay:.1f} seconds (base: {base_delay:.1f}, jitter: {jitter:.1f}, mouse: {mouse_delay:.1f})")
                time.sleep(total_delay)
                
                # Yeni Google arama parametreleri
                params = {
                    'q': f'site:.me "{term}"',  # .me domainli Karadağ sitelerinde ara
                    'num': 10,  # Daha az sonuç
                    'lr': 'lang_tr',
                    'cr': 'countryME'
                }
                
                # Proxy kullan
                if self.proxies:
                    self.rotate_proxy()
                
                response = self.make_request(
                    "https://www.google.com/search",
                    params=params,
                    timeout=15
                )
                
                if response:
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Gelişmiş parse işlemi
                        for result in soup.select('div.g'):
                            title = result.select_one('h3')
                            link = result.select_one('a[href^="/url?"]')
                            
                            if title and link:
                                url = re.search(r'url\?q=(.+?)&', link['href']).group(1)
                                if any(ext in url for ext in ['.me', '.com.me', '.co.me']):
                                    company_data = {
                                        'name': title.get_text(strip=True),
                                        'website': url,
                                        'source': 'Google'
                                    }
                                    companies.append(company_data)
                    elif response.status_code == 429 or 'sorry/index' in response.url:
                        # Handle different types of blocks
                        if 'sorry/index' in response.url:
                            # CAPTCHA detected
                            wait_time = random.uniform(1200, 1800)  # 20-30 minutes
                            logger.warning(f"CAPTCHA detected. Waiting {wait_time/60:.1f} minutes...")
                        else:
                            # Rate limit detected
                            wait_time = random.uniform(600, 1200)  # 10-20 minutes
                            logger.warning(f"Rate limit detected. Waiting {wait_time/60:.1f} minutes...")
                        
                        # Rotate proxy and user agent
                        self.rotate_proxy()
                        
                        # Add random browsing activity simulation
                        browse_time = random.uniform(30, 120)
                        logger.info(f"Simulating browsing activity for {browse_time:.1f} seconds...")
                        time.sleep(browse_time)
                        
                        # Wait the main delay
                        time.sleep(wait_time)
                        
                        # Rotate again before continuing
                        self.rotate_proxy()
                        continue
                
            except Exception as e:
                logger.error(f"Google arama hatası: {str(e)}")
                continue
        
        return companies
    
    def search_yandex(self) -> list:
        """Yandex üzerinden firma ara"""
        companies = []
        # TODO: Yandex API implementasyonu
        return companies
    
    def search_tobb_international(self) -> list:
        """TOBB üzerinden uluslararası firma araması"""
        companies = []
        try:
            # Güncel TOBB URL'i
            search_url = 'https://www.tobb.org.tr/FirmaBilgiSistemi/Sayfalar/Firma.php'
            
            search_data = {
                'sektor': 'İnşaat',
                'ulke': 'Karadağ',
                'arama': '1'
            }
            
            response = self.make_request(search_url, method='post', data=search_data)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                company_table = soup.find('table', {'class': 'firma-table'})
                if company_table:
                    for row in company_table.find_all('tr')[1:]:
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            company_data = {
                                'name': cols[0].text.strip(),
                                'sector': 'İnşaat',
                                'website': '',
                                'source': 'TOBB'
                            }
                            companies.append(company_data)
            
        except Exception as e:
            logger.error(f"TOBB uluslararası arama hatası: {e}")
        
        return companies
    
    def clean_results(self, results: list) -> list:
        """Sonuçları temizle ve birleştir"""
        unique_companies = []
        seen_names = set()
        
        for company in results:
            name = company['name'].lower().strip()
            if name not in seen_names:
                seen_names.add(name)
                
                # Birden fazla kaynaktan gelen bilgileri birleştir
                existing = next((c for c in unique_companies if c['name'].lower().strip() == name), None)
                if existing:
                    # Bilgileri güncelle/birleştir
                    existing['sources'] = list(set(existing.get('sources', []) + [company.get('source', '')]))
                    existing['emails'] = list(set(existing.get('emails', []) + company.get('emails', [])))
                    if company.get('website') and not existing.get('website'):
                        existing['website'] = company['website']
                else:
                    company['sources'] = [company.get('source', '')]
                    unique_companies.append(company)
        
        return unique_companies

    def get_company_details(self, company_data: dict) -> dict:
        """Firma detaylarını ve mail adreslerini topla"""
        details = {
            'company_name': company_data.get('name', ''),
            'sector': company_data.get('sector', ''),
            'website': company_data.get('website', ''),
            'emails': [],
            'phone': company_data.get('phone', ''),
            'address': company_data.get('address', ''),
            'source': company_data.get('source', ''),
            'montenegro_office': False,  # Karadağ ofisi var mı?
            'projects_in_montenegro': False  # Karadağ'da projesi var mı?
        }
        
        if details['website']:
            # Website içeriğini kontrol et
            try:
                response = self.session.get(details['website'], headers=self.headers, timeout=15)
                content = response.text.lower()
                
                # Karadağ ofisi/projesi kontrolü
                montenegro_keywords = ['montenegro', 'karadağ', 'podgorica', 'budva', 'bar', 'kotor']
                if any(keyword in content for keyword in montenegro_keywords):
                    details['projects_in_montenegro'] = True
                    
                # Mail adreslerini çıkart
                details['emails'] = self.extract_emails(details['website'])
                
            except Exception as e:
                logger.error(f"Website kontrol hatası: {e}")
        
        return details
    
    def extract_emails(self, website: str) -> list:
        """Web sitesinden mail adreslerini çıkart"""
        emails = set()
        try:
            domain = website.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0]
            
            # Website'ı kontrol et
            for protocol in ['https://', 'http://']:
                try:
                    url = f"{protocol}www.{domain}"
                    response = self.make_request(url)
                    
                    if response and response.status_code == 200:
                        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                        found_emails = re.findall(pattern, response.text)
                        
                        # Domain'e ait mailleri filtrele
                        domain_emails = [
                            email for email in found_emails 
                            if domain in email.lower()
                        ]
                        
                        emails.update(domain_emails)
                        
                        if not emails:  # Mail bulunamadıysa tahmin et
                            for prefix in self.mail_prefixes:
                                emails.add(f"{prefix}@{domain}")
                        
                        break
                        
                except Exception as e:
                    logger.error(f"Mail çıkartma hatası: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Mail adresleri alınamadı {website}: {str(e)}")
        
        return list(emails)

    def get_linkedin_details(self, url):
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'section.about'))
            )
            
            # Detaylı bilgi toplama
            about_section = self.driver.find_element(By.CSS_SELECTOR, 'section.about')
            website = about_section.find_element(
                By.CSS_SELECTOR, 
                'a[data-tracking-control-name="about_website"]'
            ).get_attribute('href')
            
            return {'website': website}
        
        except Exception as e:
            logger.error(f"LinkedIn detay hatası: {str(e)}")
            return {}

    def search_companies(self):
        """Ana arama metodu"""
        companies = []
        
        # Google araması
        google_results = self.search_google()
        if google_results:
            companies.extend(google_results)
            logger.info(f"Google'dan {len(google_results)} firma bulundu")
        else:
            logger.warning("Google'dan firma bulunamadı")
        
        # LinkedIn araması
        linkedin_results = self.parse_linkedin()
        if linkedin_results:
            companies.extend(linkedin_results)
            logger.info(f"LinkedIn'den {len(linkedin_results)} firma bulundu")
        else:
            logger.warning("LinkedIn'den firma bulunamadı")
        
        # Veri temizleme
        if companies:
            return self.clean_data(companies)
        else:
            logger.error("Hiç firma bulunamadı!")
            return []

    def search_linkedin(self):
        """Güncellenmiş LinkedIn arama"""
        companies = []
        try:
            if not self.setup_selenium():
                return []
            
            if not self.linkedin_login():
                return []
            
            # Yeni arama URL'i
            search_url = "https://www.linkedin.com/search/results/companies/?keywords=montenegro%20construction%20turkish&geoUrn=%5B105214%5D"
            self.driver.get(search_url)
            time.sleep(3)
            
            # Scroll ve firma toplama
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # Firma kartlarını bul
                company_cards = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    '.reusable-search__result-container'
                )
                
                for card in company_cards:
                    try:
                        name = card.find_element(By.CSS_SELECTOR, '.entity-result__title-text').text
                        description = card.find_element(By.CSS_SELECTOR, '.entity-result__primary-subtitle').text.lower()
                        
                        # İnşaat/mimarlık filtresi
                        if any(keyword in description for keyword in ['construction', 'architecture', 'building']):
                            company_url = card.find_element(By.CSS_SELECTOR, 'a.app-aware-link').get_attribute('href')
                            
                            # Detay sayfasına git
                            self.driver.execute_script(f'window.open("{company_url}", "_blank");')
                            self.driver.switch_to.window(self.driver.window_handles[-1])
                            time.sleep(2)
                            
                            # Website linkini bul
                            try:
                                website = self.driver.find_element(
                                    By.CSS_SELECTOR, 
                                    'a[href*="http"]:not([href*="linkedin"])'
                                ).get_attribute('href')
                            except:
                                website = ''
                            
                            company_data = {
                                'name': name,
                                'sector': 'Construction/Architecture',
                                'website': website,
                                'source': 'LinkedIn',
                                'linkedin_url': company_url
                            }
                            
                            companies.append(company_data)
                            logger.info(f"LinkedIn firma bulundu: {name}")
                            
                            # Detay sekmesini kapat
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])
                    
                    except Exception as e:
                        logger.error(f"LinkedIn firma kartı parse hatası: {e}")
                        continue
                
                # Scroll
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                    
                last_height = new_height
            
        except Exception as e:
            logger.error(f"Son LinkedIn hatası: {str(e)}")
            return []
        
        return companies

def try_password(args):
    file_path, password = args
    try:
        wb = load_workbook(filename=file_path, password=str(password))
        wb.close()
        return password
    except:
        return None

def generate_numbers(length):
    return (f"{n:0{length}d}" for n in range(10**length))

def brute_force_numeric(excel_path, max_length=5):
    start_time = time.time()
    total_combinations = sum(10**l for l in range(4, max_length+1))
    
    with Pool(processes=cpu_count()) as pool:
        with tqdm(total=total_combinations, desc="Denenen Şifreler") as pbar:
            for length in range(4, max_length+1):
                passwords = [(excel_path, str(p).zfill(length)) for p in range(10**length)]
                
                for result in pool.imap_unordered(try_password, passwords):
                    pbar.update(1)
                    if result:
                        pool.terminate()
                        print(f"\nŞifre bulundu: {result}")
                        print(f"Süre: {time.time()-start_time:.2f} saniye")
                        return result
    return None

def main():
    scraper = MontenegroScraper()
    
    # Paralel arama başlat
    companies = scraper.parallel_search()
    
    if not companies:
        logger.error("Hiç firma bulunamadı!")
        return
    
    # Her firma için detayları topla
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_company = {
            executor.submit(scraper.get_company_details, company): company 
            for company in companies
        }
        
        for future in as_completed(future_to_company):
            try:
                details = future.result()
                if details:
                    results.append(details)
            except Exception as e:
                logger.error(f"Detay toplama hatası: {e}")
    
    # Sonuçları kaydet
    if results:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Excel'e kaydet
        df = pd.DataFrame(results)
        df.to_excel(f'montenegro_companies_{timestamp}.xlsx', index=False)
        
        # JSON'a kaydet
        with open(f'montenegro_companies_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        logger.info(f"\nToplam {len(results)} firma kaydedildi.")

if __name__ == "__main__":
    excel_file = input("Excel dosya yolu: ").strip('"')
    found = brute_force_numeric(excel_file)
    
    if not found:
        print("Şifre bulunamadı! Lütfen maksimum uzunluğu artırın.")
