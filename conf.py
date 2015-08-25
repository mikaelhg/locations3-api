#!/usr/bin/python2
# -*- coding: utf-8 -*-

from os import getenv
import logging
from colorlog import ColoredFormatter

# Should we use MaxMind or EdgeScape
dbtype = getenv('DB_TYPE', 'maxmind')

# Update the DB every X hours
hours = int(getenv('UPDATE_HOURS', '6'))

# Filename for application settings
__app_settings = getenv('APP_SETTINGS', None)


def configure_app(app):
    if __app_settings:
        app.config.from_envvar('APP_SETTINGS')

    formatter = ColoredFormatter(
        '%(asctime)s %(log_color)s%(levelname)-8s%(reset)s %(message)s (%(name)s)',
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )

    stream = logging.StreamHandler()
    stream.setLevel(logging.INFO)
    stream.setFormatter(formatter)

    logger = logging.root
    logger.setLevel(logging.INFO)
    logger.addHandler(stream)
