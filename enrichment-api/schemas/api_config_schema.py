api_configuration_schema = {
    "type": "object",
    "properties": {
        "apis": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "use": {
                        "type": "boolean"
                    },
                    "combine-results": {
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
                                            "enum": ["endpoint", "query-params", "body", "headers", "response"]
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
                        "maximum": 120
                    },
                    "additional-variables": {
                        "type": "object"
                    }
                },
                "required": [
                    "name",
                    "use",
                    "combine-results",
                    "endpoint",
                    "method",
                    "map-fields",
                    "parameters"
                ],
                "additionalProperties": False
            },
            "minItems": 1
        },
        "duplicates-resolvers": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "function": {
                        "type": "string",
                        "enum": ["mean-average", "overwrite", "or", "and"]
                    },
                    "factors": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string"
                                },
                                "converter": {
                                    "type": "string",
                                    "enum": ["float", "int", "string-to-boolean", "null"],
                                    "default": "null"
                                },
                                "coefficient": {
                                    "type": "number",
                                    "default": 1
                                },
                                "path": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                }
                            },
                            "required": [
                                "name"
                            ],
                            "additionalProperties": False
                        },
                        "minItems": 1
                    }
                },
                "required": [
                    "path",
                    "function",
                    "factors"
                ],
                "additionalProperties": False
            }
        },
        "response-type": {
            "type": "string",
            "enum": ["full", "raw", "clean"]
        }
    },
    "additionalProperties": False,
    "required": [
        "apis",
        "response-type"
    ],
    "$defs": {
        "mappings": {
            "type": ["array", "object"],
            "patternProperties": {
                "^[A-z$].*": { "$ref": "#/$defs/mappings" }
            },
            "items": {
                "type": "string"
            },
            "additionalProperties": False
        }
    }
}