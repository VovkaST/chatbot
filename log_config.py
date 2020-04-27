from settings import WORK_DIR

CONFIG = {
        'version': 1,
        'formatters': {
            'bot_log': {
                'format': '%(asctime)s %(levelname)s: %(message)s',
                'datefmt': '%Y-%d-%m %H:%M:%S'
            },
        },
        'handlers': {
            'log_handler': {
                'class': 'logging.FileHandler',
                'formatter': 'bot_log',
                'filename': str(WORK_DIR / 'bot.log'),
                'encoding': 'UTF-8'
            },
            'crash_handler': {
                'class': 'logging.FileHandler',
                'formatter': 'bot_log',
                'filename': str(WORK_DIR / 'botCrash.log'),
                'encoding': 'UTF-8',
                'delay': True
            },
        },
        'loggers': {
            'bot': {
                'handlers': ['log_handler'],
                'level': 'INFO',
            },
            'bot_crash': {
                'handlers': ['crash_handler'],
                'level': 'CRITICAL',
            }
        },
    }
