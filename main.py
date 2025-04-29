import os
import json
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scraper_base import ScraperBase
from generic_scraper import GenericScraper

# 創建FastAPI應用
app = FastAPI(
    title="網站爬蟲API",
    description="提供多個網站的爬蟲服務API，包含各大活動平台的活動資訊爬取功能",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應該限制來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    """爬蟲請求模型
    
    Attributes:
        site: 目標網站代號，例如 'accupass'
        url: 可選的自定義URL，如果不提供則使用預設搜索頁面
        params: 可選的URL參數，用於過濾結果
            - p: 價格類型 (free: 免費)
            - t: 時間範圍 (next-week: 下週)
    """    
    site: str
    url: Optional[str] = None
    params: Optional[Dict[str, str]] = None

class GenericScrapeRequest(BaseModel):
    """通用爬蟲請求模型
    
    Attributes:
        url: 要爬取的網頁URL
        params: 可選的URL參數
    """    
    url: str
    params: Optional[Dict[str, str]] = None

class ScrapeResponse(BaseModel):
    """爬蟲響應模型
    
    Attributes:
        status: 爬蟲執行狀態 (success/error)
        data: 爬取到的活動資訊列表
            - title: 活動標題
            - link: 活動連結
            - time: 活動時間
            - location: 活動地點
        message: 執行結果描述
    """    
    status: str
    data: List[Dict[str, Any]]
    message: Optional[str] = None

@app.get("/")
async def root():
    """API根路徑
    
    使用curl命令示例:
    ```bash
    curl -X GET http://localhost:8000/
    ```
    
    響應示例:
    ```json
    {"message": "歡迎使用網站爬蟲API"}
    ```
    """
    return JSONResponse(
        content={"message": "歡迎使用網站爬蟲API"},
        media_type="application/json; charset=utf-8"
    )

@app.post("/scrape", response_model=ScrapeResponse, tags=["爬蟲"])
async def scrape(request: ScrapeRequest):
    """執行網站爬蟲
    
    Args:
        request: 包含目標網站和參數的請求對象
        
    Returns:
        ScrapeResponse: 包含爬取結果的響應對象
        
    使用curl命令示例:
    1. 基本爬蟲請求:
    ```bash
    curl -X POST http://localhost:8000/scrape \
        -H "Content-Type: application/json" \
        -d '{"site": "eventsite"}'
    ```
    
    2. 帶參數的爬蟲請求:
    ```bash
    curl -X POST http://localhost:8000/scrape \
        -H "Content-Type: application/json" \
        -d '{
            "site": "eventsite",
            "params": {
                "p": "free",
                "t": "next-week"
            }
        }'
    ```
    
    3. 自定義URL的爬蟲請求:
    ```bash
    curl -X POST http://localhost:8000/scrape \
        -H "Content-Type: application/json" \
        -d '{
            "site": "eventsite",
            "url": "https://www.eventsite.com/search",
            "params": {
                "q": "python"
            }
        }'
    ```
    
    4. n8n整合示例:
    ```bash
    # 在n8n的HTTP Request節點中使用以下配置:
    # Method: POST
    # URL: http://localhost:8000/scrape
    # Headers: {"Content-Type": "application/json"}
    # Body: {
    #   "site": "eventsite",
    #   "params": {
    #     "p": "free",
    #     "t": "next-week"
    #   }
    # }
    ```
    
    範例請求:
        ```json
        {
            "site": "eventsite",
            "params": {
                "p": "free",
                "t": "next-week"
            }
        }
        ```
    
    範例響應:
        ```json
        {
            "status": "success",
            "data": [
                {
                    "title": "活動標題",
                    "link": "活動連結",
                    "time": "活動時間",
                    "location": "活動地點"
                }
            ],
            "message": "成功從 eventsite 抓取 1 條數據"
        }
        ```
    """
    try:
        # 檢查網站是否在配置中
        scraper_base = ScraperBase('default')
        available_sites = scraper_base.config['sites'].keys()
        
        if request.site not in available_sites:
            raise HTTPException(status_code=400, detail=f"不支持的網站: {request.site}，可用的網站有: {', '.join(available_sites)}")
        
        # 嘗試動態導入對應的爬蟲模組
        module_name = f"{request.site}_scraper"
        try:
            # 嘗試導入特定網站的爬蟲模組
            scraper_module = __import__(module_name)
            scraper_class = getattr(scraper_module, f"{request.site.capitalize()}Scraper")
            scraper = scraper_class()
        except (ImportError, AttributeError) as e:
            # 如果特定網站的爬蟲模組不存在，使用通用爬蟲
            scraper = GenericScraper()
            # 從配置中獲取網站的基礎URL
            site_config = scraper_base.config['sites'].get(request.site, {})
            base_url = site_config.get('base_url', '')
            search_path = site_config.get('search_path', '')
            
            # 如果用戶沒有提供URL，則使用配置中的URL
            if not request.url and base_url:
                request.url = base_url
                if search_path:
                    request.url = f"{base_url}{search_path}"
        
        # 執行爬蟲
        results = await scraper.scrape(
            url=request.url,
            params=request.params
        )
        
        response = ScrapeResponse(
            status="success",
            data=results,
            message=f"成功從 {request.site} 抓取 {len(results)} 條數據"
        )
        
        return JSONResponse(
            content=response.dict(),
            media_type="application/json; charset=utf-8"
        )
        
    except HTTPException as e:
        # 直接重新拋出HTTP異常
        raise e
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "data": []
            },
            media_type="application/json; charset=utf-8"
        )

