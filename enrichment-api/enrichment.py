from multiprocessing import Process, Lock, Manager
from multiprocessing.managers import DictProxy
from requests import request

def enrich(body: dict, api: dict, response: DictProxy):
    try:
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
            data = {
                api["name"]: res.json()
            }
            response.update(data)
        else:
            raise res.text
    except Exception as e:
        print(f'[Error]: ${ api["name"] } -> ${ e }')

def process(body: dict, config: dict) -> dict:
    ps = []
    response = Manager().dict()
    for api in config["apis"].values():
        print(f'API[{ api ["name"] }]: { str(api["use"]) }')
        if api["use"]:
            ps.append(Process(target=enrich, args=(body, api, response)))
            ps[-1].start()
    for p in ps:
        p.join()
    return response