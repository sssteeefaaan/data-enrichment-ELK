from os import environ
from fastapi import Depends, FastAPI, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from enrichment import process
from load_configuration import load_api_config, load_log_config, LoadEnum, write_config
from multiprocessing import Manager
from requests import get
from datetime import datetime
from auth import *
from logging import getLogger
from logging.config import dictConfig
from dotenv import load_dotenv
from app import logger, log_config

load_dotenv("enrichment-api.env")
api_config = Manager().dict(load_api_config("./config/api.config.yaml", LoadEnum.FILE))
app = FastAPI(debug=environ.get("FAST_API_DEBUG", "True") == "True", title=environ.get("FAST_API_TITLE", "Data Enrichment"))

@app.post("/enrich", tags=["Data Enrichment"], description="Get additional information about the ip address")
async def enrich(body: dict = { "ip": get('https://api.myip.com').json()["ip"] }):
    try:
        return process(body, api_config)
    except BaseException as e:
        logger.error(e)
        return JSONResponse({ "message": "Unsuccess!" }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.get("/api-configuration", dependencies=[Depends(get_current_active_user)], tags=["Admin"])
def read_api_configuration():
    return api_config

@app.post("/api-configuration", dependencies=[Depends(get_current_active_user)], tags=["Admin"], description="Upload .yaml API configuration file")
async def update_api_configuration(configuration_file: UploadFile):
    try:
        filename = f'./config/user/api-{datetime.now().strftime("%Y-%m-%d@%H-%M-%S")}.config.yaml'
        content = (await configuration_file.read()).decode("utf-8")
        write_config(filename, content)
        api_config.update(load_api_config(content, LoadEnum.STRING))
        return { "message": "Success!" }
    except Exception as e:
        logger.error(e)
        return JSONResponse({ "message": "Unsuccess!" }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.get("/log-configuration", dependencies=[Depends(get_current_active_user)], tags=["Admin"])
def read_log_configuration():
    return log_config

@app.post("/log-configuration", dependencies=[Depends(get_current_active_user)], tags=["Admin"], description="Upload .yaml log configuration file")
async def update_log_configuration(configuration_file: UploadFile):
    try:
        filename = f'./config/user/log-{datetime.now().strftime("%Y-%m-%d@%H-%M-%S")}.config.yaml'
        content = (await configuration_file.read()).decode("utf-8")
        write_config(filename, content)
        log_config.update(load_log_config(content, LoadEnum.STRING))
        dictConfig(log_config)
        logger = getLogger("enrichment-api")
        return { "message": "Success!" }
    except Exception as e:
        logger.error(e)
        return JSONResponse({ "message": "Unsuccess!" }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/token", response_model=Token, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = authenticate_user(admins_db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except BaseException as e:
        logger.error(e)
        return JSONResponse({ "message": "Unsuccess!" }, status_code=status.HTTP_401_UNAUTHORIZED)