from abc import ABC, abstractmethod
from typing import List, Dict, Set
import re
import logging

class BaseEmailFinder(ABC):
    """Temel email bulma sınıfı"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.email_patterns = [
            r'[\w\.-]+@[\w\.-]+\.\w+',  # normal format
            r'[\w\.-]+\s*@\s*[\w\.-]+\.\w+',  # boşluklu format
            r'[\w\.-]+\s*\[at\]\s*[\w\.-]+\s*\[dot\]\s*\w+',  # [at] format
        ]
    
    def clean_email(self, email: str) -> str:
        """Email adresini temizler ve formatlar"""
        return email.replace('[at]', '@').replace('[dot]', '.').replace(' ', '').lower()
    
    def validate_email(self, email: str) -> bool:
        """Email adresinin geçerli olup olmadığını kontrol eder"""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, email))
    
    def extract_emails_from_text(self, text: str) -> Set[str]:
        """Metin içinden email adreslerini çıkarır"""
        found_emails = set()
        for pattern in self.email_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                email = self.clean_email(match)
                if self.validate_email(email):
                    found_emails.add(email)
        return found_emails
    
    @abstractmethod
    def find_emails(self, domain: str) -> Dict[str, List[str]]:
        """Email adresleri bulur - alt sınıflar tarafından uygulanmalı"""
        pass 