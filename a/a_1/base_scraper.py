import random
import time
from typing import Dict, Optional
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

class BaseScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.headers = self._generate_headers()
        
    def _generate_headers(self) -> Dict[str, str]:
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
    def human_like_delay(self, base_delay: float = 10.0) -> None:
        jitter = random.uniform(0.5, 1.5)
        mouse_movement = random.uniform(0.2, 0.5)
        total_delay = base_delay + jitter + mouse_movement
        time.sleep(total_delay)
        
    def simulate_mouse_movement(self, driver):
        actions = ActionChains(driver)
        for _ in range(random.randint(2, 5)):
            x_offset = random.randint(-100, 100)
            y_offset = random.randint(-100, 100)
            actions.move_by_offset(x_offset, y_offset)
        actions.perform()
