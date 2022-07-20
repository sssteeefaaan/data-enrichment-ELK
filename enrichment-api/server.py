from os import environ
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from enrichment import process
from load_configuration import *
from multiprocessing import Manager
from requests import get

apiconfig = Manager().dict(load_api_config_from_file("./config/api.config"))
logconfig = Manager().dict(load_log_config_from_file("./config/log.config"))
app = FastAPI(debug=environ.get("FAST_API_DEBUG", "True") == "True", title=environ.get("FAST_API_TITLE", "Data Enrichment"))

@app.post("/enrich")
async def enrich(body: dict = { "ip": get('https://api.myip.com').json()["ip"] }):
    return process(body, apiconfig)

@app.get("/api-configuration")
def read_api_configuration():
    return apiconfig

@app.post("/api-configuration")
async def update_api_configuration(body: dict):
    try:
        apiconfig.update(load_api_config(body))
        return { "message": "Success!" }
    except Exception as e:
        print(f'[Error]: API-CONFIGURATION: -> ${ e }')
        return JSONResponse({ "message": "Unsuccess!", "error": str(e) }, status_code=400)

@app.get("/log-configuration")
def read_log_configuration():
    return logconfig

@app.post("/log-configuration")
async def update_log_configuration(body: dict):
    try:
        logconfig.update(load_log_config(body))
        return { "message": "Success!" }
    except Exception as e:
        print(f'[Error]: LOG-CONFIGURATION: -> ${ e }')
        return JSONResponse({ "message": "Unsuccess!", "error": str(e) }, status_code=400)