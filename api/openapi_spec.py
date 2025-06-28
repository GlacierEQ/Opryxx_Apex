"""
OpenAPI/Swagger Specification for OPRYXX API
"""

OPENAPI_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "OPRYXX API",
        "version": "2.0.0",
        "description": "Ultimate PC Recovery and Optimization System API"
    },
    "servers": [
        {"url": "http://localhost:8080", "description": "Local development server"}
    ],
    "paths": {
        "/api/v1/health": {
            "get": {
                "summary": "System Health Check",
                "responses": {
                    "200": {
                        "description": "System health status",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/HealthResponse"}
                            }
                        }
                    }
                }
            }
        },
        "/api/v1/optimize": {
            "post": {
                "summary": "Trigger System Optimization",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/OptimizeRequest"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Optimization started",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/OptimizeResponse"}
                            }
                        }
                    }
                }
            }
        },
        "/api/v1/recovery": {
            "post": {
                "summary": "Execute Recovery Operation",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/RecoveryRequest"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Recovery operation executed",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/RecoveryResponse"}
                            }
                        }
                    }
                }
            }
        }
    },
    "components": {
        "schemas": {
            "HealthResponse": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["healthy", "unhealthy"]},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "uptime": {"type": "number"},
                    "system": {
                        "type": "object",
                        "properties": {
                            "cpu_percent": {"type": "number"},
                            "memory_percent": {"type": "number"},
                            "disk_percent": {"type": "number"}
                        }
                    }
                }
            },
            "OptimizeRequest": {
                "type": "object",
                "properties": {
                    "mode": {"type": "string", "enum": ["balanced", "performance", "ultra", "extreme"]},
                    "target": {"type": "string", "enum": ["memory", "cpu", "disk", "all"]}
                }
            },
            "OptimizeResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "optimizations_applied": {"type": "integer"}
                }
            },
            "RecoveryRequest": {
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "enum": ["safe_mode_exit", "boot_repair", "system_check"]},
                    "force": {"type": "boolean"}
                },
                "required": ["operation"]
            },
            "RecoveryResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "operation_id": {"type": "string"}
                }
            }
        }
    }
}