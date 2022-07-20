from json import loads
from jsonschema import validate
from schemas.api_config_schema import api_configuration_schema
from schemas.logging_config_schema import log_config_schema

def load_api_config(config : dict) -> dict:
    validate(config, api_configuration_schema)
    return config

def load_api_config_from_file(filename: str) -> dict:
    return load_api_config(loads(open(filename, "r").read()))

def load_log_config(config: dict) -> dict:
    validate(config, log_config_schema)
    return config

def load_log_config_from_file(filename: str) -> dict:
    return load_log_config(loads(open(filename, "r").read()))