@app.post("/scrape_url", response_model=ScrapeResponse, tags=["爬蟲"])
async def scrape_url(request: GenericScrapeRequest):
    """爬取任意URL的網頁內容
    
    Args:
        request: 包含目標URL和參數的請求對象
        
    Returns:
        ScrapeResponse: 包含爬取結果的響應對象
        
    使用curl命令示例:
    ```bash
    curl -X POST http://localhost:8000/scrape_url \
        -H "Content-Type: application/json" \
        -d '{
            "url": "https://example.com"
        }'
    ```
    
    範例請求:
        ```json
        {
            "url": "https://example.com",
            "params": {
                "q": "search_term"
            }
        }
        ```
    
    範例響應:
        ```json
        {
            "status": "success",
            "data": [
                {
                    "url": "https://example.com",
                    "title": "網頁標題",
                    "html": "<html>...</html>",
                    "metadata": {
                        "description": "網頁描述",
                        "keywords": "關鍵詞"
                    }
                }
            ],
            "message": "成功爬取網頁內容"
        }
        ```
    """
    try:
        # 創建通用爬蟲實例
        scraper = GenericScraper()
        
        # 執行爬蟲
        results = await scraper.scrape(
            url=request.url,
            params=request.params
        )
        
        response = ScrapeResponse(
            status="success",
            data=results,
            message=f"成功爬取網頁內容"
        )
        
        return JSONResponse(
            content=response.dict(),
            media_type="application/json; charset=utf-8"
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "data": []
            },
            media_type="application/json; charset=utf-8"
        )

@app.get("/sites")
def get_available_sites():
    """獲取支持的網站列表
    
    使用curl命令示例:
    ```bash
    curl -X GET http://localhost:8000/sites
    ```
    
    響應示例:
    ```json
    {"sites": ["eventsite"]}
    ```
    """
    # 從配置文件中讀取支持的網站
    scraper = ScraperBase('default')
    sites = list(scraper.config['sites'].keys())
    return JSONResponse(
        content={"sites": sites},
        media_type="application/json; charset=utf-8"
    )

if __name__ == "__main__":
    import uvicorn
    # 獲取環境變量或使用默認值
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True  # 開發模式下啟用熱重載
    )