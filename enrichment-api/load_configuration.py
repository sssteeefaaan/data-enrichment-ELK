from yaml import Loader, load, FullLoader
from jsonschema import validate
from schemas.api_config_schema import api_configuration_schema
from schemas.logging_config_schema import log_config_schema
from re import compile
from os import environ
from enum import Enum

loader = FullLoader
class LoadEnum(Enum):
    FILE=0
    BYTES=1
    STRING=2
    DICTIONARY=3

def construct_full_loader(loader: Loader):
    pattern = compile('\$\{[^\{\}]+\}')
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

construct_full_loader(loader)