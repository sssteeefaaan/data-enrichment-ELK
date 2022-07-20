from uvicorn import run
from load_configuration import load_config
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv("../enrichment-api.env")
    config = load_config("config/server.config.yaml")
    config.pop("additional_settings")
    config["port"] = int(config["port"])
    run("server:app", **config)