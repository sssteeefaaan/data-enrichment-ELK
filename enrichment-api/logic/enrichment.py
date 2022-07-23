from requests import request

from json import loads, dumps
from os.path import join as pathjoin
from sys import path as syspath
from threading import Thread, Lock

syspath.append(pathjoin(syspath[0], ".."))
from app import logger, redis_client

def enrich(body: dict, api: dict, lock: Lock, response: dict):
    try:
        key = f'{ api["name"] }:{ body["ip"] }'
        data = redis_client.get(key)
        if not data:
            url = api["endpoint"].replace("${IP_ADDRESS_VARIABLE}", body["ip"])
            query = api.get("query-params", None)
            if query and query.get("${IP_ADDRESS_VARIABLE}", False):
                query[query["${IP_ADDRESS_VARIABLE}"]] = body["ip"]
                query["${IP_ADDRESS_VARIABLE}"] = None
            res = request(
                method=api["method"],
                url=url,
                params=query,
                headers=api.get("headers", None),
                data=api.get("body", None)
            )
            if res.status_code == 200:
                logger.debug(f'Success for { api["name"] }!')
                data = res.json()
                redis_client.set(key, dumps(data))
            else:
                raise Exception(res.text)
        else:
            data = loads(data.decode("utf-8"))
        lock.acquire()
        response.update({
            api["name"]: data
        })
        lock.release()
    except BaseException as e:
        logger.error(e)

def process(body: dict, config: dict) -> dict:
    threads = list()
    response = dict()
    lock = Lock()
    for api in config["apis"].values():
        if api["use"]:
            threads.append(Thread(target=enrich, args=(body, api, lock, response)))
            threads[-1].start()
    for th in threads:
        th.join()
    if len(threads) == len(response.keys()):
        logger.info("Got response from all APIs")
    else:
        logger.warning("Some APIs failed")
    return response