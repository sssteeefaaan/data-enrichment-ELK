from yaml import load, FullLoader
from jsonschema import validate
from schemas.api_config_schema import api_configuration_schema
from schemas.logging_config_schema import log_config_schema
from re import compile
from os import environ

pattern = compile('\$\{[^\{\}]+\}')
loader = FullLoader
loader.add_implicit_resolver("", pattern, None)

def constructor_env_variables(loader, node):
    value = loader.construct_scalar(node)
    match = pattern.findall(value)
    if match:
        full_value = value
        for g in match:
            vals = (g[2:-1]).split(":") + [g]
            full_value = full_value.replace(
                vals[-1],
                environ.get(vals[0], vals[1])
            )
        return full_value
    return value

loader.add_constructor("", constructor_env_variables)

def load_api_config(config : dict) -> dict:
    validate(config, api_configuration_schema)
    return config

def load_api_config_from_file(filename: str) -> dict:
    return load_api_config(load_config(filename))

def load_log_config(config: dict) -> dict:
    validate(config, log_config_schema)
    return config

def load_log_config_from_file(filename: str) -> dict:
    return load_log_config(load_config(filename))

def load_config(filename: str) -> dict:
    with open(filename, "r") as f:
        ret = load(f.read(), Loader=loader)
        f.close()
    return ret