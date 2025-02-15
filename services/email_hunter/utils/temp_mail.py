import requests
from typing import Optional

class TempMail:
    """Geçici mail servisi"""
    
    def __init__(self):
        self.base_url = "https://temp-mail-api.com"  # Örnek URL
        
    def get_email_address(self) -> str:
        """Yeni geçici mail adresi al"""
        pass
    
    def get_activation_link(self) -> Optional[str]:
        """Aktivasyon linkini al"""
        pass 