from requests import request

from json import loads, dumps
from os.path import join as pathjoin
from sys import path as syspath
from threading import Thread, Lock

syspath.append(pathjoin(syspath[0], ".."))
from app import logger, redis_client
import logic.resolvers as resolvers

def enrich(params: dict, api: dict, lock: Lock, response: dict, paths : dict = dict()):
    try:
        key = api["name"]
        for pv in params.values():
            key = f"{ key }:{ pv }"
        raw_data = redis_client.get(key)
        req = dict()
        if not raw_data:
            req = { x : api.get(x, dict()) for x in ["endpoint", "headers", "query-params", "body", "field-mapping"] }
            for pk, pv in api["parameters"].items():
                value = params[pk]
                for pos in pv["positions"]:
                    if pos == "endpoint":
                        req["endpoint"] = req["endpoint"].replace(pv["key"], value)    
                    else:
                        req[pos][pv["key"]] = value
            res = request(
                method=api["method"],
                url=req["endpoint"],
                params=req["query-params"],
                headers=req["headers"],
                data=req["body"]
            )
            if res.status_code == 200:
                logger.debug(f'Success for [{ api["name"] }]')
                raw_data = res.json()
                redis_client.set(key, dumps(raw_data))
                redis_client.expire(key, int(api["cache-lasts-days"]) * 60 * 60 * 24)
            else:
                raise Exception(f"Endpoint [{ api['name'] }] failed: '{ res.text }'")
        else:
            raw_data = loads(raw_data.decode("utf-8"))
        processed_data = raw_data
        if api["map-fields"]:
            for pk, pv in api["parameters"].items():
                variables = req.get("field-mapping", None)
                if variables == None:
                    variables = dict()
                    for pos in pv["positions"]:
                        if pos == "field-mapping":
                            variables[pv["key"]] = params[pk]
            processed_data = map_fields(raw_data, api["field-mapping"], variables)
            Thread(target=check_unmapped, args=(raw_data, api["name"])).start()
        #api_paths = find_all_paths(processed_data)
        lock.acquire()
        response.update({ api["name"]: processed_data })
        #paths.update({ api["name"]: api_paths })
        lock.release()
    except BaseException as e:
        logger.error(f"{ api['name'] } -> { e }", exc_info=1, stack_info=1)

def find_all_paths(data : dict, prefix : str = "") -> list:
    ret = list()
    for k, v in data.items():
        if type(v) == dict:
            ret += find_all_paths(v, f"{ k }.")
        else:
            ret.append(f"{ prefix }{ k }")
    return ret
    
def check_unmapped(data : dict, name : str, path : str = ""):
    for k, v in data.items():
        if type(v) != dict:
            logger.warning(f"Unused field ['{ path }{ k }' -> '{ v }'] in mappings for [{ name }]")
        else:
            check_unmapped(v, name, f'{ k }.')

def map_fields(data: dict, mapping: dict, variables : dict = dict()):
    res = {}
    try:
        for k in mapping.keys():
            mp = mapping[k]
            if type(mp) == dict:
                res[k] = map_fields(data, mp, variables)
            else:
                res[k] = find_item_path(data, mp.split("."), variables)
    except KeyError as e:
        logger.error(f"KeyError: { e }", exc_info=1, stack_info=1)
    except BaseException as e:
        logger.error(e, exc_info=1, stack_info=1)
    return res

def find_item_path(data : dict, path : list, variables : dict = dict()):
    if len(path) < 1:
        return "ERROR"
    head = path.pop(0)
    head = variables.get(head, head)
    try:
        if not path:
            return data.pop(head)
        return find_item_path(data[head], path)
    except BaseException as e:
        logger.error(e, exc_info=1, stack_info=1)
        return "ERROR"
    
def check_dups(data : dict):
    paths = dict()
    for k, v in data.items():
        for p in v["paths"]:
            if paths.get(p, None):
                paths[p].append(k)
            else:
                paths[p] = [k]
    for k, v in paths.items():
        if len(v) > 1:
            logger.warning(f"Duplicated fields '{ k }' found in: { ', '.join(v) }")

def process(body: dict, config: dict) -> dict:
    threads = list()
    response = dict()
    lock = Lock()
    for api in config["apis"]:
        if api["use"]:
            threads.append(
                Thread(
                    target=enrich,
                    args=(body, api, lock, response)
                )
            )
            threads[-1].start()
    for th in threads: th.join()
    if len(threads) == len(response.keys()): logger.info("Got response from all APIs")
    else: logger.warning("Some APIs failed")
    threads.clear()
    result = dict()
    for resolver in config["duplicates-resolvers"]:
        threads.append(
            Thread(
                target=resolvers.functions[resolver["function"]],
                args=(resolver["path"], resolver["factors"], response, result, lock)
            )
        )
        threads[-1].start()
    for th in threads: th.join()
    result = {
        **response,
        **result
    }
    #Thread(target=check_dups, args=(response,)).start()
    return result