from fastapi import FastAPI, Response, status, Request
from logging import getLogger, makeLogRecord
from logging.config import dictConfig
from load_configuration import load_log_config, LoadEnum
from time import strptime

config = load_log_config("./config/log.config.yaml", LoadEnum.FILE)
dictConfig(config)
logger = getLogger("enrichment-api")

app = FastAPI()

@app.get("/log")
async def log(request: Request):
    try:
        data = {}
        for k in request.query_params.keys():
            v = request.query_params.get(k)
            if k in { "levelno", "lineno", "process", "thread" }:
                data[k] = int(v)
            elif k in { "created", "msecs", "relativeCreated" }:
                data[k] = float(v)
            elif k in { "asctime" }:
                data[k] = strptime(v, "%Y-%m-%dT%H:%M:%S%z")
            else:
                data[k] = v
        rec = makeLogRecord(data)
        logger.handle(rec)
        return Response("OK")
    except BaseException as e:
        logger.error(e)
        return Response("Failed", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, media_type="text/plain")