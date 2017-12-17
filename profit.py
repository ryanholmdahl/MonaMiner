import apis

from constants import KNOWN_COINS


def get_profitability(coin_dict, device_stats):
    if coin_dict['algorithm'] not in device_stats:
        return -1
    btc_price = apis.get_bitcoin_price()
    personal_block_per_hour = 3600 / float(coin_dict['block_time']) * \
                              (device_stats[coin_dict['algorithm']]['hashrate'] / float(coin_dict['nethash']))
    coin_per_hour = coin_dict['block_reward'] * personal_block_per_hour
    return coin_per_hour * coin_dict['exchange_rate'] * 24 * btc_price


def get_profit_dict(device_stats):
    coins = apis.get_coins()
    profits = {}
    best = None
    for coin_tag in KNOWN_COINS:
        profit = get_profitability(coins[coin_tag], device_stats)
        if profit > 0:
            profits[coin_tag] = profit
            if best is None or profit > best[1]:
                best = (coin_tag, profit)
    return profits, best[0], coins[best[0]]['algorithm']
