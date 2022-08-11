from os.path import join as pathjoin
from sys import path as syspath
from threading import Thread, Lock

syspath.append(pathjoin(syspath[0], ".."))
from app import logger
import logic.converters as converters

def find_value(data : dict, path : list):
    try:
        head = path[0]
        if len(path) == 1:
            return data[head]
        return find_value(data[head], path[1:])
    except Exception as e:
        logger.error(e, stack_info=True)
        return 0

def set_value(data : dict, path : list, value):
    try:
        head = path[0]
        if len(path) == 1:
            data[head] = value
            return
        data[head] = data.get(head, dict())
        set_value(data[head], path[1:], value)
    except Exception as e:
        logger.error(e, stack_info=True)
        return 0
    
def mean_average(path : str, factors : list, response : dict, result : dict, lock : Lock):
    avg = 0
    list_path = path.split(".")
    for f in factors:
        my_path = f.get("path", list_path)
        if type(my_path) == str:
            my_path = my_path.split(".")
        avg += f["coefficient"] * converters.functions[f["converter"]](find_value(response[f['name']], my_path))
    avg /= len(factors)
    lock.acquire()
    set_value(result, list_path, avg)
    lock.release()

def overwrite(path : str, factors : list, response : dict, result : dict, lock : Lock):
    list_path = path.split(".")
    f = factors[0]
    my_path = f.get("path", list_path)
    if type(my_path) == str:
        my_path = my_path.split(".")
    val = find_value(response[f["name"]], my_path)
    lock.acquire()
    set_value(result, list_path, val)
    lock.release()

functions = {
    "mean-average": mean_average,
    "overwrite": overwrite
}