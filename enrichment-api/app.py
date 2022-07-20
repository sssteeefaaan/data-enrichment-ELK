from uvicorn import run
from json import loads

if __name__ == "__main__":
    config = loads(open("./config/server.config", "r").read())
    config.pop("additional_settings")
    run("server:app", **config)