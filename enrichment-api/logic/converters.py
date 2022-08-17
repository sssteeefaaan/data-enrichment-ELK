from os.path import join as pathjoin
from sys import path as syspath

syspath.append(pathjoin(syspath[0], ".."))
from app import logger

def string_to_boolean(value : str, default : bool = True) -> bool:
    try:
        if value.lower() == "no":
            return False
        return True
    except:
        logger.error(f"[Converters](string_to_boolean): Couldn't convert '{ value }' to boolean!")
        return default

def null(value, default):
    return value

def to_float(value, default : float = 0):
    try:
        ret = float(value)
        return ret
    except:
        logger.error(f"[Converters](to_float): Couldn't convert '{ value }' to float!")
        return default

def to_int(value, default : int = 0):
    try:
        ret = int(value)
        return ret
    except:
        logger.error(f"[Converters](to_int): Couldn't convert '{ value }' to int!")
        return default

functions = {
    "float": to_float,
    "int": to_int,
    "string-to-boolean": string_to_boolean,
    "null": null
}