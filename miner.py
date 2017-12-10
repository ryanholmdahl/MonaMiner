import apis
import json
import time

CONFIG = json.load(open('config.json'))

KNOWN_COINS = {coin for pool in CONFIG['pools'] for coin in CONFIG['pools'][pool]['coins']}

POOL_SIZES = {
    pool: [None, None] for pool in CONFIG['pools'].keys()
}


def get_best_pool(coin, method):
    best_pool = None
    best_score = None
    for pool in CONFIG['pools'].keys():
        if coin in CONFIG['pools'][pool]['coins']:
            if method == 'cheapest':
                score = -CONFIG['pools'][pool]['fee']
            elif method == 'largest':
                if POOL_SIZES[pool][0] is None or time.time() > POOL_SIZES[pool][0] + 5:
                    POOL_SIZES[pool][0] = time.time()
                    POOL_SIZES[pool][1] = apis.get_pool_size(pool, coin)
                score = POOL_SIZES[pool][1]
            else:
                raise ValueError('Method not recognized.')
            if best_pool is None or score > best_score:
                best_pool = pool
                best_score = score
    return best_pool


def get_miner_args(coin, device_id, miner, pool_method='largest'):
    miner_args = CONFIG['miners'][miner]['args']
    pool = get_best_pool(coin, pool_method)
    pool_miner_args = CONFIG['pools'][pool]['miner_args'][miner]
    coin_pool_args = CONFIG['pools'][pool]['coin_miner_args'][coin][miner]
    args = [CONFIG['miners'][miner]['path']]
    for collection in [pool_miner_args, coin_pool_args, miner_args]:
        args += [token.replace('$DEVICE', str(device_id)) for token in collection]
    return args
