import logging
import traceback

import sys


def info(msg, extra={}):
    logging.info(msg, extra=extra)


def warn(msg, extra={}):
    logging.warning(msg, extra=extra)


def error(msg, extra={}):
    logging.error(msg, extra=extra)


def critical(msg, extra={}):
    logging.critical(msg, extra=extra)


def debug(msg, extra={}):
    logging.debug(msg, extra=extra)


def log_uncaught_exceptions(type, value, tb):
    print('log_uncaught_exceptions called')
    try:
        critical('{0}: {1}'.format(str(type), str(value)), {'traceback': ''.join(traceback.format_tb(tb))})
    except:
        print("Error occured during log:")
        print('{0}: {1}'.format(str(type), str(value)))
        print('traceback'.join(traceback.format_tb(tb)))


def init_exceptionhook():
    sys.excepthook = log_uncaught_exceptions


def init():
    init_exceptionhook()
