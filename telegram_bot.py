import asyncio
from telethon import TelegramClient, events

# TEST AŞAMASINDA SABİT DEĞERLER
API_ID = 27166914  # KENDİ API ID'NİZİ GİRİN
API_HASH = '24ed4e01f0d82677d32dce7669fd5dce'  # KENDİ API HASH'İNİZİ GİRİN
PHONE_NUMBER = '+905305401461'  # KENDİ TELEFON NUMARANIZ

# Proxy yapılandırmasını güncelleyin
PROXY = {
    'proxy_type': 'mTProto',  # Büyük/küçük harf duyarlılığına dikkat
    'addr': 'proxy.digitalresistance.dog',  # Proxy IP adresi
    'port': 443,  # Port numarası
    'secret': 'd488a2845b0e0d2d023484f7048f4e11'  # 32 karakterlik hex secret
}

# Global değişkenler
client = None
message = "bismillahirrahmanirrahim"
groups = [1
          ]
delay = 0
restart = 0

async def connect_telegram():
    global client
    try:
        client = TelegramClient(
            'session_name', 
            API_ID, 
            API_HASH,
            proxy=PROXY
        )
        await client.start(phone=lambda: PHONE_NUMBER, code_callback=lambda: input('Telegram kodunu girin: '))
        
        if not await client.is_user_authorized():
            await client.send_code_request(PHONE_NUMBER)
            await client.sign_in(PHONE_NUMBER, input('Telegramdan gelen kodu girin: '))
            
        print("Bağlantı başarılı!")
        return client
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        await client.disconnect()
        return None

async def main_menu():
    global client, message, groups, delay, restart
    while True:  # Sürekli menü döngüsü
        print("\n" + "="*30)
        print("1. Telefon Bağlantısı\n2. Mesaj Metni\n3. Grup Seçimi\n4. İşlemi Başlat\n5. Çıkış")
        choice = input("Seçiminiz: ")
        
        if choice == '1':
            PHONE_NUMBER = input("Telefon numaranızı girin (+905XXXXXXXXX formatında): ")
            client = await connect_telegram()
        elif choice == '2':
            message = input("Gönderilecek mesajı girin: ")
            print("Mesaj kaydedildi!")
        elif choice == '3':
            groups = input("Hedef grup ID'lerini virgülle ayırarak girin: ").split(',')
            print(f"{len(groups)} grup seçildi!")
        elif choice == '4':
            while True:
                delay_input = input("Mesajlar arası bekleme süresi (saniye): ")
                if delay_input.isdigit():
                    delay = int(delay_input)
                    break
                print("Lütfen geçerli bir sayı girin!")
            
            while True:
                restart_input = input("Yeniden başlama süresi (dakika): ")
                if restart_input.isdigit():
                    restart = int(restart_input)
                    break
                print("Lütfen geçerli bir sayı girin!")
            
            print("Ayarlar kaydedildi! Bot başlatılıyor...")
            if client and client.is_connected():
                await client.disconnect()
            await asyncio.sleep(5)
            client = await connect_telegram()
            # Mesaj gönderme döngüsü buraya eklenecek
            break
        elif choice == '5':
            print("Çıkış yapılıyor...")
            break
        else:
            print("Geçersiz seçim!")

if __name__ == "__main__":
    asyncio.run(main_menu()) 