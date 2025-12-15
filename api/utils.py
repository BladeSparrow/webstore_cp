import requests
from django.core.cache import cache

EXCHANGE_API_URL = "https://v6.exchangerate-api.com/v6/f356d2eb621b815d1d72c4f4/latest/USD"
CACHE_KEY = 'usd_uah_rate'
CACHE_TIMEOUT = 3600  

def get_usd_to_uah_rate():
    rate = cache.get(CACHE_KEY)
    if rate:
        return rate

    try:
        response = requests.get(EXCHANGE_API_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get('result') == 'success':
            conversion_rates = data.get('conversion_rates', {})
            uah_rate = conversion_rates.get('UAH')
            
            if uah_rate:
                cache.set(CACHE_KEY, uah_rate, CACHE_TIMEOUT)
                return uah_rate
                
    except requests.RequestException as e:
        print(f"Error fetching exchange rate: {e}")
        return None

    return None
