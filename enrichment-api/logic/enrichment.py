from requests import request

from json import loads, dumps
from os.path import join as pathjoin
from sys import path as syspath
from threading import Thread, Lock

syspath.append(pathjoin(syspath[0], ".."))
from app import logger, redis_client
import logic.resolvers as resolvers

def enrich(params: dict, api: dict, lock: Lock, response: dict):
    try:
        key = api["name"]
        for pv in params.values():
            key = f"{ key }:{ pv }"
        raw_data = redis_client.get(key)
        req = dict()
        if not raw_data:
            req = { x : api.get(x, dict()) for x in ["endpoint", "headers", "query-params", "body", "response"] }
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
                logger.debug(f'[Enrichment] Enrich -> Success for [{ api["name"] }]')
                raw_data = res.json()
                redis_client.set(key, dumps(raw_data))
                redis_client.expire(key, int(api["cache-lasts-days"]) * 60 * 60 * 24)
            else:
                raise Exception(f"Endpoint [{ api['name'] }] failed: '{ res.text }'")
        else:
            raw_data = loads(raw_data)
        processed_data = raw_data
        if api["map-fields"]:
            variables = req.get("response", dict())
            for pk, pv in api["parameters"].items():
                for pos in pv["positions"]:
                    if pos == "response":
                        variables[pv["key"]] = params[pk]
            processed_data = map_fields(raw_data, api["field-mapping"], variables)
            Thread(target=check_unmapped, args=(raw_data, api["name"])).start()
        lock.acquire()
        response["raw"].update({
                api["name"]: processed_data
            }
        )
        if api["combine-results"]:
            combine_results(response["combined"], processed_data)
        lock.release()
    except BaseException as e:
        logger.error(f'[Enrichment](enrich): { e } -> { api["name"] }')

def combine_results(data : dict, processed : dict, default = "ERROR"):
    unwanted = set([None, "ERROR", "N/A", "null", ""])
    for k, v in processed.items():
        try:
            if type(v) == dict:
                combine_results(data.setdefault(k, dict()), v)
            elif type(v) == list:
                data[k] = v
            else:
                if v not in unwanted:
                    data[k] = v
        except Exception as e:
            logger.error(f'[Enrichment](combine_results): { e }')
            data[k] = default

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
            logger.warning(f"[Enrichment](check_unmapped): Unused field ['{ path }{ k }' -> '{ v }'] in mappings for [{ name }]")
        else:
            check_unmapped(v, name, f'{ k }.')

def map_fields(data: dict, mapping: dict, variables : dict = dict()):
    res = {}
    try:
        for k, v in mapping.items():
            if type(v) == dict:
                res[k] = map_fields(data, v, variables)
            else:
                res[k] = find_item_path(data, v, variables)
    except BaseException as e:
        logger.error(f'[Enrichment](map_fields): { e }')
    return res

def find_item_path(data : dict, path : list, variables : dict = dict(), default = "ERROR"):
    if len(path) < 1:
        return default
    head = variables.get(path[0], path[0])
    try:
        if len(path) == 1:
            return data.pop(head)
        return find_item_path(data[head], path[1:], variables, default)
    except BaseException as e:
        logger.error(f'[Enrichment](find_item_path): { e } -> { path }')
        return default
    
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
            logger.warning(f"[Enrichment](check_dups): Duplicated fields '{ k }' found in: { ', '.join(v) }")

def process(body: dict, config: dict) -> dict:
    threads = list()
    response = {
        "raw": dict(),
        "combined": dict()
    }
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
    if len(threads) == len(response["raw"].keys()): logger.info("[Enrichment](process): Got response from all APIs")
    else: logger.warning("[Enrichment](process): Some APIs failed")
    threads.clear()
    result = dict()
    for resolver in config["duplicates-resolvers"]:
        threads.append(
            Thread(
                target=resolvers.functions[resolver["function"]],
                args=(resolver["path"], resolver["factors"], response["raw"], result, lock)
            )
        )
        threads[-1].start()
    for th in threads: th.join()
    combine_results(response["combined"], result)
    if config["response-type"] == "clean":
        return response["combined"]
    elif config["response-type"] == "raw":
        return response["raw"]
    else:
        return response