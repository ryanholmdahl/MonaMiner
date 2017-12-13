import time

from json.decoder import JSONDecodeError

import requests

from constants import API_WAIT_SECONDS, BITCOIN_PRICE_URL, WHATTOMINE_JSON_URL, CONFIG, USER_CONFIG

CACHED_BTC = [None, None]


def get_bitcoin_price():
    if CACHED_BTC[0] is None or time.time() > CACHED_BTC[0] + API_WAIT_SECONDS:
        try:
            r = requests.get(BITCOIN_PRICE_URL).json()
            CACHED_BTC[1] = float(r['bpi']['USD']['rate'].replace(',', ''))
            CACHED_BTC[0] = time.time()
        except Exception:
            print('Failed to update Bitcoin price.')
    return CACHED_BTC[1]


def get_coins():
    r = requests.get(WHATTOMINE_JSON_URL)
    return r.json()['coins']


CACHED_POOL_SIZES = {}


def get_pool_size(pool, coin):
    if pool not in CACHED_POOL_SIZES or time.time() > CACHED_POOL_SIZES[pool][0] + API_WAIT_SECONDS:
        try:
            request = CONFIG['pools'][pool]['coins'][coin]['pool_api']['url']
            if contains_api_key(request):
                    api_key = USER_CONFIG['pools'][pool]['api_key']
                    request.replace('$API_KEY', api_key)
            r = requests.get(request).json()
            for key in CONFIG['pools'][pool]['coins'][coin]['pool_api']['hashrate']:
                r = r[key]
            CACHED_POOL_SIZES[pool] = (time.time(), r)
        except requests.exceptions.RequestException:
            print('Request failed to get pool size of', pool, 'for', coin)
        except JSONDecodeError:
            print('Pool size response from', pool, 'for', coin, 'could not be decoded')
    return CACHED_POOL_SIZES[pool][1]

def contains_api_key(request):
    return '$API_KEY' in request

if __name__ == '__main__':
    print(get_coins().keys())
