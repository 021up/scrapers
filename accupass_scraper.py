import asyncio
from typing import Dict, List, Optional
from playwright.async_api import async_playwright
from scraper_base import ScraperBase

class AccupassScraper(ScraperBase):
    """Accupass網站爬蟲實現"""
    
    def __init__(self):
        super().__init__('accupass')
    
    async def scrape(self, url: Optional[str] = None, params: Optional[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """抓取Accupass網站上的活動信息
        
        Args:
            url: 可選的自定義URL
            params: 可選的URL參數
            
        Returns:
            包含活動信息的列表
        """
        # 使用提供的URL或構建默認URL
        target_url = url or self.build_url(self.site_config['search_path'], params)
        self.logger.info(f'開始抓取: {target_url}')
        
        async with async_playwright() as p:
            # 啟動瀏覽器
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # 設置視窗大小
                await page.set_viewport_size({"width": 1280, "height": 800})
                
                # 訪問頁面
                await page.goto(target_url, wait_until="networkidle")
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(2)
                
                # 查找活動卡片選擇器
                card_selector = None
                for selector in self.get_selector('card'):
                    if await page.query_selector(selector):
                        card_selector = selector
                        self.logger.info(f'使用選擇器: {selector}')
                        break
                
                if not card_selector:
                    raise Exception('無法找到活動卡片')
                
                # 滾動加載更多內容
                no_new_content_count = 0
                while no_new_content_count < 3:
                    # 滾動到底部
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(2)
                    
                    # 檢查新內容
                    old_count = await page.evaluate(f"document.querySelectorAll('{card_selector}').length")
                    await asyncio.sleep(1)
                    new_count = await page.evaluate(f"document.querySelectorAll('{card_selector}').length")
                    
                    if new_count <= old_count:
                        no_new_content_count += 1
                    else:
                        no_new_content_count = 0
                
                # 提取活動信息
                events = []
                cards = await page.query_selector_all(card_selector)
                self.logger.info(f'找到 {len(cards)} 個活動')
                
                for card in cards:
                    try:
                        # 提取連結
                        link_elem = await card.query_selector(self.get_selector('link')[0])
                        event_link = await link_elem.get_attribute('href') if link_elem else ''
                        if event_link and not event_link.startswith('http'):
                            event_link = f"{self.get_base_url()}{event_link}"
                        
                        # 提取標題
                        event_title = '未知標題'
                        for selector in self.get_selector('title'):
                            title_elem = await card.query_selector(selector)
                            if title_elem:
                                event_title = await title_elem.inner_text()
                                break
                        
                        # 提取時間
                        event_time = '未知時間'
                        for selector in self.get_selector('time'):
                            time_elem = await card.query_selector(selector)
                            if time_elem:
                                event_time = await time_elem.inner_text()
                                break
                        
                        # 提取地點
                        event_location = '未知地點'
                        for selector in self.get_selector('location'):
                            location_elem = await card.query_selector(selector)
                            if location_elem:
                                event_location = await location_elem.inner_text()
                                break
                        
                        events.append({
                            'title': event_title,
                            'link': event_link,
                            'time': event_time,
                            'location': event_location
                        })
                        
                    except Exception as e:
                        self.logger.error(f'提取活動信息時出錯: {e}')
                
                return events
                
            finally:
                await browser.close()

# 測試代碼
async def test_scraper():
    scraper = AccupassScraper()
    events = await scraper.scrape()
    print(f'\n抓取到 {len(events)} 個活動:')
    for i, event in enumerate(events, 1):
        print(f'{i}. {event["title"]}: {event["link"]}')

if __name__ == '__main__':
    asyncio.run(test_scraper())