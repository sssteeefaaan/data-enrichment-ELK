from dotenv import load_dotenv
from multiprocessing_logging import install_mp_handler
from redislite import Redis
from uvicorn import run

from logic.utilities import load_yaml, load_log_config, load_api_config, LoadEnum

from logging.config import dictConfig
from logging import getLogger

load_dotenv("enrichment-api.env")

api_config = load_api_config("./config/api.config.yaml", LoadEnum.FILE)

log_config = load_log_config("./config/log.config.yaml", LoadEnum.FILE)
dictConfig(log_config)
logger = getLogger("enrichment-api")
install_mp_handler(logger)

redis_client = Redis('/tmp/data-enrichment.db')

def main():
    try:
        config = load_yaml("config/server.config.yaml")
        config.pop("additional_settings")
        config["port"] = int(config["port"])

        run("logic.server:app", **config)
    except BaseException as e:
        logger.error(f"[App](main): { e }")

if __name__ == "__main__":
    main()