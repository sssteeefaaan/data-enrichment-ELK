api_configuration_schema = {
    "type": "object",
    "properties": {
        "apis": {
            "type": "object",
            "patternProperties": {
                "^[A-z$].*": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string"
                        },
                        "use": {
                            "type": "boolean"
                        },
                        "parameters": {
                            "type": "object",
                            "patternProperties":{
                                "^[A-z$].*": {
                                    "type": "object",
                                    "properties": {
                                        "positions": {
                                            "type": "array",
                                            "items": {
                                                "type": "string",
                                                "enum": ["endpoint", "query-params", "body", "headers", "field-mapping"]
                                            }
                                        },
                                        "key": {
                                            "type": "string"
                                        }
                                    },
                                    "required": ["positions", "key"],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "endpoint": {
                            "type": "string"
                        },
                        "method": {
                            "type": "string",
                            "enum": ["GET", "POST"]
                        },
                        "query-params": {
                            "type": "object",
                            "propertyNames": {
                                "pattern": "^[A-z$].*"
                            }
                        },
                        "headers": {
                            "type": "object",
                            "propertyNames": {
                                "pattern": "^[A-z$].*"
                            }
                        },
                        "body": {
                            "type": "object"
                        },
                        "map-fields": {
                            "type": "boolean"
                        },
                        "field-mapping": {
                            "$ref": "#/$defs/mappings"
                        },
                        "category": {
                            "type": "string"
                        },
                        "cache-lasts-days": {
                            "type": "integer",
                            "minimum": 1,
                            "exclusiveMaximum": 30
                        },
                        "additional-variables": {
                            "type": "object"
                        }
                    },
                    "required": [
                        "name",
                        "use",
                        "endpoint",
                        "method",
                        "map-fields",
                        "parameters"
                    ]
                }
            },
            "additionalProperties": False
        }
    },
    "required": [
        "apis"
    ],
    "additionalProperties": False,

    "$defs": {
        "mappings": {
            "type": ["string", "object"],
            "patternProperties": {
                "^[A-z$].*": { "$ref": "#/$defs/mappings" }
            },
            "additionalProperties": False
        }
    }
}