from fastapi import Depends, FastAPI, Request, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from requests import get

from datetime import datetime
from os.path import join as pathjoin
from os import environ
from sys import path as syspath
from json import dumps

syspath.append(pathjoin(syspath[0], ".."))
from app import logger, api_config, log_config, redis_client
from authentication.auth import *
from logic.enrichment import process
from logic.utilities import load_api_config, load_log_config, LoadEnum, write_config, setup_config_change

setup_config_change(logger, log_config, api_config, redis_client)
app = FastAPI(debug=environ.get("FAST_API_DEBUG", "True") == "True", title=environ.get("FAST_API_TITLE", "Data Enrichment"))

@app.post("/enrich", tags=["Data Enrichment"], description="Get additional information about the ip address")
async def enrich(request : Request, body: dict = { "ip": get('https://api.myip.com').json()["ip"] }):
    try:
        logger.warning(f"POST-Enrich: Accessed from [{ request.client.host }:{ request.client.port }]")
        return process(body, api_config)
    except BaseException as e:
        logger.error(e, exc_info=1, stack_info=1)
        return JSONResponse({ "message": "Unsuccess!" }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.get("/api-configuration", dependencies=[Depends(get_current_active_user)], tags=["Admin"])
def read_api_configuration(request : Request):
    logger.debug(f"GET-API-Configuration: Accessed from [{ request.client.host }:{ request.client.port }]")
    return api_config

@app.post("/api-configuration", dependencies=[Depends(get_current_active_user)], tags=["Admin"], description="Upload .yaml API configuration file")
async def update_api_configuration(request : Request, configuration_file: UploadFile):
    try:
        logger.debug(f"POST-API-Configuration: Accessed from [{ request.client.host }:{ request.client.port }]")
        filename = f'./config/user/api-{ datetime.now().strftime("%Y-%m-%d@%H-%M-%S") }.config.yaml'
        content = (await configuration_file.read()).decode("utf-8")
        write_config(filename, content)
        config = load_api_config(content, LoadEnum.STRING)
        redis_client.publish("api-config", dumps(config))
        return { "message": "Success!" }
    except Exception as e:
        logger.error(e, exc_info=1, stack_info=1)
        return JSONResponse({ "message": "Unsuccess!" }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.get("/log-configuration", dependencies=[Depends(get_current_active_user)], tags=["Admin"])
def read_log_configuration(request : Request):
    logger.debug(f"GET-Log-Configuration: Accessed from [{ request.client.host }:{ request.client.port }]")
    return log_config

@app.post("/log-configuration", dependencies=[Depends(get_current_active_user)], tags=["Admin"], description="Upload .yaml log configuration file")
async def update_log_configuration(request : Request, configuration_file: UploadFile):
    try:
        logger.debug(f"POST-Log-Configuration: Accessed from [{ request.client.host }:{ request.client.port }]")
        filename = f'./config/user/log-{ datetime.now().strftime("%Y-%m-%d@%H-%M-%S") }.config.yaml'
        content = (await configuration_file.read()).decode("utf-8")
        write_config(filename, content)
        config = load_log_config(content, LoadEnum.STRING)
        redis_client.publish("log-config", dumps(config))
        return { "message": "Success!" }
    except Exception as e:
        logger.error(e, exc_info=1, stack_info=1)
        return JSONResponse({ "message": "Unsuccess!" }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/token", response_model=Token, tags=["Authentication"])
async def login_for_access_token(request : Request, form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        logger.debug(f"POST-Token: Accessed from [{ request.client.host }:{ request.client.port }]")
        user = authenticate_user(admins_db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                "Incorrect username or password",
                { "WWW-Authenticate": "Bearer" }
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data = { "sub": user.username }, expires_delta = access_token_expires
        )
        return { "access_token": access_token, "token_type": "bearer" }
    except BaseException as e:
        logger.error(e, exc_info=1, stack_info=1)
        return JSONResponse({ "message": "Unsuccess!" }, status_code=status.HTTP_401_UNAUTHORIZED)