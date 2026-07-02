"""Configuração de logging do Django com arquivos separados por aplicação."""
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"

LOG_DIR.mkdir(exist_ok=True)

APPS = [

    "ibge",

    "ingestion",

]


handlers = {}

loggers = {}


for app in APPS:

    handler_name = f"{app}_file"

    handlers[handler_name] = {

        "level": "INFO",

        "class": "logging.FileHandler",

        "filename": LOG_DIR / f"{app}.log",

        "encoding": "utf-8",

        "formatter": "default",

    }


    loggers[app] = {

        "handlers": [handler_name],

        "level": "INFO",

        "propagate": False,

    }


LOGGING = {

    "version": 1,

    "disable_existing_loggers": False,

    "formatters": {

        "default": {

            "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s"

        }

    },

    "handlers": handlers,

    "loggers": loggers,

}