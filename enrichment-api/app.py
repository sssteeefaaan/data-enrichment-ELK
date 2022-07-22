from uvicorn import run
from load_configuration import load_yaml, load_log_config, LoadEnum
from logging import getLogger
from logging.config import dictConfig
from dotenv import load_dotenv
from multiprocessing_logging import install_mp_handler

load_dotenv("enrichment-api.env")
log_config = load_log_config("./config/log.config.yaml", LoadEnum.FILE)
dictConfig(log_config)
logger = getLogger("enrichment-api")
install_mp_handler(logger)

if __name__ == "__main__":
    try:
        config = load_yaml("config/server.config.yaml")
        config.pop("additional_settings")
        config["port"] = int(config["port"])
        run("server:app", **config)
    except BaseException as e:
        logger.exception(e)