api_configuration_schema = {
    "type": "object",
    "properties": {
        "apis": {
            "type": "object",
            "patternProperties": {
                "^.*$": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string"
                        },
                        "use": {
                            "type": "boolean"
                        },
                        "endpoint": {
                            "type": "string"
                        },
                        "method": {
                            "type": "string",
                            "enum": ["GET", "POST"]
                        },
                        "query-params": {
                            "type": "object"
                        },
                        "headers": {
                            "type": "object"
                        },
                        "body": {
                            "type": "object"
                        },
                        "field-mapping": {
                            "type": "object"
                        },
                        "vars": {
                            "type": "object"
                        }
                    },
                    "required": [
                        "name",
                        "use",
                        "endpoint",
                        "method",
                        "field-mapping"
                    ]
                }
            }
        }
    },
    "required": [
        "apis"
    ]
}