#!/usr/bin/python2
# -*- coding: utf-8 -*-

from os import getenv

# Update the DB every X hours
hours = int(getenv('UPDATE_HOURS', '6'))

# Filename for application settings
app_settings = getenv('APP_SETTINGS', None)


def configure_app(app):
    if app_settings:
        app.config.from_envvar('APP_SETTINGS')
