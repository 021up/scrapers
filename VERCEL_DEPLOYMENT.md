# Vercel 部署指南

## 優化說明

本項目已針對 Vercel 無伺服器環境進行了特殊優化，主要解決了 Playwright 在 Vercel 環境中的運行問題。以下是優化的關鍵點：

### 1. 優化的 vercel.json 配置

```json
{
    "version": 2,
    "builds": [
        {
            "src": "main.py",
            "use": "@vercel/python",
            "config": {
                "maxLambdaSize": "50mb",
                "buildCommand": "pip install -r requirements.txt && pip install playwright && PLAYWRIGHT_BROWSERS_PATH=/tmp/playwright-browsers playwright install chromium --with-deps && chmod -R 777 /tmp/playwright-browsers"
            }
        }
    ],
    "routes": [
        {
            "src": "/(.*)",
            "dest": "main.py"
        }
    ],
    "env": {
        "PYTHONUNBUFFERED": "1",
        "PLAYWRIGHT_BROWSERS_PATH": "/tmp/playwright-browsers",
        "PYTHON_VERSION": "3.9",
        "PORT": "8000",
        "NODE_VERSION": "18",
        "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD": "0",
        "PLAYWRIGHT_BROWSERS_PATH_PREFIX": "/tmp",
        "PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH": "/tmp/playwright-browsers/chromium-*/chrome-linux/chrome"
    }
}
```

### 2. 優化的 Playwright 配置

我們創建了 `playwright_config.py` 文件，提供針對 Vercel 環境優化的瀏覽器啟動參數：

- 減少記憶體使用量的瀏覽器參數
- 禁用不必要的功能和服務
- 針對無伺服器環境的特殊設置

## 部署步驟

### 準備工作

1. 確保你已經有一個 Vercel 帳戶
2. 安裝 Vercel CLI：

```bash
npm i -g vercel
```

### 部署流程

1. 登入 Vercel：

```bash
vercel login
```

2. 在專案根目錄執行部署命令：

```bash
vercel
```

3. 按照提示完成部署配置：
   - 選擇要部署的專案
   - 確認專案設置
   - 等待部署完成

4. 部署完成後，Vercel 會提供一個部署 URL，可以通過該 URL 訪問你的爬蟲 API 服務。

## 故障排除

如果在 Vercel 環境中遇到 Playwright 相關問題，請檢查：

1. 檢查 Vercel 日誌中是否有關於 Playwright 或 Chromium 的錯誤
2. 確認 `vercel.json` 中的環境變數設置正確
3. 確認 `playwright_config.py` 中的配置適合你的使用場景

## 限制說明

在 Vercel 無伺服器環境中使用 Playwright 有一些限制：

1. 執行時間限制：Vercel 函數有執行時間限制，長時間運行的爬蟲任務可能會超時
2. 記憶體限制：即使經過優化，Playwright 仍然需要較多的記憶體資源
3. 冷啟動延遲：首次請求時可能會有較長的啟動時間

針對這些限制，建議：

1. 優化爬蟲代碼，減少頁面加載和處理時間
2. 考慮使用分頁爬取或增量爬取策略
3. 對於大規模爬蟲任務，考慮使用專用伺服器而非無伺服器環境