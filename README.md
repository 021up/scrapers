# 通用網站爬蟲API服務

這是一個基於FastAPI的通用網站爬蟲API服務，支持多個網站的數據抓取，並可以輕鬆擴展新的爬蟲功能。目前支持的網站包括Accupass等。

## 功能特點

- 模塊化的爬蟲架構，易於擴展
- 基於FastAPI的RESTful API
- 支持異步操作
- 使用Playwright實現瀏覽器自動化
- 配置文件管理爬蟲參數
- 支持與n8n整合

## 安裝步驟

1. 克隆代碼庫：
```bash
git clone <repository-url>
cd scrapers
```

2. 創建虛擬環境（推薦）：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安裝依賴：
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

服務將在 http://localhost:8000 啟動，可以通過環境變量 `HOST` 和 `PORT` 自定義主機和端口。

### API端點

1. 獲取支持的網站列表：
```
GET /sites
```

2. 執行爬蟲：
```
POST /scrape
```

請求體示例：
```json
{
    "site": "accupass",
    "params": {
        "p": "free",
        "s": "relevance",
        "t": "next-week"
    }
}
```

### 與n8n整合

1. 在n8n中創建HTTP Request節點
2. 設置請求方法為POST
3. 設置URL為 `http://your-api-host:8000/scrape`
4. 設置請求體，包含目標網站和參數

## 部署到Vercel

1. 安裝Vercel CLI：
```bash
npm i -g vercel
```

2. 配置vercel.json：
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

1. 在 `config.yaml` 中添加新網站的配置
2. 創建新的爬蟲類（繼承 `ScraperBase`）
3. 實現 `scrape` 方法

## 注意事項

- 請遵守目標網站的使用條款和robots.txt規則
- 建議設置適當的請求延遲，避免對目標網站造成壓力
- 在生產環境中應該限制CORS來源
- 定期更新依賴包以修復安全漏洞

## 授權

MIT License