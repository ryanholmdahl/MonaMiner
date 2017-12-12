import datetime
import json
import subprocess
import time
from collections import defaultdict
import pickle

from matplotlib import pyplot as plt

import miner
import profit


# TODO: dynamic benchmarking, shared workers


def load_profit_history(device_ids):
    try:
        profit_history, update_times = pickle.load(open('device_profit_history.pkl', 'rb'))
        for device_id in device_ids:
            if device_id not in profit_history:
                profit_history[device_id] = defaultdict(list)
    except FileNotFoundError:
        profit_history = {device_id: defaultdict(list) for device_id in device_ids}
        update_times = []
    return profit_history, update_times


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
    profit_history, update_times = load_profit_history(devices.keys())
    while True:
        print(datetime.datetime.now())
        update_times.append(datetime.datetime.now())
        for device in devices:
            coin_profits, best_coin, best_algo = profit.get_profit_dict(devices[device], miner.KNOWN_COINS)
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
                plt.plot(update_times[-len(profit_history[device][coin]):], profit_history[device][coin], label=coin)
            plt.legend()
            plt.gcf().autofmt_xdate()
            plt.savefig('history_{}.png'.format(device))
            plt.clf()
        pickle.dump((profit_history, update_times), open('device_profit_history.pkl', 'wb'))
        time.sleep(600)
