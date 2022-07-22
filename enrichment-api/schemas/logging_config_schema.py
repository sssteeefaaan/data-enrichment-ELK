log_config_schema = {
    "type": "object",
    "properties": {
        "version": {
            "type": "number"
        },
        "handlers": {
            "type": "object"
        },
        "loggers": {
            "type": "object"
        },
        "root": {
            "type": "object"
        },
        "formatters": {
            "type": "object"
        }
    },
    "required": [ "version", "handlers", "loggers", "root", "formatters" ]
}