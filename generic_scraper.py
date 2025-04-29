import asyncio
from typing import Dict, List, Optional, Any
from playwright.async_api import async_playwright, Page
from scraper_base import ScraperBase
from playwright_config import get_optimized_browser_config
import json

class GenericScraper(ScraperBase):
    """通用網站爬蟲實現，可爬取任意URL的網頁內容"""
    
    def __init__(self):
        super().__init__('default')
    
    async def scrape(self, url: str, params: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """抓取任意網站的內容
        
        Args:
            url: 目標網站URL
            params: 可選的URL參數
            
        Returns:
            包含網頁內容的字典
        """
        if not url:
            raise ValueError("必須提供URL")
            
        # 如果有參數，將其添加到URL
        if params:
            from urllib.parse import urlencode
            query_string = urlencode(params)
            url = f"{url}{'&' if '?' in url else '?'}{query_string}"
            
        self.logger.info(f'開始抓取: {url}')
        
        async with async_playwright() as p:
            # 啟動瀏覽器，使用優化配置
            browser = await p.chromium.launch(**get_optimized_browser_config())
            page = await browser.new_page()
            
            try:
                # 設置視窗大小
                await page.set_viewport_size({"width": 1280, "height": 800})
                
                # 訪問頁面
                await page.goto(url, wait_until="networkidle")
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(2)
                
                # 滾動加載更多內容
                self.logger.info('開始滾動加載更多內容...')
                last_height = 0
                consecutive_same_count = 0
                max_consecutive_same = 5  # 連續5次相同高度才確定真的沒有更多內容
                scroll_count = 0
                
                while True:
                    # 滾動到底部
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(2)  # 等待內容加載
                    
                    # 獲取當前頁面高度
                    current_height = await page.evaluate("document.body.scrollHeight")
                    scroll_count += 1
                    
                    self.logger.info(f'滾動 {scroll_count} 次，當前頁面高度: {current_height}')
                    
                    if current_height == last_height:
                        consecutive_same_count += 1
                        self.logger.info(f'連續 {consecutive_same_count} 次沒有新內容')
                        
                        # 嘗試點擊「載入更多」按鈕（如果存在）
                        try:
                            load_more_selectors = [
                                'button.load-more', '.btn-load-more', 'a.more', 
                                '[class*="load-more"]', '[class*="loadMore"]',
                                'button:has-text("載入更多")', 'button:has-text("加載更多")',
                                'button:has-text("Load more")', 'a:has-text("Show more")'
                            ]
                            
                            for selector in load_more_selectors:
                                load_more_button = await page.query_selector(selector)
                                if load_more_button:
                                    await load_more_button.click()
                                    await asyncio.sleep(2)
                                    self.logger.info(f'點擊了「{selector}」按鈕')
                                    break
                        except Exception as e:
                            self.logger.debug(f'沒有找到或無法點擊載入更多按鈕: {e}')
                        
                        if consecutive_same_count >= max_consecutive_same:
                            self.logger.info('已達到頁面底部，停止滾動')
                            break
                    else:
                        consecutive_same_count = 0
                        self.logger.info(f'發現新內容，頁面高度從 {last_height} 增加到 {current_height}')
                    
                    last_height = current_height
                
                # 獲取頁面HTML內容
                html_content = await page.content()
                page_title = await page.title()
                page_url = page.url
                
                # 提取頁面元數據
                metadata = await self._extract_metadata(page)
                
                return [{
                    'url': page_url,
                    'title': page_title,
                    'html': html_content,
                    'metadata': metadata
                }]
                
            finally:
                await browser.close()
    
    async def _extract_metadata(self, page: Page) -> Dict[str, str]:
        """提取頁面元數據
        
        Args:
            page: Playwright頁面對象
            
        Returns:
            包含元數據的字典
        """
        metadata = {}
        
        # 提取所有meta標籤
        meta_elements = await page.query_selector_all('meta')
        
        for meta in meta_elements:
            try:
                name = await meta.get_attribute('name') or await meta.get_attribute('property')
                content = await meta.get_attribute('content')
                
                if name and content:
                    metadata[name] = content
            except Exception as e:
                self.logger.debug(f'提取meta標籤時出錯: {e}')
        
        return metadata

# 測試代碼
async def test_scraper():
    scraper = GenericScraper()
    url = input("請輸入要爬取的URL: ")
    results = await scraper.scrape(url)
    
    if results:
        print(f"\n成功爬取: {results[0]['title']}")
        print(f"URL: {results[0]['url']}")
        print(f"元數據: {json.dumps(results[0]['metadata'], indent=2, ensure_ascii=False)}")
        print(f"HTML長度: {len(results[0]['html'])} 字符")
        
        # 保存HTML到文件
        with open('scraped_page.html', 'w', encoding='utf-8') as f:
            f.write(results[0]['html'])
        print("HTML內容已保存到 scraped_page.html")

if __name__ == '__main__':
    asyncio.run(test_scraper())