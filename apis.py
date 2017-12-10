import requests

WHATTOMINE_JSON_URL = 'http://whattomine.com/coins.json'
BITCOIN_PRICE_URL = 'https://api.coindesk.com/v1/bpi/currentprice.json'

CACHED_BTC = [0.]


def get_bitcoin_price():
    try:
        r = requests.get(BITCOIN_PRICE_URL).json()
        CACHED_BTC.append(float(r['bpi']['USD']['rate'].replace(',', '')))
    except Exception:
        print('Failed to update Bitcoin price.')
    return CACHED_BTC[-1]


def get_coins():
    r = requests.get(WHATTOMINE_JSON_URL)
    return r.json()['coins']

POOL_APIS = {
    'miningpoolhub': {
        'url': 'https://$COIN.miningpoolhub.com/index.php?page=api&action=getpoolstatus&api_key'
                     '=7f931dc99e1c794cb5e5b00850342e32cb3b37cdfe477eac81563abf1907c568',
        'hashrate': lambda j: float(j['getpoolstatus']['data']['hashrate'])
    },
    'electroneum_space': {
        'url': 'http://api.electroneum.space/v1/stats/browser',
        'hashrate': lambda j: float(j['config']['pool']['hashrate'])
    }
}


def get_pool_size(pool, coin):
    r = requests.get(POOL_APIS[pool]['url'].replace('$COIN', coin)).json()
    return POOL_APIS[pool]['hashrate'](r)


if __name__ == '__main__':
    print(get_coins().keys())
