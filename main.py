import datetime
import json
import pickle
import subprocess
import time
from collections import defaultdict

import pygal

import miner
import profit
from constants import MINER_POLL_SECONDS, COIN_UPDATE_SECONDS


def load_profit_history(device_ids):
    try:
        profit_history = pickle.load(open('device_profit_history.pkl', 'rb'))
        for device_id in device_ids:
            if device_id not in profit_history:
                profit_history[device_id] = defaultdict(list)
    except FileNotFoundError:
        profit_history = {device_id: defaultdict(list) for device_id in device_ids}
    return profit_history


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


def start_new_miner(device_id, coin, miner_name):
    args = miner.get_miner_args(coin, device_id, miner_name)
    print('Device', device_id, 'starting new process with arguments', args)
    return subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE)


def update_device_coin(device_id, device_stats, current_coin, miner_process):
    coin_profits, best_coin, best_algo = profit.get_profit_dict(device_stats)
    if miner_process is None or best_coin != current_coin:
        if miner_process is not None:
            miner_process.terminate()
            miner_process.wait()
        miner_process = start_new_miner(device_id, best_coin, device_stats[best_algo]["miner"])
    print('Device', device_id, 'now mining', best_coin, 'at ${}'.format(coin_profits[best_coin]))
    return best_coin, best_algo, miner_process, coin_profits


def poll_miner(device_id, current_coin, miner_name, miner_process):
    if miner_process.poll() is not None:
        miner_process = start_new_miner(device_id, current_coin, miner_name)
    return miner_process


def plot_profit_history(device_id, device_profit_history):
    line_chart = pygal.DateTimeLine(x_label_rotation=35,
                                    truncate_label=-1,
                                    x_value_formatter=lambda dt: dt.strftime('%d, %b %Y'),
                                    show_dots=False,
                                    y_title='USD/Day')
    line_chart.title = 'Device {} Profit'.format(device_id)

    max_profits = defaultdict(int)
    for coin in device_profit_history:
        line_chart.add(coin, device_profit_history[coin])
        for t, p in device_profit_history[coin]:
            max_profits[t] = max(max_profits[t], p)
    line_chart.add('Max Profit', sorted(list(max_profits.items()), key=lambda x: x[0]))
    line_chart.render_to_file('profit_{}.html'.format(device_id))


def main():
    all_device_stats = get_device_stats()
    device_current_coin = {device_id: None for device_id in all_device_stats}
    device_current_algo = {device_id: None for device_id in all_device_stats}
    miner_processes = {device_id: None for device_id in all_device_stats}
    profit_history = load_profit_history(all_device_stats.keys())
    seconds_to_poll_update = 0
    seconds_to_coin_update = 0
    while True:
        loop_start = time.time()
        if seconds_to_coin_update <= 0:
            now = datetime.datetime.now()
            print(now)
            for device_id, device_stats in all_device_stats.items():
                device_current_coin[device_id], device_current_algo[device_id], \
                miner_processes[device_id], coin_profits = update_device_coin(device_id, device_stats,
                                                                              device_current_coin[device_id],
                                                                              miner_processes[device_id])
                for coin in coin_profits:
                    profit_history[device_id][coin].append((now, coin_profits[coin]))
                plot_profit_history(device_id, profit_history[device_id])
            pickle.dump(profit_history, open('device_profit_history.pkl', 'wb'))
            seconds_to_coin_update = COIN_UPDATE_SECONDS
        coin_update_end = time.time()

        seconds_to_poll_update -= time.time() - loop_start
        if seconds_to_poll_update <= 0:
            for device_id, device_stats in all_device_stats.items():
                miner_processes[device_id] = poll_miner(device_id, device_current_coin[device_id],
                                                        device_stats[device_current_algo[device_id]]['miner'],
                                                        miner_processes[device_id])
            seconds_to_poll_update = MINER_POLL_SECONDS
        seconds_to_coin_update -= time.time() - coin_update_end

        sleep_time = max(0, min(seconds_to_coin_update, seconds_to_poll_update))
        time.sleep(sleep_time)
        seconds_to_coin_update -= sleep_time
        seconds_to_poll_update -= sleep_time


if __name__ == '__main__':
    main()
