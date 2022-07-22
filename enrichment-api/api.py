from uvicorn.workers import UvicornWorker
from load_configuration import load_yaml, load_log_config, LoadEnum
from logging import getLogger
from logging.config import dictConfig
from dotenv import load_dotenv
from multiprocessing_logging import install_mp_handler
from multiprocessing import Manager

load_dotenv("enrichment-api.env")
manager = Manager().dict()
manager["log_config"] = load_log_config("./config/log.config.yaml", LoadEnum.FILE)
dictConfig(manager["log_config"])
manager["logger"] = getLogger("enrichment-api")
install_mp_handler(manager["logger"])
config = load_yaml("config/server.config.yaml")
config.pop("additional_settings")
config["port"] = int(config["port"])

class MyUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = config