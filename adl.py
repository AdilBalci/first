from telethon.sync import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
import sys
import csv
import traceback
import time
import random

class TelegramScraper:
    def __init__(self, api_id, api_hash, phone):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.client = TelegramClient(f"session_{phone}", api_id, api_hash)
        
    async def connect(self):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone)
            await self.client.sign_in(self.phone, input('Doğrulama kodunu girin: '))
    
    async def get_members_from_group(self, target_group):
        all_participants = []
        try:
            async for user in self.client.iter_participants(target_group, aggressive=False):
                if not user.bot and not user.deleted and user.privacy_settings is None:
                    all_participants.append({
                        'id': user.id,
                        'username': user.username,
                        'phone': user.phone
                    })
                    if len(all_participants) >= 50:  # Günlük limit
                        break
        except Exception as e:
            print(f"Hata: {e}")
            
        return all_participants

    async def add_members_to_channel(self, channel, members):
        added = 0
        for member in members:
            try:
                user_to_add = InputPeerUser(member['id'], 0)
                await self.client(InviteToChannelRequest(channel, [user_to_add]))
                added += 1
                print(f"Eklenen üye: {member['username']}")
                time.sleep(random.randint(30, 60))  # Rate limiting'den kaçınmak için
                
            except UserPrivacyRestrictedError:
                print(f"Kullanıcı gizlilik ayarları nedeniyle eklenemedi: {member['username']}")
            except PeerFloodError:
                print("Çok fazla istek gönderildi. Biraz bekleyin.")
                break
            except Exception as e:
                print(f"Hata: {e}")
                
        return added

# Kullanım örneği
async def main():
    # Her hesap için ayrı API bilgileri
    accounts = [
        {"api_id": "API_ID_1", "api_hash": "API_HASH_1", "phone": "PHONE_1"},
        # Diğer hesapları buraya ekleyin
    ]
    
    target_groups = [
        "hedef_grup_1",
        "hedef_grup_2"
    ]
    
    destination_channels = [
        "hedef_kanal_1",
        "hedef_kanal_2"
    ]
    
    for account in accounts:
        scraper = TelegramScraper(account["api_id"], account["api_hash"], account["phone"])
        await scraper.connect()
        
        for group in target_groups:
            members = await scraper.get_members_from_group(group)
            
            for channel in destination_channels:
                added = await scraper.add_members_to_channel(channel, members)
                print(f"Toplam eklenen üye sayısı: {added}")
        
        await scraper.client.disconnect()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main()) 