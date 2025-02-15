from browser_use import Agent
from langchain_openai import ChatOpenAI
import asyncio
import json
from dotenv import load_dotenv
import os

# Çevresel değişkenleri yükle
load_dotenv()

async def main():
    agent = Agent(
        task="""1. https://gosbteknopark.com/firmalarimiz/ sitesine git
                2. Tüm firma linklerini topla
                3. Her firma sayfasında:
                   - Firma adı (h1)
                   - Web sitesi (target=_blank olan link)
                   - Telefon ve e-posta bilgileri""",
        llm=ChatOpenAI(
            model="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY")  # .env'den oku
        ),
        headless=True
    )
    
    result = await agent.run()
    
    with open("firmalar.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    asyncio.run(main()) 