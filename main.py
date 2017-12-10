import datetime
import subprocess
import time
from collections import defaultdict
from matplotlib import pyplot as plt
import apis
import json

import miner
import profit

# TODO: dynamic benchmarking, shared workers


def get_device_stats():
    benchmarks = json.load(open('devices.json'))
    return {
        device_id: {
            algo: {
                "miner": max(miner_dict.keys(), key=(lambda m: miner_dict[m])),
                "hashrate": max(miner_dict.values())
            } for algo, miner_dict in algo_dict.items()
        } for device_id, algo_dict in benchmarks.items()
    }


def start_new_miner(device, coin, miner_name):
    args = miner.get_miner_args(coin, device, miner_name)
    print('Device', device, 'starting new process with arguments', args)
    return subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE)

if __name__ == '__main__':
    devices = get_device_stats()
    device_current_coin = {}
    miner_processes = {}
    profit_history = {device: defaultdict(list) for device in devices}
    update_times = []
    while True:
        print(datetime.datetime.now())
        update_times.append(datetime.datetime.now())
        btc = apis.get_bitcoin_price()
        for device in devices:
            coin_profits, best_coin, best_algo = profit.get_profit_dict(devices[device], miner.KNOWN_COINS, btc)
            if device not in miner_processes or best_coin != device_current_coin[device]:
                device_current_coin[device] = best_coin
                if device in miner_processes:
                    miner_processes[device].terminate()
                    returncode = miner_processes[device].wait()
                miner_processes[device] = start_new_miner(device, best_coin, devices[device][best_algo]["miner"])
            print('Device', device, 'now mining',
                  device_current_coin[device], 'at ${}'.format(coin_profits[best_coin]))
            for coin in coin_profits:
                profit_history[device][coin].append(coin_profits[coin])
                plt.plot(update_times, profit_history[device][coin], label=coin)
            plt.legend()
            plt.gcf().autofmt_xdate()
            plt.savefig('history_{}.png'.format(device))
            plt.clf()
        time.sleep(600)
