import sys
import numpy as np
from pandas import read_csv
import matplotlib.pyplot as plt


def show_cpu_usage_rate(csv_file_path):
    if (not isinstance(csv_file_path, str) or not csv_file_path.endswith('.csv')):
        raise Exception("You must enter csv file path.")

    # line chart demo
    data = read_csv(csv_file_path)
    cpu_usr = data['CPU.STAT.usr'].tolist()

    t = np.arange(0.0, 3.0, 0.1)
    s = 1 + np.sin(2 * np.pi * t)

    fig, ax = plt.subplots()
    # cpu usage(x axis) from 0 to 100
    ax.plot(t, cpu_usr)
    ax.set(ylim=(0, 100))

    ax.set(xlabel='time (s)', ylabel='usage rate %',
        title='cpu usage rate line chart')
    ax.grid()
    fig.savefig(csv_file_path[:-4] + '.png')
    plt.show()


def show_storage_usage_rate(csv_file_path):
    if (not isinstance(csv_file_path, str) or not csv_file_path.endswith('.csv')):
        raise Exception("You must enter csv file path.")

    data = read_csv(csv_file_path)
    t = np.arange(0.0, 3.0, 0.1) # time mock
    # use different kind of color to draw iowait_r, iowait_w 

    # i/o await
    storage_r_await = data['STORAGE.STAT.r_await'].tolist()
    storage_w_await = data['STORAGE.STAT.w_await'].tolist()

    # i/o throughput
    storage_r_throughput = data['STORAGE.STAT.rMBs']
    storage_w_throughput = data['STORAGE.STAT.wMBs']
    storage_total_throughput = storage_r_throughput + storage_w_throughput
    storage_total_throughput.tolist()
    
    plt.plot(t, storage_r_await, label="storage_r_await")
    plt.plot(t, storage_w_await, label="storage_w_await")
    
    plt.xlabel("recording time in second")
    plt.ylabel("r/w await in ms")
    
    plt.legend()
    plt.show()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise Exception("Only accept one argument as csv file's path")
    show_cpu_usage_rate(sys.argv[1])
