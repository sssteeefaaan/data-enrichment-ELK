log_config_schema = {
    "type": "object",
    "properties": {
        "version": {
            "type": "number"
        },
        "formatters": {
            "type": "object"
        },
        "filters": {
            "type": "object"
        },
        "handlers": {
            "type": "object"
        },
        "loggers": {
            "type": "object",
            "properties": {
                "enrichment-api": {
                    "type": "object"
                }
            },
            "required": [ "enrichment-api" ]
        },
        "root": {
            "type": "object"
        },
        "disable_existing_loggers": {
            "type": "boolean"
        },
        "incremental": {
            "type": "boolean"
        }
    },
    "required": [ "handlers", "loggers", "root", "formatters" ],
    "additionalProperties": False
}