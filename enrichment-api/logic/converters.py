def string_to_boolean(value : str) -> bool:
    if value.lower() == "no":
        return False
    return True

def null(value):
    return value

functions = {
    "float": float,
    "int": int,
    "string-to-boolean": string_to_boolean,
    "null": null
}