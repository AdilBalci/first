import re
from typing import Dict, Optional, List

class DataProcessor:
    def __init__(self):
        self.email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_regex = r'\+?\d[\d -]{8,12}\d'
        
    def clean_company_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Firma verilerini temizle ve doğrula"""
        cleaned_data = {}
        
        if 'name' in data:
            cleaned_data['name'] = self._clean_text(data['name'])
            
        if 'website' in data:
            cleaned_data['website'] = self._validate_url(data['website'])
            
        if 'emails' in data:
            cleaned_data['emails'] = self._extract_emails(data['emails'])
            
        if 'phones' in data:
            cleaned_data['phones'] = self._extract_phones(data['phones'])
            
        return cleaned_data
        
    def _clean_text(self, text: str) -> str:
        """Metni temizle ve normalize et"""
        if not text:
            return ''
            
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        return text
        
    def _validate_url(self, url: str) -> Optional[str]:
        """URL'yi doğrula ve normalize et"""
        if not url:
            return None
            
        url = url.strip().lower()
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
            
        return url
        
    def _extract_emails(self, text: str) -> List[str]:
        """Metinden email adreslerini çıkar"""
        if not text:
            return []
            
        return list(set(re.findall(self.email_regex, text)))
        
    def _extract_phones(self, text: str) -> List[str]:
        """Metinden telefon numaralarını çıkar"""
        if not text:
            return []
            
        phones = re.findall(self.phone_regex, text)
        return [self._normalize_phone(p) for p in phones]
        
    def _normalize_phone(self, phone: str) -> str:
        """Telefon numarasını normalize et"""
        phone = re.sub(r'[ -]', '', phone)
        if not phone.startswith('+'):
            phone = f'+90{phone}'  # Türkiye kodu varsayılan
        return phone
