from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import time
import asyncio
from datetime import timedelta
from telethon.errors import SessionPasswordNeededError
import re  # Eksik import eklendi

# Kullanıcı ayarları
settings = {
    'phone': '+905305401461',
    'api_id': '27166914',
    'api_hash': '24ed4e01f0d82677d32dce7669fd5dce',
    'message': 'bismillahirrahmanirrahim',
    'groups': [2],
    'interval': 10,
    'repeat_after': 1,  # 1 dakika = 60 saniye
}

async def connect_telegram():
    client = TelegramClient(
        session=f"session_{settings['phone']}",
        api_id=settings['api_id'],
        api_hash=settings['api_hash']
    )
    
    await client.connect()
    
    if not await client.is_user_authorized():
        print("\n📲 Telegram doğrulama kodu gönderildi:")
        print("1. Telegram uygulamasındaki bildirimi kontrol edin")
        print("2. SMS olarak gelen kodu kullanabilirsiniz")
        
        # Kod alma döngüsü
        while True:
            try:
                code = input("\n✉️ 5 haneli kodu girin: ").strip()
                if len(code) == 5 and code.isdigit():
                    await client.sign_in(settings['phone'], code)
                    break
                print("❌ Geçersiz kod! Sadece 5 rakam girin")
            except SessionPasswordNeededError:
                print("\n🔐 2 Aşamalı Doğrulama Gerekli")
                password = input("Uygulama şifrenizi girin: ")
                await client.sign_in(password=password)
                break
            except Exception as e:
                print(f"❌ Hata: {type(e).__name__} - {str(e)}")
                if "CodeInvalid" in str(e):
                    print("⚠️ Yanlış kod! Tekrar deneyin")
                else:
                    raise

    print("✅ Başarıyla giriş yapıldı")
    return client

async def select_groups():
    # Otomatik olarak 2. grubu seç
    client = await connect_telegram()
    result = await client(GetDialogsRequest(
        offset_date=None,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=100,
        hash=0
    ))
    
    groups = [dialog for dialog in result.chats if (
        hasattr(dialog, 'megagroup') and dialog.megagroup
    )]
    
    if len(groups) >= 2:
        settings['groups'] = [groups[1]]  # 2. grup (0-based index)
        print(f"✅ {groups[1].title} grubu otomatik seçildi")
    else:
        print("❌ En az 2 grup bulunamadı!")
        exit()

def menu():
    while True:
        print("\n=== Telegram Oto Mesaj Botu ===")
        print("1) Telefon Bağlantısı ve API Ayarları")
        print("2) Mesaj Metni Belirle")
        print("3) Grupları Seç")
        print("4) Gönderimi Başlat")
        print("5) Çıkış")
        
        choice = input("Seçiminiz: ").strip()
        
        if choice == '1':
            # Telefon numarası validasyonu
            while True:
                phone = input("\nTelefon numarası (+905551234567): ").strip()
                if phone.startswith('+') and phone[1:].isdigit() and len(phone) == 13:
                    settings['phone'] = phone
                    break
                print("❌ Geçersiz format! Örnek: +905551234567")

            # API bilgileri validasyonu
            while True:
                settings['api_id'] = input("\nAPI ID: ").strip()
                if len(settings['api_id']) == 8 and settings['api_id'].isdigit():
                    break
                print("❌ API ID 8 haneli numara olmalı!")

            while True:
                settings['api_hash'] = input("API Hash: ").strip()
                if len(settings['api_hash']) == 32 and re.match("^[a-f0-9]+$", settings['api_hash']):
                    break
                print("❌ API Hash 32 karakterli hexadecimal olmalı!")

            # Bağlantı testi
            try:
                async def test_connection():
                    client = None
                    try:
                        client = await connect_telegram()
                        me = await client.get_me()
                        print(f"\n🔗 Bağlantı başarılı! Kullanıcı: {me.first_name} {me.last_name}")
                    finally:
                        if client:
                            await client.disconnect()
                
                # Event loop'u manuel olarak yönet
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(test_connection())
                loop.close()
                
            except Exception as e:
                print(f"\n❌ KRİTİK HATA: {type(e).__name__}")
                print(f"Detay: {str(e)}")
                if "AUTH_KEY" in str(e):
                    print("Çözüm: 'session_' ile başlayan dosyayı silin")
                settings.update({'api_id': '', 'api_hash': '', 'phone': ''})
        
        elif choice == '2':
            settings['message'] = input("\nMesaj metnini girin: ").strip()
            print(f"✅ Mesaj ayarlandı: '{settings['message']}'")
        
        elif choice == '3':
            asyncio.run(select_groups())
        
        elif choice == '4':
            if not all([settings['phone'], settings['api_id'], settings['api_hash'], settings['groups']]):
                print("\n❌ Lütfen önce 1-3 arası tüm ayarları yapın!")
                continue
            
            print(f"\n⏳ Gönderim başlatılıyor... (Durdurmak için CTRL+C)")
            asyncio.run(start_sending())
        
        elif choice == '5':
            print("\nÇıkış yapılıyor...")
            break
        
        else:
            print("\n❌ Geçersiz seçim! Lütfen 1-5 arası rakam girin")

async def start_sending():
    client = await connect_telegram()
    print("\nGönderim başladı (Durdurmak için CTRL+C)")
    try:
        while True:
            await client.send_message(
                entity=settings['groups'][0],
                message=settings['message']
            )
            print(f"[{time.strftime('%H:%M:%S')}] Mesaj gönderildi")
            await asyncio.sleep(settings['interval'])
    except KeyboardInterrupt:
        print("\nGönderim durduruldu")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    menu() 