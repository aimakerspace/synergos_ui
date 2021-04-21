###############################
# Configurations - navigation #
###############################

_nav_config_dev = {
    'app': {
        'host': "0.0.0.0",
        'port': 12345
    },
    'db': {
        "path": "./test_db_210325.json"
    },
    'source_list': {
        '01_mlflow': "http://localhost/mlflow/",
        '02_rabbitmq': "http://localhost:15672",
        '03_graylog': "http://localhost:9000",
        '04_amundsen': "http://localhost:5000",
        '05_neo4j': "http://localhost:7474/browser"
    }
}

_nav_config_prod = {
    'app': {
        'host': "0.0.0.0",
        'port': 12345
    },
    'db': {
        "path": "./test_db_210325.json"
    },
    'source_list': {
        '01_mlflow': "http://localhost/mlflow/",
        '02_rabbitmq': "http://localhost:15672",
        '03_graylog': "http://localhost:9000",
        '04_amundsen': "http://localhost:5000",
        '05_neo4j': "http://localhost:7474/browser"
    }
}

nav_config = {
    "ENV": "DEV", # define which key to load, must be the same as defined
    "DEV": _nav_config_dev,
    "PROD": _nav_config_prod
}