tortoise = {
    "connections": {
        "default": "postgres://admin:password@localhost:5432/database"
    },
    "apps": {
        "models": {
            "models": [
                "service.models"
            ],
            "default_connection": "default",
        }
    },
}

endpoint = "http://user:password@localhost:6503"
