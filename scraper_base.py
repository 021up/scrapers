import yaml
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

class ScraperBase:
    """爬蟲基礎類，提供通用功能和配置管理"""
    
    def __init__(self, site_name: str, config_path: Optional[str] = None):
        """初始化爬蟲
        
        Args:
            site_name: 網站名稱，對應配置文件中的站點
            config_path: 配置文件路徑，默認為當前目錄的config.yaml
        """
        self.site_name = site_name
        self.config_path = config_path or str(Path(__file__).parent / 'config.yaml')
        self.config = self._load_config()
        self.site_config = self.config['sites'].get(site_name, {})
        
        # 設置日誌
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(f'scraper.{site_name}')
    
    def _load_config(self) -> Dict[str, Any]:
        """加載配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise Exception(f'加載配置文件失敗: {e}')
    
    def get_selector(self, selector_type: str) -> List[str]:
        """獲取指定類型的選擇器列表
        
        Args:
            selector_type: 選擇器類型（如 'card', 'title' 等）
            
        Returns:
            選擇器列表
        """
        selectors = self.site_config.get('selectors', {}).get(selector_type, [])
        if isinstance(selectors, str):
            return [selectors]
        return selectors
    
    def get_base_url(self) -> str:
        """獲取網站基礎URL"""
        return self.site_config.get('base_url', '')
    
    def get_default_params(self) -> Dict[str, str]:
        """獲取默認請求參數"""
        return self.site_config.get('default_params', {})
    
    def get_timeout(self) -> int:
        """獲取請求超時設置"""
        return self.config['default'].get('timeout', 30)
    
    def get_retry_count(self) -> int:
        """獲取重試次數設置"""
        return self.config['default'].get('retry_count', 3)
    
    def get_delay(self) -> int:
        """獲取請求延遲設置"""
        return self.config['default'].get('delay', 2)
    
    def build_url(self, path: str = '', params: Optional[Dict[str, str]] = None) -> str:
        """構建完整的請求URL
        
        Args:
            path: URL路徑
            params: URL參數
            
        Returns:
            完整的URL字符串
        """
        from urllib.parse import urljoin, urlencode
        
        # 合併基礎URL和路徑
        url = urljoin(self.get_base_url(), path.lstrip('/'))
        
        # 合併默認參數和自定義參數
        all_params = self.get_default_params()
        if params:
            all_params.update(params)
        
        # 添加參數到URL
        if all_params:
            url = f'{url}?{urlencode(all_params)}'
        
        return url
    
    async def scrape(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """執行爬蟲（需要在子類中實現）
        
        Returns:
            包含抓取數據的列表
        """
        raise NotImplementedError('子類必須實現scrape方法')