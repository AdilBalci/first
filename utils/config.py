import os
from dotenv import load_dotenv
import logging
from pathlib import Path

# .env dosyasını yükle
load_dotenv()

# Proje kök dizini
BASE_DIR = Path(__file__).resolve().parent.parent

# API Anahtarları
HUNTER_API_KEY = os.getenv('HUNTER_API_KEY')
VOILA_NORBERT_API_KEY = os.getenv('VOILA_NORBERT_API_KEY')
SNOV_IO_API_KEY = os.getenv('SNOV_IO_API_KEY')

# Proxy Ayarları
USE_PROXY = os.getenv('USE_PROXY', 'True').lower() == 'true'
PROXY_TIMEOUT = int(os.getenv('PROXY_TIMEOUT', '30'))
PROXY_UPDATE_INTERVAL = int(os.getenv('PROXY_UPDATE_INTERVAL', '300'))
PROXY_MAX_FAILURES = int(os.getenv('PROXY_MAX_FAILURES', '3'))

# Rate Limiting
REQUESTS_PER_MINUTE = int(os.getenv('REQUESTS_PER_MINUTE', '60'))
DELAY_BETWEEN_REQUESTS = float(os.getenv('DELAY_BETWEEN_REQUESTS', '2.0'))

# Arama Ayarları
MAX_SEARCH_RESULTS = int(os.getenv('MAX_SEARCH_RESULTS', '100'))
MAX_SEARCH_DEPTH = int(os.getenv('MAX_SEARCH_DEPTH', '3'))
SEARCH_TIMEOUT = int(os.getenv('SEARCH_TIMEOUT', '30'))

# Dosya Yolları
OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', 'output'))
LOG_DIR = Path(os.getenv('LOG_DIR', 'logs'))
CACHE_DIR = Path(os.getenv('CACHE_DIR', 'cache'))

# Klasörleri oluştur
OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = LOG_DIR / 'app.log'

# Logging ayarları
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Email arama pattern'leri
EMAIL_PATTERNS = [
    r'[\w\.-]+@[\w\.-]+\.\w+',  # Standart email
    r'[\w\.-]+\s*[\[\(]at\[\)\]]\s*[\w\.-]+\s*[\[\(]dot[\)\]]\s*\w+',  # [at] [dot] formatı
    r'[\w\.-]+\s*@\s*[\w\.-]+\s*\.\s*\w+',  # Boşluklu email
]

# Yönetici pozisyonları için arama terimleri
MANAGEMENT_TITLES = [
    'CEO', 'CTO', 'CFO', 'COO', 'CMO',
    'Founder', 'Co-Founder', 'Kurucu', 'Ortak',
    'Director', 'Direktör', 'Yönetici',
    'Manager', 'Müdür', 'Head of'
]

# Google arama sorguları
SEARCH_QUERIES = [
    'site:{domain} "contact" OR "iletişim"',
    'site:{domain} "email" OR "e-mail" OR "mail"',
    'site:{domain} "@{domain}"',
    'site:linkedin.com/company/{company} "email" OR "contact"',
    'filetype:pdf site:{domain} "contact" OR "email"',
]

# HTTP istekleri için varsayılan timeout
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '10'))

# Cache ayarları
CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'
CACHE_TTL = int(os.getenv('CACHE_TTL', '86400'))  # 24 saat 