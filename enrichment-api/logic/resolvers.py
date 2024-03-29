from os.path import join as pathjoin
from sys import path as syspath
from threading import Thread, Lock

syspath.append(pathjoin(syspath[0], ".."))
from app import logger
import logic.converters as converters

def find_value(data : dict, path : list, default = 0):
    try:
        head = path[0]
        if len(path) == 1:
            return data[head]
        return find_value(data[head], path[1:])
    except Exception as e:
        logger.error(f'[Resolvers](find_value): { e } -> { path }')
        return default

def set_value(data : dict, path : list, value):
    try:
        head = path[0]
        if len(path) == 1:
            data[head] = value
        else:
            data[head] = data.get(head, dict())
            set_value(data[head], path[1:], value)
    except Exception as e:
        logger.error(f'[Resolvers](set_value): { e } -> { path }')
    
def mean_average(path : list, factors : list, response : dict, result : dict, lock : Lock):
    try:
        avg = 0
        for f in factors:
            my_path = f.get("path", path)
            avg += f["coefficient"] * converters.functions[f["converter"]](find_value(response[f['name']], my_path))
        avg /= len(factors)
        lock.acquire()
        set_value(result, path, avg)
        lock.release()
    except Exception as e:
        logger.error(f'[Resolvers](mean_average): { e } -> { path }')

def overwrite(path : list, factors : list, response : dict, result : dict, lock : Lock):
    try:
        f = factors[0]
        my_path = f.get("path", path)
        val = find_value(response[f["name"]], my_path)
        lock.acquire()
        set_value(result, path, val)
        lock.release()
    except Exception as e:
        logger.error(f'[Resolvers](overwrite): { e } -> { path }')

def or_resolver(path : list, factors : list, response : dict, result : dict, lock : Lock):
    try:
        value = False
        for f in factors:
            my_path = f.get("path", path)
            value = value or converters.functions[f.get("converter", "null")](find_value(response[f['name']], my_path, False), False)
            if value:
                break
        lock.acquire()
        set_value(result, path, value)
        lock.release()
    except Exception as e:
        logger.error(f'[Resolvers](or_resolver): { e } -> { path }')
        

def and_resolver(path : list, factors : list, response : dict, result : dict, lock : Lock):
    try:
        value = True
        for f in factors:
            my_path = f.get("path", path)
            value = value and converters.functions[f.get("converter", "null")](find_value(response[f['name']], my_path, True), True)
            if not value:
                break
        lock.acquire()
        set_value(result, path, value)
        lock.release()
    except Exception as e:
        logger.error(f'[Resolvers](and_resolvser): { e } -> { path }')

functions = {
    "mean-average": mean_average,
    "overwrite": overwrite,
    "or": or_resolver,
    "and": and_resolver
}