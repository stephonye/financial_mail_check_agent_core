"""
汇率转换服务 - 支持多种汇率API
"""
import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Union
from decimal import Decimal
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExchangeRateService:
    """汇率转换服务类"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('EXCHANGE_RATE_API_KEY')
        self.cache = {}
        self.cache_expiry = {}
        
    def get_exchange_rate(self, from_currency: str, to_currency: str = 'USD') -> Optional[Decimal]:
        """获取汇率"""
        if from_currency.upper() == to_currency.upper():
            return Decimal('1.0')
        
        # 检查缓存
        cache_key = f"{from_currency}_{to_currency}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        # 尝试多种汇率API
        rate = self._try_exchangerate_api(from_currency, to_currency)
        if rate is None:
            rate = self._try_frankfurter_api(from_currency, to_currency)
        if rate is None:
            rate = self._try_fallback_rates(from_currency, to_currency)
        
        if rate is not None:
            self.cache[cache_key] = rate
            self.cache_expiry[cache_key] = datetime.now() + timedelta(hours=1)
        
        return rate
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        if cache_key in self.cache and cache_key in self.cache_expiry:
            return datetime.now() < self.cache_expiry[cache_key]
        return False
    
    def _try_exchangerate_api(self, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """使用 exchangerate-api.com"""
        try:
            if self.api_key:
                url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/pair/{from_currency}/{to_currency}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('result') == 'success':
                        return Decimal(str(data['conversion_rate']))
            
            # 免费版本（有限制）
            url = f"https://open.er-api.com/v6/latest/{from_currency}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('result') == 'success':
                    rates = data.get('rates', {})
                    return Decimal(str(rates.get(to_currency, 1)))
                    
        except Exception as e:
            logger.warning(f"exchangerate-api failed: {e}")
        
        return None
    
    def _try_frankfurter_api(self, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """使用 Frankfurter API (免费)"""
        try:
            url = f"https://api.frankfurter.app/latest?from={from_currency}&to={to_currency}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                rates = data.get('rates', {})
                return Decimal(str(rates.get(to_currency, 1)))
        except Exception as e:
            logger.warning(f"frankfurter-api failed: {e}")
        
        return None
    
    def _try_fallback_rates(self, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """备用汇率（静态数据）"""
        # 常见货币对USD的近似汇率（定期需要更新）
        fallback_rates = {
            'EUR': Decimal('1.10'),
            'GBP': Decimal('1.27'),
            'JPY': Decimal('0.0068'),
            'CNY': Decimal('0.14'),
            'CAD': Decimal('0.74'),
            'AUD': Decimal('0.67'),
            'CHF': Decimal('1.12'),
            'HKD': Decimal('0.13'),
            'SGD': Decimal('0.74'),
            'INR': Decimal('0.012'),
            'KRW': Decimal('0.00075'),
            'BRL': Decimal('0.20'),
            'MXN': Decimal('0.059'),
            'RUB': Decimal('0.011'),
        }
        
        # 如果目标货币是USD，直接返回汇率
        if to_currency.upper() == 'USD':
            return fallback_rates.get(from_currency.upper())
        
        # 如果都是非USD货币，通过USD中转计算
        usd_from_rate = fallback_rates.get(from_currency.upper())
        usd_to_rate = fallback_rates.get(to_currency.upper())
        
        if usd_from_rate and usd_to_rate:
            return usd_from_rate / usd_to_rate
        
        return None
    
    def convert_amount(self, amount: Union[float, Decimal, str], 
                      from_currency: str, to_currency: str = 'USD') -> Optional[Decimal]:
        """转换金额"""
        try:
            amount_decimal = Decimal(str(amount))
            exchange_rate = self.get_exchange_rate(from_currency.upper(), to_currency.upper())
            
            if exchange_rate is not None:
                return amount_decimal * exchange_rate
            else:
                logger.warning(f"无法获取 {from_currency} 到 {to_currency} 的汇率")
                return None
                
        except Exception as e:
            logger.error(f"金额转换失败: {e}")
            return None


def create_exchange_service() -> ExchangeRateService:
    """创建汇率服务实例"""
    return ExchangeRateService()


# 示例使用
if __name__ == "__main__":
    service = ExchangeRateService()
    
    # 测试汇率转换
    test_cases = [
        (100, 'EUR', 'USD'),
        (1000, 'JPY', 'USD'),
        (500, 'GBP', 'USD'),
        (100, 'USD', 'USD'),
    ]
    
    for amount, from_curr, to_curr in test_cases:
        result = service.convert_amount(amount, from_curr, to_curr)
        if result:
            print(f"{amount} {from_curr} = {result:.2f} {to_curr}")
        else:
            print(f"无法转换 {amount} {from_curr} 到 {to_curr}")