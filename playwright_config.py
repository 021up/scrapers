# Playwright在Vercel無伺服器環境的優化配置

from typing import Dict, Any
import os

def get_optimized_browser_config() -> Dict[str, Any]:
    """
    返回針對Vercel無伺服器環境優化的Playwright瀏覽器配置
    
    Returns:
        Dict[str, Any]: 優化的瀏覽器配置參數
    """
    # 檢測是否在Vercel環境中運行
    is_vercel = os.environ.get('VERCEL', '0') == '1'
    
    # 基本配置
    config = {
        "headless": True,
        # 減少記憶體使用
        "args": [
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--disable-setuid-sandbox",
            "--no-sandbox",
            "--no-zygote",
            "--single-process",
            "--disable-extensions",
            "--disable-accelerated-2d-canvas",
            "--disable-web-security",
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-breakpad",
            "--disable-component-extensions-with-background-pages",
            "--disable-features=TranslateUI,BlinkGenPropertyTrees",
            "--disable-ipc-flooding-protection",
            "--disable-renderer-backgrounding",
            "--mute-audio",
            "--disable-default-apps",
            "--disable-sync",
            "--hide-scrollbars",
            "--metrics-recording-only",
            "--no-first-run",
            "--safebrowsing-disable-auto-update",
            "--disable-features=site-per-process",
            "--disable-threaded-animation",
            "--disable-threaded-scrolling",
            "--disable-histogram-customizer",
            "--memory-pressure-off",
            "--use-gl=swiftshader",
            "--ignore-certificate-errors",
            "--window-size=1280,720"
        ],
        # 減少記憶體使用的額外選項
        "handle_sigint": False,
        "handle_sigterm": False,
        "handle_sighup": False
    }
    
    # 在Vercel環境中的特殊配置
    if is_vercel:
        # 使用環境變數中指定的Chromium可執行文件路徑
        executable_path = os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH')
        if executable_path:
            config['executablePath'] = executable_path
        
        # 在Vercel環境中進一步限制資源使用
        config['args'].extend([
            "--js-flags=--expose-gc",
            "--disable-notifications",
            "--disable-infobars",
            "--disable-translate",
            "--disable-save-password-bubble"
        ])
    
    return config