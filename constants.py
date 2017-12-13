import json

CONFIG = json.load(open('config.json'))
USER_CONFIG = json.load(open('user_config.json'))
KNOWN_COINS = {coin for pool in CONFIG['pools'] for coin in CONFIG['pools'][pool]['coins'].keys()}

WHATTOMINE_JSON_URL = 'http://whattomine.com/coins.json'
BITCOIN_PRICE_URL = 'https://api.coindesk.com/v1/bpi/currentprice.json'
API_WAIT_SECONDS = 5
