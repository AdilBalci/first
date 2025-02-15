import logging
from services.email_finder.core import EmailFinder
from utils.config import LOG_LEVEL, OUTPUT_DIR
from datetime import datetime
import json
from pathlib import Path

# Logging ayarları
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

def test_domains():
    """Test edilecek domainler"""
    return [
        "etiya.com",
        "arcelik.com",
        "aselsan.com.tr",
        "turktelekom.com.tr",
        "thy.com"
    ]

def save_results(domain: str, emails: list, success_rate: float):
    """Sonuçları kaydet"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"email_results_{domain}_{timestamp}.json"
    filepath = Path(OUTPUT_DIR) / filename
    
    results = {
        "domain": domain,
        "emails": sorted(list(emails)),
        "success_rate": success_rate,
        "timestamp": timestamp
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Sonuçlar kaydedildi: {filepath}")

def main():
    finder = EmailFinder()
    
    for domain in test_domains():
        logger.info(f"\n{'='*50}")
        logger.info(f"Domain taranıyor: {domain}")
        logger.info(f"{'='*50}")
        
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            # Email'leri bul
            emails = finder.find_emails(domain)
            success_rate = finder.success_rate
            
            logger.info(f"\nBulunan email'ler ({len(emails)}):")
            for email in sorted(emails):
                logger.info(f"- {email}")
            
            logger.info(f"\nBaşarı oranı: {success_rate}%")
            
            # Sonuçları kaydet
            save_results(domain, emails, success_rate)
            
            # Başarı oranı kontrolü
            if success_rate >= 50:
                logger.info("Başarılı! Sonraki domain'e geçiliyor...")
                break
            else:
                retry_count += 1
                if retry_count < max_retries:
                    logger.warning(f"Düşük başarı oranı. Yeniden deneniyor... (Deneme {retry_count}/{max_retries})")
                else:
                    logger.error(f"Maximum deneme sayısına ulaşıldı. Sonraki domain'e geçiliyor...")
        
        logger.info(f"\n{'='*50}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nProgram kullanıcı tarafından durduruldu.")
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {str(e)}")