#!/usr/bin/python

import os, sys
import logging, logging.config
from logging import handlers
# from LogHelper import LogHelper

class LogHelper(object):
    def __init__(self):
        self.DEBUG = True
        self.LOG_PATH = 'EmailProcessor.log'
        self.LOGGING = {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
               'detail': {
                    'format': '%(name)s %(levelname)s %(asctime)s %(module)s %(process)d %(thread)d [%(pathname)s:%(lineno)d] %(message)s'
                },
                'verbose': {
                    'format': '%(name)s %(levelname)s %(asctime)s [%(pathname)s:%(lineno)d] %(message)s'
                },
                'simple': {
                    'format': '%(name)s %(levelname)s %(message)s'
                },
            },
            'handlers': {
               'console':{
                    'level':'NOTSET',
                    'class':'logging.StreamHandler',
                    'stream':sys.stderr,
                    'formatter': 'simple' #'simple'
                },
                'file':{
                    'level':'DEBUG',
                    'class':'logging.handlers.RotatingFileHandler',
                    'filename': os.path.join(os.getcwd(), self.LOG_PATH),
                    'formatter': 'verbose',
                    'maxBytes': 1024*1024*20,  # 20MB
                    'backupCount': 5,
                }
            },
            'loggers': {
                'CommonLogger': {
                    'handlers': ['console', 'file'] if self.DEBUG else ['file'],
                    'level': 'DEBUG' if self.DEBUG else 'INFO', #'INFO'
                    'propagate': False,
                    # very important in multithread environment, means disable propagation from current logger to the *root* logger.
                },
            }
        }
        self.common_logger = {
                    'handlers': ['console', 'file'] if self.DEBUG else ['file'],
                    'level': 'DEBUG' if self.DEBUG else 'INFO', #'INFO'
                    'propagate': False,
                    # very important in multithread environment, means disable propagation from current logger to the *root* logger.
        }

    def get_logger(self, logger_name=None):
        if isinstance(logger_name,str) or isinstance(logger_name,unicode):
            self.LOGGING['loggers'][logger_name] = self.common_logger
            logging.config.dictConfig(self.LOGGING)
            logger = logging.getLogger(logger_name)
        else:
            logging.config.dictConfig(self.LOGGING)
            logger = logging.getLogger("CommonLogger")

        return logger

if __name__ == '__main__':
    logger = LogHelper().get_logger('myLogger')
    logger.info('Info')
    logger.debug('Debug')
    logger.error('Error')
