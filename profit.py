import apis


def get_profitability(coin_dict, device_stats):
    if coin_dict['algorithm'] not in device_stats:
        return -1
    btc = apis.get_bitcoin_price()
    personal_block_per_hour = 3600 / float(coin_dict['block_time']) * \
                              (device_stats[coin_dict['algorithm']]['hashrate'] / float(coin_dict['nethash']))
    coin_per_hour = coin_dict['block_reward'] * personal_block_per_hour
    return coin_per_hour * coin_dict['exchange_rate'] * 24 * btc


def get_profit_dict(device_stats, known_coins):
    coins = apis.get_coins()
    for coin in coins:
        coins[coin]['name'] = coin
    profits = {}
    best = None
    for coin_dict in coins.values():
        profit = get_profitability(coin_dict, device_stats)
        if profit > 0 and coin_dict['name'] in known_coins:
            profits[coin_dict['name']] = profit
            if best is None or profit > best[1]:
                best = (coin_dict['name'], profit)
    return profits, best[0], coins[best[0]]['algorithm']
