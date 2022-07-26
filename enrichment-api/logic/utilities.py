from jsonschema import validate

from enum import Enum
from json import loads
from logging import getLogger
from logging.config import dictConfig
from multiprocessing_logging import install_mp_handler
from os.path import join as pathjoin
from os import environ
from re import compile, sub
from sys import path as syspath
from yaml import Loader, load, FullLoader

syspath.append(pathjoin(syspath[0], ".."))
from schemas.api_config_schema import api_configuration_schema
from schemas.logging_config_schema import log_config_schema

loader = FullLoader
class LoadEnum(Enum):
    FILE=0
    BYTES=1
    STRING=2
    DICTIONARY=3

def construct_full_loader(loader: Loader):
    pattern = compile('\$\{\s*[A-Za-z0-9_]+\s*([\:]\s*[^\}\s]+\s*)?\}')
    loader.add_implicit_resolver("", pattern, None)

    def constructor_env_variables(loader : Loader, node):
        full_value = loader.construct_scalar(node)
        value = sub("\s", "", full_value)
        vals = (value[2:-1]).split(":") + [value]
        value = value.replace(
            vals[-1],
            environ.get(vals[0], vals[1])
        )
        return value

    loader.add_constructor("", constructor_env_variables)

def load_yaml(filename: str) -> dict:
    with open(filename, "r") as f:
        ret = load(f.read(), Loader=loader)
        f.close()
    return ret

def write_config(filename: str, content: str):
    with open(filename, "w") as f:
        f.write(content)
        f.close()

def validate_api_config(config : dict) -> bool:
    validate(config, api_configuration_schema)
    return True

def load_api_config_from_string(content: str) -> dict:
    c = load(content, Loader=loader)
    validate_api_config(c)
    return c

def load_api_config_from_file(filename: str) -> dict:
    c = load_yaml(filename)
    validate_api_config(c)
    return c

def validate_log_config(config: dict) -> dict:
    validate(config, log_config_schema)
    return config

def load_log_config_from_file(filename: str) -> dict:
    c = load_yaml(filename)
    validate_log_config(c)
    return c

def load_log_config_from_string(content: str) -> dict:
    c = load(content, Loader=loader)
    validate_log_config(c)
    return c

def load_api_config(source: dict | bytes | str, type: LoadEnum):
    if type == LoadEnum.DICTIONARY:
        validate_api_config(source)
        return source
    elif type == LoadEnum.STRING:
        return load_api_config_from_string(source)
    elif type == LoadEnum.BYTES:
        s_conf = source.decode("utf-8")
        return load_api_config_from_string(s_conf)
    elif type == LoadEnum.FILE:
        return load_api_config_from_file(source)
    raise BaseException("UNKNOWN TYPE")

def load_log_config(source: dict | bytes | str, type: LoadEnum):
    if type == LoadEnum.DICTIONARY:
        validate_log_config(source)
        return source
    elif type == LoadEnum.STRING:
        return load_log_config_from_string(source)
    elif type == LoadEnum.BYTES:
        s_conf = source.decode("utf-8")
        return load_log_config_from_string(s_conf)
    elif type == LoadEnum.FILE:
        return load_log_config_from_file(source)
    raise BaseException("UNKNOWN TYPE")


def setup_config_change(logger, log_config, api_config, redis_client):

    def change_api_config(msg):
        try:
            api_config.update(loads(msg["data"].decode("utf-8")))
        except BaseException as e:
            logger.error(e)

    def change_log_config(msg):
        try:
            log_config.update(loads(msg["data"].decode("utf-8")))
            dictConfig(log_config)
            logger = getLogger("enrichment-api")
            install_mp_handler(logger)
        except BaseException as e:
            logger.error(e)

    pub_sub = redis_client.pubsub()
    pub_sub.subscribe(**{
        "api-config": change_api_config,
        "log-config": change_log_config
    })
    pub_sub.run_in_thread(0.1)

construct_full_loader(loader)