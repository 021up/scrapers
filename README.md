# 通用網站爬蟲API服務

這是一個基於FastAPI的通用網站爬蟲API服務，支援多個網站的資料抓取，並可以輕鬆擴展新的爬蟲功能。

## 功能特點

- 模組化的爬蟲架構，易於擴展
- 基於FastAPI的RESTful API
- 支援非同步操作
- 使用Playwright實現瀏覽器自動化
- 設定檔管理爬蟲參數
- 支援與n8n整合
- **通用爬蟲功能**，可爬取任意URL的網頁內容
- 自動捲動載入頁面至無法爬取更多內容
- 提取完整HTML內容和頁面元資料

## 安裝步驟

1. 複製程式碼庫：
```bash
git clone <repository-url>
cd scrapers
```

2. 建立虛擬環境（推薦）：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安裝相依套件：
```bash
pip install -r requirements.txt
```

4. 安裝Playwright瀏覽器：
```bash
python -m playwright install chromium
```

## 使用方法

### 啟動服務

```bash
python main.py
```

服務將在 http://localhost:8000 啟動，可以透過環境變數 `HOST` 和 `PORT` 自訂主機和連接埠。

### API端點

1. 取得支援的網站列表：
```
GET /sites
```

2. 執行預設網站爬蟲：
```
POST /scrape
```

請求本體範例：
```json
{
    "site": "example_site",
    "params": {
        "keyword": "search_term",
        "category": "example_category"
    }
}
```

3. 爬取任意URL網頁內容：
```
POST /scrape_url
```

請求本體範例：
```json
{
    "url": "https://example.com",
    "params": {
        "q": "search_term"
    }
}
```

回應範例：
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

### 與n8n整合

1. 在n8n中建立HTTP Request節點
2. 設定請求方法為POST
3. 設定URL為 `http://your-api-host:8000/scrape` 或 `http://your-api-host:8000/scrape_url`
4. 設定請求本體，包含目標網站和參數

#### n8n伺服器架設或內網穿透

使用n8n與本爬蟲服務整合時，您需要確保：

1. **伺服器架設**：將本爬蟲服務部署到可公開存取的伺服器上，使n8n能夠直接存取API端點。

2. **內網穿透**：如果您在本地開發環境執行爬蟲服務，可以使用以下工具實現內網穿透：
   - [ngrok](https://ngrok.com/)：`ngrok http 8000`
   - [Cloudflare Tunnel](https://www.cloudflare.com/products/tunnel/)
   - [Localtunnel](https://github.com/localtunnel/localtunnel)：`npx localtunnel --port 8000`

   設定完成後，使用產生的公開URL替換n8n中的 `http://your-api-host:8000`。

## 部署到Vercel

1. 安裝Vercel CLI：
```bash
npm i -g vercel
```

2. 設定vercel.json：
```json
{
    "version": 2,
    "builds": [
        {
            "src": "main.py",
            "use": "@vercel/python"
        }
    ],
    "routes": [
        {
            "src": "/(.*)",
            "dest": "main.py"
        }
    ]
}
```

3. 部署：
```bash
vercel
```

## 擴展新網站

1. 在 `config.yaml` 中新增網站的設定
2. 建立新的爬蟲類別（繼承 `ScraperBase`）
3. 實作 `scrape` 方法

## 注意事項

- 請遵守目標網站的使用條款和robots.txt規則
- 建議設定適當的請求延遲，避免對目標網站造成壓力
- 在生產環境中應該限制CORS來源
- 定期更新相依套件以修復安全漏洞

## 授權

MIT License

---

# Universal Web Scraper API Service

This is a universal web scraper API service based on FastAPI, supporting data extraction from multiple websites and easily extensible with new scraper functionalities.

## Features

- Modular scraper architecture, easy to extend
- RESTful API based on FastAPI
- Support for asynchronous operations
- Browser automation using Playwright
- Scraper parameters managed via configuration files
- Integration with n8n
- **Universal scraper functionality** for crawling web content from any URL
- Automatic scrolling to load pages until no more content can be scraped
- Extraction of complete HTML content and page metadata

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd scrapers
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browser:
```bash
python -m playwright install chromium
```

## Usage

### Starting the Service

```bash
python main.py
```

The service will start at http://localhost:8000. You can customize the host and port using the `HOST` and `PORT` environment variables.

### API Endpoints

1. Get list of supported websites:
```
GET /sites
```

2. Execute default website scraper:
```
POST /scrape
```

Request body example:
```json
{
    "site": "example_site",
    "params": {
        "keyword": "search_term",
        "category": "example_category"
    }
}
```

3. Scrape content from any URL:
```
POST /scrape_url
```

Request body example:
```json
{
    "url": "https://example.com",
    "params": {
        "q": "search_term"
    }
}
```

Response example:
```json
{
    "status": "success",
    "data": [
        {
            "url": "https://example.com",
            "title": "Page Title",
            "html": "<html>...</html>",
            "metadata": {
                "description": "Page description",
                "keywords": "keywords"
            }
        }
    ],
    "message": "Successfully scraped web content"
}
```

### Integration with n8n

1. Create an HTTP Request node in n8n
2. Set the request method to POST
3. Set the URL to `http://your-api-host:8000/scrape` or `http://your-api-host:8000/scrape_url`
4. Set the request body to include the target website and parameters

#### n8n Server Setup or Local Tunneling

When integrating this scraper service with n8n, you need to ensure:

1. **Server Setup**: Deploy the scraper service to a publicly accessible server so n8n can directly access the API endpoints.

2. **Local Tunneling**: If you're running the scraper service in a local development environment, you can use the following tools for local tunneling:
   - [ngrok](https://ngrok.com/): `ngrok http 8000`
   - [Cloudflare Tunnel](https://www.cloudflare.com/products/tunnel/)
   - [Localtunnel](https://github.com/localtunnel/localtunnel): `npx localtunnel --port 8000`

   After setup, replace `http://your-api-host:8000` in n8n with the generated public URL.

## Deployment to Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Configure vercel.json:
```json
{
    "version": 2,
    "builds": [
        {
            "src": "main.py",
            "use": "@vercel/python"
        }
    ],
    "routes": [
        {
            "src": "/(.*)",
            "dest": "main.py"
        }
    ]
}
```

3. Deploy:
```bash
vercel
```

## Extending with New Websites

1. Add new website configuration in `config.yaml`
2. Create a new scraper class (inheriting from `ScraperBase`)
3. Implement the `scrape` method

## Notes

- Please comply with the terms of use and robots.txt rules of target websites
- It's recommended to set appropriate request delays to avoid putting pressure on target websites
- In production environments, CORS origins should be restricted
- Regularly update dependencies to fix security vulnerabilities

## License

MIT License