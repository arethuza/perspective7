import inspect
import time
from collections import defaultdict, namedtuple
import sys

performance_table = defaultdict(lambda: [0, 0, sys.maxsize, 0])


def start():
    return time.clock()


def end(module_name, start_time):
    caller_name = inspect.stack()[1][3]
    end2(module_name, caller_name, start_time)

def end2(module_name, function_name, start_time):
    key = module_name + "." + function_name
    perf_counter = performance_table[key]
    elapsed = time.clock() - start_time
    perf_counter[0] += 1
    perf_counter[1] += elapsed
    if elapsed < perf_counter[2]:
        perf_counter[2] = elapsed
    if elapsed > perf_counter[3]:
        perf_counter[3] = elapsed

def get_report():
    result = {}
    for key, entry in performance_table.items():
        count = entry[0]
        min = entry[2] * 1000
        average = (entry[1] / count) * 1000
        max = entry[3] * 1000
        result[key] = [count, average, min, max]
    return result

