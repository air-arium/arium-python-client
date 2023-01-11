import logging.config
import os


def get_logger(logger_class="apac") -> logging.Logger:
    if logger_class.split('.')[0] not in logging.Logger.manager.loggerDict:
        logger_class = "apac"
    if logger_class not in get_logger.loggers:
        logger = logging.getLogger(logger_class)
        get_logger.loggers[logger_class] = logger
    return get_logger.loggers[logger_class]


try:
    logging.config.fileConfig(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging_config.ini'))
except Exception as e:
    try:
        logging.config.fileConfig('logging_config.ini')
    except KeyError as e:
        DEFAULT_LOGGING = {
            'version': 1,
            'disable_existing_loggers': False,
            'loggers': {
                '': {
                    'level': 'INFO',
                },
                'root': {
                    'level': 'INFO',
                },
                'apac': {
                    'level': 'INFO',
                },
                'auth': {
                    'level': 'INFO',
                },
            }
        }
        logging.config.dictConfig(DEFAULT_LOGGING)

get_logger.loggers = {}
